# AI-Powered Quant Agent

World-class quantitative analyst powered by Claude (AWS Bedrock) or GPT-4 (OpenAI).

## 🎯 Overview

This AI agent performs institutional-grade quantitative analysis at JP Morgan level:

- **Market Intelligence**: Macro analysis, regime detection, sector rotation
- **Strategy Development**: Backtesting, optimization, parameter tuning
- **Risk Management**: VaR, CVaR, stress testing, correlation analysis
- **Portfolio Management**: MPT optimization, rebalancing, allocation
- **Automated Reporting**: Investment memos, risk reports, daily briefs

## 🏗️ Architecture

```
ai_agent/
├── core/
│   └── agent.py              # Main QuantAgent class
├── tools/                    # Tools the agent can use
│   ├── market_data.py        # Price history, fundamentals, macro indicators
│   ├── backtesting.py        # Strategy backtesting with costs
│   ├── risk_analysis.py      # VaR, CVaR, stress testing, correlation
│   ├── portfolio.py          # MPT optimization, efficient frontier
│   ├── technical.py          # Moving averages, RSI, support/resistance
│   └── fundamental.py        # Buffett screening, quality metrics
└── workflows/                # Pre-defined workflows
    ├── market_analysis.py    # Daily analysis, regime detection, screening
    └── reporting.py          # Investment memos, risk reports, reviews
```

## 🚀 Quick Start

### 1. Installation

```bash
# Core dependencies (if not already installed)
pip install pandas numpy boto3 openai yfinance arcticdb

# The agent uses your existing OpenBB and yfinance setup
```

### 2. Setup Credentials

**Option A: AWS Bedrock (Claude)**
```bash
# Configure AWS credentials
aws configure
# Or set environment variables:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

**Option B: OpenAI**
```bash
export OPENAI_API_KEY=your_api_key_here
```

### 3. Basic Usage

```python
from ai_agent.core.agent import create_agent

# Create agent
agent = create_agent(provider="bedrock")  # or "openai"

# Analyze stocks
response = agent.analyze_market(["AAPL", "GOOGL", "MSFT"])
print(response)

# Optimize portfolio
response = agent.optimize_portfolio(
    symbols=["AAPL", "GOOGL", "JPM", "JNJ", "XOM"],
    objective="sharpe"
)
print(response)

# Risk analysis
portfolio = {"AAPL": 0.30, "GOOGL": 0.30, "JPM": 0.40}
response = agent.risk_report(portfolio)
print(response)
```

## 📚 Examples

### Example 1: Daily Market Analysis

```python
from ai_agent.workflows.market_analysis import create_market_workflow

# Create workflow
workflow = create_market_workflow(provider="bedrock")

# Run daily analysis
watchlist = ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA"]
report = workflow.run_daily_analysis(watchlist)
print(report)
```

### Example 2: Stock Deep Dive

```python
# Comprehensive analysis on a single stock
report = workflow.analyze_stock_deep_dive(
    symbol="AAPL",
    peer_symbols=["MSFT", "GOOGL", "META"]
)
print(report)
```

### Example 3: Generate Investment Memo

```python
from ai_agent.workflows.reporting import create_reporting_workflow

workflow = create_reporting_workflow(provider="bedrock")

memo = workflow.generate_investment_memo(
    symbol="AAPL",
    action="BUY",
    thesis="Strong moat, expanding services, solid balance sheet"
)

# Save to file
with open("reports/AAPL_memo.md", "w") as f:
    f.write(memo)
```

### Example 4: Screen Market for Opportunities

```python
# Screen S&P 500 using Buffett criteria
report = workflow.screen_market(universe="sp500", min_score=4)
print(report)
```

### Example 5: Portfolio Risk Report

```python
portfolio = {
    "AAPL": 0.20, "GOOGL": 0.20, "MSFT": 0.20,
    "JPM": 0.20, "JNJ": 0.20
}

