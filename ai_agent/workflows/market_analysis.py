"""
Market Analysis Workflows
=========================

Pre-defined workflows for autonomous market analysis and regime detection.
"""

from typing import List, Dict, Optional
from ai_agent.core.agent import QuantAgent


class MarketAnalysisWorkflow:
    """
    Autonomous market analysis workflow
    
    Performs comprehensive market analysis including:
    - Macro regime detection
    - Sector rotation analysis
    - Individual stock analysis
    - Risk assessment
    """
    
    def __init__(self, agent: QuantAgent):
        self.agent = agent
    
    def run_daily_analysis(self, watchlist: List[str]) -> str:
        """
        Run daily market analysis on watchlist
        
        Args:
            watchlist: List of symbols to analyze
        
        Returns:
            Daily market report
        """
        prompt = f"""Perform a comprehensive daily market analysis:

**Watchlist**: {', '.join(watchlist)}

Please provide:

1. **Macro Environment Assessment**
   - Fetch current macro indicators (10Y yield, VIX, Dollar Index, S&P 500)
   - Assess current market regime (risk-on/risk-off, high/low volatility)
   - Identify macro headwinds/tailwinds

2. **Sector Analysis**
   - Get sector performance (1 day, 5 days, 1 month)
   - Identify leading and lagging sectors
   - Sector rotation signals

3. **Watchlist Analysis**
   For each stock:
   - Fetch latest fundamentals (valuation, quality metrics)
   - Calculate technical indicators (MAs, RSI)
   - Assess risk metrics (beta, volatility)

4. **Portfolio Implications**
   - Opportunities to buy (undervalued, strong momentum)
   - Risks to watch (overvalued, deteriorating fundamentals)
   - Rebalancing recommendations

5. **Summary**
   - Top 3 actionable insights
   - Risk level assessment (low/moderate/high)
   - Recommended actions for today

Use all available tools to fetch data and perform analysis."""
        
        return self.agent.chat(prompt)
    
    def detect_regime_change(self) -> str:
        """
        Detect if market regime has changed
        
        Returns:
            Regime analysis report
        """
        prompt = """Perform market regime detection analysis:

1. **Current State**
   - Fetch current macro indicators
   - Get sector performance (1 week, 1 month, 3 months)
   - Analyze S&P 500 technical indicators

2. **Historical Comparison**
   - Compare current VIX to 3-month average
   - Compare sector correlations (rising = risk-off, falling = risk-on)
   - Check if we're in bull/bear/transition phase

3. **Regime Assessment**
   - Current regime: Low Vol / High Vol / Crisis / Recovery / Expansion
   - Confidence level in assessment
   - Leading indicators of potential regime change

4. **Investment Implications**
   - Sectors to overweight in current regime
   - Sectors to underweight
   - Defensive positioning recommendations

5. **Monitoring Plan**
   - Key metrics to watch for regime change
   - Trigger levels for action

Use tools to fetch all necessary data."""
        
        return self.agent.chat(prompt)
    
    def analyze_stock_deep_dive(self, symbol: str, peer_symbols: Optional[List[str]] = None) -> str:
        """
        Deep dive analysis on a single stock
        
        Args:
            symbol: Stock symbol to analyze
            peer_symbols: Optional peer symbols for comparison
        
        Returns:
            Deep dive report
        """
        peer_str = f" vs peers {', '.join(peer_symbols)}" if peer_symbols else ""
        
        prompt = f"""Perform a deep dive analysis on {symbol}{peer_str}:

1. **Business Quality Assessment**
   - Fetch fundamentals (valuation, profitability, financial health)
   - Run quality metrics (ROIC, FCF yield, margins)
   - Assess competitive moat (high margins + high ROE = moat)

2. **Valuation Analysis**
   - Current valuation ratios (P/E, P/B, P/S)
   - Compare to historical averages
   {f"- Compare to peer group: {', '.join(peer_symbols or [])}" if peer_symbols else ""}
   - Fair value estimate

3. **Technical Analysis**
   - Calculate moving averages (20, 50, 200 day)
   - RSI and momentum indicators
   - Support/resistance levels
   - Trend assessment

4. **Risk Analysis**
   - Calculate beta and volatility
   - Stress test (2008, 2020, rising rates scenarios)
   - Downside risk assessment

5. **Investment Thesis**
   - Bull case (3 key positives)
   - Bear case (3 key risks)
   - Recommended action: Strong Buy / Buy / Hold / Sell / Strong Sell
   - Target price and expected return
   - Position sizing recommendation

Use all available tools for comprehensive analysis."""
        
        if peer_symbols:
            prompt += f"\n\nPeer symbols for comparison: {', '.join(peer_symbols)}"
        
        return self.agent.chat(prompt)
    
    def screen_market(self, universe: str = "sp500", min_score: int = 4) -> str:
        """
        Screen entire market for investment opportunities
        
        Args:
            universe: Market universe to screen ('sp500', 'russell1000')
            min_score: Minimum Buffett score (0-6)
        
        Returns:
            Screening results
        """
        # For demonstration, use a subset of S&P 500
        symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", 
            "BRK-B", "JPM", "V", "JNJ", "WMT", "PG", "XOM", "CVX",
            "UNH", "HD", "MA", "BAC", "ABBV", "PFE", "KO", "PEP",
            "COST", "AVGO", "MRK", "LLY", "TMO", "ACN", "CSCO"
        ]
        
        prompt = f"""Screen the market for high-quality value investments:

**Universe**: {universe} (using representative sample)
**Symbols**: {', '.join(symbols)}
**Minimum Score**: {min_score}/6 Buffett criteria

Tasks:

1. **Buffett Value Screen**
   - Run buffett_screen on all symbols
   - Filter for score >= {min_score}
   - Identify top value opportunities

2. **Quality Assessment**
   - Run quality_metrics on passing stocks
   - Identify stocks with economic moats
   - Rank by quality score

3. **Sector Diversification**
   - Group results by sector
   - Ensure diversification across sectors
   - Identify sector concentration risks

4. **Final Recommendations**
   - Top 10 stocks ranked by holistic score (value + quality)
   - Sector breakdown
   - Suggested portfolio allocation
   - Expected portfolio risk/return

5. **Watchlist**
   - Stocks that almost passed (score = {min_score - 1})
   - Monitor for potential upgrades

Use buffett_screen and quality_metrics tools."""
        
        return self.agent.chat(prompt)


# Convenience function
def create_market_workflow(provider: str = "bedrock", **kwargs) -> MarketAnalysisWorkflow:
    """
    Create a market analysis workflow
    
    Args:
        provider: 'bedrock' or 'openai'
        **kwargs: Additional agent config options
    
    Returns:
        MarketAnalysisWorkflow instance
    """
    from ai_agent.core.agent import create_agent
    agent = create_agent(provider=provider, **kwargs)
    return MarketAnalysisWorkflow(agent)
