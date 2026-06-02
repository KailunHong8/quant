"""
AI-Powered Quant Analyst Agent
==============================

World-class quantitative analyst powered by Claude (Bedrock) or OpenAI.
Performs institutional-grade analysis, strategy development, and risk management.

Architecture:
- LLM Brain: Claude 3.5 Sonnet (Bedrock) or GPT-4 (OpenAI)
- Tools: Market data, backtesting, risk analysis, portfolio management
- Memory: Conversation history + market context
- Workflows: Pre-defined analysis patterns

Based on JP Morgan quant analyst capabilities:
1. Market regime analysis
2. Strategy development & backtesting
3. Risk management & stress testing
4. Portfolio optimization
5. Research report generation
"""

import json
import os
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class Message:
    """Chat message in agent conversation"""
    role: str  # 'user', 'assistant', 'system', 'tool'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tool_calls: Optional[List[Dict]] = None
    tool_results: Optional[List[Dict]] = None


@dataclass
class AgentConfig:
    """Configuration for the AI agent"""
    provider: str = "bedrock"  # 'bedrock' or 'openai'
    model: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"  # or 'gpt-4o'
    temperature: float = 0.1  # Low temperature for analytical precision
    max_tokens: int = 8000
    aws_region: str = "us-east-1"
    
    # Agent personality
    system_prompt: str = """You are a world-class quantitative analyst and trader at JP Morgan.

Your expertise includes:
- **Quantitative Research**: Statistical analysis, factor modeling, machine learning
- **Portfolio Management**: Risk-adjusted returns, Sharpe optimization, diversification
- **Risk Management**: VaR, CVaR, stress testing, scenario analysis, tail risk
- **Strategy Development**: Backtesting, parameter optimization, transaction cost modeling
- **Macro Analysis**: Economic cycles, sector rotation, regime detection
- **Corporate Finance**: DCF valuation, ROIC analysis, capital structure
- **Derivatives**: Options pricing, Greeks, hedging strategies

Your approach:
1. **Data-driven**: Always ground analysis in quantitative evidence
2. **Risk-aware**: Consider downside scenarios and tail risks
3. **Rigorous**: Use proper statistical methods and financial theory
4. **Practical**: Account for transaction costs, slippage, market impact
5. **Clear**: Communicate complex concepts clearly to non-quants

Available tools: You have access to market data (OpenBB), backtesting engines, 
risk calculators, portfolio optimizers, and report generators.

Your output should be institutional-grade: precise, actionable, and well-documented."""
    
    # Operational settings
    enable_caching: bool = True
    cache_dir: str = "quant_data/agent_cache"
    max_iterations: int = 10  # Max tool-calling loops
    verbose: bool = True


