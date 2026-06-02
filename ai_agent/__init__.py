"""
AI-Powered Quant Agent
======================

World-class quantitative analyst powered by Claude (Bedrock) or GPT-4 (OpenAI).

Quick Start:
    >>> from ai_agent.core.agent import create_agent
    >>> agent = create_agent(provider="bedrock")
    >>> agent.chat("What's the current market regime?")

Or use workflows:
    >>> from ai_agent.workflows import create_market_workflow
    >>> workflow = create_market_workflow()
    >>> workflow.run_daily_analysis(["AAPL", "GOOGL", "MSFT"])
"""

__version__ = "1.0.0"
__author__ = "AI Quant Agent"

from .core.agent import QuantAgent, AgentConfig, create_agent

__all__ = [
    'QuantAgent',
    'AgentConfig',
    'create_agent',
]
