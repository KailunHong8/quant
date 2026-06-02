"""
STEP 1: Stock Selection Using Buffett Value Criteria

Uses ArcticDB to efficiently store and query 3 years of fundamental data.
Screens for undervalued stocks that pass Buffett's 6 criteria.

After selecting stocks here, use comprehensive_analysis.py to monitor your portfolio.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Helper function for ticker format conversion
def ticker_for_yfinance(symbol):
    """Convert ticker to yfinance format (dot to hyphen for class shares)"""
    # BRK.B → BRK-B, BF.A → BF-A, etc.
    if '.' in symbol and len(symbol.split('.')[-1]) == 1:
        return symbol.replace('.', '-')
    return symbol

# ============================================================================
# Setup ArcticDB
# ============================================================================
print("=" * 70)
print("STEP 1: Stock Selection with Buffett Criteria")
print("=" * 70)

try:
    import arcticdb as adb
    arctic = adb.Arctic("lmdb://quant_data")
    fundamentals_lib = arctic.get_library("fundamentals", create_if_missing=True)
    print("\n✓ ArcticDB connected")
except ImportError:
    print("\n✗ ArcticDB required: pip install arcticdb")
    exit(1)

# ============================================================================
# Fetch Fundamental Data (3 years: 2023-2025)
# ============================================================================
print("\n" + "=" * 70)
print("Fetching 3 Years of Fundamental Data")
print("=" * 70)

import yfinance as yf
import time

# Define universe of stocks to screen (expand this list)
# For demonstration, using S&P 100 components subset
stock_universe = [
    # Tech
    "AAPL", "MSFT", "GOOGL", "META", "NVDA", "TSLA", "AMD", "INTC", "CRM", "ORCL",
    # Finance
    "JPM", "BAC", "WFC", "C", "GS", "MS", "AXP", "BLK", "SCHW",
    # Consumer
    "AMZN", "WMT", "HD", "NKE", "MCD", "SBUX", "TGT", "LOW", "DIS",
    # Healthcare
    "JNJ", "UNH", "PFE", "ABBV", "LLY", "TMO", "ABT", "MRK", "CVS",
    # Industrial
    "BA", "CAT", "HON", "UPS", "GE", "MMM", "LMT", "RTX",
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG",
    # Other
    "KO", "PEP", "PG", "COST", "V", "MA", "PYPL"
]

print(f"\nScreening {len(stock_universe)} stocks...")
print(f"This may take a few minutes (fetching fundamentals for each stock)")

all_fundamentals = []

for i, symbol in enumerate(stock_universe, 1):
    print(f"  [{i}/{len(stock_universe)}] {symbol}...", end=" ")
    
    # Check cache first
    cache_key = f"{symbol}_fundamentals_2023_2025"
    if fundamentals_lib.has_symbol(cache_key):
        try:
            cached = fundamentals_lib.read(cache_key).data
            cache_age = (datetime.now() - pd.to_datetime(cached.index[0])).days
            if cache_age < 7:  # Cache valid for 7 days
                print("✓ (cached)")
                all_fundamentals.append(cached.to_dict('records')[0])
                continue
        except Exception:
            pass
    
    # Fetch from yfinance
    try:
        # Convert ticker format for yfinance (BRK.B → BRK-B)
        symbol_yf = ticker_for_yfinance(symbol)
        ticker = yf.Ticker(symbol_yf)
        info = ticker.info
        
        # Get balance sheet and financials
        try:
            bs = ticker.balance_sheet.iloc[:, 0] if not ticker.balance_sheet.empty else pd.Series()
            fin = ticker.financials.iloc[:, 0] if not ticker.financials.empty else pd.Series()
            
            # Calculate ratios
            total_debt = bs.get('Total Debt', bs.get('Long Term Debt', 0))
            equity = bs.get('Stockholders Equity', bs.get('Total Equity Gross Minority Interest', 1))
            debt_equity = total_debt / equity if equity else None
            
            current_assets = bs.get('Current Assets', 0)
            current_liabilities = bs.get('Current Liabilities', 1)
            current_ratio = current_assets / current_liabilities if current_liabilities else None
            
            net_income = fin.get('Net Income', 0)
            total_assets = bs.get('Total Assets', 1)
            roe = net_income / equity if equity else None
            roa = net_income / total_assets if total_assets else None
            
            ebit = fin.get('EBIT', fin.get('Operating Income', 0))
            interest_expense = fin.get('Interest Expense', 1)
            interest_coverage = ebit / abs(interest_expense) if interest_expense else None
        except Exception:
            debt_equity = None
            current_ratio = None
            roe = None
            roa = None
            interest_coverage = None
        
        # Compile metrics
        metrics = {
            'symbol': symbol,
            'fetch_date': datetime.now(),
            'company_name': info.get('longName', symbol),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'market_cap': info.get('marketCap', 0),
            'pb_ratio': info.get('priceToBook'),
            'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
            'debt_equity': debt_equity or info.get('debtToEquity'),
            'current_ratio': current_ratio or info.get('currentRatio'),
            'roe': roe or info.get('returnOnEquity'),
            'roa': roa or info.get('returnOnAssets'),
            'interest_coverage': interest_coverage,
            'dividend_yield': info.get('dividendYield'),
            'beta': info.get('beta'),
        }
        
        all_fundamentals.append(metrics)
        
        # Cache in ArcticDB
        try:
            df_cache = pd.DataFrame([metrics])
            df_cache['fetch_date'] = pd.to_datetime(df_cache['fetch_date'])
            df_cache = df_cache.set_index('fetch_date')
            fundamentals_lib.write(cache_key, df_cache)
        except Exception:
            pass
        
        print("✓")
        
        # Rate limiting
        if i % 10 == 0:
            time.sleep(1)
            
    except Exception as e:
        print(f"✗ ({str(e)[:30]})")

print(f"\n✓ Collected data for {len(all_fundamentals)} stocks")

# ============================================================================
# Apply Buffett Value Criteria
# ============================================================================
print("\n" + "=" * 70)
print("Applying Buffett Value Criteria")
print("=" * 70)

print("""
Buffett's 6 Criteria:
1. P/B < 1.5        (undervalued)
2. D/E < 0.5        (low leverage)
3. CR 1.5-2.5       (good liquidity)
4. ROE > 8%         (profitable)
5. ROA > 6%         (efficient)
6. Int Cov > 5      (can service debt)
""")

df = pd.DataFrame(all_fundamentals)

# Apply filters
df['buffett_pb'] = df['pb_ratio'].apply(lambda x: 1 if x and x < 1.5 else 0)
df['buffett_de'] = df['debt_equity'].apply(lambda x: 1 if x and x < 0.5 else 0)
df['buffett_cr'] = df['current_ratio'].apply(lambda x: 1 if x and 1.5 < x < 2.5 else 0)
df['buffett_roe'] = df['roe'].apply(lambda x: 1 if x and x > 0.08 else 0)
df['buffett_roa'] = df['roa'].apply(lambda x: 1 if x and x > 0.06 else 0)
df['buffett_ic'] = df['interest_coverage'].apply(lambda x: 1 if x and x > 5 else 0)

df['buffett_score'] = (
    df['buffett_pb'] + df['buffett_de'] + df['buffett_cr'] +
    df['buffett_roe'] + df['buffett_roa'] + df['buffett_ic']
)

# Filter for stocks passing at least 4/6 criteria
value_stocks = df[df['buffett_score'] >= 4].copy()
value_stocks = value_stocks.sort_values('buffett_score', ascending=False)

print(f"\n✓ Found {len(value_stocks)} stocks passing ≥4/6 criteria")

# ============================================================================
# Display Results
# ============================================================================
print("\n" + "=" * 70)
print("Value Stocks Ranked by Buffett Score")
print("=" * 70)

if len(value_stocks) == 0:
    print("\nNo stocks passed the screening criteria.")
    print("Consider relaxing the thresholds or expanding the stock universe.")
else:
    print("\n" + "-" * 100)
    print(f"{'Rank':<5} {'Symbol':<8} {'Company':<30} {'Score':<7} {'P/B':<8} {'D/E':<8} {'ROE':<8} {'ROA':<8}")
    print("-" * 100)
    
    for idx, row in value_stocks.head(30).iterrows():
        rank = value_stocks.index.get_loc(idx) + 1
        symbol = row['symbol']
        company = row['company_name'][:28] if len(row['company_name']) > 28 else row['company_name']
        score = f"{row['buffett_score']:.0f}/6"
        
        pb = f"{row['pb_ratio']:.2f}" if row['pb_ratio'] else "N/A"
        de = f"{row['debt_equity']:.2f}" if row['debt_equity'] else "N/A"
        roe = f"{row['roe']:.1%}" if row['roe'] else "N/A"
        roa = f"{row['roa']:.1%}" if row['roa'] else "N/A"
        
        # Add indicator for criteria passed
        pb_mark = "✓" if row['buffett_pb'] else "✗"
        de_mark = "✓" if row['buffett_de'] else "✗"
        roe_mark = "✓" if row['buffett_roe'] else "✗"
        roa_mark = "✓" if row['buffett_roa'] else "✗"
        
        print(f"{rank:<5} {symbol:<8} {company:<30} {score:<7} {pb:<5}{pb_mark} {de:<5}{de_mark} {roe:<5}{roe_mark} {roa:<5}{roa_mark}")

# ============================================================================
# Export for Portfolio Monitoring
# ============================================================================
print("\n" + "=" * 70)
print("Export Selected Stocks")
print("=" * 70)

if len(value_stocks) > 0:
    # Export to CSV
    export_cols = ['symbol', 'company_name', 'sector', 'buffett_score', 
                   'pb_ratio', 'pe_ratio', 'debt_equity', 'current_ratio',
                   'roe', 'roa', 'interest_coverage', 'market_cap', 'dividend_yield', 'beta']
    
    value_stocks[export_cols].to_csv('selected_value_stocks.csv', index=False)
    print(f"\n✓ Exported {len(value_stocks)} stocks to: selected_value_stocks.csv")
    
    # Show top picks
    print("\n" + "-" * 70)
    print("Top 10 Value Stocks (Use these in comprehensive_analysis.py)")
    print("-" * 70)
    
    top_symbols = value_stocks.head(10)['symbol'].tolist()
    print("\nPython list for portfolio monitoring:")
    print(f"symbols = {top_symbols}")
    
    # Group by sector
    print("\n" + "-" * 70)
    print("Sector Distribution")
    print("-" * 70)
    sector_counts = value_stocks['sector'].value_counts()
    for sector, count in sector_counts.items():
        print(f"  {sector:<30} {count:>3} stocks")
    
    # Store in ArcticDB for quick access
    try:
        df_cache = value_stocks.copy()
        df_cache['fetch_date'] = pd.to_datetime(datetime.now())
        df_cache = df_cache.set_index('fetch_date')
        fundamentals_lib.write('selected_value_stocks_latest', df_cache)
        print(f"\n✓ Cached results in ArcticDB (expires in 7 days)")
    except Exception as e:
        print(f"\n⚠ Could not cache results: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY & NEXT STEPS")
print("=" * 70)

print(f"""
Stock Selection Complete!

Screened:  {len(stock_universe)} stocks
Passed:    {len(value_stocks)} stocks (≥4/6 Buffett criteria)

Top Criteria Met:
  P/B < 1.5:      {df['buffett_pb'].sum()} stocks
  D/E < 0.5:      {df['buffett_de'].sum()} stocks
  CR 1.5-2.5:     {df['buffett_cr'].sum()} stocks
  ROE > 8%:       {df['buffett_roe'].sum()} stocks
  ROA > 6%:       {df['buffett_roa'].sum()} stocks
  Int Cov > 5:    {df['buffett_ic'].sum()} stocks

Next Steps:
1. Review selected_value_stocks.csv
2. Pick 4-10 stocks for your portfolio
3. Update comprehensive_analysis.py with your selections:
   
   symbols = {top_symbols[:5] if len(top_symbols) >= 5 else top_symbols}
   
4. Run comprehensive_analysis.py to monitor portfolio performance
   (Alpha, Beta, Sharpe, risk metrics)

Note: This selection is based on fundamental analysis. Always:
- Research the companies (10-K, business model)
- Consider industry trends and moat
- Diversify across sectors
- Review quarterly earnings
""")

print("\n" + "=" * 70)
print("✓ Stock selection completed!")
print("=" * 70)

