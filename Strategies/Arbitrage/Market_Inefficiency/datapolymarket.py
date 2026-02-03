import requests

# 1️⃣ Obtener eventos activos
events_url = "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=5"
events_resp = requests.get(events_url).json()

print("Eventos activos:")
print("Eventos activos con etiquetas:")

for e in events_resp:
    # Mostrar título del evento y su ID
    print(f"- {e['title']} (ID: {e['id']})")
    
    # Mostrar las etiquetas del evento
    if 'tags' in e:
        print("  Etiquetas:")
        for tag in e['tags']:
            print(f"    - {tag['label']} (slug: {tag['slug']})")
    else:
        print("  Sin etiquetas")

# 2️⃣ Obtener markets de cada evento
for event in events_resp:
    event_id = event['id']
    markets_url = f"https://gamma-api.polymarket.com/markets?event_id={event_id}"
    markets_resp = requests.get(markets_url).json()
    
    print(f"\nMarkets para evento '{event['title']}':")
    for market in markets_resp:
        print(market)
        market_name = market['question']
        slug = market['slug']
        token_ids = market.get('clobTokenIds', [])
        print(f"  - Market: {market_name} (slug: {slug}) | Tokens: {token_ids}")

        # 3️⃣ Obtener orderbook de cada token
        for token_id in token_ids:
            book_url = f"https://clob.polymarket.com/book?token_id={token_id}"
            book_resp = requests.get(book_url).json()

            bids = book_resp.get('bids', [])
            asks = book_resp.get('asks', [])

            # Precios top de cada lado
            top_bid = bids[0]['price'] if bids else None
            top_ask = asks[0]['price'] if asks else None

            print(f"    Token {token_id}: top_bid={top_bid}, top_ask={top_ask}")

        # 4️⃣ Ejemplo simple de cálculo de spread entre tokens
        if len(token_ids) >= 2:
            token1, token2 = token_ids[:2]
            book1 = requests.get(f"https://clob.polymarket.com/book?token_id={token1}").json()
            book2 = requests.get(f"https://clob.polymarket.com/book?token_id={token2}").json()

            bid1 = float(book1['bids'][0]['price']) if book1['bids'] else 0
            ask2 = float(book2['asks'][0]['price']) if book2['asks'] else 0

            spread = ask2 - bid1
            print(f"    Spread token1 -> token2: {spread:.4f}")
