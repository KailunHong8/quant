# AI Agent Setup Guide

Complete setup guide for the AI-powered quant analyst.

## 📋 Prerequisites

1. **Python 3.9+** with existing packages:
   - pandas, numpy, yfinance, arcticdb (already installed in your environment)

2. **AWS Bedrock** (recommended) OR **OpenAI** access:
   - **Option A: AWS Bedrock** - Lower cost, better for long contexts
   - **Option B: OpenAI** - Easier setup, no AWS account needed

3. **Your existing quant toolkit** (already set up):
   - OpenBB, ArcticDB, yfinance

## 🚀 Setup Steps

### Step 1: Install Additional Dependencies

```bash
# Activate your virtual environment
source .venv311/bin/activate

# Install LLM provider SDKs
pip install boto3  # For AWS Bedrock
pip install openai  # For OpenAI

# Optional: Install scipy for advanced portfolio optimization
pip install scipy
```

### Step 2: Configure Credentials

#### Option A: AWS Bedrock (Recommended)

```bash
# Configure AWS CLI
aws configure
# Enter your:
#   AWS Access Key ID
#   AWS Secret Access Key  
#   Default region: us-east-1
#   Default output format: json

# Test access
aws sts get-caller-identity
```

**Enable Bedrock Model Access:**
1. Go to AWS Console → Bedrock → Model access
2. Request access to "Claude 3.5 Sonnet v2"
3. Wait for approval (usually instant)

#### Option B: OpenAI

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Add to your ~/.bashrc or ~/.zshrc for persistence
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
```

### Step 3: Test Installation

```bash
# Test basic import
python -c "from ai_agent.core.agent import create_agent; print('✓ Import successful')"

# Run interactive agent
python run_ai_agent.py

# Or run example script
python examples/example_basic_usage.py
```

## 🎯 First Usage

### Interactive CLI (Easiest)

```bash
# Start interactive session
python run_ai_agent.py

# Try these queries:
What's the current market regime?
Analyze AAPL fundamentals
Screen AAPL, GOOGL, MSFT using Buffett criteria
```

### Python Script

```python
from ai_agent.core.agent import create_agent

# Create agent
agent = create_agent(provider="bedrock")  # or "openai"

# Ask questions
response = agent.chat("What's the current market regime?")
print(response)

# Analyze stocks
response = agent.analyze_market(["AAPL", "GOOGL", "MSFT"])
print(response)
```

### Using Workflows

```python
from ai_agent.workflows import create_market_workflow

# Create workflow
workflow = create_market_workflow(provider="bedrock")

# Run daily analysis
report = workflow.run_daily_analysis(["AAPL", "GOOGL", "MSFT"])
print(report)
```

## ⚙️ Configuration

Edit `config/ai_agent_config.yaml`:

```yaml
llm:
  provider: bedrock  # or 'openai'
  
  bedrock:
    model: anthropic.claude-3-5-sonnet-20241022-v2:0
    region: us-east-1
    temperature: 0.1
  
  openai:
    model: gpt-4o
    temperature: 0.1

agent:
  verbose: true
  max_iterations: 10
```

## 💰 Cost Estimates

### AWS Bedrock (Claude 3.5 Sonnet)
- **Input**: $3.00 per 1M tokens
- **Output**: $15.00 per 1M tokens
- **Typical query**: 5K-20K tokens = **$0.05-$0.50 per analysis**
- **Daily analysis workflow**: ~50K tokens = **$1-2 per day**

### OpenAI (GPT-4o)
- **Input**: $2.50 per 1M tokens
- **Output**: $10.00 per 1M tokens
- **Typical query**: 5K-20K tokens = **$0.04-$0.40 per analysis**
- **Daily analysis workflow**: ~50K tokens = **$0.80-$1.50 per day**

**Cost Saving Tips:**
1. Enable ArcticDB caching (already configured)
2. Use smaller sample sizes for screening
3. Set `verbose=False` to reduce token usage
4. Use workflows instead of ad-hoc queries (more efficient prompts)

## 🔧 Troubleshooting

### Import Errors

```bash
# Make sure PYTHONPATH includes quant directory
cd /path/to/quant
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Or add to .bashrc/.zshrc
echo 'export PYTHONPATH=$PYTHONPATH:/path/to/quant' >> ~/.bashrc
```

### AWS Bedrock Errors

**"AccessDeniedException":**
- Check AWS credentials: `aws sts get-caller-identity`
- Verify Bedrock access in AWS Console → Bedrock → Model access
- Ensure Claude 3.5 Sonnet v2 is enabled

**"ModelNotFound":**
- Region must be us-east-1, us-west-2, or eu-west-1
- Check model ID in config matches available models

**"ThrottlingException":**
- Too many requests, add delays between calls
- Or upgrade to higher limits in AWS Console

### OpenAI Errors

**"AuthenticationError":**
```bash
# Check API key
echo $OPENAI_API_KEY
# Should output: sk-...

