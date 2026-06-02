"""
Technical Analysis Tools
=======================

Tools for technical indicators and chart pattern analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional


def calculate_moving_averages(
    symbol: str,
    periods: List[int] = [20, 50, 200],
    period: str = "1y"
) -> Dict:
    """
    Calculate moving averages for technical analysis
    
    Args:
        symbol: Ticker symbol
        periods: List of MA periods (default [20, 50, 200])
        period: Historical period to analyze
    
    Returns:
        Moving average values and crossover signals
    
    Tool Definition:
        name: calculate_moving_averages
        description: Calculate simple moving averages and identify crossover signals
        parameters:
            symbol: string - ticker symbol
            periods: array - MA periods (default [20, 50, 200])
            period: string - historical period
    """
    try:
        from .market_data import get_price_history
        
        # Fetch price data
        prices_data = get_price_history(symbol, period=period)
        
        if isinstance(prices_data[symbol], dict) and 'error' in prices_data[symbol]:
            return prices_data[symbol]
        
        prices = prices_data[symbol]['Close']
        
        # Calculate MAs
        mas = {}
        for p in periods:
            ma = prices.rolling(window=p).mean()
            mas[f'MA{p}'] = float(ma.iloc[-1]) if not ma.empty else None
        
        current_price = float(prices.iloc[-1])
        
        # Detect crossovers and trends
        signals = []
        
        # Golden cross / Death cross (50 vs 200 MA)
        if 50 in periods and 200 in periods:
            ma50 = prices.rolling(window=50).mean()
            ma200 = prices.rolling(window=200).mean()
            
            if not ma50.empty and not ma200.empty:
                # Check if recent crossover occurred
                if ma50.iloc[-1] > ma200.iloc[-1] and ma50.iloc[-5] < ma200.iloc[-5]:
                    signals.append("Golden Cross: 50 MA crossed above 200 MA (bullish)")
                elif ma50.iloc[-1] < ma200.iloc[-1] and ma50.iloc[-5] > ma200.iloc[-5]:
                    signals.append("Death Cross: 50 MA crossed below 200 MA (bearish)")
        
        # Price vs MA trend
        for p in periods:
            ma = prices.rolling(window=p).mean()
            if not ma.empty:
                ma_val = ma.iloc[-1]
                if current_price > ma_val:
                    signals.append(f"Price above {p} MA (bullish)")
                else:
                    signals.append(f"Price below {p} MA (bearish)")
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'moving_averages': mas,
            'signals': signals,
            'interpretation': "Bullish trend" if current_price > mas.get('MA200', 0) else "Bearish trend"
        }
    
    except Exception as e:
        return {"error": str(e)}


def calculate_rsi(
    symbol: str,
    period: int = 14,
    timeframe: str = "3mo"
) -> Dict:
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        symbol: Ticker symbol
        period: RSI period (default 14)
        timeframe: Historical period
    
    Returns:
        RSI value and interpretation
    
    Tool Definition:
        name: calculate_rsi
        description: Calculate Relative Strength Index for momentum analysis
        parameters:
            symbol: string - ticker symbol
            period: number - RSI period (default 14)
            timeframe: string - historical period
    """
    try:
        from .market_data import get_price_history
        
        prices_data = get_price_history(symbol, period=timeframe)
        
        if isinstance(prices_data[symbol], dict) and 'error' in prices_data[symbol]:
            return prices_data[symbol]
        
        prices = prices_data[symbol]['Close']
        
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = float(rsi.iloc[-1])
        
        # Interpretation
        if current_rsi > 70:
            interpretation = "Overbought (RSI > 70): Potential sell signal"
            signal = "bearish"
        elif current_rsi < 30:
            interpretation = "Oversold (RSI < 30): Potential buy signal"
            signal = "bullish"
        else:
            interpretation = "Neutral (30 < RSI < 70)"
            signal = "neutral"
        
        return {
            'symbol': symbol,
            'rsi': current_rsi,
            'period': period,
            'interpretation': interpretation,
            'signal': signal
        }
    
    except Exception as e:
        return {"error": str(e)}


def detect_support_resistance(
    symbol: str,
    period: str = "1y"
) -> Dict:
    """
    Detect support and resistance levels
    
    Args:
        symbol: Ticker symbol
        period: Historical period to analyze
    
    Returns:
        Support and resistance levels
    
    Tool Definition:
        name: detect_support_resistance
        description: Identify key support and resistance price levels
        parameters:
            symbol: string - ticker symbol
            period: string - historical period
    """
    try:
        from .market_data import get_price_history
        
        prices_data = get_price_history(symbol, period=period)
        
        if isinstance(prices_data[symbol], dict) and 'error' in prices_data[symbol]:
            return prices_data[symbol]
        
        df = prices_data[symbol]
        
        # Find local maxima (resistance) and minima (support)
        window = 20
        df['local_max'] = df['High'].rolling(window=window, center=True).apply(
            lambda x: x.iloc[window//2] == x.max(), raw=False
        )
        df['local_min'] = df['Low'].rolling(window=window, center=True).apply(
            lambda x: x.iloc[window//2] == x.min(), raw=False
        )
        
        # Get resistance levels (local maxima)
        resistance_levels = df[df['local_max'] == 1]['High'].values
        resistance_levels = sorted(set([float(x) for x in resistance_levels]))[-3:]  # Top 3
        
        # Get support levels (local minima)
        support_levels = df[df['local_min'] == 1]['Low'].values
        support_levels = sorted(set([float(x) for x in support_levels]))[:3]  # Bottom 3
        
        current_price = float(df['Close'].iloc[-1])
        
        # Find nearest support and resistance
        nearest_resistance = min([r for r in resistance_levels if r > current_price], default=None)
        nearest_support = max([s for s in support_levels if s < current_price], default=None)
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'interpretation': f"Key levels: Support at {nearest_support:.2f}, Resistance at {nearest_resistance:.2f}" if nearest_support and nearest_resistance else "Unable to determine key levels"
        }
    
    except Exception as e:
        return {"error": str(e)}


# Tool registration
TOOLS = {
    "calculate_moving_averages": {
        "function": calculate_moving_averages,
        "description": "Calculate simple moving averages and detect crossover signals (golden cross, death cross)",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Ticker symbol"
                },
                "periods": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "MA periods (default [20, 50, 200])"
                },
                "period": {
                    "type": "string",
                    "description": "Historical period"
                }
            },
            "required": ["symbol"]
        }
    },
    "calculate_rsi": {
        "function": calculate_rsi,
        "description": "Calculate Relative Strength Index (RSI) to identify overbought/oversold conditions",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Ticker symbol"
                },
                "period": {
                    "type": "number",
                    "description": "RSI period (default 14)"
                },
                "timeframe": {
                    "type": "string",
                    "description": "Historical period"
                }
            },
            "required": ["symbol"]
        }
    },
    "detect_support_resistance": {
        "function": detect_support_resistance,
        "description": "Detect key support and resistance price levels using local extrema",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Ticker symbol"
                },
                "period": {
                    "type": "string",
                    "description": "Historical period"
                }
            },
            "required": ["symbol"]
        }
    }
}
