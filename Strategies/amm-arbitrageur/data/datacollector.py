import requests
import pandas as pd
from datetime import datetime, timezone
import time

# ------------------- Configuración -------------------
API_KEY = "5416676bb1355388c99743344da1b45a"
SUBGRAPH_ID = "A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum"  # PancakeSwap V2
URL = f"https://gateway.thegraph.com/api/subgraphs/id/{SUBGRAPH_ID}"
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

BATCH_SIZE = 200  # aumentado para traer más resultados por llamada
MAX_PAIRS = 200  # por ejemplo
MAX_PAIRS_DAYDATA = 200
MAX_SWAPS = 200
SLEEP_BETWEEN_CALLS = 0.5  # segundos de espera entre peticiones

def fetch_top_pairs_by_liquidity_and_volume(top_n=MAX_PAIRS):
    pairs = []
    skip = 0
    while True:
        query = f"""
        {{
            pairs(first: {BATCH_SIZE}, skip: {skip}, orderBy: reserveUSD, orderDirection: desc) {{
                id
                token0 {{ id symbol name decimals tradeVolumeUSD }}
                token1 {{ id symbol name decimals tradeVolumeUSD }}
                reserve0
                reserve1
                reserveUSD
                volumeUSD
            }}
        }}
        """
        resp = requests.post(URL, headers=HEADERS, json={"query": query}).json()
        time.sleep(SLEEP_BETWEEN_CALLS)  # <-- espera para no saturar la API

        if "data" not in resp or resp["data"] is None:
            break
        data = resp["data"]["pairs"]
        if not data:
            break

        for p in data:
            token0_vol = float(p["token0"].get("tradeVolumeUSD", 0))
            token1_vol = float(p["token1"].get("tradeVolumeUSD", 0))
            if token0_vol > 10000 or token1_vol > 10000:
                pairs.append(p)
                if len(pairs) >= top_n:
                    return pairs
        skip += BATCH_SIZE
    return pairs

# ------------------- Datos diarios -------------------
def fetch_pair_day_data(pair_map):
    all_day_data = []
    pair_ids = list(pair_map.keys())[:MAX_PAIRS_DAYDATA]

    for pid in pair_ids:
        query = f"""
        {{
            pairDayDatas(first: 1, where: {{pairAddress: "{pid}"}}, orderBy: date, orderDirection: desc) {{
                dailyTxns
                dailyVolumeToken0
                dailyVolumeToken1
                dailyVolumeUSD
                date
                id
                pairAddress
                reserve0
                reserve1
                reserveUSD
                totalSupply
            }}
        }}
        """
        resp = requests.post(URL, headers=HEADERS, json={"query": query}).json()
        time.sleep(SLEEP_BETWEEN_CALLS)
        if not resp or "data" not in resp or resp["data"] is None:
            print(f"⚠️ No data para pair {pid}: {resp}")
            continue

        d_list = resp["data"].get("pairDayDatas")
        if not d_list:
            print(f"⚠️ pairDayData vacío para pair {pid}")
            continue
        d = d_list[0]

        token0 = pair_map[pid]["token0"]
        token1 = pair_map[pid]["token1"]

        price0_1 = float(d["reserve1"]) / float(d["reserve0"]) if float(d["reserve0"])>0 else None
        price1_0 = float(d["reserve0"]) / float(d["reserve1"]) if float(d["reserve1"])>0 else None

        all_day_data.append({
            "pair_id": pid,
            "date": datetime.utcfromtimestamp(int(d["date"])).strftime("%Y-%m-%d"),
            "token0": token0,
            "token1": token1,
            "reserve0": float(d["reserve0"]),
            "reserve1": float(d["reserve1"]),
            "reserveUSD": float(d["reserveUSD"]),
            "dailyVolumeToken0": float(d["dailyVolumeToken0"]),
            "dailyVolumeToken1": float(d["dailyVolumeToken1"]),
            "dailyVolumeUSD": float(d["dailyVolumeUSD"]),
            "dailyTxns": int(d["dailyTxns"]),
            "totalSupply": float(d["totalSupply"]),
            "price_token0_token1": price0_1,
            "price_token1_token0": price1_0
        })
        print(f"✅ Datos diarios descargados para pair {pid}")
    return all_day_data

