from py_clob_client.client import ClobClient
import os
from dotenv import load_dotenv
load_dotenv()

host = "https://clob.polymarket.com"
chain_id = 137  # Polygon mainnet
private_key = os.getenv("PRIVATE_KEY_METAMASK")
print("Using private key:", private_key)
client = ClobClient(host, key=private_key, chain_id=chain_id)

if client:
    print("ClobClient initialized successfully")

else:
    print("Failed to initialize ClobClient")

# Get existing API key, or create one if none exists
user_api_creds = client.create_or_derive_api_creds()

print("TYPE:", type(user_api_creds))
print("CREDS:", user_api_creds)
print("API Key:", user_api_creds.api_key)
print("Secret:", user_api_creds.api_secret)
print("Passphrase:", user_api_creds.api_passphrase)


# Choose based on your wallet type (see table above)
signature_type = 0  # EOA example
funder_address = "0x128b12a39785b0ce4584fbf79b6daae9072446f3"  # For EOA, funder is your wallet

client = ClobClient(
    host,
    key=private_key,
    chain_id=chain_id,
    creds=user_api_creds,
    signature_type=signature_type,
    funder=funder_address
)


from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

# Get market info first
market = client.get_market("TOKEN_ID")

response = client.create_and_post_order(
    OrderArgs(
        token_id="TOKEN_ID",
        price=0.50,       # Price per share ($0.50)
        size=10,          # Number of shares
        side=BUY,         # BUY or SELL
    ),
    options={
        "tick_size": market["tickSize"],
        "neg_risk": market["negRisk"],    # True for multi-outcome events
    },
    order_type=OrderType.GTC  # Good-Til-Cancelled
)

print("Order ID:", response["orderID"])
print("Status:", response["status"])

# View all open orders
open_orders = trading_client.get_open_orders()
print(f"You have {len(open_orders)} open orders")

# View your trade history
trades = trading_client.get_trades()
print(f"You've made {len(trades)} trades")

# Cancel an order
trading_client.cancel_order(response["orderID"])