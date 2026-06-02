"""
Basic AI Agent Usage Example
============================

Simple example showing how to use the AI Quant Agent for market analysis.

Prerequisites:
- AWS credentials configured (for Bedrock) OR
- OPENAI_API_KEY environment variable set (for OpenAI)
"""

from ai_agent.core.agent import create_agent

# Example 1: Simple market analysis
def example_market_analysis():
    """Analyze a few stocks"""
    
    print("=" * 80)
    print("Example 1: Basic Market Analysis")
    print("=" * 80)
    
    # Create agent (uses Bedrock Claude by default)
    agent = create_agent(provider="bedrock", verbose=True)
    
    # Ask for analysis
    response = agent.analyze_market(
        symbols=["AAPL", "GOOGL", "MSFT"],
        analysis_type="comprehensive"
    )
    
    print("\n" + "=" * 80)
    print("ANALYSIS RESULT:")
    print("=" * 80)
    print(response)
    
    # Save conversation
    agent.save_conversation("conversations/market_analysis_example.json")


# Example 2: Custom question
def example_custom_question():
    """Ask a custom question"""
    
    print("\n" + "=" * 80)
    print("Example 2: Custom Question")
    print("=" * 80)
    
    agent = create_agent(provider="bedrock", verbose=True)
    
    # Ask any question
    question = """
    I'm looking to invest in technology stocks with strong fundamentals 
    and reasonable valuation. Can you screen AAPL, GOOGL, MSFT, NVDA, and META 
    using Buffett's criteria and quality metrics, then recommend the top 2?
    """
    
    response = agent.chat(question)
    
    print("\n" + "=" * 80)
    print("RESPONSE:")
    print("=" * 80)
    print(response)


# Example 3: Portfolio optimization
def example_portfolio_optimization():
    """Optimize a portfolio"""
    
    print("\n" + "=" * 80)
    print("Example 3: Portfolio Optimization")
    print("=" * 80)
    
    agent = create_agent(provider="bedrock", verbose=True)
    
    # Optimize portfolio
    response = agent.optimize_portfolio(
        symbols=["AAPL", "GOOGL", "JPM", "JNJ", "XOM"],
        objective="sharpe"
    )
    
    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULT:")
    print("=" * 80)
    print(response)


# Example 4: Risk assessment
def example_risk_assessment():
    """Assess portfolio risk"""
    
    print("\n" + "=" * 80)
    print("Example 4: Risk Assessment")
    print("=" * 80)
    
    agent = create_agent(provider="bedrock", verbose=True)
    
    # Define portfolio
    portfolio = {
        "AAPL": 0.20,
        "GOOGL": 0.20,
        "MSFT": 0.20,
        "JPM": 0.20,
        "JNJ": 0.20
    }
    
    # Get risk report
    response = agent.risk_report(portfolio)
    
    print("\n" + "=" * 80)
    print("RISK REPORT:")
    print("=" * 80)
    print(response)


# Example 5: Using OpenAI instead of Bedrock
def example_openai():
    """Use OpenAI instead of AWS Bedrock"""
    
    print("\n" + "=" * 80)
    print("Example 5: Using OpenAI")
    print("=" * 80)
    
    # Create agent with OpenAI
    # Requires: export OPENAI_API_KEY=your_key_here
    agent = create_agent(
        provider="openai",
        model="gpt-4o",  # or "gpt-4o-mini" for faster/cheaper
        verbose=True
    )
    
    response = agent.chat("What's the current market regime based on macro indicators?")
    
    print("\n" + "=" * 80)
    print("RESPONSE:")
    print("=" * 80)
    print(response)


if __name__ == "__main__":
    # Run examples
    # Uncomment the ones you want to try
    
    example_market_analysis()
    # example_custom_question()
    # example_portfolio_optimization()
    # example_risk_assessment()
    # example_openai()
