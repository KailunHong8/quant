"""
Workflow Examples
=================

Examples using pre-defined workflows for autonomous operations.
"""

from ai_agent.workflows.market_analysis import create_market_workflow
from ai_agent.workflows.reporting import create_reporting_workflow


def example_daily_analysis():
    """Run daily market analysis workflow"""
    
    print("=" * 80)
    print("Daily Market Analysis Workflow")
    print("=" * 80)
    
    # Create workflow
    workflow = create_market_workflow(provider="bedrock", verbose=True)
    
    # Define watchlist
    watchlist = ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "META", "TSLA"]
    
    # Run daily analysis
    report = workflow.run_daily_analysis(watchlist)
    
    print("\n" + "=" * 80)
    print("DAILY ANALYSIS REPORT:")
    print("=" * 80)
    print(report)


def example_regime_detection():
    """Detect market regime changes"""
    
    print("\n" + "=" * 80)
    print("Market Regime Detection")
    print("=" * 80)
    
    workflow = create_market_workflow(provider="bedrock", verbose=True)
    
    report = workflow.detect_regime_change()
    
    print("\n" + "=" * 80)
    print("REGIME ANALYSIS:")
    print("=" * 80)
    print(report)


def example_stock_deep_dive():
    """Deep dive analysis on a single stock"""
    
    print("\n" + "=" * 80)
    print("Stock Deep Dive: AAPL")
    print("=" * 80)
    
    workflow = create_market_workflow(provider="bedrock", verbose=True)
    
    # Analyze AAPL vs peers
    report = workflow.analyze_stock_deep_dive(
        symbol="AAPL",
        peer_symbols=["MSFT", "GOOGL", "META"]
    )
    
    print("\n" + "=" * 80)
    print("DEEP DIVE REPORT:")
    print("=" * 80)
    print(report)


def example_market_screening():
    """Screen the market for opportunities"""
    
    print("\n" + "=" * 80)
    print("Market Screening Workflow")
    print("=" * 80)
    
    workflow = create_market_workflow(provider="bedrock", verbose=True)
    
    # Screen for high-quality value stocks
    report = workflow.screen_market(universe="sp500", min_score=4)
    
    print("\n" + "=" * 80)
    print("SCREENING RESULTS:")
    print("=" * 80)
    print(report)


def example_investment_memo():
    """Generate an investment memo"""
    
    print("\n" + "=" * 80)
    print("Investment Memo Generation")
    print("=" * 80)
    
    workflow = create_reporting_workflow(provider="bedrock", verbose=True)
    
    # Generate memo for a BUY recommendation
    memo = workflow.generate_investment_memo(
        symbol="AAPL",
        action="BUY",
        thesis="Strong competitive moat in consumer electronics, expanding services revenue, "
               "solid balance sheet with massive buyback program, trading at reasonable valuation."
    )
    
    print("\n" + "=" * 80)
    print("INVESTMENT MEMO:")
    print("=" * 80)
    print(memo)
    
    # Save to file
    with open("reports/AAPL_investment_memo.md", "w") as f:
        f.write(memo)
    print("\n✓ Memo saved to reports/AAPL_investment_memo.md")


def example_portfolio_review():
    """Generate a portfolio performance review"""
    
    print("\n" + "=" * 80)
    print("Portfolio Review")
    print("=" * 80)
    
    workflow = create_reporting_workflow(provider="bedrock", verbose=True)
    
    # Define portfolio
    portfolio = {
        "AAPL": 0.15,
        "GOOGL": 0.15,
        "MSFT": 0.15,
        "JPM": 0.10,
        "JNJ": 0.10,
        "WMT": 0.10,
        "XOM": 0.10,
        "CVX": 0.075,
        "PG": 0.075,
    }
    
    # Generate review
    review = workflow.generate_portfolio_review(portfolio, period="quarterly")
    
    print("\n" + "=" * 80)
    print("PORTFOLIO REVIEW:")
    print("=" * 80)
    print(review)


def example_risk_report():
    """Generate a comprehensive risk report"""
    
    print("\n" + "=" * 80)
    print("Risk Report Generation")
    print("=" * 80)
    
    workflow = create_reporting_workflow(provider="bedrock", verbose=True)
    
    # Define portfolio
    portfolio = {
        "AAPL": 0.20,
        "GOOGL": 0.20,
        "MSFT": 0.20,
        "NVDA": 0.20,
        "META": 0.20
    }
    
    # Generate risk report
    report = workflow.generate_risk_report(portfolio)
    
    print("\n" + "=" * 80)
    print("RISK REPORT:")
    print("=" * 80)
    print(report)


def example_daily_brief():
    """Generate a concise daily brief"""
    
    print("\n" + "=" * 80)
    print("Daily Market Brief")
    print("=" * 80)
    
    workflow = create_reporting_workflow(provider="bedrock", verbose=True)
    
    watchlist = ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA"]
    
    brief = workflow.generate_daily_brief(watchlist)
    
    print("\n" + "=" * 80)
    print("DAILY BRIEF:")
    print("=" * 80)
    print(brief)


if __name__ == "__main__":
    # Run workflow examples
    # Uncomment the ones you want to try
    
    example_daily_analysis()
    # example_regime_detection()
    # example_stock_deep_dive()
    # example_market_screening()
    # example_investment_memo()
    # example_portfolio_review()
    # example_risk_report()
    # example_daily_brief()
