"""
TLT Calendar Strategy - Institutional Flow-Based Trading

STRATEGY LOGIC:
Based on predictable month-end rebalancing flows in Treasury markets:
- SHORT early in the month (days 1-5) when institutions raise cash
- LONG late in the month (7 days before month-end to 1 day before) to capture rebalancing demand
- FLAT otherwise

MARKET STRUCTURE RATIONALE:
- Passive funds rebalance to index weights at month-end
- Pension funds adjust duration for reporting snapshots  
- Mutual funds reinvest inflows received earlier in month
- Treasury settlement cycles affect liquidity timing
- Volume spikes 30-50% on final trading day per Fed NY research

This implementation uses:
1. OpenBB for TLT price data
2. Custom signal generation based on trading day position in month
3. Manual portfolio construction (GS Quant backtests module requires credentials)
4. Transaction cost modeling
5. Comprehensive performance metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Try to import GS Quant instruments (optional for instrument modeling)
try:
    from gs_quant.instrument import ETF
    GS_QUANT_AVAILABLE = True
except ImportError:
    GS_QUANT_AVAILABLE = False
    print("ℹ GS Quant not available - using manual backtest implementation")

print("=" * 80)
print("TLT Calendar Strategy Backtest")
print("Exploiting Month-End Institutional Rebalancing Flows")
print("=" * 80)

# ============================================================================
# PART 1: Data Collection
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: Fetching TLT Historical Data")
print("=" * 80)

try:
    from openbb import obb
    
    # Fetch TLT data from 2004 (inception) to present
    # Using yfinance provider for maximum history
    result = obb.equity.price.historical(
        symbol="TLT",
        start_date="2004-01-01",
        end_date=datetime.now().strftime("%Y-%m-%d"),
        provider="yfinance"
    )
    
    df = result.to_dataframe()
    prices = df['close'].copy()
    
    print(f"✓ Fetched {len(prices)} days of TLT data")
    print(f"  Date range: {prices.index[0].date()} to {prices.index[-1].date()}")
    print(f"  Start price: ${prices.iloc[0]:.2f}")
    print(f"  End price: ${prices.iloc[-1]:.2f}")
    print(f"  Buy-and-Hold Return: {(prices.iloc[-1]/prices.iloc[0] - 1)*100:.1f}%")
    
except Exception as e:
    print(f"Error fetching data: {e}")
    print("Falling back to yfinance directly...")
    import yfinance as yf
    ticker = yf.Ticker("TLT")
    df = ticker.history(start="2004-01-01", end=datetime.now().strftime("%Y-%m-%d"))
    prices = df['Close'].copy()
    print(f"✓ Fetched {len(prices)} days of TLT data via yfinance")

# ============================================================================
# PART 2: Signal Generation - Calendar-Based Entry/Exit
# ============================================================================
print("\n" + "=" * 80)
print("PART 2: Generating Calendar-Based Trading Signals")
print("=" * 80)

# Initialize signal dataframes
signals = pd.DataFrame(index=prices.index)
signals['price'] = prices
signals['position'] = 0  # 0=flat, 1=long, -1=short

# Identify trading day position within each month
signals['month'] = signals.index.to_period('M')
signals['day_of_month'] = signals.groupby('month').cumcount() + 1
signals['days_in_month'] = signals.groupby('month')['day_of_month'].transform('max')
signals['days_until_month_end'] = signals['days_in_month'] - signals['day_of_month']

# Define the strategy rules
SHORT_ENTRY_DAY = 1      # First trading day of month
SHORT_EXIT_DAY = 5       # Hold short for 5 days
LONG_ENTRY_DAYS_BEFORE_END = 7  # Enter long 7 days before month-end
LONG_EXIT_DAYS_BEFORE_END = 1   # Exit long 1 day before month-end

# Generate positions
for idx in signals.index:
    day_num = signals.loc[idx, 'day_of_month']
    days_until_end = signals.loc[idx, 'days_until_month_end']
    
    # SHORT WINDOW: Days 1-5 of month
    if day_num >= SHORT_ENTRY_DAY and day_num <= SHORT_EXIT_DAY:
        signals.loc[idx, 'position'] = -1
    
    # LONG WINDOW: 7 days before month-end to 1 day before month-end
    elif days_until_end <= LONG_ENTRY_DAYS_BEFORE_END and days_until_end > LONG_EXIT_DAYS_BEFORE_END:
        signals.loc[idx, 'position'] = 1
    
    # Otherwise FLAT
    else:
        signals.loc[idx, 'position'] = 0

# Calculate position changes for transaction cost modeling
signals['position_change'] = signals['position'].diff().fillna(0)
signals['trade'] = signals['position_change'].abs() > 0

print(f"\nStrategy Calendar Rules:")
print(f"  SHORT: Days {SHORT_ENTRY_DAY}-{SHORT_EXIT_DAY} of each month")
print(f"  LONG: {LONG_ENTRY_DAYS_BEFORE_END} to {LONG_EXIT_DAYS_BEFORE_END} days before month-end")
print(f"  FLAT: All other days")
print(f"\nSignal Statistics:")
print(f"  Total trading days: {len(signals)}")
print(f"  Days SHORT: {(signals['position'] == -1).sum()} ({(signals['position'] == -1).sum()/len(signals)*100:.1f}%)")
print(f"  Days LONG: {(signals['position'] == 1).sum()} ({(signals['position'] == 1).sum()/len(signals)*100:.1f}%)")
print(f"  Days FLAT: {(signals['position'] == 0).sum()} ({(signals['position'] == 0).sum()/len(signals)*100:.1f}%)")
print(f"  Total trades: {signals['trade'].sum()}")
print(f"  Avg trades per year: {signals['trade'].sum() / (len(signals)/252):.1f}")

# ============================================================================
# PART 3: Backtest Execution with Transaction Costs
# ============================================================================
print("\n" + "=" * 80)
print("PART 3: Backtest Execution")
print("=" * 80)

# Transaction cost assumptions
TRANSACTION_COST_BPS = 5  # 5 basis points per trade (realistic for TLT ETF)
BORROW_COST_ANNUAL = 0.005  # 0.5% annual borrow cost for shorting

# Calculate daily returns
signals['market_return'] = signals['price'].pct_change()

# Calculate strategy returns (position * market_return)
signals['strategy_return_gross'] = signals['position'].shift(1) * signals['market_return']

# Apply transaction costs
signals['transaction_cost'] = 0.0
signals.loc[signals['trade'], 'transaction_cost'] = TRANSACTION_COST_BPS / 10000

# Apply borrow costs on short positions (daily)
signals['borrow_cost'] = 0.0
signals.loc[signals['position'].shift(1) == -1, 'borrow_cost'] = BORROW_COST_ANNUAL / 252

# Net strategy return
signals['strategy_return_net'] = (
    signals['strategy_return_gross'] 
    - signals['transaction_cost'] 
    - signals['borrow_cost']
)

# Calculate cumulative returns
signals['strategy_cumulative'] = (1 + signals['strategy_return_net']).cumprod()
signals['buyhold_cumulative'] = (1 + signals['market_return']).cumprod()

# Performance metrics
total_return_strategy = signals['strategy_cumulative'].iloc[-1] - 1
total_return_buyhold = signals['buyhold_cumulative'].iloc[-1] - 1

annual_return_strategy = (1 + total_return_strategy) ** (252 / len(signals)) - 1
annual_return_buyhold = (1 + total_return_buyhold) ** (252 / len(signals)) - 1

volatility_strategy = signals['strategy_return_net'].std() * np.sqrt(252)
volatility_buyhold = signals['market_return'].std() * np.sqrt(252)

sharpe_strategy = annual_return_strategy / volatility_strategy if volatility_strategy > 0 else 0
sharpe_buyhold = annual_return_buyhold / volatility_buyhold if volatility_buyhold > 0 else 0

# Maximum drawdown
def calculate_max_drawdown(cumulative_returns):
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    return drawdown.min()

max_dd_strategy = calculate_max_drawdown(signals['strategy_cumulative'])
max_dd_buyhold = calculate_max_drawdown(signals['buyhold_cumulative'])

# Win rate
winning_trades = signals[signals['strategy_return_net'] > 0]
losing_trades = signals[signals['strategy_return_net'] < 0]
win_rate = len(winning_trades) / len(signals) if len(signals) > 0 else 0

print(f"\nPerformance Summary ({signals.index[0].date()} to {signals.index[-1].date()}):")
print(f"  Period: {len(signals)/252:.1f} years")
print("\n" + "-" * 80)
print(f"{'Metric':<30} {'Strategy':>15} {'Buy & Hold':>15} {'Difference':>15}")
print("-" * 80)
print(f"{'Total Return':<30} {total_return_strategy:>14.1%} {total_return_buyhold:>14.1%} {total_return_strategy-total_return_buyhold:>14.1%}")
print(f"{'Annualized Return':<30} {annual_return_strategy:>14.1%} {annual_return_buyhold:>14.1%} {annual_return_strategy-annual_return_buyhold:>14.1%}")
print(f"{'Volatility':<30} {volatility_strategy:>14.1%} {volatility_buyhold:>14.1%} {volatility_strategy-volatility_buyhold:>14.1%}")
print(f"{'Sharpe Ratio':<30} {sharpe_strategy:>14.2f} {sharpe_buyhold:>14.2f} {sharpe_strategy-sharpe_buyhold:>14.2f}")
print(f"{'Max Drawdown':<30} {max_dd_strategy:>14.1%} {max_dd_buyhold:>14.1%} {max_dd_strategy-max_dd_buyhold:>14.1%}")
print(f"{'Win Rate (Daily)':<30} {win_rate:>14.1%} {'N/A':>15} {'N/A':>15}")

print(f"\nTransaction Costs:")
print(f"  Total trades: {signals['trade'].sum()}")
print(f"  Transaction cost drag: {signals['transaction_cost'].sum()*100:.2f}%")
print(f"  Borrow cost drag: {signals['borrow_cost'].sum()*100:.2f}%")
print(f"  Total cost drag: {(signals['transaction_cost'].sum() + signals['borrow_cost'].sum())*100:.2f}%")

# ============================================================================
# PART 4: Rolling Performance Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PART 4: Rolling Performance Analysis")
print("=" * 80)

# Calculate rolling 1-year Sharpe ratio
rolling_window = 252  # 1 year
signals['rolling_sharpe'] = (
    signals['strategy_return_net'].rolling(rolling_window).mean() * 252
) / (
    signals['strategy_return_net'].rolling(rolling_window).std() * np.sqrt(252)
)

print(f"\nRolling 1-Year Sharpe Ratio:")
print(f"  Mean: {signals['rolling_sharpe'].mean():.2f}")
print(f"  Median: {signals['rolling_sharpe'].median():.2f}")
print(f"  Std Dev: {signals['rolling_sharpe'].std():.2f}")
print(f"  Min: {signals['rolling_sharpe'].min():.2f}")
print(f"  Max: {signals['rolling_sharpe'].max():.2f}")

# Yearly performance breakdown
signals['year'] = signals.index.year
yearly_performance = signals.groupby('year').apply(
    lambda x: pd.Series({
        'Strategy Return': (1 + x['strategy_return_net']).prod() - 1,
        'Buy&Hold Return': (1 + x['market_return']).prod() - 1,
        'Outperformance': ((1 + x['strategy_return_net']).prod() - 1) - ((1 + x['market_return']).prod() - 1)
    })
)

print(f"\nYearly Performance Breakdown:")
print("-" * 70)
print(f"{'Year':<8} {'Strategy':>12} {'Buy&Hold':>12} {'Alpha':>12}")
print("-" * 70)
for year, row in yearly_performance.iterrows():
    print(f"{year:<8} {row['Strategy Return']:>11.1%} {row['Buy&Hold Return']:>11.1%} {row['Outperformance']:>11.1%}")

# ============================================================================
# PART 5: Sensitivity Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PART 5: Sensitivity Analysis - Timing Windows")
print("=" * 80)

def backtest_with_params(prices, short_days, long_days_before_end):
    """Run backtest with different timing parameters"""
    sig = pd.DataFrame(index=prices.index)
    sig['price'] = prices
    sig['position'] = 0
    sig['month'] = sig.index.to_period('M')
    sig['day_of_month'] = sig.groupby('month').cumcount() + 1
    sig['days_in_month'] = sig.groupby('month')['day_of_month'].transform('max')
    sig['days_until_month_end'] = sig['days_in_month'] - sig['day_of_month']
    
    for idx in sig.index:
        day_num = sig.loc[idx, 'day_of_month']
        days_until_end = sig.loc[idx, 'days_until_month_end']
        
        if day_num >= 1 and day_num <= short_days:
            sig.loc[idx, 'position'] = -1
        elif days_until_end <= long_days_before_end and days_until_end > 1:
            sig.loc[idx, 'position'] = 1
        else:
            sig.loc[idx, 'position'] = 0
    
    sig['market_return'] = sig['price'].pct_change()
    sig['strategy_return'] = sig['position'].shift(1) * sig['market_return']
    
    total_return = (1 + sig['strategy_return']).prod() - 1
    annual_return = (1 + total_return) ** (252 / len(sig)) - 1
    volatility = sig['strategy_return'].std() * np.sqrt(252)
    sharpe = annual_return / volatility if volatility > 0 else 0
    
    return annual_return, volatility, sharpe

print("\nTesting different timing combinations:")
print("-" * 70)
print(f"{'Short Days':<12} {'Long Days':<12} {'Annual Ret':>12} {'Volatility':>12} {'Sharpe':>10}")
print("-" * 70)

sensitivity_results = []
for short_days in [3, 4, 5, 6, 7]:
    for long_days in [5, 6, 7, 8, 9]:
        ann_ret, vol, sharpe = backtest_with_params(prices, short_days, long_days)
        sensitivity_results.append({
            'short_days': short_days,
            'long_days': long_days,
            'annual_return': ann_ret,
            'volatility': vol,
            'sharpe': sharpe
        })
        print(f"{short_days:<12} {long_days:<12} {ann_ret:>11.1%} {vol:>11.1%} {sharpe:>10.2f}")

# Find optimal parameters
best = max(sensitivity_results, key=lambda x: x['sharpe'])
print(f"\nOptimal Parameters (by Sharpe):")
print(f"  Short days: {best['short_days']}")
print(f"  Long entry days before month-end: {best['long_days']}")
print(f"  Sharpe Ratio: {best['sharpe']:.2f}")

# ============================================================================
# PART 6: Market Regime Analysis
# ============================================================================
print("\n" + "=" * 80)
print("PART 6: Performance by Interest Rate Regime")
print("=" * 80)

# Approximate rate regimes based on TLT price trends
# Rising TLT = Falling Rates (bull market for bonds)
# Falling TLT = Rising Rates (bear market for bonds)

signals['tlt_200ma'] = signals['price'].rolling(200).mean()
signals['regime'] = 'Unknown'
signals.loc[signals['price'] > signals['tlt_200ma'], 'regime'] = 'Bull (Falling Rates)'
signals.loc[signals['price'] < signals['tlt_200ma'], 'regime'] = 'Bear (Rising Rates)'

regime_performance = signals.groupby('regime').apply(
    lambda x: pd.Series({
        'Days': len(x),
        'Strategy Ann. Return': (1 + x['strategy_return_net'].mean()) ** 252 - 1,
        'Market Ann. Return': (1 + x['market_return'].mean()) ** 252 - 1,
        'Strategy Sharpe': (x['strategy_return_net'].mean() * 252) / (x['strategy_return_net'].std() * np.sqrt(252))
    })
)

print(f"\nPerformance by Interest Rate Environment:")
print("-" * 70)
print(regime_performance.to_string())

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY & KEY TAKEAWAYS")
print("=" * 80)

print(f"""
Strategy: TLT Calendar Effect (Month-End Rebalancing)
Period: {len(signals)/252:.1f} years ({signals.index[0].date()} to {signals.index[-1].date()})

