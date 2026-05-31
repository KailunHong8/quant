# Quant — Agentic Trading System

AI-powered paper-trading platform: React frontend, FastAPI backend, AWS Bedrock (Claude Sonnet 4.6), FMP market data.

## Quick Start

### Backend

```bash
cd AI_lab
cp .env.example .env          # fill in AWS credentials; FMP key and Bedrock settings are pre-set
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
# API: http://localhost:8000   Docs: http://localhost:8000/docs
```

### Frontend

```bash
cd AI_lab/frontend && npm install && npm run dev
# App: http://localhost:5173
```

### Environment Variables (`AI_lab/.env`)

| Variable | Description |
|---|---|
| `FMP_API_KEY` | FMP free-tier key (pre-set in .env.example) |
| `BEDROCK_REGION` | Bedrock region — `eu-west-1` (pre-set) |
| `BEDROCK_MODEL_ID` | Model ID — `eu.anthropic.claude-sonnet-4-6` (pre-set) |
| `AWS_ACCESS_KEY_ID` | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials |
| `DATABASE_URL` | SQLite (default) or PostgreSQL URL |

See [SPEC.md](SPEC.md) for the full functional specification.

---

## Legacy: Quantitative Finance Toolkit

Professional quant workflow combining market data, portfolio analytics, risk management, and value investing.

## 🆕 NEW: AI-Powered Quant Agent

**World-class quantitative analyst powered by Claude (AWS Bedrock) or GPT-4 (OpenAI)**

The AI agent performs institutional-grade analysis at JP Morgan level:
- 📊 **Market Intelligence**: Macro analysis, regime detection, sector rotation
- 🧠 **Strategy Development**: Backtesting, optimization, parameter tuning
- ⚠️ **Risk Management**: VaR, CVaR, stress testing, correlation analysis
- 💼 **Portfolio Management**: MPT optimization, rebalancing, allocation
- 📝 **Automated Reporting**: Investment memos, risk reports, daily briefs

### Quick Start with AI Agent

```bash
# Interactive CLI
python run_ai_agent.py

# Or use in Python
python examples/example_basic_usage.py
```

**See [AI_AGENT_README.md](AI_AGENT_README.md) for complete documentation.**

## Quick Start: Two-Step Workflow

### Step 1: Stock Selection (Run First)

**Option A: Quick Scan (57 hand-picked stocks)**
```bash
# Activate environment
source .venv311/bin/activate

# Screen curated list of quality stocks
python scripts/stock_selection_buffett.py
```
- Fast: ~2-5 minutes
- Good starting point
- Manually selected quality companies

**Option B: Full Market Scan (500-5000 stocks) - RECOMMENDED**
```bash
# Scan entire S&P 500
python scripts/market_scanner_full.py
```
- Comprehensive: All S&P 500 stocks
- Parallel processing: ~10-15 minutes
- Finds hidden gems
- Configure universe in script:
  - `SCAN_SP500 = True` (500 stocks, ~15 min)
  - `SCAN_RUSSELL_1000 = True` (1000 stocks, ~30 min)
  - `SCAN_ALL_US = True` (5000+ stocks, ~2-3 hours)

**What it does:**
- Downloads complete stock list automatically
- Applies Buffett's 6 value criteria
- Parallel fetching (10 stocks at once)
- Smart ArcticDB caching (skip re-fetching)
- Progress tracking with ETA
- Exports results with sector analysis

**Output:** 
- `market_scan_s&p_500_YYYYMMDD.csv` (all stocks)
- `value_stocks_s&p_500_YYYYMMDD.csv` (filtered results)

### Step 1.5: Interactive Dashboard (RECOMMENDED) 🌟
```bash
# Launch interactive web dashboard
streamlit run streamlit_value_dashboard.py
```

**What it does:**
- 🎛️ **Real-time filtering** with sliders (adjust criteria, see results instantly)
- 📊 **Interactive charts** (Quality vs Value quadrants, zoom, hover for details)
- 💾 **One-click CSV export** from the dashboard
- 🎨 **Beautiful UI** with tabs, metrics, and detailed stock cards
- 🔄 **Live updates** as you adjust any filter
- 📱 **Shareable** (can deploy to cloud for free)

**Features:**
- Sliders for all criteria (Holistic Score, Buffett Score, P/B, P/E, ROE, ROA, D/E, etc.)
- Multi-select for sectors
- Quick presets: "High Quality", "Deep Value", "Societal Impact"
- 4 tabs: Quality vs Value charts, Sector analysis, Rankings, Full data
- Top 5 detailed cards with all metrics
- Correlation and diversification insights

