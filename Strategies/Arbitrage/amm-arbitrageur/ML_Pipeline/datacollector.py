import requests
import pandas as pd
from datetime import datetime, timezone
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GRAPH_API_KEY")
SUBGRAPH_ID = os.getenv("SUBGRAPH_ID")
URL = f"https://gateway.thegraph.com/api/subgraphs/id/{SUBGRAPH_ID}"
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

BATCH_SIZE = 200 
MAX_PAIRS = 200 
MAX_PAIRS_DAYDATA = 200
MAX_SWAPS = 200
SLEEP_BETWEEN_CALLS = 0.5 

def fetch_top_pairs_by_liquidity_and_volume(top_n=MAX_PAIRS):
    """
    Retrieves the top trading pairs from the Subgraph based on liquidity (reserveUSD).
    
    The function iterates through the pairs using pagination (skip/first) and applies 
    a client-side filter to include only those where at least one token has a 
    trade volume exceeding $10,000.
    
    Args:
        top_n (int): The maximum number of filtered pairs to retrieve.
        
    Returns:
        list: A list of dictionaries containing pair details (id, tokens, reserves, volume).
    """
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
        time.sleep(SLEEP_BETWEEN_CALLS)  

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

def fetch_pair_day_data(pair_map):
    """
    Fetches the most recent daily historical data for a specific set of pairs.
    
    It queries the `pairDayDatas` entity to get snapshot metrics like daily volume,
    transactions, and reserves. It also calculates the relative price between 
    token0 and token1 based on current reserves.
    
    Args:
        pair_map (dict): A mapping of pair IDs to their basic token information.
        
    Returns:
        list: A list of dictionaries containing daily performance metrics per pair.
    """
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
            print(f" No data for pair {pid}: {resp}")
            continue

        d_list = resp["data"].get("pairDayDatas")
        if not d_list:
            print(f" Empty pairDayData for pair {pid}")
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
        print(f" Daily data downloaded for pair {pid}")
    return all_day_data

def fetch_pair_swaps(pair_ids):
    """
    Retrieves individual swap events for each pair to build a granular dataset.
    
    This approach enables the ML pipeline to calculate statistical features 
    such as trade frequency, volume volatility (std dev), and total liquidity flow.
    
    Args:
        pair_ids (list): List of liquidity pool addresses (pair_id).
        
    Returns:
        list: A flat list of dictionaries, where each entry is a single swap event.
    """
    all_swaps_rows = [] 
    
    # Iterate through the pairs up to the defined limit
    for pid in pair_ids[:MAX_PAIRS_DAYDATA]:
        skip = 0
        pair_swaps_count = 0
        
        while True:
            # GraphQL query targeting individual swap metrics
            query = f"""
            {{
                swaps(
                    first: {BATCH_SIZE}, 
                    skip: {skip}, 
                    orderBy: timestamp, 
                    orderDirection: desc, 
                    where: {{pair: "{pid}"}}
                ) {{
                    amountUSD
                    timestamp
                }}
            }}
            """
            try:
                resp = requests.post(URL, headers=HEADERS, json={"query": query}).json()
                swaps = resp.get("data", {}).get("swaps", [])
                
                # Exit loop if no more swaps are found for this pair
                if not swaps:
                    break
                    
                for s in swaps:
                    # Flattening the data: one dictionary per swap event
                    all_swaps_rows.append({
                        "pair_id": pid,
                        "timestamp": int(s["timestamp"]),
                        # amountUSD is critical for calculating volume-weighted features
                        "amountUSD": float(s["amountUSD"] if s["amountUSD"] else 0)
                    })
                    pair_swaps_count += 1
                
                # Pagination control and safety limit per execution
                if len(swaps) < BATCH_SIZE or len(all_swaps_rows) >= MAX_SWAPS:
                    break
                
                skip += BATCH_SIZE
                # Avoid rate-limiting from the Subgraph API
                time.sleep(SLEEP_BETWEEN_CALLS)
                
            except Exception as e:
                print(f"Error fetching swaps for pair {pid}: {e}")
                break
        
        print(f" Downloaded {pair_swaps_count} individual swaps for pair {pid}")
        
    return all_swaps_rows # Returns a list compatible with pd.DataFrame()

def fetch_pair_liquidity(pair_ids):
    """
    Calculates the net liquidity flow by comparing 'mints' and 'burns'.
    
    It queries the latest mint (liquidity provision) and burn (liquidity removal) 
    events for each pair to determine the net USD value added or removed 
    recently from the pools.
    
    Args:
        pair_ids (list): List of pair contract addresses to query.
        
    Returns:
        list: A list containing the 'liquidity_added_removed' metric for each pair.
    """
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

if __name__ == "__main__":
    print(" Downloading pairs filtered by liquidity and volume...")
    all_pairs = fetch_top_pairs_by_liquidity_and_volume(top_n=MAX_PAIRS)
    pair_map = {p["id"]: {"token0": p["token0"]["symbol"], "token1": p["token1"]["symbol"]} for p in all_pairs} 
    print(pair_map)

    print(" Downloading daily data for pairs...")
    daily_data = fetch_pair_day_data(pair_map)

    print(" Downloading swaps...")
    swaps_data = fetch_pair_swaps(list(pair_map.keys()))

    print(" Downloading liquidity mints/burns...")
    liq_data = fetch_pair_liquidity(list(pair_map.keys()))

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

    df_pairs.to_csv("pairs.csv", index=False)
    df_daily.to_csv("pair_day_data.csv", index=False)
    df_swaps.to_csv("pair_swaps.csv", index=False)
    df_liq.to_csv("pair_liquidity.csv", index=False)

    print(" CSV files generated successfully.")