Results:
  Total Return: {total_return_strategy:.1%} vs {total_return_buyhold:.1%} (Buy&Hold)
  Annualized Return: {annual_return_strategy:.1%} vs {annual_return_buyhold:.1%}
  Sharpe Ratio: {sharpe_strategy:.2f} vs {sharpe_buyhold:.2f}
  Max Drawdown: {max_dd_strategy:.1%} vs {max_dd_buyhold:.1%}
  
Key Insights:
  ✓ Strategy exploits institutional month-end rebalancing flows
  ✓ Calendar-based approach requires no forecasting
  ✓ Reduced market exposure ({((signals['position'] != 0).sum()/len(signals)*100):.0f}% invested vs 100%)
  ✓ {'Outperforms' if annual_return_strategy > annual_return_buyhold else 'Underperforms'} buy-and-hold by {abs(annual_return_strategy-annual_return_buyhold):.1%} annually

Market Structure Foundation:
  - Passive funds rebalance to index weights at month-end
  - Pension funds adjust duration for reporting
  - Mutual funds reinvest inflows
  - Treasury volume spikes 30-50% on final trading day
  
Next Steps for Robustness:
  1. Out-of-sample testing on recent years
  2. Cross-validation with other Treasury ETFs (IEF, SHY)
  3. Add trend filters (e.g., only long in downtrend)
  4. Model actual borrow costs from prime broker
  5. Test with realistic slippage (wider spreads at month-end)
  6. Consider ETF creation/redemption effects
""")

print("=" * 80)
print("✓ Backtest Complete!")
print("=" * 80)

# Optional: Save results to CSV
output_file = f"tlt_calendar_backtest_{datetime.now().strftime('%Y%m%d')}.csv"
signals[['price', 'position', 'strategy_return_net', 'strategy_cumulative', 'buyhold_cumulative']].to_csv(output_file)
print(f"\n✓ Results saved to: {output_file}")