**Alternative: Static Dashboard (if Streamlit not installed)**
```bash
python scripts/visualize_value_stocks.py
# Generates PNG charts + CSV export
# Edit CUSTOM_CRITERIA at bottom to adjust filters
```

### Step 2: Portfolio Monitoring (Run Ongoing)

**Option A: Standard Analysis**
```bash
python scripts/comprehensive_analysis.py
```
- Alpha & Beta vs S&P 500
- Buffett criteria tracking
- Risk metrics (VaR, CVaR, drawdown)

**Option B: Enhanced Institutional Analysis (RECOMMENDED)**
```bash
python scripts/comprehensive_analysis_enhanced.py
```
- 📊 Macroeconomic context (10Y yield, VIX, Dollar)
- 💎 Quality metrics (ROIC, FCF yield, earnings quality, moat indicators)
- 🏢 Sector diversification analysis
- 🎓 Nobel Prize-winning frameworks (Markowitz, Fama-French, Shiller)
- 🌍 Societal impact scoring

**⚠ Important:** Update `symbols = [...]` with your picks from Step 1/1.5

## Core Philosophy: Value + Quality + Societal Impact

This toolkit combines three investment principles:

1. **Buffett Value Investing**: Financial solidity (low leverage, high profitability)
2. **Goldman Sachs Quality Focus**: Competitive moats, sustainable economics (ROIC >15%)
3. **Societal Value**: Companies improving human wellbeing (Healthcare, Tech, Infrastructure)

## Main Scripts

### `visualize_value_stocks.py` - Interactive Dashboard ⭐ NEW
**Purpose:** Visualize and filter stock universe with customizable criteria

**Features:**
- **Quality vs Value Quadrant**: Find companies with high ROE at low P/B (top-left corner)
- **Sector Breakdown**: Understand diversification and societal impact
- **Institutional Scoring**: Weighted composite of quality, value, safety, and societal value
- **Customizable Filters**: Easily adjust criteria and re-export filtered list
- **6 Professional Charts**: 
  1. Quality (ROE) vs Value (P/B) scatter
  2. Safety (D/E) vs Efficiency (ROA)
  3. Buffett score distribution
  4. Sector allocation with societal scoring
  5. Valuation by market cap
  6. Top 20 ranked stocks

**Output:**
- Dashboard PNG: `value_stock_dashboard_YYYYMMDD.png`
- Filtered picks CSV: `my_portfolio_picks_YYYYMMDD.csv`

### `comprehensive_analysis_enhanced.py` - Institutional Portfolio Analysis ⭐ NEW
**Purpose:** Monitor portfolio with Goldman Sachs-level insights

**Enhanced Features:**
- **Macroeconomic Context**:
  - 10-Year Treasury yield (rate environment)
  - VIX volatility index (market stress)
  - Dollar Index (currency headwinds/tailwinds)
  - Regime assessment (high rate vs low rate, risk-on vs risk-off)

- **Quality Metrics** (Beyond Buffett):
  - **ROIC** (Return on Invested Capital): True economic profitability, >15% = moat
  - **FCF Yield**: Free cash flow / market cap, >5% = strong cash generation
  - **Earnings Quality**: Operating CF / Net Income, >1.0 = real earnings
  - **Gross Margin**: >40% = pricing power
  - **Asset Turnover**: Revenue / Assets, efficiency measure

- **Sector Diversification**:
  - Sector allocation breakdown
  - Concentration risk warnings (max 30% per sector)
  - Correlation matrix (avg correlation <0.50 = good diversification)
  - Similar stock pairs identified

- **Institutional Rankings**:
  - Quality score (0-100): ROIC + FCF + Earnings Quality
  - Composite score: 40% Quality + 30% Sharpe + 30% Alpha
  - Moat indicators clearly displayed

- **Portfolio Construction Principles**:
  - Modern Portfolio Theory (Markowitz diversification)
  - Fama-French value factors
  - Shiller behavioral insights
  - Buffett quality-at-reasonable-price

**Output:**
Detailed institutional-grade analysis suitable for presentation to investment committees

### `stock_selection_buffett.py` - Find Value Stocks
**Purpose:** Screen universe to find undervalued opportunities

**Features:**
- Screens 50+ stocks automatically (expandable to 500+)
- Buffett's 6 criteria with pass/fail indicators
- 3-year fundamental data cached in ArcticDB
- Sector distribution analysis
- Export results for review

