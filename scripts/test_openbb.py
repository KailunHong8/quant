import pandas as pd

try:
	from openbb import obb
	output = obb.equity.price.historical(symbols="AAPL", provider="yfinance")
	df = output.to_dataframe() if hasattr(output, "to_dataframe") else output.to_df()
except Exception:
	import yfinance as yf
	df = yf.download("AAPL", auto_adjust=False)

print(df.tail())

close_col = (
	"Close"
	if "Close" in df.columns
	else "close"
	if "close" in df.columns
	else "Adj Close"
	if "Adj Close" in df.columns
	else df.columns[-1]
)
df["SMA20"] = df[close_col].rolling(20).mean()
df["SMA50"] = df[close_col].rolling(50).mean()
print(df[[close_col, "SMA20", "SMA50"]].tail())
