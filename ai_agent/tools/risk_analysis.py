"""
Risk Analysis Tools
==================

Tools for portfolio risk analysis including VaR, CVaR, stress testing, and correlation analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta


def calculate_var_cvar(
    returns: List[float],
    confidence_level: float = 0.95
) -> Dict:
    """
    Calculate Value at Risk (VaR) and Conditional VaR (CVaR)
    
    Args:
        returns: List of returns
        confidence_level: Confidence level (default 0.95 for 95%)
    
    Returns:
        VaR and CVaR metrics
    
    Tool Definition:
        name: calculate_var_cvar
        description: Calculate Value at Risk and Conditional Value at Risk (Expected Shortfall)
        parameters:
            returns: array - list of returns
            confidence_level: number - confidence level (0.95 for 95%)
    """
    try:
        returns_array = np.array(returns)
        var = np.percentile(returns_array, (1 - confidence_level) * 100)
        cvar = returns_array[returns_array <= var].mean()
        
        return {
            'var': float(var),
            'cvar': float(cvar),
            'confidence_level': confidence_level,
            'interpretation': f"{confidence_level*100}% of the time, losses will not exceed {abs(var)*100:.2f}%"
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_portfolio_beta(
    portfolio_returns: List[float],
    market_returns: List[float]
) -> Dict:
    """
    Calculate portfolio beta relative to market
    
    Args:
        portfolio_returns: Portfolio returns
        market_returns: Market benchmark returns (e.g., S&P 500)
    
    Returns:
        Beta and alpha metrics
    
    Tool Definition:
        name: calculate_portfolio_beta
        description: Calculate portfolio beta and alpha relative to market benchmark (CAPM)
        parameters:
            portfolio_returns: array - portfolio returns
            market_returns: array - market benchmark returns
    """
    try:
        port_ret = np.array(portfolio_returns)
        mkt_ret = np.array(market_returns)
        
        # Ensure same length
        min_len = min(len(port_ret), len(mkt_ret))
        port_ret = port_ret[:min_len]
        mkt_ret = mkt_ret[:min_len]
        
        # Calculate beta
        covariance = np.cov(port_ret, mkt_ret)[0, 1]
        market_variance = np.var(mkt_ret)
        beta = covariance / market_variance if market_variance > 0 else 0
        
        # Calculate alpha
        portfolio_return = np.mean(port_ret) * 252  # Annualized
        market_return = np.mean(mkt_ret) * 252
        risk_free_rate = 0.04  # Assume 4%
        
        expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
        alpha = portfolio_return - expected_return
        
        return {
            'beta': float(beta),
            'alpha': float(alpha),
            'correlation': float(np.corrcoef(port_ret, mkt_ret)[0, 1]),
            'interpretation': f"Portfolio is {abs(beta - 1)*100:.1f}% {'more' if beta > 1 else 'less'} volatile than market"
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_correlation_matrix(
    symbols: List[str],
    period: str = "1y"
) -> Dict:
    """
    Calculate correlation matrix for a list of symbols
    
    Args:
        symbols: List of ticker symbols
        period: Time period for calculation
    
    Returns:
        Correlation matrix and diversification metrics
    
    Tool Definition:
        name: calculate_correlation_matrix
        description: Calculate correlation matrix and diversification metrics for portfolio holdings
        parameters:
            symbols: array - list of ticker symbols
            period: string - time period (1mo, 3mo, 6mo, 1y, 2y, 5y)
    """
    try:
        from .market_data import get_price_history
        
        # Fetch price data
        prices_data = get_price_history(symbols, period=period)
        
        # Calculate returns for each symbol
        returns_dict = {}
        for symbol in symbols:
            if symbol in prices_data and not isinstance(prices_data[symbol], dict):
                prices = prices_data[symbol]['Close']
                returns = prices.pct_change().dropna()
                returns_dict[symbol] = returns
        
        # Create returns dataframe
        returns_df = pd.DataFrame(returns_dict)
        
        # Calculate correlation matrix
        corr_matrix = returns_df.corr()
        
        # Calculate average correlation (excluding diagonal)
        mask = np.triu(np.ones_like(corr_matrix), k=1).astype(bool)
        avg_correlation = corr_matrix.where(mask).stack().mean()
        
        # Find highly correlated pairs (>0.7)
        high_corr_pairs = []
        for i in range(len(corr_matrix)):
            for j in range(i+1, len(corr_matrix)):
                if corr_matrix.iloc[i, j] > 0.7:
                    high_corr_pairs.append({
                        'symbol1': corr_matrix.index[i],
                        'symbol2': corr_matrix.columns[j],
                        'correlation': float(corr_matrix.iloc[i, j])
                    })
        
        # Diversification assessment
        if avg_correlation < 0.3:
            diversification = "Excellent"
        elif avg_correlation < 0.5:
            diversification = "Good"
        elif avg_correlation < 0.7:
            diversification = "Moderate"
        else:
            diversification = "Poor"
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'average_correlation': float(avg_correlation),
            'high_correlation_pairs': high_corr_pairs,
            'diversification_assessment': diversification,
            'interpretation': f"Average correlation of {avg_correlation:.2f} indicates {diversification.lower()} diversification"
        }
    
    except Exception as e:
        return {"error": str(e)}


def stress_test_portfolio(
    symbols: List[str],
    weights: List[float],
    scenario: str = "2008_crisis"
) -> Dict:
    """
    Perform stress testing on portfolio
    
    Args:
        symbols: List of ticker symbols
        weights: Portfolio weights for each symbol
        scenario: Stress scenario ('2008_crisis', '2020_covid', 'rising_rates', 'custom')
    
    Returns:
        Stress test results
    
    Tool Definition:
        name: stress_test_portfolio
        description: Perform stress testing on portfolio using historical crisis scenarios
        parameters:
            symbols: array - list of ticker symbols
            weights: array - portfolio weights (must sum to 1.0)
            scenario: string - stress scenario (2008_crisis, 2020_covid, rising_rates)
    """
    try:
        from .market_data import get_price_history
        
        # Define stress scenarios
        scenarios = {
            '2008_crisis': {
                'start_date': '2008-09-01',
                'end_date': '2009-03-01',
                'name': '2008 Financial Crisis'
            },
            '2020_covid': {
                'start_date': '2020-02-01',
                'end_date': '2020-04-01',
                'name': 'COVID-19 Market Crash'
            },
            'rising_rates': {
                'start_date': '2022-01-01',
                'end_date': '2022-12-31',
                'name': '2022 Rising Rates Environment'
            }
        }
        
        if scenario not in scenarios:
            return {"error": f"Unknown scenario: {scenario}"}
        
        scenario_config = scenarios[scenario]
        
        # Fetch historical data for scenario period
        prices_data = get_price_history(
            symbols,
            start_date=scenario_config['start_date'],
            end_date=scenario_config['end_date']
        )
        
        # Calculate returns during stress period
        portfolio_returns = []
        for symbol, weight in zip(symbols, weights):
            if symbol in prices_data and not isinstance(prices_data[symbol], dict):
                prices = prices_data[symbol]['Close']
                total_return = (prices.iloc[-1] / prices.iloc[0] - 1)
                portfolio_returns.append(total_return * weight)
        
        portfolio_stress_return = sum(portfolio_returns)
        
        # Calculate max drawdown during period
        portfolio_values = [1.0]  # Start at 1
        for symbol, weight in zip(symbols, weights):
            if symbol in prices_data and not isinstance(prices_data[symbol], dict):
                prices = prices_data[symbol]['Close']
                normalized = prices / prices.iloc[0]
                # Weight contribution
                # (Simplified - assumes daily rebalancing)
        
        return {
            'scenario': scenario_config['name'],
            'period': f"{scenario_config['start_date']} to {scenario_config['end_date']}",
            'portfolio_return': float(portfolio_stress_return),
            'interpretation': f"Portfolio would have {'gained' if portfolio_stress_return > 0 else 'lost'} {abs(portfolio_stress_return)*100:.2f}% during {scenario_config['name']}",
            'recommendation': "Consider hedging strategies if downside risk is unacceptable" if portfolio_stress_return < -0.20 else "Portfolio showed resilience"
        }
    
    except Exception as e:
        return {"error": str(e)}


# Tool registration
TOOLS = {
    "calculate_var_cvar": {
        "function": calculate_var_cvar,
        "description": "Calculate Value at Risk (VaR) and Conditional Value at Risk (CVaR/Expected Shortfall) for risk assessment",
        "parameters": {
            "type": "object",
            "properties": {
                "returns": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of returns"
                },
                "confidence_level": {
                    "type": "number",
                    "description": "Confidence level (default 0.95)"
                }
            },
            "required": ["returns"]
        }
    },
    "calculate_portfolio_beta": {
        "function": calculate_portfolio_beta,
        "description": "Calculate portfolio beta and alpha using CAPM framework",
        "parameters": {
            "type": "object",
            "properties": {
                "portfolio_returns": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Portfolio returns"
                },
                "market_returns": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Market benchmark returns (e.g., S&P 500)"
                }
            },
            "required": ["portfolio_returns", "market_returns"]
        }
    },
    "calculate_correlation_matrix": {
        "function": calculate_correlation_matrix,
        "description": "Calculate correlation matrix and identify diversification level and highly correlated holdings",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ticker symbols"
                },
                "period": {
                    "type": "string",
                    "enum": ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
                    "description": "Time period for calculation"
                }
            },
            "required": ["symbols"]
        }
    },
    "stress_test_portfolio": {
        "function": stress_test_portfolio,
        "description": "Stress test portfolio using historical crisis scenarios (2008 crisis, 2020 COVID, rising rates)",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ticker symbols"
                },
                "weights": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Portfolio weights (must sum to 1.0)"
                },
                "scenario": {
                    "type": "string",
                    "enum": ["2008_crisis", "2020_covid", "rising_rates"],
                    "description": "Stress test scenario"
                }
            },
            "required": ["symbols", "weights", "scenario"]
        }
    }
}
