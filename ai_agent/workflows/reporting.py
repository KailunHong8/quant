"""
Reporting Workflows
==================

Generate institutional-grade investment reports and memos.
"""

from typing import List, Dict, Optional
from ai_agent.core.agent import QuantAgent
from datetime import datetime


class ReportingWorkflow:
    """
    Generate JP Morgan-style investment reports
    """
    
    def __init__(self, agent: QuantAgent):
        self.agent = agent
    
    def generate_investment_memo(
        self,
        symbol: str,
        action: str = "BUY",
        thesis: Optional[str] = None
    ) -> str:
        """
        Generate an investment memo (JP Morgan style)
        
        Args:
            symbol: Stock symbol
            action: Investment action (BUY/SELL/HOLD)
            thesis: Optional investment thesis
        
        Returns:
            Investment memo
        """
        thesis_section = f"\n\n**Our Thesis**: {thesis}" if thesis else ""
        
        prompt = f"""Generate a professional investment memo for {symbol}:

**Recommendation**: {action}
**Date**: {datetime.now().strftime("%B %d, %Y")}
{thesis_section}

Structure the memo as follows:

**INVESTMENT MEMO: {symbol}**

**Executive Summary**
- One-paragraph summary of recommendation
- Key investment highlights (3-4 bullets)
- Target price and expected return
- Risk rating (Low/Medium/High)

**Business Overview**
- What does the company do?
- Market position and competitive advantages
- Key products/services and revenue drivers

**Financial Analysis**
- Fetch current fundamentals
- Valuation: P/E, P/B, P/S vs historical and peers
- Profitability: ROE, ROA, margins, ROIC
- Financial health: Debt levels, current ratio, interest coverage
- Growth: Revenue and earnings trends
- Cash generation: FCF yield, operating cash flow

**Quality Assessment**
- Economic moat indicators (high ROIC + margins)
- Competitive positioning
- Management quality (capital allocation)
- Sustainability of business model

**Technical Analysis**
- Price trends and momentum
- Support/resistance levels
- Technical signals

**Risk Analysis**
- Key risks (3-4 bullets)
- Downside scenario analysis
- Stress test results
- Volatility and beta

**Valuation**
- Current valuation metrics
- Fair value estimate with methodology
- Implied return potential
- Comparison to peers

**Investment Recommendation**
- Clear BUY/SELL/HOLD recommendation
- Position sizing guidance (% of portfolio)
- Entry price targets
- Stop-loss levels
- Catalysts to watch

**Conclusion**
- Restate recommendation with conviction level
- Key monitoring points

Use all available tools to fetch comprehensive data."""
        
        return self.agent.chat(prompt)
    
    def generate_portfolio_review(
        self,
        portfolio: Dict[str, float],
        period: str = "quarterly"
    ) -> str:
        """
        Generate a portfolio performance review
        
        Args:
            portfolio: Dict of {symbol: weight}
            period: Review period
        
        Returns:
            Portfolio review report
        """
        symbols = list(portfolio.keys())
        weights = list(portfolio.values())
        
        prompt = f"""Generate a comprehensive portfolio review:

**Portfolio Holdings**:
{chr(10).join([f"- {s}: {w*100:.1f}%" for s, w in portfolio.items()])}

**Review Period**: {period}

Report Structure:

**PORTFOLIO PERFORMANCE REVIEW**

**1. Executive Summary**
- Overall performance vs benchmark (S&P 500)
- Key drivers of performance
- Major changes in period
- Forward outlook

**2. Performance Attribution**
- Fetch price history for all holdings
- Calculate returns by position
- Top 3 contributors and detractors
- Sector attribution

**3. Current Holdings Analysis**
For each holding:
- Current weight vs target
- Performance contribution
- Updated fundamental metrics
- Updated rating (Buy/Hold/Sell)
- Rebalancing recommendation

**4. Risk Metrics**
- Portfolio beta and volatility
- VaR and CVaR
- Correlation matrix
- Concentration risks
- Stress test results (multiple scenarios)

**5. Portfolio Optimization**
- Current vs optimal allocation
- Suggested rebalancing trades
- Expected improvement in Sharpe ratio
- Risk-adjusted return forecast

**6. Market Context**
- Current macro environment
- Sector performance and rotation
- Implications for portfolio positioning

**7. Action Items**
- Positions to trim/add
- Rebalancing needs
- Risk management actions
- Monitoring priorities

Use tools to fetch data and calculate all metrics."""
        
        return self.agent.chat(prompt)
    
    def generate_risk_report(
        self,
        portfolio: Dict[str, float]
    ) -> str:
        """
        Generate comprehensive risk report
        
        Args:
            portfolio: Dict of {symbol: weight}
        
        Returns:
            Risk report
        """
        symbols = list(portfolio.keys())
        weights = list(portfolio.values())
        
        prompt = f"""Generate a comprehensive risk report:

**Portfolio**:
{chr(10).join([f"- {s}: {w*100:.1f}%" for s, w in portfolio.items()])}

**PORTFOLIO RISK REPORT**

**1. Executive Summary**
- Overall risk level (Low/Medium/High)
- Key risk factors
- Recommended risk mitigation actions

**2. Market Risk**
- Portfolio beta vs market
- Volatility analysis
- Correlation to major indices
- Sector exposures

**3. Value at Risk (VaR)**
- Calculate VaR and CVaR at 95% and 99% confidence
- Interpretation in dollar terms
- Historical VaR comparison

**4. Stress Testing**
- 2008 Financial Crisis scenario
- 2020 COVID crash scenario
- Rising rates scenario
- Projected losses in each scenario
- Portfolio resilience assessment

**5. Concentration Risk**
- Single position limits (flag if >10%)
- Sector concentration (flag if >30%)
- Correlation analysis
- Diversification quality score

**6. Tail Risk Analysis**
- Maximum drawdown potential
- Black swan scenario analysis
- Liquidity risk
- Counter-party risk

**7. Risk Mitigation Recommendations**
- Suggested hedging strategies
- Diversification improvements
- Position sizing adjustments
- Stop-loss recommendations

**8. Risk Monitoring Dashboard**
- Key metrics to track daily
- Warning thresholds
- Action triggers

Use all risk analysis tools available."""
        
        return self.agent.chat(prompt)
    
    def generate_daily_brief(self, watchlist: List[str]) -> str:
        """
        Generate a concise daily market brief
        
        Args:
            watchlist: List of symbols to monitor
        
        Returns:
            Daily brief
        """
        prompt = f"""Generate a concise daily market brief:

**Watchlist**: {', '.join(watchlist)}

**DAILY MARKET BRIEF - {datetime.now().strftime("%B %d, %Y")}**

**Market Overview** (2-3 sentences)
- Fetch macro indicators (10Y yield, VIX, S&P 500)
- Current market sentiment and regime
- Key macro events/drivers

**Sector Movers** (1 paragraph)
- Get 1-day sector performance
- Leading and lagging sectors
- Rotation signals

**Watchlist Alerts** (bullet points)
For each stock in watchlist:
- Any significant price moves (>2%)
- Technical signals (MA crossovers, RSI extremes)
- Fundamental changes

**Trading Opportunities** (3-5 bullets)
- Stocks showing buy signals
- Stocks to trim
- Risk warnings

**Today's Focus**
- Top priority action
- Key level to watch

Keep it concise and actionable. Use tools to fetch latest data."""
        
        return self.agent.chat(prompt)


# Convenience function
def create_reporting_workflow(provider: str = "bedrock", **kwargs) -> ReportingWorkflow:
    """Create a reporting workflow"""
    from ai_agent.core.agent import create_agent
    agent = create_agent(provider=provider, **kwargs)
    return ReportingWorkflow(agent)
