import requests
import pandas as pd
from datetime import datetime, timezone

# ------------------- Configuración -------------------
API_KEY = "5416676bb1355388c99743344da1b45a"
SUBGRAPH_ID = "A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum"  # PancakeSwap V2
URL = f"https://gateway.thegraph.com/api/subgraphs/id/{SUBGRAPH_ID}"
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

BATCH_SIZE = 1000
MAX_PAIRS = 50
MAX_PAIRS_DAYDATA = 20
MAX_SWAPS = 500

# ------------------- Funciones -------------------

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
