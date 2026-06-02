"""
AI Agent Tools
==============

Tool library for the AI quant agent.

Tools are automatically registered with the agent when imported.
Each tool provides a specific capability:
- market_data: Fetch market data, fundamentals, macroeconomic indicators
- backtesting: Run strategy backtests
- risk_analysis: Calculate risk metrics, VaR, stress tests
- portfolio: Portfolio optimization, allocation, rebalancing
- technical: Technical indicators and chart patterns
- fundamental: Fundamental analysis and screening
"""

# Import all tool modules to register them
from . import market_data
from . import backtesting
from . import risk_analysis
from . import portfolio
from . import technical
from . import fundamental

__all__ = [
    'market_data',
    'backtesting',
    'risk_analysis',
    'portfolio',
    'technical',
    'fundamental'
]