class QuantAgent:
    """
    AI-powered quant analyst agent
    
    Capabilities:
    - Market analysis and regime detection
    - Strategy development and backtesting
    - Risk analysis and portfolio optimization
    - Automated reporting
    
    Example:
        >>> agent = QuantAgent()
        >>> response = agent.analyze_market(["AAPL", "GOOGL", "MSFT"])
        >>> print(response)
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the agent with LLM client and tools"""
        self.config = config or AgentConfig()
        self.messages: List[Message] = []
        self.tools: Dict[str, Callable] = {}
        
        # Initialize LLM client
        self._init_llm_client()
        
        # Load tools
        self._load_tools()
        
        # Add system message
        self.messages.append(Message(
            role="system",
            content=self.config.system_prompt
        ))
        
        if self.config.verbose:
            print("✓ AI Quant Agent initialized")
            print(f"  Provider: {self.config.provider}")
            print(f"  Model: {self.config.model}")
            print(f"  Tools loaded: {len(self.tools)}")
    
    def _init_llm_client(self):
        """Initialize the LLM client (Bedrock or OpenAI)"""
        if self.config.provider == "bedrock":
            try:
                import boto3
                self.client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=self.config.aws_region
                )
                if self.config.verbose:
                    print("✓ AWS Bedrock client initialized")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Bedrock client: {e}")
        
        elif self.config.provider == "openai":
            try:
                from openai import OpenAI
                api_key = os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable not set")
                self.client = OpenAI(api_key=api_key)
                if self.config.verbose:
                    print("✓ OpenAI client initialized")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize OpenAI client: {e}")
        
        else:
            raise ValueError(f"Unknown provider: {self.config.provider}")
    
    def _load_tools(self):
        """Load available tools for the agent"""
        # Import all tool modules
        from ai_agent.tools import (
            market_data, backtesting, risk_analysis, 
            portfolio, technical, fundamental
        )
        
        # Register tools from each module
        for module in [market_data, backtesting, risk_analysis, portfolio, technical, fundamental]:
            if hasattr(module, 'TOOLS'):
                for tool_name, tool_def in module.TOOLS.items():
                    self.register_tool(
                        name=tool_name,
                        func=tool_def["function"],
                        description=tool_def["description"],
                        parameters=tool_def["parameters"]
                    )
        
        if self.config.verbose:
            print(f"✓ Loaded {len(self.tools)} tools")
    
    def register_tool(self, name: str, func: Callable, description: str, parameters: Dict):
        """
        Register a new tool for the agent
        
        Args:
            name: Tool name
            func: Function to call
            description: Tool description for LLM
            parameters: JSON schema for parameters
        """
        self.tools[name] = {
            "function": func,
            "definition": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        if self.config.verbose:
            print(f"✓ Registered tool: {name}")
    
    def chat(self, user_message: str) -> str:
        """
        Send a message to the agent and get response
        
        Args:
            user_message: User's question or instruction
        
        Returns:
            Agent's response
        """
        # Add user message
        self.messages.append(Message(role="user", content=user_message))
        
        # Conversation loop with tool calling
        for iteration in range(self.config.max_iterations):
            if self.config.verbose:
                print(f"\n[Iteration {iteration + 1}]")
            
            # Call LLM
            response = self._call_llm()
            
            # Check if tool calls are needed
            if response.tool_calls:
                # Execute tools
                tool_results = self._execute_tools(response.tool_calls)
                response.tool_results = tool_results
                self.messages.append(response)
                
                # Add tool results as message
                tool_message = Message(
                    role="tool",
                    content=json.dumps(tool_results, default=str)
                )
                self.messages.append(tool_message)
                
                # Continue loop to let LLM process results
                continue
            else:
                # No more tool calls, final response
                self.messages.append(response)
                return response.content
        
        # Max iterations reached
        return "Analysis incomplete: maximum iteration limit reached. Please refine your query."
    
    def _call_llm(self) -> Message:
        """Call the LLM with current conversation"""
        if self.config.provider == "bedrock":
            return self._call_bedrock()
        elif self.config.provider == "openai":
            return self._call_openai()
    
    def _call_bedrock(self) -> Message:
        """Call AWS Bedrock Claude"""
        # Convert messages to Bedrock format
        system_msg = next((m.content for m in self.messages if m.role == "system"), "")
        conversation = [
            {"role": m.role, "content": m.content}
            for m in self.messages
            if m.role in ["user", "assistant"]
        ]
        
        # Prepare tool definitions
        tools = [tool["definition"] for tool in self.tools.values()]
        
        # Call Bedrock
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": system_msg,
            "messages": conversation,
        }
        
        if tools:
            request_body["tools"] = tools
        
        try:
            response = self.client.invoke_model(
                modelId=self.config.model,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract response
            content = response_body.get("content", [])
            text_content = ""
            tool_calls = []
            
            for item in content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")
                elif item.get("type") == "tool_use":
                    tool_calls.append({
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "arguments": item.get("input", {})
                    })
            
            return Message(
                role="assistant",
                content=text_content,
                tool_calls=tool_calls if tool_calls else None
            )
        
        except Exception as e:
            error_msg = f"Bedrock API error: {str(e)}"
            if self.config.verbose:
                print(f"✗ {error_msg}")
            return Message(role="assistant", content=error_msg)
    
    def _call_openai(self) -> Message:
        """Call OpenAI GPT"""
        # Convert messages to OpenAI format
        messages = [
            {"role": m.role, "content": m.content}
            for m in self.messages
            if m.role in ["system", "user", "assistant"]
        ]
        
        # Prepare tool definitions
        tools = [
            {"type": "function", "function": tool["definition"]}
            for tool in self.tools.values()
        ]
        
        try:
            kwargs = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
            }
            
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            response = self.client.chat.completions.create(**kwargs)
            
            message = response.choices[0].message
            
            # Extract tool calls if any
            tool_calls = None
            if message.tool_calls:
                tool_calls = [
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments)
                    }
                    for tc in message.tool_calls
                ]
            
            return Message(
                role="assistant",
                content=message.content or "",
                tool_calls=tool_calls
            )
        
        except Exception as e:
            error_msg = f"OpenAI API error: {str(e)}"
            if self.config.verbose:
                print(f"✗ {error_msg}")
            return Message(role="assistant", content=error_msg)
    
    def _execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
        """Execute requested tool calls"""
        results = []
        
        for call in tool_calls:
            tool_name = call["name"]
            tool_args = call["arguments"]
            
            if tool_name not in self.tools:
                result = {"error": f"Tool '{tool_name}' not found"}
            else:
                try:
                    if self.config.verbose:
                        print(f"  Calling tool: {tool_name}")
                        print(f"    Args: {tool_args}")
                    
                    func = self.tools[tool_name]["function"]
                    result = func(**tool_args)
                    
                    if self.config.verbose:
                        print(f"  ✓ Tool executed successfully")
                
                except Exception as e:
                    result = {"error": str(e)}
                    if self.config.verbose:
                        print(f"  ✗ Tool error: {e}")
            
            results.append({
                "tool_call_id": call.get("id"),
                "tool_name": tool_name,
                "result": result
            })
        
        return results
    
    def analyze_market(self, symbols: List[str], analysis_type: str = "comprehensive") -> str:
        """
        Perform market analysis on given symbols
        
        Args:
            symbols: List of ticker symbols
            analysis_type: 'comprehensive', 'technical', 'fundamental', 'risk'
        
        Returns:
            Analysis report
        """
        prompt = f"""Analyze the following stocks: {', '.join(symbols)}

Analysis type: {analysis_type}

Please provide:
1. Current market regime assessment
2. Individual stock analysis (fundamentals, technicals, risk)
3. Sector and diversification analysis
4. Risk metrics (Beta, volatility, correlations)
5. Investment recommendation with rationale

Use the available tools to fetch data and perform calculations."""
        
        return self.chat(prompt)
    
    def develop_strategy(self, strategy_idea: str, universe: List[str]) -> str:
        """
        Develop and backtest a trading strategy
        
        Args:
            strategy_idea: Description of strategy logic
            universe: Stock universe to test on
        
        Returns:
            Strategy development report
        """
        prompt = f"""Develop and backtest the following strategy:

Strategy: {strategy_idea}
Universe: {', '.join(universe)}

Please:
1. Formalize the strategy logic and entry/exit rules
2. Backtest on historical data with realistic assumptions
3. Calculate performance metrics (Sharpe, Sortino, Max DD, Win Rate)
4. Analyze transaction costs and slippage impact
5. Perform sensitivity analysis on key parameters
6. Provide risk assessment and recommendations

Use the backtesting tools available."""
        
        return self.chat(prompt)
    
    def optimize_portfolio(self, symbols: List[str], objective: str = "sharpe") -> str:
        """
        Optimize portfolio allocation
        
        Args:
            symbols: List of ticker symbols
            objective: 'sharpe', 'min_variance', 'max_return', 'risk_parity'
        
        Returns:
            Portfolio optimization report
        """
        prompt = f"""Optimize portfolio allocation for: {', '.join(symbols)}

Objective: {objective}

Please:
1. Fetch historical returns and calculate covariance matrix
2. Run portfolio optimization (Modern Portfolio Theory)
3. Generate efficient frontier
4. Provide recommended allocation with rationale
5. Calculate portfolio risk metrics (VaR, CVaR, Beta)
6. Suggest rebalancing strategy

Use portfolio optimization tools."""
        
        return self.chat(prompt)
    
    def risk_report(self, portfolio: Dict[str, float]) -> str:
        """
        Generate comprehensive risk report
        
        Args:
            portfolio: Dict of {symbol: weight}
        
        Returns:
            Risk analysis report
        """
        symbols_str = ", ".join([f"{s} ({w:.1%})" for s, w in portfolio.items()])
        
        prompt = f"""Generate a comprehensive risk report for this portfolio:

{symbols_str}

Please analyze:
1. Portfolio-level risk metrics (VaR, CVaR, volatility, max drawdown)
2. Stress testing (2008 crisis, 2020 COVID, rising rates scenario)
3. Factor exposure (market beta, size, value, momentum)
4. Correlation analysis and diversification benefits
5. Tail risk assessment
6. Hedging recommendations

Use risk analysis tools."""
        
        return self.chat(prompt)
    
    def save_conversation(self, filepath: str):
        """Save conversation history to file"""
        data = {
            "config": {
                "provider": self.config.provider,
                "model": self.config.model,
                "timestamp": datetime.now().isoformat()
            },
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                    "tool_calls": m.tool_calls,
                    "tool_results": m.tool_results
                }
                for m in self.messages
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"✓ Conversation saved to {filepath}")
    
    def load_conversation(self, filepath: str):
        """Load conversation history from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.messages = [
            Message(
                role=m["role"],
                content=m["content"],
                timestamp=datetime.fromisoformat(m["timestamp"]),
                tool_calls=m.get("tool_calls"),
                tool_results=m.get("tool_results")
            )
            for m in data["messages"]
        ]
        
        print(f"✓ Conversation loaded from {filepath}")


# Convenience function for quick initialization
def create_agent(provider: str = "bedrock", model: Optional[str] = None, **kwargs) -> QuantAgent:
    """
    Create a quant agent with sensible defaults
    
    Args:
        provider: 'bedrock' or 'openai'
        model: Model name (optional, uses defaults)
        **kwargs: Additional config options
    
    Returns:
        Initialized QuantAgent
    
    Example:
        >>> agent = create_agent(provider="bedrock")
        >>> agent.chat("What's the current market regime?")
    """
    config = AgentConfig(provider=provider, **kwargs)
    if model:
        config.model = model
    return QuantAgent(config)


if __name__ == "__main__":
    # Example usage
    print("AI Quant Agent - Example Usage")
    print("=" * 80)
    
    # Create agent
    agent = create_agent(provider="bedrock", verbose=True)
    
    # Example analysis
    response = agent.analyze_market(
        symbols=["AAPL", "GOOGL", "MSFT"],
        analysis_type="comprehensive"
    )
    print("\n" + "=" * 80)
    print("ANALYSIS RESULT:")
    print("=" * 80)
    print(response)