# If empty, set it:
export OPENAI_API_KEY="sk-..."
```

**"RateLimitError":**
- You've exceeded OpenAI rate limits
- Wait a bit or upgrade your OpenAI plan

### Data Fetching Errors

**"Failed to fetch data":**
- Check internet connection
- yfinance may be rate-limited (wait a bit)
- Symbol may be invalid or delisted

**"ArcticDB error":**
```bash
# Clear cache and retry
rm -rf quant_data/agent_cache/*
```

## 📚 Directory Structure

After setup, you'll have:

```
quant/
├── ai_agent/                      # AI agent code
│   ├── core/
│   │   └── agent.py               # Main agent
│   ├── tools/                     # Tools (market data, risk, etc.)
│   │   ├── market_data.py
│   │   ├── backtesting.py
│   │   ├── risk_analysis.py
│   │   ├── portfolio.py
│   │   ├── technical.py
│   │   └── fundamental.py
│   └── workflows/                 # Pre-defined workflows
│       ├── market_analysis.py
│       └── reporting.py
├── examples/                      # Example scripts
│   ├── example_basic_usage.py
│   └── example_workflows.py
├── config/
│   └── ai_agent_config.yaml       # Configuration
├── reports/                       # Generated reports
├── conversations/                 # Saved conversations
├── logs/                          # Log files
├── run_ai_agent.py               # Interactive CLI
├── AI_AGENT_README.md            # Complete documentation
└── AI_AGENT_SETUP.md             # This file
```

## 🎓 Learning Path

1. **Start Here**: `examples/example_basic_usage.py`
   - Basic queries and API usage
   - Simple market analysis

2. **Next**: `examples/example_workflows.py`
   - Daily analysis workflow
   - Investment memo generation
   - Portfolio review

3. **Advanced**: Custom workflows
   - Modify `ai_agent/workflows/` for your strategies
   - Create custom tool combinations
   - Build automated monitoring systems

## 🔐 Security Best Practices

1. **Never commit API keys**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   echo "config/secrets.yaml" >> .gitignore
   ```

2. **Use environment variables**
   ```bash
   # In ~/.bashrc or ~/.zshrc
   export AWS_ACCESS_KEY_ID="..."
   export AWS_SECRET_ACCESS_KEY="..."
   export OPENAI_API_KEY="..."
   ```

3. **Rotate keys regularly**
   - AWS: Create new keys every 90 days
   - OpenAI: Rotate if exposed

4. **Monitor usage**
   - AWS: CloudWatch metrics
   - OpenAI: Usage dashboard

## 🚦 Next Steps

1. **Run First Analysis**
   ```bash
   python run_ai_agent.py
   # Try: "What's the current market regime?"
   ```

2. **Customize Configuration**
   ```bash
   # Edit config/ai_agent_config.yaml
   # Set your watchlist and preferences
   ```

3. **Integrate with Existing Workflows**
   ```python
   # Use AI agent to analyze results from your scanners
   from ai_agent.core.agent import create_agent
   import pandas as pd
   
   # Load your screening results
   df = pd.read_csv("value_stocks_s&p_500_20260106.csv")
   top_symbols = df.head(10)['symbol'].tolist()
   
   # Get AI analysis
   agent = create_agent()
   analysis = agent.analyze_market(top_symbols)
   ```

4. **Build Custom Workflows**
   - See `ai_agent/workflows/` for examples
   - Create workflows for your specific strategies
   - Automate daily/weekly analysis

## 📖 Resources

- **Main Documentation**: [AI_AGENT_README.md](AI_AGENT_README.md)
- **Examples**: `examples/` directory
- **Your Existing Docs**: 
  - [README.md](README.md) - Original quant toolkit
  - [docs/context.txt](docs/context.txt) - Corporate finance framework
  - [docs/gs_quant_explanation.md](docs/gs_quant_explanation.md) - GS Quant integration

## ❓ FAQ

**Q: Which provider should I use?**
A: AWS Bedrock (Claude) is recommended for:
- Lower cost (~30% cheaper)
- Better handling of long contexts
- More analytical/precise outputs

OpenAI (GPT-4) is good for:
- Easier setup (no AWS account needed)
- Faster initial responses
- More conversational style

**Q: How much will this cost?**
A: For typical usage:
- Daily analysis: $1-2 per day
- Deep dives: $0.50-1 each
- Monthly cost: ~$50-100 for active use

**Q: Can I use this offline?**
A: No, requires internet for:
- LLM API calls (Bedrock/OpenAI)
- Market data fetching (yfinance)

But ArcticDB caching minimizes data fetching.

**Q: Is my data secure?**
A: Yes:
- AWS Bedrock: Data not used for training
- OpenAI: Opt out of training via settings
- All data stays in your local cache (ArcticDB)

**Q: Can I customize the agent's personality?**
A: Yes! Edit `system_prompt` in `ai_agent/core/agent.py`:
```python
system_prompt = """You are a [your style] analyst at [firm]..."""
```

## 🎉 You're Ready!

Start with:
```bash
python run_ai_agent.py
```

Or dive into examples:
```bash
python examples/example_basic_usage.py
```

**Happy analyzing!** 🚀
