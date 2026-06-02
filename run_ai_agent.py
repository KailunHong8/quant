#!/usr/bin/env python3
"""
AI Quant Agent - Interactive CLI
================================

Interactive command-line interface for the AI quant agent.

Usage:
    python run_ai_agent.py
    
    Or with specific provider:
    python run_ai_agent.py --provider openai
    python run_ai_agent.py --provider bedrock --verbose
"""

import argparse
import sys
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Quant Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_ai_agent.py
  python run_ai_agent.py --provider openai
  python run_ai_agent.py --provider bedrock --verbose
  
Queries to try:
  - What's the current market regime?
  - Analyze AAPL, GOOGL, MSFT fundamentals
  - Screen for value stocks: AAPL, GOOGL, JPM, JNJ, XOM
  - Optimize portfolio: AAPL, GOOGL, JPM for max Sharpe
  - What are the risks in my portfolio of AAPL 50%, GOOGL 50%?
"""
    )
    
    parser.add_argument(
        '--provider',
        type=str,
        default='bedrock',
        choices=['bedrock', 'openai'],
        help='LLM provider (default: bedrock)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help='Specific model to use (optional)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        default='chat',
        choices=['chat', 'workflow'],
        help='Interaction mode (default: chat)'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 80)
    print("AI-POWERED QUANT AGENT")
    print("World-Class Quantitative Analysis")
    print("=" * 80)
    print(f"Provider: {args.provider.upper()}")
    print(f"Mode: {args.mode.upper()}")
    print(f"Date: {datetime.now().strftime('%B %d, %Y %H:%M')}")
    print("=" * 80)
    print()
    
    # Import after banner (so user sees something quickly)
    try:
        from ai_agent.core.agent import create_agent
        from ai_agent.workflows.market_analysis import MarketAnalysisWorkflow
        from ai_agent.workflows.reporting import ReportingWorkflow
    except ImportError as e:
        print(f"Error: Failed to import AI agent modules: {e}")
        print("\nMake sure you're running from the quant directory:")
        print("  cd /path/to/quant")
        print("  export PYTHONPATH=$PYTHONPATH:$(pwd)")
        print("  python run_ai_agent.py")
        sys.exit(1)
    
    # Create agent
    try:
        print("Initializing AI agent...")
        agent_kwargs = {
            'provider': args.provider,
            'verbose': args.verbose
        }
        if args.model:
            agent_kwargs['model'] = args.model
        
        agent = create_agent(**agent_kwargs)
        print()
    except Exception as e:
        print(f"Error: Failed to initialize agent: {e}")
        print("\nCheck your credentials:")
        if args.provider == 'bedrock':
            print("  AWS Bedrock: Run 'aws configure' or set AWS environment variables")
        else:
            print("  OpenAI: Set OPENAI_API_KEY environment variable")
        sys.exit(1)
    
    if args.mode == 'chat':
        run_chat_mode(agent)
    else:
        run_workflow_mode(agent)


def run_chat_mode(agent):
    """Interactive chat mode"""
    print("Chat Mode - Ask me anything about markets, stocks, or portfolios")
    print("Commands: 'quit' or 'exit' to end, 'save' to save conversation, 'help' for examples")
    print("=" * 80)
    print()
    
    conversation_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input("\n🤔 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            elif user_input.lower() == 'save':
                filename = f"conversations/chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                agent.save_conversation(filename)
                continue
            
            # Send to agent
            print("\n🤖 Agent: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            
            conversation_count += 1
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Try rephrasing your question or type 'help' for examples.")


def run_workflow_mode(agent):
    """Workflow selection mode"""
    from ai_agent.workflows.market_analysis import MarketAnalysisWorkflow
    from ai_agent.workflows.reporting import ReportingWorkflow
    
    market = MarketAnalysisWorkflow(agent)
    reporting = ReportingWorkflow(agent)
    
    print("Workflow Mode - Select a pre-defined workflow")
    print("=" * 80)
    print()
    print("Available workflows:")
    print("  1. Daily Market Analysis")
    print("  2. Market Regime Detection")
    print("  3. Stock Deep Dive")
    print("  4. Market Screening")
    print("  5. Investment Memo")
    print("  6. Portfolio Review")
    print("  7. Risk Report")
    print("  8. Daily Brief")
    print("  9. Back to Chat Mode")
    print("  0. Exit")
    print()
    
    while True:
        try:
            choice = input("Select workflow (0-9): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            
            elif choice == '9':
                run_chat_mode(agent)
                break
            
            elif choice == '1':
                watchlist = input("Enter watchlist (comma-separated, e.g., AAPL,GOOGL,MSFT): ").strip()
                symbols = [s.strip() for s in watchlist.split(',')]
                print("\nRunning daily analysis...")
                result = market.run_daily_analysis(symbols)
                print("\n" + "=" * 80)
                print(result)
                print("=" * 80)
            
            elif choice == '2':
                print("\nDetecting market regime...")
                result = market.detect_regime_change()
                print("\n" + "=" * 80)
                print(result)
                print("=" * 80)
            
            elif choice == '3':
                symbol = input("Enter symbol: ").strip().upper()
                peers = input("Enter peer symbols (comma-separated, optional): ").strip()
                peer_list = [s.strip() for s in peers.split(',')] if peers else None
                print(f"\nAnalyzing {symbol}...")
                result = market.analyze_stock_deep_dive(symbol, peer_list)
                print("\n" + "=" * 80)
                print(result)
                print("=" * 80)
            
            elif choice == '4':
                min_score = input("Minimum Buffett score (1-6, default 4): ").strip()
                min_score = int(min_score) if min_score else 4
                print("\nScreening market...")
                result = market.screen_market(min_score=min_score)
                print("\n" + "=" * 80)
                print(result)
                print("=" * 80)
            
            elif choice == '5':
                symbol = input("Enter symbol: ").strip().upper()
                action = input("Action (BUY/SELL/HOLD): ").strip().upper()
                thesis = input("Investment thesis (optional): ").strip()
                print(f"\nGenerating investment memo for {symbol}...")
                result = reporting.generate_investment_memo(symbol, action, thesis or None)
                print("\n" + "=" * 80)
                print(result)
                print("=" * 80)
                
                # Save option
                save = input("\nSave memo to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = f"reports/{symbol}_memo_{datetime.now().strftime('%Y%m%d')}.md"
                    with open(filename, 'w') as f:
                        f.write(result)
                    print(f"✓ Saved to {filename}")
            
            elif choice == '6':
                print("Enter portfolio (e.g., AAPL:0.30,GOOGL:0.30,JPM:0.40):")
                portfolio_str = input("Portfolio: ").strip()
                portfolio = {}
                for item in portfolio_str.split(','):
                    sym, weight = item.split(':')
                    portfolio[sym.strip()] = float(weight.strip())
                
                print("\nGenerating portfolio review...")
                result = reporting.generate_portfolio_review(portfolio)
                print("\n" + "=" * 80)
                print(result)
                print("=" * 80)
            
            elif choice == '7':
                print("Enter portfolio (e.g., AAPL:0.30,GOOGL:0.30,JPM:0.40):")
                portfolio_str = input("Portfolio: ").strip()
                portfolio = {}
                for item in portfolio_str.split(','):
                    sym, weight = item.split(':')
                    portfolio[sym.strip()] = float(weight.strip())
                
                print("\nGenerating risk report...")
                result = reporting.generate_risk_report(portfolio)
                print("\n" + "=" * 80)
                print(result)
                print("=" * 80)
            
            elif choice == '8':
                watchlist = input("Enter watchlist (comma-separated): ").strip()
                symbols = [s.strip() for s in watchlist.split(',')]
                print("\nGenerating daily brief...")
                result = reporting.generate_daily_brief(symbols)
                print("\n" + "=" * 80)
                print(result)
                print("=" * 80)
            
            else:
                print("Invalid choice. Please select 0-9.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}")


def print_help():
    """Print example queries"""
    print("\n" + "=" * 80)
    print("EXAMPLE QUERIES")
    print("=" * 80)
    print()
    print("Market Analysis:")
    print("  - What's the current market regime?")
    print("  - Analyze macro indicators and assess risk-on/risk-off sentiment")
    print("  - Get sector performance for the last month")
    print()
    print("Stock Analysis:")
    print("  - Analyze AAPL fundamentals and valuation")
    print("  - Compare AAPL to MSFT and GOOGL")
    print("  - Run Buffett screen on AAPL, GOOGL, JPM, JNJ, XOM")
    print("  - Calculate quality metrics for NVDA")
    print()
    print("Portfolio:")
    print("  - Optimize allocation for AAPL, GOOGL, JPM, JNJ, XOM")
    print("  - Is my portfolio of AAPL 50%, GOOGL 50% well diversified?")
    print("  - Calculate VaR for portfolio: AAPL 30%, GOOGL 30%, JPM 40%")
    print("  - Stress test my portfolio against 2008 crisis")
    print()
    print("Technical:")
    print("  - Calculate moving averages for AAPL")
    print("  - What's the RSI for NVDA?")
    print("  - Find support and resistance for MSFT")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
