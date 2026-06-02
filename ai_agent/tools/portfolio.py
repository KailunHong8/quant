"""
Portfolio Management Tools
=========================

Tools for portfolio optimization, allocation, and rebalancing using Modern Portfolio Theory.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime


def optimize_portfolio(
    symbols: List[str],
    objective: str = "sharpe",
    constraints: Optional[Dict] = None,
    period: str = "2y"
) -> Dict:
    """
    Optimize portfolio allocation using Modern Portfolio Theory
    
    Args:
        symbols: List of ticker symbols
        objective: Optimization objective ('sharpe', 'min_variance', 'max_return', 'risk_parity')
        constraints: Optional constraints (e.g., max_weight, sector_limits)
        period: Historical period for calculation
    
    Returns:
        Optimal portfolio weights and metrics
    
    Tool Definition:
        name: optimize_portfolio
        description: Optimize portfolio allocation using MPT (Mean-Variance Optimization)
        parameters:
            symbols: array - list of ticker symbols
            objective: string - optimization goal (sharpe, min_variance, max_return, risk_parity)
            constraints: object - optional constraints
            period: string - historical period for calculation
    """
    try:
        from .market_data import get_price_history
        
        # Fetch price data
        prices_data = get_price_history(symbols, period=period)
        
        # Calculate returns
        returns_dict = {}
        for symbol in symbols:
            if symbol in prices_data and not isinstance(prices_data[symbol], dict):
                prices = prices_data[symbol]['Close']
                returns = prices.pct_change().dropna()
                returns_dict[symbol] = returns
        
        returns_df = pd.DataFrame(returns_dict)
        
        # Calculate mean returns and covariance matrix
        mean_returns = returns_df.mean() * 252  # Annualized
        cov_matrix = returns_df.cov() * 252  # Annualized
        
        # Number of assets
        n_assets = len(symbols)
        
        # Optimization based on objective
        if objective == "sharpe":
            # Maximize Sharpe ratio
            weights = _optimize_sharpe(mean_returns, cov_matrix, constraints)
        
        elif objective == "min_variance":
            # Minimize portfolio variance
            weights = _optimize_min_variance(cov_matrix, constraints)
        
        elif objective == "max_return":
            # Maximize return for given risk level
            weights = _optimize_max_return(mean_returns, cov_matrix, constraints)
        
        elif objective == "risk_parity":
            # Risk parity allocation
            weights = _risk_parity_weights(cov_matrix)
        
        else:
            return {"error": f"Unknown objective: {objective}"}
        
        # Calculate portfolio metrics
        portfolio_return = np.dot(weights, mean_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - 0.04) / portfolio_volatility  # Assuming 4% risk-free rate
        
        # Format results
        allocation = {
            symbol: float(weight)
            for symbol, weight in zip(symbols, weights)
        }
        
        return {
            'allocation': allocation,
            'expected_return': float(portfolio_return),
            'expected_volatility': float(portfolio_volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'objective': objective,
            'interpretation': f"Optimized for {objective}: {portfolio_return*100:.2f}% return, {portfolio_volatility*100:.2f}% vol, {sharpe_ratio:.2f} Sharpe"
        }
    
    except Exception as e:
        return {"error": str(e)}


def _optimize_sharpe(mean_returns, cov_matrix, constraints):
    """Optimize for maximum Sharpe ratio"""
    n_assets = len(mean_returns)
    
    # Simple equal weight as fallback
    # For production, use scipy.optimize
    try:
        from scipy.optimize import minimize
        
        def neg_sharpe(weights):
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (portfolio_return - 0.04) / portfolio_volatility
            return -sharpe
        
        # Constraints: weights sum to 1
        constraints_opt = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        
        # Bounds: 0 <= weight <= 1
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess: equal weight
        init_guess = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            neg_sharpe,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_opt
        )
        
        return result.x
    
    except ImportError:
        # Fallback to equal weight
        return np.array([1/n_assets] * n_assets)


def _optimize_min_variance(cov_matrix, constraints):
    """Optimize for minimum variance"""
    n_assets = len(cov_matrix)
    
    try:
        from scipy.optimize import minimize
        
        def portfolio_variance(weights):
            return np.dot(weights.T, np.dot(cov_matrix, weights))
        
        constraints_opt = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        init_guess = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            portfolio_variance,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_opt
        )
        
        return result.x
    
    except ImportError:
        return np.array([1/n_assets] * n_assets)


def _optimize_max_return(mean_returns, cov_matrix, constraints):
    """Optimize for maximum return given risk tolerance"""
    # For simplicity, weight by returns (not optimal but reasonable)
    weights = mean_returns / mean_returns.sum()
    return np.array(weights)


def _risk_parity_weights(cov_matrix):
    """Calculate risk parity weights"""
    n_assets = len(cov_matrix)
    
    # Start with equal risk contribution
    # Inverse volatility weighting as approximation
    volatilities = np.sqrt(np.diag(cov_matrix))
    weights = 1 / volatilities
    weights = weights / weights.sum()
    
    return weights


def generate_efficient_frontier(
    symbols: List[str],
    num_portfolios: int = 50,
    period: str = "2y"
) -> Dict:
    """
    Generate efficient frontier
    
    Args:
        symbols: List of ticker symbols
        num_portfolios: Number of portfolio points to generate
        period: Historical period for calculation
    
    Returns:
        Efficient frontier data
    
    Tool Definition:
        name: generate_efficient_frontier
        description: Generate efficient frontier showing risk-return tradeoffs
        parameters:
            symbols: array - list of ticker symbols
            num_portfolios: number - number of portfolio points (default 50)
            period: string - historical period
    """
    try:
        from .market_data import get_price_history
        
        # Fetch price data
        prices_data = get_price_history(symbols, period=period)
        
        # Calculate returns
        returns_dict = {}
        for symbol in symbols:
            if symbol in prices_data and not isinstance(prices_data[symbol], dict):
                prices = prices_data[symbol]['Close']
                returns = prices.pct_change().dropna()
                returns_dict[symbol] = returns
        
        returns_df = pd.DataFrame(returns_dict)
        mean_returns = returns_df.mean() * 252
        cov_matrix = returns_df.cov() * 252
        
        # Generate random portfolios
        n_assets = len(symbols)
        results = []
        
        for _ in range(num_portfolios):
            # Random weights
            weights = np.random.random(n_assets)
            weights /= weights.sum()
            
            # Calculate metrics
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (portfolio_return - 0.04) / portfolio_volatility
            
            results.append({
                'return': float(portfolio_return),
                'volatility': float(portfolio_volatility),
                'sharpe': float(sharpe),
                'weights': weights.tolist()
            })
        
        # Sort by volatility
        results.sort(key=lambda x: x['volatility'])
        
        return {
            'portfolios': results,
            'num_portfolios': len(results),
            'interpretation': f"Generated {len(results)} portfolio combinations showing risk-return tradeoff"
        }
    
    except Exception as e:
        return {"error": str(e)}


def calculate_rebalancing_needs(
    current_allocation: Dict[str, float],
    target_allocation: Dict[str, float],
    threshold: float = 0.05
) -> Dict:
    """
    Calculate portfolio rebalancing needs
    
    Args:
        current_allocation: Current portfolio weights {symbol: weight}
        target_allocation: Target portfolio weights {symbol: weight}
        threshold: Rebalancing threshold (default 5%)
    
    Returns:
        Rebalancing recommendations
    
    Tool Definition:
        name: calculate_rebalancing_needs
        description: Calculate how much to buy/sell to rebalance portfolio to target allocation
        parameters:
            current_allocation: object - current weights {symbol: weight}
            target_allocation: object - target weights {symbol: weight}
            threshold: number - rebalancing threshold (default 0.05)
    """
    try:
        rebalancing_actions = []
        
        all_symbols = set(list(current_allocation.keys()) + list(target_allocation.keys()))
        
        for symbol in all_symbols:
            current_weight = current_allocation.get(symbol, 0)
            target_weight = target_allocation.get(symbol, 0)
            difference = target_weight - current_weight
            
            if abs(difference) > threshold:
                action = "buy" if difference > 0 else "sell"
                rebalancing_actions.append({
                    'symbol': symbol,
                    'current_weight': float(current_weight),
                    'target_weight': float(target_weight),
                    'difference': float(difference),
                    'action': action,
                    'amount': abs(float(difference))
                })
        
        needs_rebalancing = len(rebalancing_actions) > 0
        
        return {
            'needs_rebalancing': needs_rebalancing,
            'actions': rebalancing_actions,
            'num_actions': len(rebalancing_actions),
            'interpretation': f"{'Rebalancing recommended' if needs_rebalancing else 'Portfolio is within tolerance'}: {len(rebalancing_actions)} positions need adjustment"
        }
    
    except Exception as e:
        return {"error": str(e)}


# Tool registration
TOOLS = {
    "optimize_portfolio": {
        "function": optimize_portfolio,
        "description": "Optimize portfolio allocation using Modern Portfolio Theory (MPT). Supports multiple objectives: maximize Sharpe ratio, minimize variance, maximize return, or risk parity.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ticker symbols"
                },
                "objective": {
                    "type": "string",
                    "enum": ["sharpe", "min_variance", "max_return", "risk_parity"],
                    "description": "Optimization objective"
                },
                "constraints": {
                    "type": "object",
                    "description": "Optional constraints (e.g., max_weight per position)"
                },
                "period": {
                    "type": "string",
                    "enum": ["1y", "2y", "3y", "5y"],
                    "description": "Historical period for calculation"
                }
            },
            "required": ["symbols"]
        }
    },
    "generate_efficient_frontier": {
        "function": generate_efficient_frontier,
        "description": "Generate efficient frontier showing optimal risk-return combinations",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ticker symbols"
                },
                "num_portfolios": {
                    "type": "number",
                    "description": "Number of portfolio points to generate (default 50)"
                },
                "period": {
                    "type": "string",
                    "description": "Historical period for calculation"
                }
            },
            "required": ["symbols"]
        }
    },
    "calculate_rebalancing_needs": {
        "function": calculate_rebalancing_needs,
        "description": "Calculate rebalancing actions needed to align portfolio with target allocation",
        "parameters": {
            "type": "object",
            "properties": {
                "current_allocation": {
                    "type": "object",
                    "description": "Current portfolio weights {symbol: weight}"
                },
                "target_allocation": {
                    "type": "object",
                    "description": "Target portfolio weights {symbol: weight}"
                },
                "threshold": {
                    "type": "number",
                    "description": "Rebalancing threshold (default 0.05 for 5%)"
                }
            },
            "required": ["current_allocation", "target_allocation"]
        }
    }
}
