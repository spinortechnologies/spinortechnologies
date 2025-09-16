import pandas as pd
from decimal import Decimal, getcontext
from itertools import combinations, permutations
import networkx as nx
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

getcontext().prec = 60  # precisión alta

MAX_CYCLE_LEN = 1000
FEE_DEFAULT = 0.003

# ---------------------- Funciones AMM ----------------------
def get_amount_out(amount_in: Decimal, reserve_in: Decimal, reserve_out: Decimal, fee: float = FEE_DEFAULT) -> Decimal:
    if amount_in <= 0 or reserve_in <= 0 or reserve_out <= 0:
        return Decimal(0)
    fee_multiplier = Decimal(1) - Decimal(str(fee))
    amount_in_with_fee = amount_in * fee_multiplier
    numerator = amount_in_with_fee * reserve_out
    denominator = reserve_in + amount_in_with_fee
    return numerator / denominator

def simulate_cycle_final_amount(cycle, amount_in=Decimal('1')):
    amt = Decimal(amount_in)
    local_reserves = [(Decimal(e["reserve_in"]), Decimal(e["reserve_out"]), e.get("fee", FEE_DEFAULT)) for e in cycle]
    for i, e in enumerate(cycle):
        reserve_in, reserve_out, fee = local_reserves[i]
        out = get_amount_out(amt, reserve_in, reserve_out, fee)
        reserve_in += amt
        reserve_out -= out
        local_reserves[i] = (reserve_in, reserve_out, fee)
        amt = out
    return amt

def profit_for_cycle(cycle, x=Decimal('1')):
    return simulate_cycle_final_amount(cycle, x) - x

# ---------------------- Leer CSVs ----------------------
df_pairs = pd.read_csv("pairs.csv")
df_daily = pd.read_csv("pair_day_data.csv")
df_swaps = pd.read_csv("pair_swaps.csv")
df_liq = pd.read_csv("pair_liquidity.csv")

# ---------------------- Construir grafo ----------------------
def build_graph(df_pairs):
    G = nx.DiGraph()
    for _, row in df_pairs.iterrows():
        t0, t1 = row["token0"], row["token1"]
        r0, r1 = Decimal(str(row["reserve0"])), Decimal(str(row["reserve1"]))
        pair_id = row["pair_id"]
        # Añadimos ambos sentidos
        G.add_edge(t0, t1, pair_id=pair_id, reserve_in=r0, reserve_out=r1, fee=FEE_DEFAULT)
        G.add_edge(t1, t0, pair_id=pair_id, reserve_in=r1, reserve_out=r0, fee=FEE_DEFAULT)
    return G

G = build_graph(df_pairs)

# ---------------------- Generar ciclos ----------------------
def find_cycles(G, max_len=MAX_CYCLE_LEN):
    cycles_list = []
    nodes = list(G.nodes)
    
    def dfs(path, visited):
        if len(path) > max_len:
            return
        last_node = path[-1]
        for neighbor in G.successors(last_node):
            if neighbor == path[0] and len(path) >= 2:
                cycles_list.append(path + [neighbor])
            elif neighbor not in visited:
                dfs(path + [neighbor], visited | {neighbor})
    
    for n in nodes:
        dfs([n], {n})
    
    # eliminar duplicados por rotación
    unique_cycles = []
    seen = set()
    for c in cycles_list:
        sig = tuple(sorted(c))
        if sig not in seen:
            seen.add(sig)
            unique_cycles.append(c)
    return unique_cycles

all_cycles = find_cycles(G)

# ---------------------- Extraer features ----------------------
def extract_cycle_features(cycle, G, df_pairs, df_daily, df_swaps, df_liq):
    features = {}
    features["length"] = len(cycle)-1
    reserves = []
    fees = []
    volumes = []
    liquidity_changes = []
    avg_swaps = []
    num_swaps = []
    
    for i in range(len(cycle)-1):
        u, v = cycle[i], cycle[i+1]
        edge = G[u][v]
        pair_id = edge["pair_id"]
        reserves.append(float(edge["reserve_in"]))
        fees.append(float(edge["fee"]))
        
        # volumen diario
        vol_row = df_daily[df_daily["pair_id"]==pair_id]
        volumes.append(vol_row["dailyVolumeUSD"].values[0] if not vol_row.empty else 0)
        
        # liquidez
        liq_row = df_liq[df_liq["pair_id"]==pair_id]
        liquidity_changes.append(liq_row["liquidity_added_removed"].values[0] if not liq_row.empty else 0)
        
        # swaps
        swaps_row = df_swaps[df_swaps["pair_id"]==pair_id]
        avg_swaps.append(swaps_row["avg_swap_price"].values[0] if not swaps_row.empty else 0)
        num_swaps.append(swaps_row["num_swaps_last_hour"].values[0] if not swaps_row.empty else 0)
    
    features["reserve_min"] = min(reserves) if reserves else 0
    features["reserve_max"] = max(reserves) if reserves else 0
    features["reserve_mean"] = sum(reserves)/len(reserves) if reserves else 0
    features["fee_total"] = sum(fees)
    features["volume_total"] = sum(volumes)
    features["liquidity_total"] = sum(liquidity_changes)
    features["avg_swap_price_mean"] = sum(avg_swaps)/len(avg_swaps) if avg_swaps else 0
    features["num_swaps_total"] = sum(num_swaps)
    
    # profit simulado con 1 unidad de token inicial
    cycle_edges = [G[cycle[i]][cycle[i+1]] for i in range(len(cycle)-1)]
    features["profit"] = float(profit_for_cycle(cycle_edges, Decimal('1')))
    
    features["cycle_tokens"] = "-".join(cycle)
    
    return features

features_list = [extract_cycle_features(c, G, df_pairs, df_daily, df_swaps, df_liq) for c in all_cycles]
df_cycles = pd.DataFrame(features_list)
df_cycles.to_csv("cycles_features.csv", index=False)
print("✅ Features de ciclos generadas y guardadas.")

# ---------------------- ML: RandomForest ----------------------
X = df_cycles.drop(columns=["profit","cycle_tokens"])
y = df_cycles["profit"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(f"R2 score: {r2_score(y_test, y_pred):.4f}")

# importancia de features
importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
print("🔹 Importancia de features:")
print(importances)
