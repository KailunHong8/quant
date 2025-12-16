# pip install vollib
from vollib.black_scholes import price as bs_price
from vollib.black_scholes.implied_volatility import implied_volatility

S = 100.0     # spot
K = 105.0     # strike
r = 0.01      # risk-free rate
t = 30/365    # time to expiry in years
sigma = 0.2   # vol
flag = 'c'    # call

bs = bs_price(flag, S, K, t, r, sigma)
print("Black-Scholes price:", bs)

# invert to find implied vol from market price
market_price = bs  # pretend market equals model
iv = implied_volatility(market_price, S, K, t, r, flag)
print("Implied vol:", iv)