# ------------------- Swaps -------------------
def fetch_pair_swaps(pair_ids):
    all_swaps = []
    now_ts = int(datetime.now(timezone.utc).timestamp())
    one_hour_ago = now_ts - 3600

    for pid in pair_ids[:MAX_PAIRS_DAYDATA]:
        skip = 0
        swaps_list = []
        while True:
            query = f"""
            {{
                swaps(first: {BATCH_SIZE}, skip: {skip}, orderBy: timestamp, orderDirection: desc, where: {{pair: "{pid}"}}) {{
                    id
                    amount0In
                    amount1In
                    amount0Out
                    amount1Out
                    amountUSD
                    timestamp
                }}
            }}
            """
            resp = requests.post(URL, headers=HEADERS, json={"query": query}).json()
            time.sleep(SLEEP_BETWEEN_CALLS)
            swaps = resp.get("data", {}).get("swaps")
            if not swaps or len(swaps_list) >= MAX_SWAPS:
                break
            for s in swaps[:MAX_SWAPS - len(swaps_list)]:
                amount0 = float(s["amount0In"]) + float(s["amount0Out"])
                amount1 = float(s["amount1In"]) + float(s["amount1Out"])
                price = amount1 / amount0 if amount0 > 0 else None
                swaps_list.append({"timestamp": int(s["timestamp"]), "price": price})
            skip += BATCH_SIZE

        num_swaps_hour = sum(1 for s in swaps_list if s["timestamp"] >= one_hour_ago)
        avg_price = sum(s["price"] for s in swaps_list if s["price"] is not None)/num_swaps_hour if num_swaps_hour>0 else None

        all_swaps.append({
            "pair_id": pid,
            "num_swaps_last_hour": num_swaps_hour,
            "avg_swap_price": avg_price
        })
        print(f"✅ Datos d descargados para pair ")
    return all_swaps



# ------------------- Liquidez -------------------
def fetch_pair_liquidity(pair_ids):
    all_liq = []
    for pid in pair_ids[:MAX_PAIRS_DAYDATA]:
        query_mint = f"""{{ mints(first: {MAX_SWAPS}, where: {{pair: "{pid}"}}) {{ amountUSD }} }}"""
        resp_mint = requests.post(URL, headers=HEADERS, json={"query": query_mint}).json()
        mints_sum = sum(float(m["amountUSD"]) for m in resp_mint.get("data", {}).get("mints", []) if m["amountUSD"] not in (None, ""))

        query_burn = f"""{{ burns(first: {MAX_SWAPS}, where: {{pair: "{pid}"}}) {{ amountUSD }} }}"""
        resp_burn = requests.post(URL, headers=HEADERS, json={"query": query_burn}).json()
        time.sleep(SLEEP_BETWEEN_CALLS)
        burns_sum = sum(float(b["amountUSD"]) for b in resp_burn.get("data", {}).get("burns", []) if b["amountUSD"] not in (None, ""))

        all_liq.append({
            "pair_id": pid,
            "liquidity_added_removed": mints_sum - burns_sum
        })
    return all_liq

# ------------------- Script principal -------------------
if __name__ == "__main__":
    print("📥 Descargando pares filtrados por liquidez y volumen...")
    all_pairs = fetch_top_pairs_by_liquidity_and_volume(top_n=MAX_PAIRS)
    pair_map = {p["id"]: {"token0": p["token0"]["symbol"], "token1": p["token1"]["symbol"]} for p in all_pairs}
    print(pair_map)

    print("📥 Descargando datos diarios de pares...")
    daily_data = fetch_pair_day_data(pair_map)

    print("📥 Descargando swaps...")
    swaps_data = fetch_pair_swaps(list(pair_map.keys()))

    print("📥 Descargando liquidez mints/burns...")
    liq_data = fetch_pair_liquidity(list(pair_map.keys()))

    # Convertimos a DataFrame
    df_daily = pd.DataFrame(daily_data)
    df_swaps = pd.DataFrame(swaps_data)
    df_liq = pd.DataFrame(liq_data)
    df_pairs = pd.DataFrame([{
        "pair_id": p["id"],
        "token0": p["token0"]["symbol"],
        "token1": p["token1"]["symbol"],
        "reserve0": float(p["reserve0"]),
        "reserve1": float(p["reserve1"]),
        "reserveUSD": float(p["reserveUSD"]),
        "volumeUSD": float(p["volumeUSD"]),
        "price_token0_token1": float(p["reserve1"])/float(p["reserve0"]) if float(p["reserve0"])>0 else None,
        "price_token1_token0": float(p["reserve0"])/float(p["reserve1"]) if float(p["reserve1"])>0 else None
    } for p in all_pairs])

    # Guardar CSV
    df_pairs.to_csv("pairs.csv", index=False)
    df_daily.to_csv("pair_day_data.csv", index=False)
    df_swaps.to_csv("pair_swaps.csv", index=False)
    df_liq.to_csv("pair_liquidity.csv", index=False)

    print("💾 CSV generados correctamente.")

