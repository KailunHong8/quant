"""
GS Quant + OpenBB Integration Example

Professional quant workflow: Market Data → Portfolio Analytics → Risk Management → Instruments

For detailed explanations, see: docs/integration_guide.md
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
import warnings
warnings.filterwarnings('ignore')

# Helper function to format dates (handles both datetime and date objects)
def format_date(dt):
    """Convert datetime or date object to date string"""
    if isinstance(dt, date) and not hasattr(dt, 'hour'):
        # Already a date object
        return dt
    elif hasattr(dt, 'date') and callable(dt.date):
        # datetime object, convert to date
        return dt.date()
    else:
        # fallback to string
        return str(dt)

# ============================================================================
# PART 1: Market Data Collection
# ============================================================================
print("=" * 70)
print("PART 1: Market Data Collection")
print("=" * 70)

try:
    from openbb import obb
    import yfinance as yf
    
    symbols = ["DASH", "GOOGL", "TSLA", "NVDA"]
    
    print(f"\nFetching data for: {', '.join(symbols)}")
    print("Using OpenBB with yfinance provider")
    
    # Fetch data via OpenBB
    result = obb.equity.price.historical(symbol=','.join(symbols))
    data = result.to_dataframe()
    
    # Pivot for multiple symbols (symbol column → columns per symbol)
    if 'symbol' in data.columns:
        portfolio_prices = data.pivot_table(index='date', columns='symbol', values='close')
    else:
        portfolio_prices = pd.DataFrame({symbols[0]: data['close']})
    
    portfolio_prices = portfolio_prices[symbols].dropna()
    
    print(f"\n✓ Successfully fetched {len(portfolio_prices)} days of data using OpenBB")
    print(f"  Date range: {format_date(portfolio_prices.index[0])} to {format_date(portfolio_prices.index[-1])}")
    print(f"\nLatest prices:")
    print(portfolio_prices.tail())
        
except Exception as e:
    print(f"Error fetching data via OpenBB: {e}")
    print("Using yfinance as fallback")
    
    data = yf.download(symbols, period="1y", auto_adjust=False, progress=False)
    
    if len(symbols) == 1:
        portfolio_prices = pd.DataFrame({symbols[0]: data['Close']})
    else:
        portfolio_prices = data['Close'][symbols]
    
    portfolio_prices = portfolio_prices.dropna()
    print(f"\n✓ Successfully fetched {len(portfolio_prices)} days of data")
    print(f"  Date range: {format_date(portfolio_prices.index[0])} to {format_date(portfolio_prices.index[-1])}")
    print(f"\nLatest prices:")
    print(portfolio_prices.tail())

# ============================================================================
# PART 2: Portfolio Analytics
# ============================================================================
print("\n" + "=" * 70)
print("PART 2: Portfolio Analytics (Chapter 8: Portfolio Theory)")
print("=" * 70)

if 'portfolio_prices' in locals() and not portfolio_prices.empty:
    # Calculate returns
    returns = portfolio_prices.pct_change().dropna()
    
    print(f"\nAnalysis Period: {len(returns)} trading days")
    print(f"Date range: {format_date(returns.index[0])} to {format_date(returns.index[-1])}")
    
    # Individual asset statistics
    print("\n" + "-" * 70)
    print("Individual Assets (Annualized Metrics)")
    print("-" * 70)
    
    asset_stats = []
    for col in returns.columns:
        # Annualize metrics: 252 = trading days/year
        # Return: daily_mean × 252
        # Volatility: daily_std × √252 (volatility scales with √time)
        mean_return = returns[col].mean() * 252
        volatility = returns[col].std() * np.sqrt(252)
        sharpe = mean_return / volatility if volatility > 0 else 0
        asset_stats.append({
            'Asset': col,
            'Return': mean_return,
            'Volatility': volatility,
            'Sharpe': sharpe
        })
        print(f"  {col:6s}: Return={mean_return:7.2%}, Vol={volatility:6.2%}, Sharpe={sharpe:5.2f}")
    
    # Portfolio statistics (equal-weighted)
    portfolio_returns = returns.mean(axis=1)
    portfolio_mean = portfolio_returns.mean() * 252
    portfolio_vol = portfolio_returns.std() * np.sqrt(252)
    portfolio_sharpe = portfolio_mean / portfolio_vol if portfolio_vol > 0 else 0
    
    print("\n" + "-" * 70)
    print("Equal-Weighted Portfolio")
    print("-" * 70)
    print(f"  Annual Return:     {portfolio_mean:7.2%}")
    print(f"  Annual Volatility: {portfolio_vol:6.2%}")
    print(f"  Sharpe Ratio:      {portfolio_sharpe:5.2f}")
    
    # Diversification benefit
    avg_individual_vol = np.mean([s['Volatility'] for s in asset_stats])
    div_benefit = (avg_individual_vol - portfolio_vol) / avg_individual_vol
    print(f"  Diversification benefit: {div_benefit:.1%} reduction in volatility")
    
    # Correlation matrix
    corr_matrix = returns.corr()
    print("\n" + "-" * 70)
    print("Correlation Matrix")
    print("-" * 70)
    print(corr_matrix.round(3))
    
    avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
    print(f"\nAverage correlation: {avg_corr:.3f}")
    
    # Covariance matrix
    cov_matrix = returns.cov() * 252
    print("\n" + "-" * 70)
    print("Annualized Covariance Matrix")
    print("-" * 70)
    print(cov_matrix.round(6))

# ============================================================================
# PART 3: Risk Metrics
# ============================================================================
print("\n" + "=" * 70)
print("PART 3: Risk Metrics (Chapter 7: Risk Management)")
print("=" * 70)

if 'portfolio_returns' in locals():
    # Value at Risk (VaR)
    var_95 = np.percentile(portfolio_returns, 5)
    var_99 = np.percentile(portfolio_returns, 1)
    
    # Conditional Value at Risk (CVaR / Expected Shortfall)
    cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
    cvar_99 = portfolio_returns[portfolio_returns <= var_99].mean()
    
    print("\n" + "-" * 70)
    print("Value at Risk (VaR)")
    print("-" * 70)
    print(f"  95% VaR: {var_95:7.2%} (worst 5% of days)")
    print(f"  99% VaR: {var_99:7.2%} (worst 1% of days)")
    
    print(f"\n  Conditional VaR (Expected Shortfall):")
    print(f"  95% CVaR: {cvar_95:7.2%} (avg loss when VaR breached)")
    print(f"  99% CVaR: {cvar_99:7.2%}")
    
    # Maximum Drawdown
    cum_returns = (1 + portfolio_returns).cumprod()
    running_max = cum_returns.expanding().max()
    drawdown = (cum_returns - running_max) / running_max
    max_drawdown = drawdown.min()
    
    max_dd_idx = drawdown.idxmin()
    peak_idx = running_max[:max_dd_idx].idxmax()
    dd_duration = (max_dd_idx - peak_idx).days
    
    print("\n" + "-" * 70)
    print("Drawdown Analysis")
    print("-" * 70)
    print(f"  Maximum Drawdown: {max_drawdown:7.2%}")
    print(f"  Peak date:  {format_date(peak_idx)}")
    print(f"  Trough date: {format_date(max_dd_idx)}")
    print(f"  Duration: {dd_duration} days")
    
    # Risk-Adjusted Return Metrics
    downside_returns = portfolio_returns[portfolio_returns < 0]
    downside_std = downside_returns.std() * np.sqrt(252)
    sortino = portfolio_mean / downside_std if downside_std > 0 else 0
    calmar = portfolio_mean / abs(max_drawdown) if max_drawdown != 0 else 0
    
    print("\n" + "-" * 70)
    print("Risk-Adjusted Performance")
    print("-" * 70)
    print(f"  Sharpe Ratio:  {portfolio_sharpe:5.2f}")
    print(f"  Sortino Ratio: {sortino:5.2f}")
    print(f"  Calmar Ratio:  {calmar:5.2f}")

# ============================================================================
# PART 4: GS Quant Integration
# ============================================================================
print("\n" + "=" * 70)
print("PART 4: GS Quant Integration - Instrument Construction")
print("=" * 70)

try:
    import gs_quant
    from gs_quant.instrument import EqStock
    
    print(f"✓ GS Quant version: {gs_quant.__version__}")
    
    # Create equity instruments
    print("\nCreating equity instruments:")
    instruments = {}
    for symbol in symbols:
        equity = EqStock(identifier=symbol, name=symbol)
        instruments[symbol] = equity
        print(f"  ✓ {symbol}: {type(equity).__name__}")
    
    print("\nGS Quant modules available:")
    print("  - gs_quant.instrument: EqStock, EqOption, IRSwap, FXOption, Bond")
    print("  - gs_quant.risk: Delta, Gamma, Vega, scenario analysis")
    print("  - gs_quant.backtests: Strategy backtesting framework")
    print("  - gs_quant.markets: Pricing contexts (requires GS credentials)")
    
except ImportError as e:
    print(f"✗ GS Quant import error: {e}")
except Exception as e:
    print(f"✗ GS Quant error: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
✓ Successfully demonstrated:
  1. Market data collection via OpenBB (yfinance provider)
  2. Portfolio analytics (returns, volatility, Sharpe ratio, correlations)
  3. Risk metrics (VaR, CVaR, drawdown, risk-adjusted returns)
  4. GS Quant instrument construction

For detailed explanations of the concepts, see: docs/integration_guide.md

Key Metrics Summary:""")

if 'portfolio_sharpe' in locals():
    print(f"  Portfolio Sharpe Ratio: {portfolio_sharpe:.2f}")
    print(f"  Portfolio Max Drawdown: {max_drawdown:.2%}")
    print(f"  99% Daily VaR: {var_99:.2%}")
    print(f"  Diversification Benefit: {div_benefit:.1%}")

print("\n" + "=" * 70)
print("✓ Script completed successfully!")
print("=" * 70)
