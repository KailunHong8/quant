"""
Integration Example: OpenBB (Market Data) + GS Quant (Strategy & Risk)

This demonstrates how to:
1. Get market data from OpenBB (no credentials needed)
2. Use GS Quant for portfolio construction and risk analysis
3. Build trading strategies using GS Quant's backtesting framework

Note: Full GS Quant features (live pricing, risk models) require GS credentials,
but you can use OpenBB data with GS Quant's strategy/portfolio/risk frameworks.
"""

import pandas as pd
from datetime import date, timedelta

# ============================================================================
# PART 1: Get Market Data from OpenBB (No credentials needed)
# ============================================================================
print("="*70)
print("PART 1: Fetching Market Data from OpenBB")
print("="*70)

try:
    from openbb import obb
    
    # Fetch historical data for multiple stocks
    symbols = ["AAPL", "MSFT", "GOOGL"]
    all_data = {}
    
    for symbol in symbols:
        try:
            result = obb.equity.price.historical(symbol, provider="yfinance")
            df = result.to_dataframe()
            all_data[symbol] = df
            print(f"✓ Fetched {len(df)} days of data for {symbol}")
        except Exception as e:
            print(f"✗ Error fetching {symbol}: {e}")
    
    # Combine into portfolio data
    if all_data:
        portfolio_prices = pd.DataFrame({
            symbol: df['Close'] if 'Close' in df.columns else df.iloc[:, 0]
            for symbol, df in all_data.items()
        })
        print(f"\nPortfolio price data shape: {portfolio_prices.shape}")
        print(portfolio_prices.tail())
        
except ImportError:
    print("OpenBB not available - using mock data")
    # Mock data for demonstration
    dates = pd.date_range(end=date.today(), periods=252, freq='D')
    portfolio_prices = pd.DataFrame({
        'AAPL': 150 + pd.Series(range(252)) * 0.1 + pd.Series(range(252)).apply(lambda x: (x % 10) * 2),
        'MSFT': 300 + pd.Series(range(252)) * 0.15 + pd.Series(range(252)).apply(lambda x: (x % 8) * 1.5),
        'GOOGL': 100 + pd.Series(range(252)) * 0.12 + pd.Series(range(252)).apply(lambda x: (x % 12) * 1.8)
    }, index=dates)
    portfolio_prices.index.name = 'Date'

# ============================================================================
# PART 2: GS Quant - Portfolio Construction & Risk Analysis
# ============================================================================
print("\n" + "="*70)
print("PART 2: GS Quant Portfolio & Risk Analysis")
print("="*70)

try:
    import gs_quant
    from gs_quant.markets import Portfolio
    from gs_quant.instrument import Instrument
    from gs_quant.common import AssetClass
    
    print(f"✓ GS Quant version: {gs_quant.__version__}")
    
    # GS Quant Portfolio Concepts (Chapter 8: Portfolio Theory)
    print("\n--- Portfolio Construction (Chapter 8: Portfolio Theory) ---")
    print("""
    GS Quant's Portfolio class allows you to:
    - Construct portfolios of instruments
    - Calculate portfolio-level risk metrics
    - Optimize portfolio weights (mean-variance optimization)
    - Analyze factor exposures
    
    Finance Theory: Efficient Frontier, Sharpe Ratio, Portfolio Optimization
    """)
    
    # Note: Creating actual instruments requires GS asset IDs or proper instrument definitions
    # For demonstration, we show the concept
    print("Portfolio construction requires instrument definitions.")
    print("With GS credentials, you can create instruments like:")
    print("  - Equity('AAPL')")
    print("  - Option(...)")
    print("  - Swap(...)")
    
    # Portfolio risk concepts
    print("\n--- Risk Management (Chapters 7, 20-21: Risk & Options) ---")
    print("""
    GS Quant Risk Measures include:
    - Delta, Gamma, Vega, Theta, Rho (Options Greeks - Chapter 21)
    - Value at Risk (VaR) - Chapter 7
    - Stress Testing & Scenarios - Chapter 24
    - P&L Attribution
    
    Example usage (requires instrument definitions):
      portfolio.calc(risk.DollarPrice)
      portfolio.calc(risk.Delta)
      portfolio.calc(risk.Vega)
    """)
    
except ImportError as e:
    print(f"GS Quant import error: {e}")

# ============================================================================
# PART 3: GS Quant - Strategy Backtesting Framework
# ============================================================================
print("\n" + "="*70)
print("PART 3: GS Quant Strategy Backtesting")
print("="*70)

