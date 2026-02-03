import pandas as pd
import numpy as np
import networkx as nx
import os
import glob
import logging
from decimal import Decimal, getcontext, InvalidOperation
from itertools import combinations
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# -----------------------------------------------------------------------------
# CONFIGURATION & LOGGING
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

getcontext().prec = 60  # High precision for crypto calculations

# Constants
MAX_CYCLE_LEN = 3  # Reduced from 1000 to realistic arb length (3-4 hops) to prevent infinite loops
FEE_DEFAULT = 0.003
MIN_LIQUIDITY_USD = 1000  # Filter out dust pools

# -----------------------------------------------------------------------------
# 1. MATH & SIMULATION ENGINE
# -----------------------------------------------------------------------------
class ArbitrageMath:
    """
    Handles all high-precision math for Uniswap V2-style AMM logic.
    """
    
    @staticmethod
    def get_amount_out(amount_in: Decimal, reserve_in: Decimal, reserve_out: Decimal, fee: float = FEE_DEFAULT) -> Decimal:
        """
        Calculates the amount of tokens received for a given input amount.
        Formula: amountOut = (amountIn * 0.997 * reserveOut) / (reserveIn + amountIn * 0.997)
        """
        if amount_in <= 0 or reserve_in <= 0 or reserve_out <= 0:
            return Decimal("0")
        
        try:
            amount_in_with_fee = amount_in * (Decimal("1") - Decimal(str(fee)))
            numerator = amount_in_with_fee * reserve_out
            denominator = reserve_in + amount_in_with_fee
            return numerator / denominator
        except (InvalidOperation, ZeroDivisionError):
            return Decimal("0")

    @staticmethod
    def simulate_cycle(cycle_nodes, graph, initial_amount=Decimal('1.0')):
        """
        Simulates a trade execution along a path of nodes to calculate final output.
        
        Args:
            cycle_nodes (list): List of token symbols (nodes) in the cycle.
            graph (nx.DiGraph): The market graph containing edge data (reserves).
            initial_amount (Decimal): The starting amount of the first token.
            
        Returns:
            Decimal: The final amount of the starting token after the cycle.
        """
        current_amount = initial_amount
        
        # Create a local copy of reserves to simulate slippage without affecting global state
        # In a real high-freq engine, we would need a more complex state manager.
        
        for i in range(len(cycle_nodes) - 1):
            u, v = cycle_nodes[i], cycle_nodes[i+1]
            if not graph.has_edge(u, v):
                return Decimal("0")
                
            edge_data = graph[u][v]
            r_in = edge_data['reserve_in']
            r_out = edge_data['reserve_out']
            fee = edge_data['fee']
            
            amount_out = ArbitrageMath.get_amount_out(current_amount, r_in, r_out, fee)
            
            # Simulate pool update for the next hop (Slippage impact)
            # r_in increases, r_out decreases
            # Note: This simple loop assumes we don't hit the same pool twice in a way that matters strictly 
            # for this simplified calculation, or that the cycle is simple.
            current_amount = amount_out
            
        return current_amount

