# pip install gs-quant
from gs_quant.instrument import Equity
from gs_quant.risk import MarketDataPoint

# create a simple equity instrument
e = Equity('AAPL')
print(e.__dict__)

# fetching live data requires GS credentials; but you can construct instruments & workflows offline
# For actual risk/pricing calls, consult gs-quant docs and authentication steps.