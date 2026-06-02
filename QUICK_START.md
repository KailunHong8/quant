# AI Quant Agent - Quick Start Guide

Get started in 5 minutes! 🚀

## 🎯 Prerequisites

You need **ONE** of these:
- **AWS Bedrock** access (recommended) - more cost-effective
- **OpenAI API** key - easier to set up

## 📦 Installation

```bash
# Activate your environment
source .venv311/bin/activate

# Install LLM provider (choose one)
pip install boto3        # For AWS Bedrock
pip install openai       # For OpenAI

# Optional: For advanced portfolio optimization
pip install scipy
```

## 🔑 Setup Credentials

### Option A: AWS Bedrock (Recommended)
```bash
aws configure
# Enter your AWS credentials
# Region: us-east-1
```

Then enable Claude in AWS Console:
1. Go to Bedrock → Model access
2. Request access to "Claude 3.5 Sonnet v2"
3. Wait for approval (usually instant)

### Option B: OpenAI
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

## 🚀 First Run

### Interactive Mode (Easiest!)
```bash
python run_ai_agent.py
```

Then try:
```
What's the current market regime?
Analyze AAPL fundamentals
Screen AAPL, GOOGL, MSFT using Buffett criteria
```

### Python Script
```python
from ai_agent.core.agent import create_agent

# Create agent
agent = create_agent(provider="bedrock")  # or "openai"

# Ask anything
response = agent.chat("What's the current market regime?")
print(response)
```

## 📊 Common Use Cases

### 1. Market Analysis
```python
from ai_agent.workflows import create_market_workflow

workflow = create_market_workflow()

# Daily analysis
workflow.run_daily_analysis(["AAPL", "GOOGL", "MSFT"])

# Regime detection
workflow.detect_regime_change()

# Deep dive on stock
workflow.analyze_stock_deep_dive("AAPL", peer_symbols=["MSFT", "GOOGL"])
```

### 2. Stock Screening
```python
# Screen for high-quality value stocks
workflow.screen_market(universe="sp500", min_score=4)
```

### 3. Portfolio Optimization
```python
agent.optimize_portfolio(
    symbols=["AAPL", "GOOGL", "JPM", "JNJ", "XOM"],
    objective="sharpe"
)
```

### 4. Risk Analysis
```python
from ai_agent.workflows import create_reporting_workflow

reporting = create_reporting_workflow()

portfolio = {
    "AAPL": 0.30,
    "GOOGL": 0.30,
    "JPM": 0.40
}

# Get comprehensive risk report
reporting.generate_risk_report(portfolio)
```

### 5. Investment Memo
```python
# Generate JP Morgan-style memo
reporting.generate_investment_memo(
    symbol="AAPL",
    action="BUY",
    thesis="Strong moat in consumer electronics, expanding services"
)
```

## 💡 Example Queries

Try these in interactive mode:

**Market Intelligence**
- "What's the current market regime?"
- "Which sectors are leading this month?"
- "Is volatility elevated?"

**Stock Analysis**
- "Analyze AAPL fundamentals and valuation"
- "Compare AAPL to MSFT and GOOGL"
- "Run Buffett screen on AAPL, GOOGL, JPM"
- "What are the technical signals for NVDA?"

**Portfolio**
- "Optimize allocation for AAPL, GOOGL, JPM, JNJ, XOM for max Sharpe"
- "Is my portfolio of AAPL 50%, GOOGL 50% diversified?"
- "Calculate VaR for: AAPL 30%, GOOGL 30%, JPM 40%"
- "Stress test my portfolio against 2008 crisis"

**Strategy**
- "Should I buy AAPL at current levels?"
- "What are the key risks in holding NVDA?"
- "When should I rebalance my portfolio?"

## 📚 Documentation

- **Complete Guide**: [AI_AGENT_README.md](AI_AGENT_README.md)
- **Setup Details**: [AI_AGENT_SETUP.md](AI_AGENT_SETUP.md)
- **Implementation**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## 🔧 Troubleshooting

**Import errors:**
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/quant
```

**AWS Bedrock errors:**
```bash
# Verify credentials
aws sts get-caller-identity

# Check model access in AWS Console
```

**OpenAI errors:**
```bash
# Check API key
echo $OPENAI_API_KEY
```

## 💰 Cost

Typical costs per query:
- Simple analysis: $0.05
- Deep dive: $0.50
- Investment memo: $0.60

Daily usage: $1-2/day  
Monthly: $50-100 for active use

## 🎓 Learn More

Run examples:
```bash
python examples/example_basic_usage.py
python examples/example_workflows.py
```

## ⚡ Quick Commands

```bash
# Interactive CLI
python run_ai_agent.py

# Chat mode
python run_ai_agent.py --mode chat

# Workflow mode
python run_ai_agent.py --mode workflow

# Use OpenAI instead of Bedrock
python run_ai_agent.py --provider openai

# Verbose output
python run_ai_agent.py --verbose
```

## 🎉 You're Ready!

Start analyzing: `python run_ai_agent.py`

Need help? Check the full documentation or run: `python run_ai_agent.py` and type `help`

---

**Pro Tip**: Enable ArcticDB caching (already configured) to reduce costs by 80% on repeated queries!