# -----------------------------------------------------------------------------
# 2. DATA MANAGEMENT & SCHEMA
# -----------------------------------------------------------------------------
class DataManager:
    """
    Responsible for loading, validating, and merging data sources.
    Enforces schema validity to prevent 'garbage in, garbage out'.
    """
    
    REQUIRED_COLUMNS = {
        'pairs': ['pair_id', 'token0', 'token1', 'reserve0', 'reserve1', 'reserveUSD'],
        'daily': ['pair_id', 'dailyVolumeUSD', 'reserveUSD'],
        'swaps': ['pair_id', 'timestamp', 'amountUSD'],
        'liquidity': ['pair_id', 'liquidity_added_removed']
    }

    def __init__(self, pairs_path, daily_path, swaps_path, liq_path):
        self.paths = {
            'pairs': pairs_path,
            'daily': daily_path,
            'swaps': swaps_path,
            'liquidity': liq_path
        }
        self.data = {}

    def load_and_validate(self):
        """Loads CSVs and checks for existence and required columns."""
        for key, path in self.paths.items():
            if not os.path.exists(path):
                logger.warning(f"File not found: {path}. Creating empty DataFrame.")
                self.data[key] = pd.DataFrame(columns=self.REQUIRED_COLUMNS[key])
                continue
            
            df = pd.read_csv(path)
            # Ensure pair_id is string
            if 'pair_id' in df.columns:
                df['pair_id'] = df['pair_id'].astype(str)
            
            # Check columns
            missing = [c for c in self.REQUIRED_COLUMNS[key] if c not in df.columns]
            if missing:
                raise ValueError(f"Dataset {key} missing columns: {missing}")
            
            self.data[key] = df
            logger.info(f"Loaded {key} with shape {df.shape}")

    def get_enriched_pairs(self):
        """
        Merges auxiliary data (daily, swaps, liquidity) onto the base pairs data.
        """
        # 1. Aggregating Daily Data
        # We take the mean or sum depending on the logic. 
        # Since the user mentioned daily data might be multiple rows, we aggregate by pair_id.
        daily_agg = self.data['daily'].groupby('pair_id').agg({
            'dailyVolumeUSD': 'sum', # Total volume observed
            'reserveUSD': 'mean'     # Average liquidity observed
        }).rename(columns={'dailyVolumeUSD': 'vol_usd_daily', 'reserveUSD': 'liq_usd_daily'})

        # 2. Aggregating Swaps
        # Calculate volatility/activity from swaps
        if not self.data['swaps'].empty:
            swap_stats = self.data['swaps'].groupby('pair_id').agg({
                'amountUSD': ['count', 'mean', 'std']
            })
            swap_stats.columns = ['swap_count', 'swap_avg_size', 'swap_volatility']
        else:
            swap_stats = pd.DataFrame(columns=['swap_count', 'swap_avg_size', 'swap_volatility'])

        # 3. Aggregating Liquidity Events
        if not self.data['liquidity'].empty:
            liq_flow = self.data['liquidity'].groupby('pair_id')['liquidity_added_removed'].sum().to_frame('net_liq_flow')
        else:
            liq_flow = pd.DataFrame(columns=['net_liq_flow'])

        # Merge everything
        base = self.data['pairs'].copy()
        merged = base.merge(daily_agg, on='pair_id', how='left')
        merged = merged.merge(swap_stats, on='pair_id', how='left')
        merged = merged.merge(liq_flow, on='pair_id', how='left')

        # Filter low liquidity pairs (Dust) to avoid contaminating the model
        merged = merged[merged['reserveUSD'] > MIN_LIQUIDITY_USD]
        
        logger.info(f"Enriched pairs shape: {merged.shape}")
        return merged

