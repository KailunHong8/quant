"""
Backtesting Tools
=================

Tools for backtesting trading strategies with realistic assumptions.
Includes transaction costs, slippage, and position sizing.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Callable


def simple_backtest(
    symbols: List[str],
    start_date: str,
    end_date: str,
    strategy_signals: Dict[str, List[int]],
    initial_capital: float = 100000,
    transaction_cost_bps: float = 5.0,
    slippage_bps: float = 2.0
) -> Dict:
    """
    Run a simple backtest with buy/sell signals
    
    Args:
        symbols: List of symbols to trade
        start_date: Start date YYYY-MM-DD
        end_date: End date YYYY-MM-DD
        strategy_signals: Dict of {symbol: [signals]} where 1=buy, -1=sell, 0=hold
        initial_capital: Starting capital
        transaction_cost_bps: Transaction cost in basis points
        slippage_bps: Slippage in basis points
    
    Returns:
        Backtest results with metrics
    
    Tool Definition:
        name: simple_backtest
        description: Backtest a trading strategy with realistic transaction costs and slippage
        parameters:
            symbols: array - list of ticker symbols
            start_date: string - start date YYYY-MM-DD
            end_date: string - end date YYYY-MM-DD
            strategy_signals: object - signals for each symbol (1=buy, -1=sell, 0=hold)
            initial_capital: number - starting capital (default 100000)
            transaction_cost_bps: number - transaction cost in basis points (default 5)
            slippage_bps: number - slippage in basis points (default 2)
    """
    try:
        from .market_data import get_price_history
        
        # Fetch price data
        prices_data = get_price_history(symbols, start_date=start_date, end_date=end_date)
        
        # Initialize portfolio
        portfolio = {
            'cash': initial_capital,
            'positions': {symbol: 0 for symbol in symbols},
            'value_history': [],
            'dates': []
        }
        
        # Get all dates
        first_symbol = symbols[0]
        if isinstance(prices_data[first_symbol], dict) and 'error' in prices_data[first_symbol]:
            return {"error": f"Failed to fetch data: {prices_data[first_symbol]['error']}"}
        
        dates = prices_data[first_symbol].index
        
        # Run backtest
        for date in dates:
            current_prices = {}
            for symbol in symbols:
                if symbol in prices_data and not isinstance(prices_data[symbol], dict):
                    if date in prices_data[symbol].index:
                        current_prices[symbol] = prices_data[symbol].loc[date, 'Close']
            
            # Execute trades based on signals
            for symbol in symbols:
                if symbol not in strategy_signals:
                    continue
                
                signal_idx = len(portfolio['dates'])
                if signal_idx >= len(strategy_signals[symbol]):
                    continue
                
                signal = strategy_signals[symbol][signal_idx]
                current_price = current_prices.get(symbol)
                
                if current_price is None:
                    continue
                
                # Apply slippage
                if signal > 0:  # Buy
                    execution_price = current_price * (1 + slippage_bps / 10000)
                elif signal < 0:  # Sell
                    execution_price = current_price * (1 - slippage_bps / 10000)
                else:
                    continue
                
                # Calculate trade size (equal weight)
                target_position_value = portfolio['cash'] / len(symbols)
                current_position = portfolio['positions'][symbol]
                
                if signal > 0 and current_position == 0:  # Buy
                    shares = int(target_position_value / execution_price)
                    cost = shares * execution_price
                    transaction_fee = cost * (transaction_cost_bps / 10000)
                    total_cost = cost + transaction_fee
                    
                    if portfolio['cash'] >= total_cost:
                        portfolio['cash'] -= total_cost
                        portfolio['positions'][symbol] = shares
                
                elif signal < 0 and current_position > 0:  # Sell
                    shares = current_position
                    proceeds = shares * execution_price
                    transaction_fee = proceeds * (transaction_cost_bps / 10000)
                    net_proceeds = proceeds - transaction_fee
                    
                    portfolio['cash'] += net_proceeds
                    portfolio['positions'][symbol] = 0
            
            # Calculate portfolio value
            portfolio_value = portfolio['cash']
            for symbol, shares in portfolio['positions'].items():
                if symbol in current_prices:
                    portfolio_value += shares * current_prices[symbol]
            
            portfolio['value_history'].append(portfolio_value)
            portfolio['dates'].append(date)
        
        # Calculate metrics
        returns = pd.Series(portfolio['value_history']).pct_change().dropna()
        
        total_return = (portfolio['value_history'][-1] / initial_capital - 1)
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        win_rate = (returns > 0).sum() / len(returns) if len(returns) > 0 else 0
        
        return {
            'initial_capital': initial_capital,
            'final_value': portfolio['value_history'][-1],
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'num_trades': sum(len([s for s in strategy_signals.get(sym, []) if s != 0]) for sym in symbols),
            'value_history': portfolio['value_history'],
            'dates': [str(d.date()) for d in portfolio['dates']]
        }
    
    except Exception as e:
        return {"error": str(e)}


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.04) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: List of returns
        risk_free_rate: Annual risk-free rate (default 4%)
    
    Returns:
        Sharpe ratio
    
    Tool Definition:
        name: calculate_sharpe_ratio
        description: Calculate Sharpe ratio (risk-adjusted return)
        parameters:
            returns: array - list of period returns
            risk_free_rate: number - annual risk-free rate (default 0.04)
    """
    try:
        returns_array = np.array(returns)
        excess_returns = returns_array - (risk_free_rate / 252)  # Daily risk-free rate
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return float(sharpe)
    except Exception as e:
        return {"error": str(e)}


