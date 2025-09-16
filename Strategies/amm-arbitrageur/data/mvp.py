import requests
import pandas as pd
from datetime import datetime, timezone
from decimal import Decimal, getcontext
import time

getcontext().prec = 60  # precisión alta

FEE_DEFAULT = 0.003  # fee AMM por defecto

# ------------------- Configuración TheGraph -------------------
API_KEY = "5416676bb1355388c99743344da1b45a"
SUBGRAPH_ID = "A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum"  # PancakeSwap V2
URL = f"https://gateway.thegraph.com/api/subgraphs/id/{SUBGRAPH_ID}"
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

BATCH_SIZE = 1000
MAX_PAIRS = 50

# ------------------- Funciones AMM -------------------
def get_amount_out(amount_in: Decimal, reserve_in: Decimal, reserve_out: Decimal, fee: float = FEE_DEFAULT) -> Decimal:
    if amount_in <= 0 or reserve_in <= 0 or reserve_out <= 0:
        return Decimal(0)
    fee_multiplier = Decimal(1) - Decimal(str(fee))
    amount_in_with_fee = amount_in * fee_multiplier
    numerator = amount_in_with_fee * reserve_out
    denominator = reserve_in + amount_in_with_fee
    return numerator / denominator

# ------------------- Extracción de pares -------------------
def fetch_top_pairs_by_liquidity_and_volume(top_n=MAX_PAIRS):
    pairs = []
    skip = 0
    while True:
        query = f"""
        {{
            pairs(first: {BATCH_SIZE}, skip: {skip}, orderBy: reserveUSD, orderDirection: desc) {{
                id
                token0 {{ symbol }}
                token1 {{ symbol }}
                reserve0
                reserve1
            }}
        }}
        """
        resp = requests.post(URL, headers=HEADERS, json={"query": query}).json()
        if "data" not in resp or resp["data"] is None:
            break
        data = resp["data"]["pairs"]
        if not data:
            break
        for p in data:
            pairs.append(p)
            if len(pairs) >= top_n:
                return pairs
        skip += BATCH_SIZE
    return pairs

# ------------------- Construir grafo -------------------
def build_graph_from_pools(pools):
    graph = {}
    for p in pools:
        t0, t1 = p["token0"]["symbol"], p["token1"]["symbol"]
        r0, r1 = Decimal(str(p["reserve0"])), Decimal(str(p["reserve1"]))

        # t0 -> t1
        graph.setdefault(t0, []).append({
            "to": t1,
            "pair_id": p["id"],
            "reserve_in": r0,
            "reserve_out": r1,
            "fee": FEE_DEFAULT,
            "token_in": t0,
            "token_out": t1
        })
        # t1 -> t0
        graph.setdefault(t1, []).append({
            "to": t0,
            "pair_id": p["id"],
            "reserve_in": r1,
            "reserve_out": r0,
            "fee": FEE_DEFAULT,
            "token_in": t1,
            "token_out": t0
        })
    return graph

# ------------------- Detección de ciclos -------------------
def find_simple_cycles(graph, max_len=3):
    cycles = []
    nodes = list(graph.keys())

    def dfs(start, current, path_edges, visited, depth):
        if depth > max_len:
            return
        for edge in graph.get(current, []):
            nxt = edge["to"]
            if nxt == start and path_edges:
                cycles.append(path_edges + [edge])
            if nxt in visited or nxt == start:
                continue
            dfs(start, nxt, path_edges + [edge], visited | {nxt}, depth + 1)

    for n in nodes:
        dfs(n, n, [], {n}, 1)
    return cycles

# ------------------- Simulación y profit -------------------
def simulate_cycle_final_amount(cycle, amount_in: Decimal):
    amt = Decimal(amount_in)
    local_reserves = [(e["reserve_in"], e["reserve_out"], e["fee"]) for e in cycle]
    for i, e in enumerate(cycle):
        reserve_in, reserve_out, fee = local_reserves[i]
        out = get_amount_out(amt, reserve_in, reserve_out, fee)
        reserve_in += amt
        reserve_out -= out
        local_reserves[i] = (reserve_in, reserve_out, fee)
        amt = out
    return amt

def profit_for_cycle(cycle, x: Decimal):
    return simulate_cycle_final_amount(cycle, x) - x

def maximize_profit_for_cycle(cycle, x_min=Decimal('1e-12'), x_max=None, tol=1e-6, max_iter=80):
    first_res_in = Decimal(cycle[0]["reserve_in"])
    if x_max is None:
        x_max = max(Decimal('1e-6'), first_res_in * Decimal('0.2'))
    if x_max <= x_min:
        return (Decimal(0), Decimal(0))

    phi = Decimal((1 + 5 ** 0.5) / 2)
    invphi = 1 / phi
    a, b = Decimal(x_min), Decimal(x_max)
    c, d = b - (b - a) * Decimal(invphi), a + (b - a) * Decimal(invphi)
    fc, fd = profit_for_cycle(cycle, c), profit_for_cycle(cycle, d)
    iter_count = 0
    while (b - a) > Decimal(str(tol)) and iter_count < max_iter:
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - (b - a) * Decimal(invphi)
            fc = profit_for_cycle(cycle, c)
        else:
            a, c, fc = c, d, fd
            d = a + (b - a) * Decimal(invphi)
            fd = profit_for_cycle(cycle, d)
        iter_count += 1
    candidates = [a, b, c, d]
    best_x = max(candidates, key=lambda xx: float(profit_for_cycle(cycle, xx)))
    best_profit = profit_for_cycle(cycle, best_x)
    return (best_x, best_profit)

# ------------------- Pipeline principal -------------------
def find_and_optimize_cycles_from_graph(pools, max_cycle_len=3, min_profit_threshold=1e-8):
    graph = build_graph_from_pools(pools)
    cycles = find_simple_cycles(graph, max_len=max_cycle_len)
    print(f"[INFO] Ciclos candidatos encontrados: {len(cycles)}")
    results = []
    for i, cyc in enumerate(cycles):
        x_best, profit_best = maximize_profit_for_cycle(cyc)
        profit_f = float(profit_best)
        x_f = float(x_best)
        if profit_f > min_profit_threshold:
            token_path = [cyc[0]["token_in"]] + [e["token_out"] for e in cyc]
            results.append({
                "cycle_index": i,
                "token_path": token_path,
                "pair_ids": [e["pair_id"] for e in cyc],
                "best_x": x_f,
                "best_profit": profit_f
            })
    print(f"[INFO] Ciclos rentables: {len(results)}")
    return results

# ------------------- Ejecución -------------------
if __name__ == "__main__":
    print("📥 Descargando pares...")
    all_pairs = fetch_top_pairs_by_liquidity_and_volume(top_n=MAX_PAIRS)
    results = find_and_optimize_cycles_from_graph(all_pairs, max_cycle_len=3, min_profit_threshold=1e-6)

    for r in results:
        print(r)
