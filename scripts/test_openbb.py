import pandas as pd

try:
	from openbb import obb
	
	# Fetch data for multiple symbols (comma-separated)
	symbols = "AAPL,MSFT,GOOGL"
	print(f"Fetching data for: {symbols}")
	
	result = obb.equity.price.historical(symbol=symbols)
	df = result.to_dataframe()
	
	print(f"✓ Successfully fetched {len(df)} rows")
	
	# Pivot to get symbols as columns (for portfolio analysis)
	portfolio_prices = df.pivot_table(values='close', index='date', columns='symbol')
	
	print("\nLatest prices:")
	print(portfolio_prices.tail())
	
	# Calculate moving averages for each stock
	print("\nCalculating moving averages...")
	for symbol in portfolio_prices.columns:
		portfolio_prices[f'{symbol}_SMA20'] = portfolio_prices[symbol].rolling(20).mean()
		portfolio_prices[f'{symbol}_SMA50'] = portfolio_prices[symbol].rolling(50).mean()
	
	# Display results for each stock
	for symbol in ['AAPL', 'MSFT', 'GOOGL']:
		print(f"\n{symbol} with Moving Averages:")
		print(portfolio_prices[[symbol, f'{symbol}_SMA20', f'{symbol}_SMA50']].tail())
	
except Exception as e:
	print(f"✗ OpenBB failed: {e}")
	print("\nFalling back to yfinance...")
	import yfinance as yf
	df = yf.download(["AAPL", "MSFT", "GOOGL"], period="1y", auto_adjust=False, progress=False)
	
	if 'Close' in df.columns:
		portfolio_prices = df['Close']
	else:
		portfolio_prices = df
	
	print(portfolio_prices.tail())
