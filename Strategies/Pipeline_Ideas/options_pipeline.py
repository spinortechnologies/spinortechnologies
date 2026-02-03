# Inputs: price history S, available strikes K_list, initial capital C0
# Parameters: mean reversion window N, alpha (aggressiveness), max_drawdown, fractional_kelly_factor

for t in range(len(S)):
    
    # 1. Get current prices and option premiums
    St = S[t]
    C_tK = {K: black_scholes_put(St, K, T-t, r, sigma) for K in K_list}
    
    # 2. Mean reversion signal
    if t >= N:
        S_mean = mean(S[t-N:t])
        price_signal = (S_mean - St) / S_mean  # positive if undervalued
    else:
        price_signal = 1  # not enough data, allow purchase

    if price_signal <= 0:  # price too high, skip
        continue
    
    # 3. Filter strikes according to mean reversion criterion
    valid_strikes = [K for K in K_list if K <= St + alpha*(S_mean - St)]
    
    best_utility = -inf
    best_choice = None
    
    # 4. Evaluate expected utility for each strike and candidate quantity
    for K in valid_strikes:
        for x_candidate in x_candidates:  # possible discrete quantities
            # Simulate or model S_{t+1}
            S_future = simulate_future_price(St)
            payoff = max(K - S_future, 0)
            
            utility = S_future*x_candidate - x_candidate*payoff - x_candidate*C_tK[K]
            
            # 5. Apply Kelly criterion (optional)
            p_ITM = probability_ITM(St, K, T-t, sigma)  # probability of exercise
            b = (payoff - C_tK[K]) / C_tK[K]  # net relative gain
            kelly_fraction = (b*p_ITM - (1-p_ITM)) / b
            x_kelly = fractional_kelly_factor * kelly_fraction * capital
            
            adjusted_utility = utility * (x_kelly / x_candidate)
            
            # 6. Check drawdown
            if check_drawdown(x_kelly) > max_drawdown:
                x_kelly *= 0.5  # reduce exposure
            
            # 7. Select the best option
            if adjusted_utility > best_utility:
                best_utility = adjusted_utility
                best_choice = (t, K, x_kelly)
    
    # 8. Execute purchase
    if best_choice:
        execute_order(best_choice)
        update_portfolio(best_choice)