"""

Detectar ciclos de arbitraje + optimizar tamaño de operación (x) para cada ciclo.

Entrada esperada:
- pools: lista de dicts, cada dict:
    {
      "pair_id": "0x....",
      "token0": "TOKEN0_SYMBOL_OR_ADDR",
      "token1": "TOKEN1_SYMBOL_OR_ADDR",
      "reserve0": float(...),   # cantidad token0 en pool
      "reserve1": float(...),   # cantidad token1 en pool
      "fee": 0.003  # comision del AMM (opcional, por defecto 0.003)
    }

Ejemplo de pools mínimo:
pools = [
  {"pair_id":"0xA", "token0":"WETH","token1":"USDC","reserve0":100.0,"reserve1":200000.0},
  {"pair_id":"0xB", "token0":"USDC","token1":"ABC","reserve0":50000.0,"reserve1":1000000.0},
  ...
]


from math import isclose
from decimal import Decimal, getcontext
from typing import List, Dict, Tuple
import time

# mayor precisión para operaciones con grandes cantidades
getcontext().prec = 60

FEE_DEFAULT = 0.003  # 0.3%

# ------------------ utilidades AMM UniswapV2 ------------------

def get_amount_out(amount_in: Decimal, reserve_in: Decimal, reserve_out: Decimal, fee: float = FEE_DEFAULT) -> Decimal:
    Uniswap V2 getAmountOut using Decimal for precision.
    if amount_in <= 0 or reserve_in <= 0 or reserve_out <= 0:
        return Decimal(0)
    fee_multiplier = Decimal(1) - Decimal(str(fee))
    amount_in_with_fee = amount_in * fee_multiplier
    numerator = amount_in_with_fee * reserve_out
    denominator = reserve_in + amount_in_with_fee
    return numerator / denominator

# ------------------ construir grafo ------------------

def build_graph_from_pools(pools: List[Dict]) -> Dict[str, List[Dict]]:

    Construye un grafo dirigido: graph[token] = list of edges

    graph = {}
    for p in pools:
        t0 = p["token0"]
        t1 = p["token1"]
        r0 = Decimal(str(p["reserve0"]))
        r1 = Decimal(str(p["reserve1"]))
        fee = p.get("fee", FEE_DEFAULT)

        # arista t0 -> t1 (input t0 gives output t1)
        graph.setdefault(t0, []).append({
            "to": t1,
            "pair_id": p["pair_id"],
            "reserve_in": r0,
            "reserve_out": r1,
            "fee": fee,
            "token_in": t0,
            "token_out": t1
        })
        # arista t1 -> t0
        graph.setdefault(t1, []).append({
            "to": t0,
            "pair_id": p["pair_id"],
            "reserve_in": r1,
            "reserve_out": r0,
            "fee": fee,
            "token_in": t1,
            "token_out": t0
        })
    return graph

# ------------------ búsqueda de ciclos simples (DFS limitado) ------------------

def find_simple_cycles(graph: Dict[str, List[Dict]], max_len: int = 4) -> List[List[Dict]]:

    Encuentra ciclos simples hasta longitud max_len.
    Devuelve lista de ciclos; cada ciclo es lista de edges (en orden).
    Nota: esto puede ser costoso si hay muchos nodos; max_len pequeño (3 o 4) es práctico.
    cycles = []
    nodes = list(graph.keys())

    def dfs(start, current, path_edges, visited, depth):
        if depth > max_len:
            return
        for edge in graph.get(current, []):
            nxt = edge["to"]
            # si volvemos al inicio y path non-empty -> ciclo válido
            if nxt == start and path_edges:
                # formamos ciclo: path_edges + [edge]
                cycle = path_edges + [edge]
                # Para evitar ciclos rotacionales duplicados, normalizamos por el menor pair_id/token sequence
                cycles.append(cycle)
            # evitar repetir nodo en el mismo path (simple cycle)
            if nxt in visited or nxt == start:
                continue
            # continuar
            dfs(start, nxt, path_edges + [edge], visited | {nxt}, depth + 1)

    for n in nodes:
        dfs(n, n, [], {n}, 1)
    # eliminar duplicados equivalentes (rotaciones)
    unique = []
    seen_signatures = set()
    for cyc in cycles:
        # signature: sequence of token_in-token_out or pair_ids normalized by rotation
        toks = [e["token_in"] for e in cyc] + [cyc[-1]["token_out"]]
        # rotate to smallest lexicographic representation
        reps = []
        L = len(toks) - 1
        for k in range(L):
            rotated = toks[k:k+L] + toks[:k]
            reps.append(tuple(rotated))
        sig = min(reps)
        if sig not in seen_signatures:
            seen_signatures.add(sig)
            unique.append(cyc)
    return unique

# ------------------ simular ciclo y función de profit ------------------

def simulate_cycle_final_amount(cycle: List[Dict], amount_in: Decimal) -> Decimal:

    Simula swaps sucesivos siguiendo los edges de 'cycle'.
    amount_in = cantidad inicial del token_in del primer edge.
    Devuelve la cantidad final (del mismo token de inicio) después de aplicar los swaps del ciclo.
    amt = Decimal(amount_in)
    # Para cada edge, aplicamos get_amount_out con las reservas actuales.
    # Importante: usamos reservas estáticas (reserva actual), NO actualizamos reservas como si ejecutáramos la operación
    # Si se quiere simular impacto secuencial real hay que actualizar reservas (más costoso). Pero para flashswap ciclo
    # y simulación exacta de slippage, actualizamos reservas en cada paso.
    # Implementamos actualización de reservas para precisión.
    # Creamos copias locales de reservas:
    local_reserves = []
    for e in cycle:
        local_reserves.append((Decimal(e["reserve_in"]), Decimal(e["reserve_out"]), e["fee"]))
    # Recorremos edges y actualizamos reservas conforme swap (x -> y)
    for i, e in enumerate(cycle):
        reserve_in, reserve_out, fee = local_reserves[i]
        out = get_amount_out(amt, reserve_in, reserve_out, fee)
        # actualizar reservas: reserve_in += amt , reserve_out -= out
        reserve_in = reserve_in + amt
        reserve_out = reserve_out - out
        local_reserves[i] = (reserve_in, reserve_out, fee)
        amt = out  # para siguiente swap
    # amt ahora es cantidad en token_out del último swap.
    # Si el ciclo termina en el token inicial, amt es cantidad final
    return amt

def profit_for_cycle(cycle: List[Dict], x: Decimal) -> Decimal:

    profit = final_amount - x, as Decimal

    final = simulate_cycle_final_amount(cycle, x)
    return final - Decimal(x)

# ------------------ optimización unidimensional (golden-section) ------------------

def maximize_profit_for_cycle(cycle: List[Dict], x_min: Decimal = Decimal('1e-12'), x_max: Decimal = None, tol: float = 1e-6, max_iter=80) -> Tuple[Decimal, Decimal]:

    Busca x que maximice profit_for_cycle dentro de [x_min, x_max].
    Si x_max is None, lo estimamos como fracción de la mínima reserva de entrada en el ciclo.
    Devuelve (x_best, profit_best)

    # determinar token inicial y reservas límites
    # tomamos reserva_in del primer edge
    first_res_in = Decimal(cycle[0]["reserve_in"])
    # max x razonable: por ejemplo 20% de la reserva de input del primer edge (evita slippage extremo)
    if x_max is None:
        x_max = max(Decimal('1e-6'), first_res_in * Decimal('0.2'))

    # si x_max <= x_min, devolvemos 0
    if x_max <= x_min:
        return (Decimal(0), Decimal(0))

    # golden-section search on unimodal profit function (approx)
    phi = Decimal((1 + 5 ** 0.5) / 2)
    invphi = 1 / phi
    a = Decimal(x_min)
    b = Decimal(x_max)
    # interior points
    c = b - (b - a) * Decimal(invphi)
    d = a + (b - a) * Decimal(invphi)
    fc = profit_for_cycle(cycle, c)
    fd = profit_for_cycle(cycle, d)
    iter_count = 0
    while (b - a) > Decimal(str(tol)) and iter_count < max_iter:
        if fc > fd:
            # discard d..b
            b = d
            d = c
            fd = fc
            c = b - (b - a) * Decimal(invphi)
            fc = profit_for_cycle(cycle, c)
        else:
            a = c
            c = d
            fc = fd
            d = a + (b - a) * Decimal(invphi)
            fd = profit_for_cycle(cycle, d)
        iter_count += 1

    # best among c,d,a,b
    candidates = [a, b, c, d]
    best_x = max(candidates, key=lambda xx: float(profit_for_cycle(cycle, xx)))
    best_profit = profit_for_cycle(cycle, best_x)
    return (best_x, best_profit)

# ------------------ pipeline principal ------------------

def find_and_optimize_cycles(pools: List[Dict], max_cycle_len: int = 3, min_profit_threshold: float = 1e-8):
 
    1) Construir grafo
    2) Encontrar ciclos simples hasta max_cycle_len
    3) Optimizar x para cada ciclo
    4) Retornar ciclos con profit > min_profit_threshold (en unidades del token inicial, típicamente base token)
    graph = build_graph_from_pools(pools)
    cycles = find_simple_cycles(graph, max_len=max_cycle_len)
    print(f"[INFO] ciclos candidatos encontrados: {len(cycles)} (filtrados por longitud <= {max_cycle_len})")
    results = []
    start_t = time.time()
    for i, cyc in enumerate(cycles):
        # calcular precio 'mid' aproximado multiplicativo para priorizar (no necesario)
        # intentar optimizar x
        x_best, profit_best = maximize_profit_for_cycle(cyc)
        # convertir Decimal a float para facilidad
        profit_f = float(profit_best)
        x_f = float(x_best)
        if profit_f > min_profit_threshold:
            # reconstruir token path legible
            token_path = [cyc[0]["token_in"]] + [e["token_out"] for e in cyc]
            results.append({
                "cycle_index": i,
                "token_path": token_path,
                "pair_ids": [e["pair_id"] for e in cyc],
                "best_x": x_f,
                "best_profit": profit_f
            })
    elapsed = time.time() - start_t
    print(f"[INFO] optimización completada en {elapsed:.2f}s. Ciclos rentables: {len(results)}")
    return results

# ------------------ ejemplo de uso ------------------

if __name__ == "__main__":
    # ejemplo ficticio (reemplaza con tus datos reales)
    pools = [
        {"pair_id":"P1","token0":"A","token1":"B","reserve0":1000.0,"reserve1":2000.0,"fee":0.003},
        {"pair_id":"P2","token0":"B","token1":"C","reserve0":1500.0,"reserve1":3000.0,"fee":0.003},
        {"pair_id":"P3","token0":"C","token1":"A","reserve0":500.0,"reserve1":250.0,"fee":0.003},
        # añade más pools
    ]

    results = find_and_optimize_cycles(pools, max_cycle_len=3, min_profit_threshold=1e-6)
    for r in results:
        print(r)

import networkx as nx
import math

# ==============================
# 1. Construir el grafo
# ==============================
def build_graph(pairs):

    Construye grafo dirigido a partir de lista de pares.
    pairs: lista de dicts con estructura:
        {
          "id": "pairId",
          "token0": "ETH",
          "token1": "USDC",
          "reserve0": float,
          "reserve1": float
        }
    G = nx.DiGraph()
    for p in pairs:
        t0, t1 = p["token0"], p["token1"]
        r0, r1 = p["reserve0"], p["reserve1"]

        # dirección token0 -> token1
        G.add_edge(t0, t1, pair=p["id"], a=r1, b=r0)  # precio en términos de token1/token0

        # dirección token1 -> token0
        G.add_edge(t1, t0, pair=p["id"], a=r0, b=r1)

    return G

# ==============================
# 2. Enumerar ciclos
# ==============================
def find_cycles(G, max_length=4):

    Encuentra ciclos simples hasta max_length

    all_cycles = []
    for cycle in nx.simple_cycles(G):
        if 2 <= len(cycle) <= max_length:
            all_cycles.append(cycle)
    return all_cycles

# ==============================
# 3. Calcular beneficio esperado
# ==============================
def simulate_cycle(G, cycle, amount_in=1.0):

    Simula pasar 'amount_in' tokens a través de un ciclo.
    Usa la fórmula de AMM constante: out = (amount_in * reserve_out) / (reserve_in + amount_in)
 
    amount = amount_in
    for i in range(len(cycle)):
        u = cycle[i]
        v = cycle[(i + 1) % len(cycle)]
        edge = G[u][v]

        a, b = edge["a"], edge["b"]
        # swap: amount entra como "b", sale como "a"
        amount_out = (amount * a) / (b + amount)
        amount = amount_out

    return amount - amount_in  # beneficio neto


# ==============================
# Ejemplo de uso
# ==============================
pairs = [
    {"id": "p1", "token0": "ETH", "token1": "USDC", "reserve0": 100, "reserve1": 200000},
    {"id": "p2", "token0": "USDC", "token1": "DAI", "reserve0": 200000, "reserve1": 200000},
    {"id": "p3", "token0": "DAI", "token1": "ETH", "reserve0": 200000, "reserve1": 100},
]

G = build_graph(pairs)
cycles = find_cycles(G, max_length=3)

print("🔄 Ciclos encontrados:")
for c in cycles:
    profit = simulate_cycle(G, c, amount_in=1000)
    print(c, f"Beneficio estimado: {profit:.4f}")

"""

