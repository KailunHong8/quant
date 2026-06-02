"""
STEP 2: Portfolio Monitoring & Performance Analysis

⚠ Use this AFTER selecting stocks with stock_selection_buffett.py

Monitors your selected portfolio with:
- Market data (OpenBB)
- Alpha/Beta analysis (CAPM)
- Portfolio analytics (Sharpe, volatility, correlation)
- Risk metrics (VaR, CVaR, Drawdown)
- Warren Buffett value criteria tracking
- GS Quant instruments
- ArcticDB caching

WORKFLOW:
  Step 1: stock_selection_buffett.py  → Screen universe, find value stocks
  Step 2: comprehensive_analysis.py   → Monitor your portfolio (this file)
  
UPDATE THE SYMBOLS BELOW with your selected stocks from Step 1!
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

# Helper function
def format_date(dt):
    if isinstance(dt, date) and not hasattr(dt, 'hour'):
        return dt
    elif hasattr(dt, 'date') and callable(dt.date):
        return dt.date()
    else:
        return str(dt)

# Helper functions for ticker format conversion
def ticker_for_openbb(symbol):
    """Convert ticker to OpenBB format (hyphen to dot for class shares)"""
    # BRK-B → BRK.B, BF-A → BF.A, etc.
    return symbol.replace('-', '.')

def ticker_for_yfinance(symbol):
    """Convert ticker to yfinance format (dot to hyphen for class shares)"""
    # BRK.B → BRK-B, BF.A → BF-A, etc.
    # But don't convert other dots (not class shares)
    if '.' in symbol and len(symbol.split('.')[-1]) == 1:
        # Only convert if last part is single letter (A, B, C = class shares)
        return symbol.replace('.', '-')
    return symbol

# Initialize ArcticDB if available
ARCTIC_AVAILABLE = False
try:
    import arcticdb as adb
    arctic = adb.Arctic("lmdb://quant_data")
    fundamentals_lib = arctic.get_library("fundamentals", create_if_missing=True)
    prices_lib = arctic.get_library("prices", create_if_missing=True)
    ARCTIC_AVAILABLE = True
    print("✓ ArcticDB initialized for caching")
except ImportError:
    print("ℹ ArcticDB not available (pip install arcticdb for caching)")

# ============================================================================
# PART 1: Market Data + Benchmark
# ============================================================================
print("\n" + "=" * 70)
print("PART 1: Market Data Collection")
print("=" * 70)

try:
    from openbb import obb
    
    # ========================================================================
    # UPDATE THIS: Replace with stocks from stock_selection_buffett.py
    # ========================================================================
    # Example: After running stock selection, update this list with your picks
    # symbols = ["JNJ", "PG", "KO", "WMT"]  # Your selected value stocks
    
    symbols = ['TEL', 'ABT', 'CBOE', 'DOV', 'COIN', 'BRK.B', 'SWKS', 'TTD', 'EOG', 'STE', 'TLT']  # Current portfolio
    benchmark = "SPY"
    
    print(f"\nFetching data for: {', '.join(symbols)} + {benchmark}")
    
    # Convert symbols for OpenBB (handles BRK.B, BF.A, etc.)
    # Note: Users can input either format (BRK-B or BRK.B), we normalize both
    symbols_openbb = [ticker_for_openbb(s) for s in symbols]
    
    # Fetch portfolio data
    result = obb.equity.price.historical(symbol=','.join(symbols_openbb))
    data = result.to_dataframe()
    
    if 'symbol' in data.columns:
        portfolio_prices = data.pivot_table(index='date', columns='symbol', values='close')
        # Rename columns back to original format if needed
        portfolio_prices.columns = symbols[:len(portfolio_prices.columns)]
    else:
        portfolio_prices = pd.DataFrame({symbols[0]: data['close']})
    
    # Ensure we have all requested symbols
    available_symbols = [s for s in symbols if s in portfolio_prices.columns]
    if len(available_symbols) < len(symbols):
        missing = set(symbols) - set(available_symbols)
        print(f"  ⚠ Could not fetch data for: {', '.join(missing)}")
    
    portfolio_prices = portfolio_prices[available_symbols].dropna()
    symbols = available_symbols  # Update to only include available symbols
    
    # Fetch benchmark
    spy_result = obb.equity.price.historical(symbol=benchmark)
    spy_data = spy_result.to_dataframe()
    spy_prices = spy_data['close']
    
    # Align dates
    common_dates = portfolio_prices.index.intersection(spy_prices.index)
    portfolio_prices = portfolio_prices.loc[common_dates]
    spy_prices = spy_prices.loc[common_dates]
    
    # Cache in ArcticDB (convert date index to datetime for compatibility)
    if ARCTIC_AVAILABLE:
        try:
            # Convert date index to datetime if needed
            if isinstance(portfolio_prices.index[0], date) and not isinstance(portfolio_prices.index[0], datetime):
                portfolio_prices.index = pd.to_datetime(portfolio_prices.index)
                spy_prices.index = pd.to_datetime(spy_prices.index)
            
            for sym in symbols:
                prices_lib.write(f"{sym}_daily", portfolio_prices[[sym]])
            prices_lib.write("SPY_daily", pd.DataFrame({'close': spy_prices}))
        except Exception as e:
            print(f"  ⚠ ArcticDB cache write failed: {e}")
    
    print(f"✓ Fetched {len(portfolio_prices)} days of data")
    print(f"  Date range: {format_date(portfolio_prices.index[0])} to {format_date(portfolio_prices.index[-1])}")
    
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# ============================================================================
# PART 2: Fundamental Data (OpenBB)
# ============================================================================
print("\n" + "=" * 70)
print("PART 2: Fundamental Analysis")
print("=" * 70)

fundamentals = {}

for symbol in symbols:
    try:
        # Try to fetch from cache first
        if ARCTIC_AVAILABLE and fundamentals_lib.has_symbol(f"{symbol}_metrics"):
            cached = fundamentals_lib.read(f"{symbol}_metrics").data
            if (datetime.now() - cached.index[0]).days < 30:  # Fresh data
                fundamentals[symbol] = cached.to_dict('records')[0]
                print(f"{symbol}: Using cached fundamentals")
                continue
        
        # Fetch fundamentals using yfinance directly (OpenBB providers require API keys)
        print(f"{symbol}: Fetching fundamentals via yfinance...", end=" ")
        
        try:
            import yfinance as yf
            import time
            
            # Retry logic with exponential backoff
            max_retries = 3
            retry_delay = 1
            ticker = None
            info = {}
            
            for attempt in range(max_retries):
                try:
                    # Create ticker object (convert to yfinance format: BRK.B → BRK-B)
                    symbol_yf = ticker_for_yfinance(symbol)
                    if symbol_yf != symbol:
                        print(f"[Converting {symbol} → {symbol_yf}]", end=" ")
                    ticker = yf.Ticker(symbol_yf)
                    info = ticker.info
                    
                    # Check if we got valid fundamental data (not just any data)
                    has_fundamentals = info and (
                        info.get('priceToBook') is not None or 
                        info.get('trailingPE') is not None or
                        info.get('marketCap') is not None
                    )
                    if has_fundamentals:
                        break
                    elif attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        raise e
            
            if not info or not (info.get('priceToBook') or info.get('trailingPE') or info.get('marketCap')):
                raise Exception(f"No fundamental data returned from yfinance for {symbol_yf}")
            
            # Get financial statements for calculated ratios
            try:
                balance_sheet = ticker.balance_sheet
                financials = ticker.financials
                
                # Calculate ratios from statements if available
                if not balance_sheet.empty and not financials.empty:
                    bs = balance_sheet.iloc[:, 0]  # Most recent
                    fin = financials.iloc[:, 0]
                    
                    # Debt/Equity
                    total_debt = bs.get('Total Debt', bs.get('Long Term Debt', 0))
                    stockholder_equity = bs.get('Stockholders Equity', bs.get('Total Equity Gross Minority Interest', 1))
                    debt_equity_calc = total_debt / stockholder_equity if stockholder_equity else None
                    
                    # Current Ratio
                    current_assets = bs.get('Current Assets', 0)
                    current_liabilities = bs.get('Current Liabilities', 1)
                    current_ratio_calc = current_assets / current_liabilities if current_liabilities else None
                    
                    # ROE and ROA
                    net_income = fin.get('Net Income', 0)
                    total_assets = bs.get('Total Assets', 1)
                    roe_calc = net_income / stockholder_equity if stockholder_equity else None
                    roa_calc = net_income / total_assets if total_assets else None
                    
                    # Interest Coverage
                    ebit = fin.get('EBIT', fin.get('Operating Income', 0))
                    interest_expense = fin.get('Interest Expense', 1)
                    interest_coverage_calc = ebit / abs(interest_expense) if interest_expense else None
                else:
                    debt_equity_calc = None
                    current_ratio_calc = None
                    roe_calc = None
                    roa_calc = None
                    interest_coverage_calc = None
            except Exception:
                debt_equity_calc = None
                current_ratio_calc = None
                roe_calc = None
                roa_calc = None
                interest_coverage_calc = None
            
            # Extract metrics from info dict (prefer calculated, fallback to info)
            metrics = {
                'symbol': symbol,
                'date': datetime.now(),
                'pb_ratio': info.get('priceToBook'),
                'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
                'debt_equity': debt_equity_calc or info.get('debtToEquity'),
                'current_ratio': current_ratio_calc or info.get('currentRatio'),
                'roe': roe_calc or info.get('returnOnEquity'),
                'roa': roa_calc or info.get('returnOnAssets'),
                'interest_coverage': interest_coverage_calc,
                'market_cap': info.get('marketCap'),
            }
            
            fundamentals[symbol] = metrics
            
            # Cache in ArcticDB
            if ARCTIC_AVAILABLE:
                try:
                    df_cache = pd.DataFrame([metrics])
                    df_cache['date'] = pd.to_datetime(df_cache['date'])
                    df_cache = df_cache.set_index('date')
                    fundamentals_lib.write(f"{symbol}_metrics", df_cache)
                except Exception:
                    pass
            
            print("✓")
            
        except Exception as e:
            print(f"⚠ Error: {e}")
            # Fundamentals failed, but that's OK - price-based metrics work fine
            metrics = {
                'symbol': symbol,
                'date': datetime.now(),
                'pb_ratio': None,
                'pe_ratio': None,
                'debt_equity': None,
                'current_ratio': None,
                'roe': None,
                'roa': None,
                'interest_coverage': None,
                'market_cap': None,
            }
            fundamentals[symbol] = metrics
            
    except Exception as e:
        print(f"{symbol}: Error - {e}")
        fundamentals[symbol] = {'symbol': symbol, 'date': datetime.now()}


# ============================================================================
# PART 3: Portfolio Analytics (Returns, Vol, Sharpe)
# ============================================================================
print("\n" + "=" * 70)
print("PART 3: Portfolio Analytics")
print("=" * 70)

returns = portfolio_prices.pct_change().dropna()
spy_returns = spy_prices.pct_change().dropna()

# Align
common_dates = returns.index.intersection(spy_returns.index)
returns = returns.loc[common_dates]
spy_returns = spy_returns.loc[common_dates]

print(f"\nAnalysis Period: {len(returns)} trading days")
print(f"Date range: {format_date(returns.index[0])} to {format_date(returns.index[-1])}")

# Individual asset stats
print("\n" + "-" * 70)
print(f"{'Symbol':<8} {'Return':>8} {'Vol':>8} {'Sharpe':>8} {'Beta':>8} {'Alpha':>8}")
print("-" * 70)

results = []
rf = 0.05  # 5% risk-free rate

for symbol in symbols:
    # Return and vol
    annual_ret = returns[symbol].mean() * 252
    annual_vol = returns[symbol].std() * np.sqrt(252)
    sharpe = (annual_ret - rf) / annual_vol if annual_vol > 0 else 0
    
    # Beta and Alpha (vs S&P 500)
    covariance = returns[symbol].cov(spy_returns)
    market_var = spy_returns.var()
    beta = covariance / market_var
    
    market_ret = spy_returns.mean() * 252
    capm_predicted = rf + beta * (market_ret - rf)
    alpha = annual_ret - capm_predicted
    
    results.append({
        'Symbol': symbol,
        'Return': annual_ret,
        'Volatility': annual_vol,
        'Sharpe': sharpe,
        'Beta': beta,
        'Alpha': alpha,
        'Fundamentals': fundamentals.get(symbol, {})
    })
    
    print(f"{symbol:<8} {annual_ret:7.2%} {annual_vol:7.2%} {sharpe:7.2f} {beta:7.2f} {alpha:7.2%}")

# Portfolio level
portfolio_ret = returns.mean(axis=1)
port_annual_ret = portfolio_ret.mean() * 252
port_annual_vol = portfolio_ret.std() * np.sqrt(252)
port_sharpe = (port_annual_ret - rf) / port_annual_vol

spy_annual_ret = spy_returns.mean() * 252
spy_annual_vol = spy_returns.std() * np.sqrt(252)

print("\n" + "-" * 70)
print("Portfolio vs S&P 500")
print("-" * 70)
print(f"{'Metric':<20} {'Portfolio':>12} {'S&P 500':>12} {'Difference':>12}")
print(f"{'Return':<20} {port_annual_ret:11.2%} {spy_annual_ret:11.2%} {port_annual_ret-spy_annual_ret:11.2%}")
print(f"{'Volatility':<20} {port_annual_vol:11.2%} {spy_annual_vol:11.2%} {port_annual_vol-spy_annual_vol:11.2%}")
print(f"{'Sharpe':<20} {port_sharpe:11.2f} {(spy_annual_ret-rf)/spy_annual_vol:11.2f}")

# ============================================================================
# PART 4: Risk Metrics
# ============================================================================
print("\n" + "=" * 70)
print("PART 4: Risk Metrics")
print("=" * 70)

var_95 = np.percentile(portfolio_ret, 5)
var_99 = np.percentile(portfolio_ret, 1)
cvar_95 = portfolio_ret[portfolio_ret <= var_95].mean()
cvar_99 = portfolio_ret[portfolio_ret <= var_99].mean()

cum_returns = (1 + portfolio_ret).cumprod()
running_max = cum_returns.expanding().max()
drawdown = (cum_returns - running_max) / running_max
max_drawdown = drawdown.min()

print(f"\n95% VaR:          {var_95:7.2%}")
print(f"99% VaR:          {var_99:7.2%}")
print(f"95% CVaR:         {cvar_95:7.2%}")
print(f"Max Drawdown:     {max_drawdown:7.2%}")

# ============================================================================
# PART 5: Buffett Value Screening
# ============================================================================
print("\n" + "=" * 70)
print("PART 5: Warren Buffett Value Criteria")
print("=" * 70)

print("""
Buffett's Criteria:
1. Debt/Equity < 0.5 (low leverage)
2. Current Ratio 1.5-2.5 (good liquidity)
3. P/B < 1.5 (undervalued)
4. ROE > 8% (profitable)
5. ROA > 6% (efficient)
6. Interest Coverage > 5 (can service debt)
""")

print("-" * 80)
print(f"{'Symbol':<8} {'P/B':>10} {'D/E':>10} {'CR':>10} {'ROE':>10} {'ROA':>10} {'Int Cov':>10} {'Score':>8}")
print("-" * 80)

for result in results:
    symbol = result['Symbol']
    fund = result['Fundamentals']
    
    # Get raw values
    pb = fund.get('pb_ratio')
    de = fund.get('debt_equity')
    cr = fund.get('current_ratio')
    roe = fund.get('roe')
    roa = fund.get('roa')
    ic = fund.get('interest_coverage')
    
    # Calculate score and format with pass/fail indicators
    score = 0
    checks = []
    
    # P/B < 1.5
    if pb is not None:
        pb_str = f"{pb:6.2f}" + (" ✓" if pb < 1.5 else " ✗")
        if pb < 1.5:
            score += 1
            checks.append('P/B')
    else:
        pb_str = "N/A"
    
    # D/E < 0.5
    if de is not None:
        de_str = f"{de:6.2f}" + (" ✓" if de < 0.5 else " ✗")
        if de < 0.5:
            score += 1
            checks.append('D/E')
    else:
        de_str = "N/A"
    
    # Current Ratio 1.5-2.5
    if cr is not None:
        cr_str = f"{cr:6.2f}" + (" ✓" if 1.5 < cr < 2.5 else " ✗")
        if 1.5 < cr < 2.5:
            score += 1
            checks.append('CR')
    else:
        cr_str = "N/A"
    
    # ROE > 8%
    if roe is not None:
        roe_str = f"{roe:6.1%}" + (" ✓" if roe > 0.08 else " ✗")
        if roe > 0.08:
            score += 1
            checks.append('ROE')
    else:
        roe_str = "N/A"
    
    # ROA > 6%
    if roa is not None:
        roa_str = f"{roa:6.1%}" + (" ✓" if roa > 0.06 else " ✗")
        if roa > 0.06:
            score += 1
            checks.append('ROA')
    else:
        roa_str = "N/A"
    
    # Interest Coverage > 5
    if ic is not None:
        ic_str = f"{ic:6.1f}" + (" ✓" if ic > 5 else " ✗")
        if ic > 5:
            score += 1
            checks.append('IC')
    else:
        ic_str = "N/A"
    
    result['BuffettScore'] = score
    result['BuffettChecks'] = checks
    
    print(f"{symbol:<8} {pb_str:>10} {de_str:>10} {cr_str:>10} {roe_str:>10} {roa_str:>10} {ic_str:>10} {score:>4}/6")
    
    # Show which criteria passed
    if checks:
        print(f"         Passed: {', '.join(checks)}")
    else:
        print(f"         No criteria passed")

# ============================================================================
# PART 6: Composite Ranking
# ============================================================================
print("\n" + "=" * 70)
print("PART 6: Composite Ranking")
print("=" * 70)

# Check if fundamentals are available
has_any_fundamentals = any(fundamentals[sym].get('pb_ratio') is not None for sym in symbols)

if has_any_fundamentals:
    print("""
