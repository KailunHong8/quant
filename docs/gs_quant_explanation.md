# GS Quant Codebase Explanation & Integration with OpenBB

## Overview

**GS Quant** is Goldman Sachs' Python toolkit for quantitative finance, built on their risk transfer platform. It's designed for:
- **Derivative pricing and structuring** (Chapters 20-26, Principles of Corporate Finance)
- **Trading strategy development and backtesting** (Chapters 7-8, Portfolio Theory)
- **Risk management and analytics** (Chapters 7, 20-21, Risk Management)
- **Portfolio optimization** (Chapter 8, Portfolio Theory)

## Key Codebase Structure

### 1. **Core Modules** (Can work offline with your own data)

#### `gs_quant/backtests/` - Strategy Backtesting
- **`strategy.py`**: Defines `Strategy` class for backtesting
  - `initial_portfolio`: Starting positions
  - `triggers`: Conditions that generate trades (e.g., rebalancing, risk limits)
  - `cash_accrual`: How cash earns interest
- **`triggers.py`**: Trading triggers (date-based, risk-based, etc.)
- **`backtest_engine.py`**: Runs backtests on strategies
- **Finance Theory**: Chapter 7 (Capital Budgeting), Chapter 8 (Portfolio Theory)

#### `gs_quant/risk/` - Risk Management
- **`measures.py`**: Risk measures (Delta, Gamma, Vega, Theta, VaR, etc.)
- **`scenarios.py`**: Stress testing and scenario analysis
- **Finance Theory**: Chapter 7 (Risk), Chapter 20-21 (Options Greeks), Chapter 24 (Risk Management)

#### `gs_quant/markets/` - Portfolio & Market Analytics
- **`portfolio.py`**: Portfolio construction and management
- **`portfolio_manager.py`**: Advanced portfolio operations
- **`optimizer.py`**: Portfolio optimization (mean-variance, etc.)
- **`hedge.py`**: Hedging strategies
- **Finance Theory**: Chapter 8 (Portfolio Theory), Chapter 20-21 (Hedging)

#### `gs_quant/timeseries/` - Statistical Analysis
- **`analysis.py`**: Time series analysis
- **`statistics.py`**: Statistical measures
- **`econometrics.py`**: Econometric models (Sharpe ratio, Jensen's alpha, etc.)
- **Finance Theory**: Chapter 7-8 (Portfolio Performance), Chapter 24 (Statistical Models)

### 2. **API Modules** (Require GS Credentials)

#### `gs_quant/api/` - Goldman Sachs APIs
- **`gs/`**: GS Marquee platform APIs (market data, pricing, risk)
- **`risk.py`**: Risk calculation APIs
- **`data.py`**: Market data APIs

**Note**: These require institutional credentials, but you can use OpenBB for market data instead!

## Finance Theories from "Principles of Corporate Finance"

### 1. **Options & Derivatives** (Chapters 20-21)
- **Black-Scholes Pricing**: GS Quant can price options using various models
- **Greeks**: Delta, Gamma, Theta, Vega, Rho calculations
- **Implied Volatility**: Extract from market prices
- **Hedging**: Delta hedging, portfolio hedging

### 2. **Portfolio Theory** (Chapter 8)
- **Mean-Variance Optimization**: `markets/optimizer.py`
- **Efficient Frontier**: Portfolio optimization
- **Sharpe Ratio**: Risk-adjusted returns (`timeseries/econometrics.py`)
- **Jensen's Alpha**: Performance attribution

### 3. **Risk Management** (Chapters 7, 20-21, 24)
- **Value at Risk (VaR)**: Portfolio risk measures
- **Stress Testing**: Scenario analysis
- **Factor Models**: Risk factor exposure
- **Hedging Strategies**: Risk reduction techniques

### 4. **Capital Budgeting** (Chapters 6-7)
- **NPV/IRR**: Project evaluation
- **Backtesting**: Strategy performance evaluation
- **Transaction Costs**: Realistic trading costs

## Integration Strategy: OpenBB + GS Quant

### Architecture
```
OpenBB (Market Data) → GS Quant (Strategy & Risk) → Results
```

### What Works Offline (No GS Credentials Needed):
1. **Strategy Definition**: Create strategies with triggers
2. **Backtesting Framework**: Run backtests with your own data
3. **Risk Calculations**: Calculate Greeks, VaR, etc. (if you provide pricing)
4. **Portfolio Construction**: Build and optimize portfolios
5. **Statistical Analysis**: Time series, econometrics

### What Requires GS Credentials:
1. **Live Market Data**: GS Marquee data feeds
2. **Real-time Pricing**: GS pricing engines
3. **Risk Models**: GS proprietary risk models

### Solution: Use OpenBB for Data, GS Quant for Strategy/Risk

```python
# 1. Get market data from OpenBB
from openbb import obb
data = obb.equity.price.historical("AAPL", provider="yfinance")
df = data.to_dataframe()

# 2. Use GS Quant for strategy/risk
from gs_quant.backtests import Strategy, Trigger
from gs_quant.markets import Portfolio
# Build strategy with OpenBB data
```

## Key Classes & Concepts

### Strategy (`backtests/strategy.py`)
```python
Strategy(
    initial_portfolio=[...],  # Starting positions
    triggers=[...],            # Trading rules
    cash_accrual=...          # Cash management
)
```

### Portfolio (`markets/portfolio.py`)
```python
Portfolio(
    priceables=[...],  # Instruments/positions
    name="My Portfolio"
)
```

### Risk Measures (`risk/measures.py`)
- `Delta`, `Gamma`, `Vega`, `Theta`, `Rho` (Options Greeks)
- `PnlExplain`, `PnlPredict` (P&L attribution)
- Custom risk measures

### Triggers (`backtests/triggers.py`)
- Date-based rebalancing
- Risk-based triggers (e.g., hedge when delta exceeds threshold)
- Performance-based triggers

## Example Workflow

1. **Data Collection** (OpenBB):
   - Get historical prices
   - Get fundamental data
   - Get market indicators

2. **Strategy Development** (GS Quant):
   - Define initial portfolio
   - Set up triggers (rebalancing, risk limits)
   - Configure backtest parameters

3. **Risk Analysis** (GS Quant):
   - Calculate portfolio risk
   - Run stress tests
   - Analyze Greeks

4. **Backtesting** (GS Quant):
   - Run strategy on historical data
   - Evaluate performance
   - Optimize parameters

## References to "Principles of Corporate Finance"

- **Chapter 6-7**: Capital Budgeting, NPV, Risk → Backtesting, Strategy Evaluation
- **Chapter 8**: Portfolio Theory → `markets/optimizer.py`, Portfolio construction
- **Chapter 20-21**: Options, Black-Scholes, Greeks → `risk/measures.py`, Options pricing
- **Chapter 24**: Risk Management, VaR → `risk/scenarios.py`, Risk models
- **Chapter 25-26**: Swaps, Credit Risk → GS Quant derivatives support