try:
    from gs_quant.backtests import Strategy
    from gs_quant.backtests.triggers import PeriodicTrigger, PeriodicTriggerRequirements
    from gs_quant.backtests.actions import AddTradeAction, HedgeAction
    from gs_quant.backtests.generic_engine import GenericEngine
    from datetime import timedelta
    
    print("✓ GS Quant backtesting modules imported")
    
    print("\n--- Strategy Backtesting (Chapter 7: Capital Budgeting) ---")
    print("""
    GS Quant Strategy Framework:
    
    1. Strategy Definition:
       - initial_portfolio: Starting positions
       - triggers: Conditions that generate trades
       - cash_accrual: Cash management model
    
    2. Triggers (Trading Rules):
       - PeriodicTrigger: Rebalance on schedule (e.g., monthly)
       - RiskTrigger: Trade when risk exceeds threshold
       - PerformanceTrigger: Trade based on performance
    
    3. Actions:
       - AddTradeAction: Add new positions
       - HedgeAction: Hedge existing positions
       - ExitTradeAction: Close positions
    
    4. Backtest Engines:
       - GenericEngine: General purpose
       - PredefinedAssetEngine: For predefined assets
       - EquityVolEngine: For equity volatility strategies
    
    Finance Theory: 
    - Chapter 7: Strategy evaluation, transaction costs
    - Chapter 8: Portfolio rebalancing, optimization
    """)
    
    # Example strategy structure (conceptual)
    print("\nExample Strategy Structure:")
    print("""
    strategy = Strategy(
        initial_portfolio={
            'AAPL': Equity('AAPL', quantity=100),
            'MSFT': Equity('MSFT', quantity=50)
        },
        triggers=[
            PeriodicTrigger(
                trigger_requirements=PeriodicTriggerRequirements(
                    start_date=start_date,
                    end_date=end_date,
                    frequency='1m'  # Monthly rebalancing
                ),
                actions=AddTradeAction(...)  # Rebalancing logic
            )
        ]
    )
    
    # Run backtest
    backtest = GenericEngine().run_backtest(
        strategy=strategy,
        start=start_date,
        end=end_date
    )
    """)
    
except ImportError as e:
    print(f"GS Quant backtesting import error: {e}")

# ============================================================================
# PART 4: Statistical Analysis (GS Quant Timeseries)
# ============================================================================
print("\n" + "="*70)
print("PART 4: Statistical Analysis with GS Quant")
print("="*70)

try:
    from gs_quant.timeseries import sharpe_ratio
    from gs_quant.timeseries.econometrics import RiskFreeRateCurrency
    
    print("✓ GS Quant timeseries modules imported")
    
    # Calculate portfolio returns from OpenBB data
    if 'portfolio_prices' in locals() and not portfolio_prices.empty:
        returns = portfolio_prices.pct_change().dropna()
        portfolio_returns = returns.mean(axis=1)  # Equal-weighted portfolio
        
        print(f"\nCalculated {len(portfolio_returns)} daily returns")
        print(f"Mean daily return: {portfolio_returns.mean():.4%}")
        print(f"Volatility (annualized): {portfolio_returns.std() * (252**0.5):.4%}")
        
        # Convert to GS Quant Series format (pandas Series works)
        try:
            # GS Quant's sharpe_ratio expects a pandas Series
            sharpe = sharpe_ratio(portfolio_returns, currency=RiskFreeRateCurrency.USD)
            print(f"Sharpe Ratio: {sharpe:.4f}")
            print("\n--- Performance Metrics (Chapter 8: Portfolio Theory) ---")
            print("""
            GS Quant provides:
            - Sharpe Ratio: Risk-adjusted returns
            - Jensen's Alpha: Performance attribution
            - Treynor Measure: Beta-adjusted returns
            - Modigliani Ratio: Risk-adjusted performance vs benchmark
            
            Finance Theory: Chapter 8 - Portfolio Performance Evaluation
            """)
        except Exception as e:
            print(f"Note: Full Sharpe calculation may require GS data: {e}")
    
except ImportError as e:
    print(f"GS Quant timeseries import error: {e}")

# ============================================================================
# SUMMARY: Integration Architecture
# ============================================================================
print("\n" + "="*70)
print("INTEGRATION SUMMARY")
print("="*70)
print("""
Recommended Architecture:

┌─────────────────┐
│   OpenBB        │  → Market Data (Historical prices, fundamentals)
│   (Free Tier)   │     - No credentials needed
└────────┬────────┘     - Multiple providers (yfinance, etc.)
         │
         ▼
┌─────────────────┐
│   Your Code     │  → Data transformation & preprocessing
│   (Integration) │     - Convert OpenBB data to GS Quant format
└────────┬────────┘     - Prepare data for backtesting
         │
         ▼
┌─────────────────┐
│   GS Quant      │  → Strategy & Risk Management
│   (Framework)   │     - Portfolio construction
└─────────────────┘     - Strategy backtesting
                        - Risk calculations (if you provide pricing)
                        - Statistical analysis

What Works WITHOUT GS Credentials:
✓ Strategy definition and backtesting framework
✓ Portfolio construction concepts
✓ Statistical analysis (Sharpe, Alpha, etc.)
✓ Risk measure definitions
✓ Data transformation and preprocessing

What REQUIRES GS Credentials:
✗ Live GS Marquee market data
✗ Real-time pricing engines
✗ GS proprietary risk models
✗ Live risk calculations

Solution: Use OpenBB for data, GS Quant for strategy/risk framework!
""")

print("\n" + "="*70)
print("Next Steps:")
print("="*70)
print("""
1. Get market data from OpenBB (as shown above)
2. Transform data into format GS Quant expects
3. Define strategies using GS Quant's Strategy class
4. Run backtests with GenericEngine
5. Analyze results with GS Quant's risk/statistical tools

For detailed examples, see:
- GS Quant docs: https://developer.gs.com/docs/gsquant/
- GS Quant GitHub: https://github.com/goldmansachs/gs-quant
""")

