# pip install pyql
import QuantLib as ql
from datetime import date

# market conventions
today = ql.Date(16, ql.December, 2025)
ql.Settings.instance().evaluationDate = today

# flat zero curve at 2% for demonstration
rate = 0.02
day_counter = ql.Actual365Fixed()
calendar = ql.UnitedStates(ql.UnitedStates.NYSE)
flat_curve = ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(rate)), day_counter)
discount_curve = ql.YieldTermStructureHandle(flat_curve)

# Calculate PV of $1000 in 1 year
future_value = 1000.0
years = 1.0
pv = discount_curve.discount(years) * future_value
print(f"PV of ${future_value} in {years} year at {rate*100}%: ${pv:.2f}")