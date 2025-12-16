# FinTech Quantitative Finance Project

A quantitative finance toolkit exploring financial data, derivatives pricing, and trading strategies using modern Python libraries.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Virtual environment (`.venv311`)

### Setup

```bash
# Activate virtual environment
source .venv311/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 📁 Project Structure

```
quant/
├── scripts/              # Test and example scripts
│   ├── test_openbb.py   # OpenBB market data examples
│   ├── test_pyql.py     # QuantLib examples
│   └── test_gs_openbb_integration.py  # GS Quant + OpenBB integration
├── docs/                 # Documentation
│   ├── CLAUDE_CODE_BEDROCK_SETUP.md
│   └── gs_quant_explanation.md
├── config/               # Configuration files
│   ├── claude_code_bedrock.env
│   └── setup_*.sh
└── .venv311/            # Python virtual environment
```

## 🛠️ Tools & Libraries

### Market Data
- **OpenBB**: Free market data (yfinance, etc.)
- **GS Quant**: Goldman Sachs quantitative finance toolkit

### Quantitative Finance
- **QuantLib**: Derivatives pricing and risk management
- **GS Quant**: Trading strategies, backtesting, risk analytics

### Data Analysis
- **pandas**: Data manipulation
- **numpy**: Numerical computing

## 📚 Learning Resources

This project follows concepts from:
- **Principles of Corporate Finance** (Brealey, Myers, Allen)
  - Options & Derivatives (Chapters 20-21)
  - Portfolio Theory (Chapter 8)
  - Risk Management (Chapters 7, 24)
  - Capital Budgeting (Chapters 6-7)

## 🔧 Configuration

### Claude Code + Amazon Bedrock

See `docs/CLAUDE_CODE_BEDROCK_SETUP.md` for setup instructions.

Quick setup:
```bash
# 1. Login to AWS SSO
aws sso login --profile bedrock-code-ai

# 2. Load configuration
source config/claude_code_bedrock.env

# 3. Verify
config/verify_claude_code_setup.sh
```

## 📖 Examples

### OpenBB - Market Data
```bash
python scripts/test_openbb.py
```

### QuantLib - Options Pricing
```bash
python scripts/test_pyql.py
```

### GS Quant - Strategy & Risk
```bash
python scripts/test_gs_openbb_integration.py
```

## 🔐 AWS Configuration

This project uses AWS Bedrock for Claude Code. Configuration:
- **Profile**: `bedrock-code-ai`
- **Region**: `eu-west-1`
- **SSO**: HelloFresh SSO

## 📝 Notes

- Virtual environments are gitignored
- AWS credentials should never be committed
- See individual script files for usage examples

## 🤝 Contributing

This is a personal learning project. Feel free to fork and adapt for your own use.

## 📄 License

Personal project - see individual library licenses for dependencies.