# -----------------------------------------------------------------------------
# 3. GRAPH & CYCLE ENGINE
# -----------------------------------------------------------------------------
class NetworkManager:
    """
    Manages the NetworkX graph construction and cycle detection.
    """
    
    def __init__(self, df_pairs):
        self.df_pairs = df_pairs
        self.G = self._build_graph()

    def _build_graph(self):
        G = nx.DiGraph()
        
        # Use simple iteration for speed
        #  
        # The graph represents tokens as nodes and pools as directed edges with reserve attributes.
        for row in self.df_pairs.itertuples():
            try:
                t0, t1 = row.token0, row.token1
                r0, r1 = Decimal(str(row.reserve0)), Decimal(str(row.reserve1))
                pair_id = row.pair_id
                
                # Add edges in both directions
                G.add_edge(t0, t1, pair_id=pair_id, reserve_in=r0, reserve_out=r1, fee=FEE_DEFAULT)
                G.add_edge(t1, t0, pair_id=pair_id, reserve_in=r1, reserve_out=r0, fee=FEE_DEFAULT)
            except Exception as e:
                continue
                
        logger.info(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        return G

    def find_arbitrage_cycles(self, max_len=MAX_CYCLE_LEN):
        """
        Finds simple cycles in the graph.
        """
        # simple_cycles is computationally expensive. 
        # We limit the search or use a heuristic if the graph is huge.
        # For this example, we assume the graph is filtered enough.
        
        raw_cycles = nx.simple_cycles(self.G)
        valid_cycles = []
        
        count = 0
        for cycle in raw_cycles:
            if len(cycle) > max_len:
                continue
            if len(cycle) < 3: # A cycle of 2 is just swapping back and forth (rarely profitable due to fee)
                continue
                
            # Close the loop for processing
            cycle_closed = cycle + [cycle[0]]
            valid_cycles.append(cycle_closed)
            
            count += 1
            if count > 10000: # Safety break
                logger.warning("Cycle limit reached (10k). Stopping search.")
                break
                
        logger.info(f"Found {len(valid_cycles)} valid cycles.")
        return valid_cycles

# -----------------------------------------------------------------------------
# 4. FEATURE ENGINEERING
# -----------------------------------------------------------------------------
class FeatureEngineer:
    """
    Extracts features from cycles and integrates Tick Data.
    """
    
    def __init__(self, tick_dirs):
        self.tick_dirs = tick_dirs
        self.tick_cache = {}

    def _get_tick_stats(self, token):
        """
        Robustly searches for tick data CSVs and computes volatility/momentum.
        """
        token = str(token).upper()
        if token in self.tick_cache:
            return self.tick_cache[token]
        
        # Defaults (Using None instead of 0 to allow Imputer to handle it later)
        defaults = {'tick_vol': np.nan, 'tick_rng': np.nan, 'tick_mom': np.nan}
        
        # Find file
        found_file = None
        for d in self.tick_dirs:
            # Use glob for safer pattern matching
            pattern = os.path.join(d, f"*{token}*.csv")
            matches = glob.glob(pattern)
            # Filter matches to ensure token name is distinct (e.g. avoid matching 'USDT' in 'USDT_ETH')
            # This is a simplification; robust matching requires regex on filenames
            if matches:
                found_file = matches[0] # Take the first best match
                break
        
        if not found_file:
            self.tick_cache[token] = defaults
            return defaults
            
        try:
            df = pd.read_csv(found_file)
            # Identify price column
            cols = [c.lower() for c in df.columns]
            price_col = next((c for c in df.columns if 'price' in c.lower() or 'close' in c.lower()), None)
            
            if not price_col:
                self.tick_cache[token] = defaults
                return defaults
            
            prices = pd.to_numeric(df[price_col], errors='coerce').dropna()
            if len(prices) < 10:
                self.tick_cache[token] = defaults
                return defaults
                
            # Compute stats
            # Normalize volatility by mean price to make it comparable across tokens
            mean_p = prices.mean()
            vol = prices.std() / mean_p if mean_p else 0
            rng = (prices.max() - prices.min()) / mean_p if mean_p else 0
            
            # Momentum: Slope of the last 100 ticks
            y = prices.values[-100:]
            x = np.arange(len(y))
            slope = np.polyfit(x, y, 1)[0]
            mom = slope / mean_p if mean_p else 0 # Normalized momentum
            
            stats = {'tick_vol': vol, 'tick_rng': rng, 'tick_mom': mom}
            self.tick_cache[token] = stats
            return stats
            
        except Exception as e:
            logger.error(f"Error reading tick data for {token}: {e}")
            self.tick_cache[token] = defaults
            return defaults

    def extract_features(self, cycles, graph, pair_data_lookup):
        """
        Generates the feature matrix X and target y (profit).
        """
        features_list = []
        
        for cycle in cycles:
            row = {}
            row['cycle_str'] = "-".join(cycle)
            row['length'] = len(cycle) - 1
            
            # --- Cycle Metrics ---
            reserves_usd = []
            vols_usd = []
            liq_flows = []
            swap_counts = []
            fees = []
            
            # Math Simulation
            amt_in = Decimal('100.0') # Simulate with $100 equivalent
            final_amt = ArbitrageMath.simulate_cycle(cycle, graph, amt_in)
            
            # Target Variable: Profit Percentage
            try:
                profit_pct = float((final_amt - amt_in) / amt_in)
            except:
                profit_pct = 0.0
            
            row['target_profit'] = profit_pct

            # Path Analysis
            for i in range(len(cycle) - 1):
                u, v = cycle[i], cycle[i+1]
                edge = graph[u][v]
                pair_id = edge['pair_id']
                fees.append(edge['fee'])
                
                # Lookup enriched pair data
                if pair_id in pair_data_lookup.index:
                    p_data = pair_data_lookup.loc[pair_id]
                    reserves_usd.append(p_data.get('reserveUSD', np.nan))
                    vols_usd.append(p_data.get('vol_usd_daily', np.nan))
                    liq_flows.append(p_data.get('net_liq_flow', np.nan))
                    swap_counts.append(p_data.get('swap_count', np.nan))
                else:
                    reserves_usd.append(np.nan)

            # --- Aggregate Features ---
            # Instead of sum, use min/mean for liquidity (bottleneck theory)
            row['min_reserve_usd'] = np.nanmin(reserves_usd) if reserves_usd else 0
            row['mean_vol_usd'] = np.nanmean(vols_usd) if vols_usd else 0
            row['total_fees'] = sum(fees)
            row['sum_liq_flow'] = np.nansum(liq_flows)
            
            # --- Tick Data Aggregation ---
            # We average the volatility of all tokens involved in the cycle
            tokens = list(set(cycle))
            tick_stats = [self._get_tick_stats(t) for t in tokens]
            
            row['avg_tick_vol'] = np.nanmean([d['tick_vol'] for d in tick_stats])
            row['avg_tick_mom'] = np.nanmean([d['tick_mom'] for d in tick_stats])
            
            features_list.append(row)
            
        return pd.DataFrame(features_list)

# -----------------------------------------------------------------------------
# 5. EXECUTION PIPELINE
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    
    # A. Load Data
    data_mgr = DataManager(
        pairs_path="data/pairs.csv",
        daily_path="data/pair_day_data.csv",
        swaps_path="data/pair_swaps.csv",
        liq_path="data/pair_liquidity.csv"
    )
    data_mgr.load_and_validate()
    df_pairs_enriched = data_mgr.get_enriched_pairs()
    
    # Create a lookup for fast feature extraction
    pair_lookup = df_pairs_enriched.set_index('pair_id')

    # B. Build Graph & Find Cycles
    net_mgr = NetworkManager(df_pairs_enriched)
    cycles = net_mgr.find_arbitrage_cycles(max_len=MAX_CYCLE_LEN)

    if not cycles:
        logger.error("No cycles found. Exiting.")
        exit()

    # C. Feature Engineering
    # Define tick data directories
    tick_dirs = [os.path.join(os.getcwd(), "TickDataV1"), os.path.join(os.getcwd(), "TickDataV2")]
    
    fe = FeatureEngineer(tick_dirs)
    df_features = fe.extract_features(cycles, net_mgr.G, pair_lookup)
    
    logger.info(f"Feature extraction complete. Shape: {df_features.shape}")
    
    # Check for valid data
    if df_features.empty:
        logger.error("Feature dataframe is empty.")
        exit()

    # D. Machine Learning Pipeline 
    # We drop metadata columns
    X = df_features.drop(columns=['cycle_str', 'target_profit'])
    y = df_features['target_profit']

    # Handle cases where all targets are 0 (no profitable cycles found in simulation)
    if y.sum() == 0:
        logger.warning("All targets are 0. The simulation found no profitable cycles.")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define Pipeline
    # 1. Imputer: Fills NaNs (median is robust to outliers)
    # 2. Scaler: RobustScaler handles outliers better than StandardScaler
    # 3. PCA: Dimensionality reduction (optional, but good for correlated crypto features)
    # 4. Model: RandomForest
    
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', RobustScaler()),
        ('pca', PCA(n_components=0.95)), # Keep 95% variance
        ('regressor', RandomForestRegressor(
            n_estimators=200, 
            max_depth=10, 
            random_state=42, 
            n_jobs=-1
        ))
    ])

    # Train
    logger.info("Training model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    
    print("\n" + "="*40)
    print(f"📊 MODEL RESULTS")
    print("="*40)
    print(f"R2 Score: {r2:.4f}")
    print(f"MSE:      {mse:.6f}")
    
    # Feature Importance (Harder to visualize with PCA in middle, extracting directly from RF if needed)
    # Note: With PCA, direct feature importance is obscured. If you want direct importance, remove PCA.
    
    # Save results
    df_features.to_csv("final_cycle_dataset.csv", index=False)
    print("✅ Dataset saved to final_cycle_dataset.csv")

    # Suggest next step
    print("\n👉 Next Step: Run this script. If R2 is low, verify 'pairs.csv' timestamp alignment with 'TickData'.")