risk_report = workflow.generate_risk_report(portfolio)
print(risk_report)
```

## 🛠️ Available Tools

The agent has access to these tools (called automatically as needed):

### Market Data
- `get_price_history`: Fetch OHLCV data
- `get_fundamentals`: Valuation, profitability, financial health
- `get_macro_indicators`: 10Y yield, VIX, Dollar Index, S&P 500
- `get_sector_performance`: Sector ETF returns

### Backtesting
- `simple_backtest`: Backtest with realistic costs
- `calculate_sharpe_ratio`: Risk-adjusted returns
- `calculate_max_drawdown`: Drawdown analysis

### Risk Analysis
- `calculate_var_cvar`: Value at Risk metrics
- `calculate_portfolio_beta`: Beta and alpha (CAPM)
- `calculate_correlation_matrix`: Diversification analysis
- `stress_test_portfolio`: Historical scenario testing

### Portfolio Management
- `optimize_portfolio`: MPT optimization (Sharpe, min variance, etc.)
- `generate_efficient_frontier`: Risk-return tradeoff curve
- `calculate_rebalancing_needs`: Rebalancing recommendations

### Technical Analysis
- `calculate_moving_averages`: MAs and crossover signals
- `calculate_rsi`: Momentum indicators
- `detect_support_resistance`: Key price levels

### Fundamental Analysis
- `buffett_screen`: 6 value investing criteria
- `quality_metrics`: ROIC, FCF, margins, moat detection
- `compare_peers`: Peer comparison analysis

## 🎓 Capabilities

### 1. Market Analysis

```python
agent.chat("""
Analyze the current market environment:
1. What's the macro regime (rates, volatility, sentiment)?
2. Which sectors are leading/lagging?
3. What's the risk-on/risk-off sentiment?
4. Any regime change signals?
""")
```

### 2. Stock Screening

```python
agent.chat("""
Screen for high-quality value stocks:
- Use Buffett criteria (min score 4/6)
- Calculate quality metrics (ROIC, FCF, margins)
- Identify stocks with economic moats
- Rank by holistic score
""")
```

### 3. Strategy Development

```python
agent.develop_strategy(
    strategy_idea="Buy stocks when RSI < 30, sell when RSI > 70",
    universe=["AAPL", "GOOGL", "MSFT", "JPM"]
)
```

### 4. Portfolio Optimization

```python
agent.optimize_portfolio(
    symbols=["AAPL", "GOOGL", "JPM", "JNJ", "XOM"],
    objective="sharpe"  # or 'min_variance', 'max_return', 'risk_parity'
)
```

### 5. Risk Management

```python
agent.risk_report({
    "AAPL": 0.25, "GOOGL": 0.25,
    "JPM": 0.25, "JNJ": 0.25
})
```

## 📊 Workflows

Pre-defined workflows for autonomous operations:

### MarketAnalysisWorkflow
- `run_daily_analysis(watchlist)`: Daily market report
- `detect_regime_change()`: Regime analysis
- `analyze_stock_deep_dive(symbol)`: Deep dive on single stock
- `screen_market(universe, min_score)`: Market screening

### ReportingWorkflow
- `generate_investment_memo(symbol, action)`: JPM-style memo
- `generate_portfolio_review(portfolio)`: Performance review
- `generate_risk_report(portfolio)`: Comprehensive risk analysis
- `generate_daily_brief(watchlist)`: Concise daily update

## ⚙️ Configuration

Edit `config/ai_agent_config.yaml`:

```yaml
llm:
  provider: bedrock  # or 'openai'
  bedrock:
    model: anthropic.claude-3-5-sonnet-20241022-v2:0
    temperature: 0.1
  openai:
    model: gpt-4o
    temperature: 0.1

agent:
  verbose: true
  max_iterations: 10
  enable_caching: true

analysis:
  risk:
    confidence_level: 0.95
    risk_free_rate: 0.04
  portfolio:
    default_objective: sharpe
    max_position_size: 0.10
```

## 🎯 Use Cases

### 1. Morning Routine
```python
from ai_agent.workflows import create_market_workflow, create_reporting_workflow

market = create_market_workflow()
reporting = create_reporting_workflow()

# Get daily brief
brief = reporting.generate_daily_brief(["AAPL", "GOOGL", "MSFT"])

# Check for regime changes
regime = market.detect_regime_change()

# Review portfolio
portfolio = {"AAPL": 0.30, "GOOGL": 0.30, "JPM": 0.40}
review = reporting.generate_portfolio_review(portfolio)
```

### 2. New Investment Research
```python
# Deep dive on stock
report = market.analyze_stock_deep_dive(
    symbol="NVDA",
    peer_symbols=["AMD", "INTC", "AVGO"]
)

# Generate investment memo
memo = reporting.generate_investment_memo(
    symbol="NVDA",
    action="BUY",
    thesis="AI semiconductor leader with pricing power"
)
```

### 3. Portfolio Management
```python
# Optimize allocation
allocation = agent.optimize_portfolio(
    symbols=["AAPL", "GOOGL", "JPM", "JNJ", "XOM"],
    objective="sharpe"
)

# Check rebalancing needs
from ai_agent.core.agent import QuantAgent
agent = QuantAgent()
result = agent.chat(f"""
Current allocation: AAPL 35%, GOOGL 25%, JPM 20%, JNJ 15%, XOM 5%
Target allocation: {allocation}
Calculate rebalancing needs with 5% threshold.
""")
```

### 4. Risk Monitoring
```python
# Daily risk check
risk_report = reporting.generate_risk_report(portfolio)