**Buffett Criteria:**
1. P/B < 1.5 (undervalued)
2. D/E < 0.5 (low leverage)
3. Current Ratio 1.5-2.5 (good liquidity)
4. ROE > 8% (profitable)
5. ROA > 6% (efficient)
6. Interest Coverage > 5 (can service debt)

### `comprehensive_analysis.py` - Monitor Portfolio
**Purpose:** Track performance of selected stocks

**Metrics:**
- Alpha/Beta (CAPM analysis)
- Sharpe ratio, Sortino ratio
- Portfolio correlation & diversification
- VaR, CVaR, maximum drawdown
- Buffett criteria tracking
- Composite ranking for rebalancing

### `tlt_calendar_strategy.py` - Treasury Bond Trading
**Purpose:** Exploit month-end institutional rebalancing flows in TLT

**Strategy Logic:**
- **SHORT** first 5 days of month (institutions raise cash)
- **LONG** 7 days before month-end (rebalancing demand)
- **FLAT** otherwise (~60% of time)

**Features:**
- Calendar-based signals (no forecasting needed)
- Transaction cost modeling (5bps per trade)
- Borrow cost modeling for shorts
- Sensitivity analysis (optimal timing windows)
- Regime analysis (bull vs bear rates)
- 20+ year backtest from TLT inception

**Market Structure Foundation:**
- Passive funds rebalance to index weights monthly
- Treasury volume spikes 30-50% at month-end (Fed NY research)
- Predictable institutional flows create exploitable patterns
- No complex indicators - pure calendar-based timing

**Usage:**
```bash
python scripts/tlt_calendar_strategy.py
```

**What to expect:**
- Full backtest vs buy-and-hold TLT
- Transaction cost impact analysis
- Yearly performance breakdown
- Optimal timing parameters (sensitivity analysis)
- Rolling Sharpe ratio evolution
- CSV export for further analysis

## Additional Scripts

- `test_gs_openbb_integration.py` - Basic integration example
- `test_openbb.py` - Market data testing

## Efficiency Features

### Parallel Processing
**`market_scanner_full.py` uses ThreadPoolExecutor:**
- Fetches 10 stocks simultaneously (configurable)
- 10x faster than sequential scanning
- Respects rate limits automatically

### Smart Caching
**ArcticDB stores fundamentals for 7 days:**
- First run: Fetches all data (~15 min for S&P 500)
- Second run: Instant (reads from cache)
- Updates only expired data automatically

### Progress Tracking
```
[50/500] AAPL     ✓ | Rate: 8.5/s | ETA: 8.3min
[100/500] MSFT    ✓ (cached) | Rate: 9.2/s | ETA: 7.1min
```

### Customization
Edit `market_scanner_full.py`:
```python
MAX_WORKERS = 10        # More = faster (but may hit rate limits)
CACHE_DAYS = 7          # How long to keep cached data
SCAN_SP500 = True       # Choose your universe
```

## Institutional Quality Metrics Explained

### ROIC (Return on Invested Capital) - The Moat Indicator
```
ROIC = NOPAT / Invested Capital
where Invested Capital = Equity + Debt
```
- **>15%**: Strong economic moat, pricing power (Goldman Sachs benchmark)
- **10-15%**: Decent business
- **<10%**: Commodity business, no moat

**Why it matters:** Better than ROE because it accounts for all capital (debt + equity). Companies with sustained high ROIC have durable competitive advantages.

### FCF Yield (Free Cash Flow Yield) - Cash Generation
```
FCF Yield = Free Cash Flow / Market Cap
where FCF = Operating Cash Flow - CapEx
```
- **>5%**: Strong cash generation, undervalued
- **3-5%**: Fair
- **<3%**: Expensive or capital-intensive

**Why it matters:** Cash is king. High FCF means company can self-fund growth, pay dividends, and buy back stock without taking on debt.

### Earnings Quality - Accounting vs Reality
```
Earnings Quality = Operating Cash Flow / Net Income
```
- **>1.2x**: Excellent (more cash than reported earnings)
- **0.8-1.2x**: Normal
- **<0.8x**: Warning (accounting games or working capital issues)

**Why it matters:** Prevents accounting fraud. Enron had great earnings but terrible cash flow.

### Gross Margin - Pricing Power
```
Gross Margin = (Revenue - COGS) / Revenue
```
- **>40%**: High pricing power (Apple, Google, Visa)
- **20-40%**: Moderate
- **<20%**: Commodity business (airlines, retailers)

