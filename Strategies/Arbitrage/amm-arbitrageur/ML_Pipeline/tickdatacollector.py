import requests
import pandas as pd
from datetime import datetime, timezone
import time
import os  

# ------------------- Configuración -------------------
API_KEY = "5416676bb1355388c99743344da1b45a"
SUBGRAPH_ID = "A3Np3RQbaBA6oKJgiwDJeo5T3zrYfGHPWFYayMwtNDum"  # PancakeSwap V2
URL = f"https://gateway.thegraph.com/api/subgraphs/id/{SUBGRAPH_ID}"
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

BATCH_SIZE = 500  # aumentado para traer más resultados por llamada
MAX_PAIRS = 500  # por ejemplo
MAX_PAIRS_DAYDATA = 500
MAX_SWAPS = 5000    
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


def fetch_pair_tick_data_per_minute(pair_ids, max_swaps_per_pair=5000):
    """
    Reconstruye tick data por minuto (precio promedio) para cada par.
    
    Args:
        pair_ids (list): lista de IDs de pares
        max_swaps_per_pair (int): máximo swaps a traer por par
    
    Returns:
        dict: {pair_id: DataFrame con columnas ['timestamp', 'price_minute']}
    """
    tick_data_per_minute = {}
    
    for pid in pair_ids:
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
                    timestamp
                }}
            }}
            """
            resp = requests.post(URL, headers=HEADERS, json={"query": query}).json()
            time.sleep(SLEEP_BETWEEN_CALLS)
            
            swaps = resp.get("data", {}).get("swaps")
            if not swaps or len(swaps_list) >= max_swaps_per_pair:
                break
            
            for s in swaps[:max_swaps_per_pair - len(swaps_list)]:
                amount0 = float(s["amount0In"]) + float(s["amount0Out"])
                amount1 = float(s["amount1In"]) + float(s["amount1Out"])
                price = amount1 / amount0 if amount0 > 0 else None
                swaps_list.append({
                    "timestamp": int(s["timestamp"]),
                    "price": price
                })
            
            skip += BATCH_SIZE
        
        # Crear DataFrame y convertir timestamp a datetime
        df = pd.DataFrame(swaps_list)
        if df.empty:
            print(f"⚠️ No hay swaps para pair {pid}")
            continue
        # Convertir timestamp a datetime con precisión de segundos
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

        # Mantener cada swap como fila individual
        df_ticks = df[['datetime', 'price']].copy()
        df_ticks.rename(columns={'price': 'price_tick'}, inplace=True)

        # Guardar en el diccionario
        tick_data_per_minute[pid] = df_ticks
        print(f"✅ Tick data individual reconstruido para pair {pid}, {len(df_ticks)} swaps")
    
    return tick_data_per_minute

if __name__ == "__main__":
    # ------------------- Carpeta de salida -------------------
    output_dir = "TickDataV2"
    os.makedirs(output_dir, exist_ok=True)  # crea la carpeta si no existe

    # ------------------- 1️⃣ Traer pares -------------------
    print("📥 Descargando pares filtrados por liquidez y volumen...")
    all_pairs = fetch_top_pairs_by_liquidity_and_volume(top_n=MAX_PAIRS)
    
    if not all_pairs:
        print("⚠️ No se encontraron pares")
        exit()
    
    # Mapa de pares: pair_id -> tokens
    pair_map = {p["id"]: {"token0": p["token0"]["symbol"], "token1": p["token1"]["symbol"]} for p in all_pairs}
    pair_ids = list(pair_map.keys())
    print(f"✅ {len(pair_ids)} pares obtenidos")

    # ------------------- 2️⃣ Reconstruir tick data por segundo -------------------
    print("📥 Reconstruyendo tick data individual para cada par...")
    tick_data_dict = fetch_pair_tick_data_per_minute(pair_ids, max_swaps_per_pair=MAX_SWAPS)
    
    # ------------------- 3️⃣ Guardar CSVs en carpeta -------------------
    for pid, df_ticks in tick_data_dict.items():
        token0 = pair_map[pid]["token0"]
        token1 = pair_map[pid]["token1"]
        
        # Añadimos columnas de identificación
        df_ticks["pair_id"] = pid
        df_ticks["token0"] = token0
        df_ticks["token1"] = token1
        
        filename = os.path.join(output_dir, f"tick_data_{token0}_{token1}.csv")
        df_ticks.to_csv(filename, index=False)
        print(f"💾 Tick data guardado en {filename}")
    
    print("🎉 Todos los CSV generados correctamente")