# Stress testing
result = agent.chat("""
Stress test my portfolio against:
1. 2008 Financial Crisis
2. 2020 COVID Crash
3. Rising Rates (2022)

Portfolio: AAPL 30%, GOOGL 30%, JPM 40%
""")
```

## 🧠 How It Works

1. **Tool Calling**: The LLM decides which tools to call based on your question
2. **Data Fetching**: Tools fetch data from OpenBB, yfinance, cached ArcticDB
3. **Analysis**: Tools perform calculations (Sharpe, VaR, optimization, etc.)
4. **Synthesis**: LLM synthesizes results into clear, actionable insights
5. **Iteration**: Agent can call multiple tools in sequence to answer complex questions

## 📁 Project Integration

This AI agent integrates seamlessly with your existing quant toolkit:

```
quant/
├── scripts/                      # Your existing scripts
│   ├── market_scanner_full.py
│   ├── comprehensive_analysis_enhanced.py
│   └── ...
├── ai_agent/                     # New AI agent system ⭐
│   ├── core/
│   ├── tools/
│   └── workflows/
├── examples/                     # AI agent examples ⭐
│   ├── example_basic_usage.py
│   └── example_workflows.py
├── reports/                      # Generated reports ⭐
├── config/
│   └── ai_agent_config.yaml     # AI configuration ⭐
└── quant_data/                   # Shared ArcticDB cache
```

## 🔒 Security & Best Practices

1. **API Keys**: Never commit API keys. Use environment variables.
2. **Cost Management**: 
   - Bedrock Claude Sonnet: ~$3 per 1M input tokens, ~$15 per 1M output tokens
   - OpenAI GPT-4o: ~$2.50 per 1M input tokens, ~$10 per 1M output tokens
   - Typical analysis: 5,000-20,000 tokens = $0.05-$0.50 per query
3. **Caching**: Enable ArcticDB caching to reduce data fetching costs
4. **Rate Limits**: Tools implement rate limiting for data providers

## 📖 Next Steps

1. **Run Examples**: 
   ```bash
   python examples/example_basic_usage.py
   python examples/example_workflows.py
   ```

2. **Customize Configuration**:
   - Edit `config/ai_agent_config.yaml`
   - Set your watchlist and screening criteria

3. **Create Custom Workflows**:
   - See `ai_agent/workflows/` for examples
   - Build your own workflows for specific strategies

4. **Integrate with Existing Scripts**:
   - Use agent to analyze results from your existing scanners
   - Generate memos for stocks found by `market_scanner_full.py`

## 🐛 Troubleshooting

**Import errors:**
```bash
# Make sure you're in the quant directory
cd /path/to/quant
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

**AWS Bedrock errors:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check Bedrock model access in AWS Console
# (You may need to request model access)
```

**OpenAI errors:**
```bash
# Verify API key
echo $OPENAI_API_KEY
```

## 📚 References

- **Architecture**: Based on Claude's tool use capabilities and GPT-4 function calling
- **Finance Theory**: Brealey, Myers, Allen "Principles of Corporate Finance"
- **Data Sources**: OpenBB, yfinance
- **Caching**: ArcticDB (Man Group)

## 💡 Tips

1. **Be Specific**: "Analyze AAPL fundamentals and compare to MSFT" works better than "Tell me about AAPL"
2. **Use Workflows**: Pre-defined workflows are optimized for common tasks
3. **Save Conversations**: Use `agent.save_conversation()` to keep analysis history
4. **Iterate**: The agent can handle follow-up questions: "Now compare to GOOGL"
5. **Check Tools**: If analysis seems incomplete, check which tools were called (set `verbose=True`)

## 🎉 Examples to Try

```python
# Quick wins
agent.chat("What's the current market regime?")
agent.chat("Screen AAPL, GOOGL, MSFT, NVDA using Buffett criteria")
agent.chat("Is my portfolio of AAPL 50%, GOOGL 50% well diversified?")
agent.chat("What are the support and resistance levels for AAPL?")

# Advanced analysis
agent.chat("Analyze AAPL: fundamentals, technicals, valuation vs peers, and risk. Should I buy?")
agent.chat("Optimize allocation for AAPL, GOOGL, JPM, JNJ, XOM to maximize Sharpe ratio")
agent.chat("Stress test my portfolio (AAPL 30%, GOOGL 30%, JPM 40%) against 2008 crisis")
```

---

**Ready to deploy your AI quant analyst!** 🚀

Start with `examples/example_basic_usage.py` and scale up to full autonomous workflows.
