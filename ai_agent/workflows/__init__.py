"""
AI Agent Workflows
==================

Pre-defined workflows for autonomous quant analysis operations.

Available workflows:
- MarketAnalysisWorkflow: Daily market analysis, regime detection, stock screening
- StrategyWorkflow: Strategy development, backtesting, optimization
- PortfolioWorkflow: Portfolio construction, optimization, rebalancing
- ReportingWorkflow: Investment memos, risk reports, performance analysis
"""

from .market_analysis import MarketAnalysisWorkflow, create_market_workflow

__all__ = [
    'MarketAnalysisWorkflow',
    'create_market_workflow',
]