Combines:
- Sharpe Ratio (risk-adjusted return) - 40%
- Alpha (excess return vs CAPM) - 30%
- Buffett Score (value fundamentals) - 30%
""")
else:
    print("""
Note: Fundamentals unavailable (yfinance connection issue)
Ranking based on price metrics only:
- Sharpe Ratio (risk-adjusted return) - 60%
- Alpha (excess return vs CAPM) - 40%

These quantitative metrics are still highly valuable for stock selection!
""")

df_results = pd.DataFrame(results)

# Normalize metrics to 0-100 scale
df_results['Sharpe_norm'] = (df_results['Sharpe'] - df_results['Sharpe'].min()) / (df_results['Sharpe'].max() - df_results['Sharpe'].min()) * 100
df_results['Alpha_norm'] = (df_results['Alpha'] - df_results['Alpha'].min()) / (df_results['Alpha'].max() - df_results['Alpha'].min()) * 100
df_results['Buffett_norm'] = df_results['BuffettScore'] / 6 * 100

# Check if we have any fundamental data
has_fundamentals = df_results['BuffettScore'].sum() > 0

# Composite score (adjust weights based on data availability)
if has_fundamentals:
    # Use all three factors
    df_results['Composite'] = (
        0.4 * df_results['Sharpe_norm'] +
        0.3 * df_results['Alpha_norm'] +
        0.3 * df_results['Buffett_norm']
    )
else:
    # No fundamentals, use only price-based metrics
    df_results['Composite'] = (
        0.6 * df_results['Sharpe_norm'] +
        0.4 * df_results['Alpha_norm']
    )

df_results = df_results.sort_values('Composite', ascending=False)

print("\n" + "-" * 80)
print(f"{'Rank':<6} {'Symbol':<8} {'Sharpe':>8} {'Alpha':>8} {'Return':>8} {'Beta':>8} {'Buffett':>9} {'Score':>8}")
print("-" * 80)

for idx, (_, row) in enumerate(df_results.iterrows(), 1):
    buffett_str = f"{row['BuffettScore']}/6"
    print(f"{idx:<6} {row['Symbol']:<8} {row['Sharpe']:7.2f} {row['Alpha']:7.2%} {row['Return']:7.2%} {row['Beta']:7.2f} {buffett_str:>9} {row['Composite']:7.1f}")
    
    # Show passed Buffett criteria
    if row['BuffettChecks']:
        print(f"       Passed: {', '.join(row['BuffettChecks'])}")
    
    # Show key fundamental values if available
    fund = row['Fundamentals']
    if fund.get('pb_ratio') or fund.get('roe'):
        details = []
        if fund.get('pb_ratio'):
            details.append(f"P/B={fund['pb_ratio']:.2f}")
        if fund.get('pe_ratio'):
            details.append(f"P/E={fund['pe_ratio']:.1f}")
        if fund.get('roe'):
            details.append(f"ROE={fund['roe']:.1%}")
        if details:
            print(f"       {' | '.join(details)}")

# ============================================================================
# PART 7: GS Quant Instruments
# ============================================================================
print("\n" + "=" * 70)
print("PART 7: GS Quant Instrument Construction")
print("=" * 70)

try:
    from gs_quant.instrument import EqStock
    
    print("\nCreating instruments for top-ranked stocks:")
    for _, row in df_results.head(3).iterrows():
        symbol = row['Symbol']
        eq = EqStock(identifier=symbol, name=symbol)
        print(f"  ✓ {symbol}: {type(eq).__name__}")
    
    print("\nGS Quant modules available for further analysis:")
    print("  - gs_quant.risk: Calculate Greeks, scenario analysis")
    print("  - gs_quant.backtests: Strategy backtesting")
    print("  - gs_quant.markets: Historical pricing contexts")
    
except ImportError:
    print("GS Quant not available (optional)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 70)

best = df_results.iloc[0]
print(f"""
Top Pick: {best['Symbol']}
  - Composite Score: {best['Composite']:.1f}/100
  - Sharpe Ratio: {best['Sharpe']:.2f}
  - Alpha: {best['Alpha']:.2%}
  - Buffett Score: {best['BuffettScore']}/6
  - Buffett Criteria: {', '.join(best['BuffettChecks']) if best['BuffettChecks'] else 'None passed'}

Portfolio Metrics:
  - Annual Return: {port_annual_ret:.2%} vs S&P 500: {spy_annual_ret:.2%}
  - Alpha: {port_annual_ret - spy_annual_ret:.2%}
  - Sharpe Ratio: {port_sharpe:.2f}
  - Max Drawdown: {max_drawdown:.2%}

Key Insights:
""")

if port_annual_ret > spy_annual_ret:
    print(f"  ✓ Portfolio outperforming S&P 500 by {port_annual_ret - spy_annual_ret:.2%}")
else:
    print(f"  ⚠ Portfolio underperforming S&P 500 by {abs(port_annual_ret - spy_annual_ret):.2%}")

if best['BuffettScore'] >= 4:
    print(f"  ✓ Top pick {best['Symbol']} passes {best['BuffettScore']}/6 Buffett criteria")
else:
    print(f"  ⚠ Top pick {best['Symbol']} only passes {best['BuffettScore']}/6 Buffett criteria")

print("\n" + "=" * 70)
print("✓ Analysis complete!")
print("=" * 70)

