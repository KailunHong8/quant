# Quantitative Finance Toolkit

A professional quantitative finance toolkit for derivatives pricing, portfolio optimization, and trading strategy development using industry-standard Python libraries.

## Quick Start

### Prerequisites

- Python 3.11+
- Virtual environment (`.venv311`)

### Installation

```bash
# Activate virtual environment
source .venv311/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
quant/
├── scripts/              # Analysis and backtesting scripts
│   ├── test_openbb.py   # Market data retrieval
│   ├── test_pyql.py     # QuantLib derivatives pricing
│   ├── test_gs.py       # GS Quant framework examples
│   ├── test_vollib.py   # Options volatility analysis
│   └── test_gs_openbb_integration.py  # Integrated workflow
├── docs/                 # Technical documentation
│   └── gs_quant_explanation.md
└── config/               # Configuration files
```

## Tools & Libraries

### Market Data
- **OpenBB**: Multi-source market data platform (yfinance, FRED, etc.)
- **GS Quant**: Goldman Sachs quantitative finance toolkit

### Quantitative Analysis
- **QuantLib**: Industry-standard derivatives pricing and risk management
- **GS Quant**: Portfolio optimization, backtesting, and risk analytics
- **vollib**: Black-Scholes-Merton options analytics

### Data Science
- **pandas**: Time series and data manipulation
- **numpy**: Numerical computing

## Key Capabilities

### Derivatives Pricing
- European and American options (Black-Scholes, binomial trees)
- Interest rate derivatives (swaps, caps, floors)
- Greeks calculation (Delta, Gamma, Vega, Theta, Rho)
- Implied volatility analysis

### Portfolio Management
- Mean-variance optimization
- Risk metrics (VaR, CVaR, Sharpe ratio)
- Portfolio rebalancing strategies
- Factor exposure analysis

### Strategy Backtesting
- Historical simulation with realistic transaction costs
- Performance attribution
- Risk-adjusted return metrics
- Stress testing and scenario analysis

## Usage Examples

### Market Data Analysis
```bash
python scripts/test_openbb.py
```

### Options Pricing
```bash
python scripts/test_pyql.py      # QuantLib examples
python scripts/test_vollib.py    # Volatility analysis
```

### Portfolio & Strategy Analysis
```bash
python scripts/test_gs.py                      # GS Quant examples
python scripts/test_gs_openbb_integration.py   # Integrated workflow
```

## Technical Documentation

- **GS Quant Integration**: `docs/gs_quant_explanation.md`
- **Finance Theory**: Based on "Principles of Corporate Finance" (Brealey, Myers, Allen)
  - Options & Derivatives (Chapters 20-21)
  - Portfolio Theory (Chapter 8)
  - Risk Management (Chapters 7, 24)

## License

Personal research project - see individual library licenses for dependencies.