**Why it matters:** High gross margin = competitive advantage. Can weather economic downturns.

### Holistic Score (Composite Ranking)
```
Holistic Score = 35% Institutional Score + 35% Buffett Score + 30% Societal Value
where:
  Institutional = 40% Quality + 30% Value + 30% Safety
  Buffett Score = # criteria passed (0-6)
  Societal Value = Sector-based impact (Healthcare=100, Energy=40)
```

**Interpretation:**
- **>70**: Excellent long-term investment
- **60-70**: Good quality
- **50-60**: Speculative
- **<50**: Avoid

## Traditional Metrics Explained

### Why 252?
**252 = Trading days per year**
- Annual Return = Daily Mean × 252
- Annual Volatility = Daily Std × √252 (volatility scales with √time)

### Alpha & Beta (CAPM)
```
Beta = Cov(stock, market) / Var(market)
Alpha = Actual Return - [Rf + Beta × (Market Return - Rf)]
```
- Beta > 1: More volatile than market
- Beta < 1: Less volatile than market
- Alpha > 0: Outperforming vs CAPM prediction

### Buffett Value Criteria
1. Debt/Equity < 0.5 (low leverage)
2. Current Ratio 1.5-2.5 (good liquidity)
3. P/B < 1.5 (undervalued)
4. ROE > 8% (profitable)
5. ROA > 6% (efficient)
6. Interest Coverage > 5 (can service debt)

## Dependencies

```bash
# Core packages
pip install openbb yfinance gs-quant pandas numpy matplotlib seaborn

# Interactive dashboard (RECOMMENDED)
pip install streamlit plotly

# Optional for caching (speeds up scans)
pip install arcticdb
```

## Project Structure

```
quant/
├── streamlit_value_dashboard.py              ← 🌟 Interactive dashboard (Streamlit) NEW!
├── scripts/
│   ├── market_scanner_full.py                ← STEP 1: Full market screening (S&P 500+)
│   ├── stock_selection_buffett.py            ← STEP 1: Quick scan (57 stocks)
│   ├── visualize_value_stocks.py             ← STEP 1.5: Static charts (alternative)
│   ├── comprehensive_analysis.py             ← STEP 2: Portfolio monitoring (standard)
│   ├── comprehensive_analysis_enhanced.py    ← STEP 2: Institutional analysis ⭐ NEW
│   ├── tlt_calendar_strategy.py              ← Bond trading: Month-end flows
│   ├── test_gs_openbb_integration.py         ← Basic integration example
│   └── test_openbb.py                        ← Market data testing
├── docs/
│   └── context.txt                           ← Corporate finance framework (Brealey, Myers, Allen)
├── quant_data/                               ← ArcticDB cache (auto-created)
│   ├── fundamentals/                         ← Cached fundamental data
│   └── prices/                               ← Cached price history
├── value_stocks_s&p_500_YYYYMMDD.csv        ← Market scanner output
├── my_portfolio_picks_YYYYMMDD.csv          ← Filtered picks (exported from dashboard)
├── tlt_calendar_backtest_YYYYMMDD.csv       ← TLT strategy results
└── README.md
```

## Data Sources

- **Market prices**: OpenBB (yfinance provider)
- **Fundamentals**: OpenBB (FMP provider)
- **Benchmark**: SPY (S&P 500 ETF)

## Output Example

```
Symbol    Return     Vol   Sharpe    Beta   Alpha
GOOGL     55.31%  32.45%     1.70    0.85   5.12%
NVDA      44.20%  49.77%     0.89    1.45   1.92%

Symbol    P/B   D/E    CR   ROE   ROA   Int Cov   Score
GOOGL    1.2   0.35  1.8   15%    9%      8.5     6/6 ✓
NVDA     1.4   0.28  2.1   18%   10%     12.0     6/6 ✓

Composite Ranking:
1  GOOGL    Sharpe: 1.70  Alpha: 5.12%  Buffett: 6/6  Score: 95.3
2  NVDA     Sharpe: 0.89  Alpha: 1.92%  Buffett: 6/6  Score: 78.1
```

## References

**Books:**
- "Principles of Corporate Finance" (Brealey, Myers, Allen) - Chapters 7-8, 20-21

**Libraries:**
- OpenBB: https://docs.openbb.co/
- GS Quant: https://developer.gs.com/docs/gsquant/
- ArcticDB: https://github.com/man-group/ArcticDB

## License

Personal research project - see individual library licenses for dependencies.