def calculate_max_drawdown(equity_curve: List[float]) -> Dict:
    """
    Calculate maximum drawdown
    
    Args:
        equity_curve: List of portfolio values over time
    
    Returns:
        Max drawdown metrics
    
    Tool Definition:
        name: calculate_max_drawdown
        description: Calculate maximum drawdown and drawdown duration
        parameters:
            equity_curve: array - portfolio values over time
    """
    try:
        values = np.array(equity_curve)
        running_max = np.maximum.accumulate(values)
        drawdown = (values - running_max) / running_max
        max_dd = drawdown.min()
        
        # Find drawdown duration
        in_drawdown = drawdown < 0
        if np.any(in_drawdown):
            dd_periods = []
            current_period = 0
            for is_dd in in_drawdown:
                if is_dd:
                    current_period += 1
                else:
                    if current_period > 0:
                        dd_periods.append(current_period)
                    current_period = 0
            if current_period > 0:
                dd_periods.append(current_period)
            
            max_dd_duration = max(dd_periods) if dd_periods else 0
        else:
            max_dd_duration = 0
        
        return {
            'max_drawdown': float(max_dd),
            'max_drawdown_duration': int(max_dd_duration),
            'current_drawdown': float(drawdown[-1])
        }
    
    except Exception as e:
        return {"error": str(e)}


# Tool registration
TOOLS = {
    "simple_backtest": {
        "function": simple_backtest,
        "description": "Backtest a trading strategy with realistic transaction costs and slippage. Requires buy/sell signals for each symbol over the period.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ticker symbols to trade"
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date YYYY-MM-DD"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date YYYY-MM-DD"
                },
                "strategy_signals": {
                    "type": "object",
                    "description": "Dict of {symbol: [signals]} where 1=buy, -1=sell, 0=hold for each period"
                },
                "initial_capital": {
                    "type": "number",
                    "description": "Starting capital (default 100000)"
                },
                "transaction_cost_bps": {
                    "type": "number",
                    "description": "Transaction cost in basis points (default 5)"
                },
                "slippage_bps": {
                    "type": "number",
                    "description": "Slippage in basis points (default 2)"
                }
            },
            "required": ["symbols", "start_date", "end_date", "strategy_signals"]
        }
    },
    "calculate_sharpe_ratio": {
        "function": calculate_sharpe_ratio,
        "description": "Calculate Sharpe ratio for risk-adjusted return measurement",
        "parameters": {
            "type": "object",
            "properties": {
                "returns": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of period returns"
                },
                "risk_free_rate": {
                    "type": "number",
                    "description": "Annual risk-free rate (default 0.04)"
                }
            },
            "required": ["returns"]
        }
    },
    "calculate_max_drawdown": {
        "function": calculate_max_drawdown,
        "description": "Calculate maximum drawdown, drawdown duration, and current drawdown from equity curve",
        "parameters": {
            "type": "object",
            "properties": {
                "equity_curve": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Portfolio values over time"
                }
            },
            "required": ["equity_curve"]
        }
    }
}
