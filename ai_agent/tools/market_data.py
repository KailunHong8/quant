"""
Market Data Tools
=================

Tools for fetching market data, fundamentals, and macroeconomic indicators.
Uses OpenBB as primary data source with caching via ArcticDB.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
import warnings
warnings.filterwarnings('ignore')

# Try to import ArcticDB for caching
try:
    import arcticdb as adb
    arctic = adb.Arctic("lmdb://quant_data")
    prices_lib = arctic.get_library("prices", create_if_missing=True)
    fundamentals_lib = arctic.get_library("fundamentals", create_if_missing=True)
    ARCTIC_AVAILABLE = True
except ImportError:
    ARCTIC_AVAILABLE = False


def get_price_history(
    symbols: Union[str, List[str]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "1y"
) -> Dict[str, pd.DataFrame]:
    """
    Fetch historical price data for symbols
    
    Args:
        symbols: Single symbol or list of symbols
        start_date: Start date (YYYY-MM-DD) or None
        end_date: End date (YYYY-MM-DD) or None
        period: Period if dates not specified ('1y', '2y', '5y', 'max')
    
    Returns:
        Dict of {symbol: DataFrame with OHLCV data}
    
    Tool Definition:
        name: get_price_history
        description: Fetch historical OHLCV price data for one or more stocks
        parameters:
            symbols: string or array - ticker symbols
            start_date: string - start date YYYY-MM-DD (optional)
            end_date: string - end date YYYY-MM-DD (optional)
            period: string - time period if dates not given (1y, 2y, 5y, max)
    """
    if isinstance(symbols, str):
        symbols = [symbols]
    
    results = {}
    
    for symbol in symbols:
        try:
            # Try cache first if available
            cache_key = f"{symbol}_prices_{period}"
            if ARCTIC_AVAILABLE and not start_date:
                try:
                    df = prices_lib.read(cache_key).data
                    # Check if cache is recent (within 1 day)
                    if (datetime.now() - df.index[-1]).days < 1:
                        results[symbol] = df
                        continue
                except Exception:
                    pass
            
            # Fetch from OpenBB
            from openbb import obb
            
            if start_date:
                data = obb.equity.price.historical(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date or datetime.now().strftime("%Y-%m-%d"),
                    provider="yfinance"
                )
            else:
                # Use yfinance directly for period-based queries
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period)
                df.index = df.index.tz_localize(None)  # Remove timezone
                results[symbol] = df
                
                # Cache it
                if ARCTIC_AVAILABLE:
                    try:
                        prices_lib.write(cache_key, df)
                    except Exception:
                        pass
                
                continue
            
            df = data.to_dataframe()
            df.index = pd.to_datetime(df.index)
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            
            results[symbol] = df
            
            # Cache it
            if ARCTIC_AVAILABLE and not start_date:
                try:
                    prices_lib.write(cache_key, df)
                except Exception:
                    pass
        
        except Exception as e:
            results[symbol] = {"error": str(e)}
    
    return results


def get_fundamentals(
    symbols: Union[str, List[str]],
    metrics: Optional[List[str]] = None
) -> Dict[str, Dict]:
    """
    Fetch fundamental data for symbols
    
    Args:
        symbols: Single symbol or list of symbols
        metrics: Specific metrics to fetch (optional, fetches all if None)
            Options: 'income', 'balance', 'cash_flow', 'ratios', 'metrics'
    
    Returns:
        Dict of {symbol: {metric_type: data}}
    
    Tool Definition:
        name: get_fundamentals
        description: Fetch fundamental financial data (income statement, balance sheet, ratios, etc.)
        parameters:
            symbols: string or array - ticker symbols
            metrics: array - specific metrics ('income', 'balance', 'cash_flow', 'ratios', 'metrics')
    """
    if isinstance(symbols, str):
        symbols = [symbols]
    
    if metrics is None:
        metrics = ['ratios', 'metrics']  # Default to key metrics
    
    results = {}
    
    for symbol in symbols:
        try:
            symbol_data = {}
            
            # Try cache first
            cache_key = f"{symbol}_fundamentals"
            if ARCTIC_AVAILABLE:
                try:
                    cached = fundamentals_lib.read(cache_key).data
                    # Check if cache is recent (within 7 days)
                    cache_date = cached.iloc[0]['_cached_at'] if '_cached_at' in cached.columns else datetime.min
                    if isinstance(cache_date, str):
                        cache_date = datetime.fromisoformat(cache_date)
                    if (datetime.now() - cache_date).days < 7:
                        results[symbol] = cached.to_dict('records')[0]
                        continue
                except Exception:
                    pass
            
            # Fetch from yfinance (more reliable for fundamentals)
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract key metrics
            fundamentals = {
                'symbol': symbol,
                '_cached_at': datetime.now().isoformat(),
                
                # Valuation
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'pb_ratio': info.get('priceToBook'),
                'ps_ratio': info.get('priceToSalesTrailing12Months'),
                
                # Profitability
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'roic': None,  # Will calculate if needed
                'gross_margin': info.get('grossMargins'),
                'operating_margin': info.get('operatingMargins'),
                'profit_margin': info.get('profitMargins'),
                
                # Financial Health
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'debt_to_equity': info.get('debtToEquity'),
                'interest_coverage': None,  # Will calculate if needed
                
                # Growth
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                
                # Cash Flow
                'operating_cash_flow': info.get('operatingCashflow'),
                'free_cash_flow': info.get('freeCashflow'),
                'fcf_yield': None,  # Will calculate
                
                # Dividend
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                
                # Other
                'beta': info.get('beta'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
            }
            
            # Calculate derived metrics
            if fundamentals['free_cash_flow'] and fundamentals['market_cap']:
                fundamentals['fcf_yield'] = fundamentals['free_cash_flow'] / fundamentals['market_cap']
            
            # Get additional data if requested
            if 'ratios' in metrics and ticker.quarterly_financials is not None:
                try:
                    # Get latest quarter data
                    latest_financials = ticker.quarterly_financials.iloc[:, 0]
                    fundamentals['latest_quarter_revenue'] = latest_financials.get('Total Revenue')
                    fundamentals['latest_quarter_net_income'] = latest_financials.get('Net Income')
                except Exception:
                    pass
            
            results[symbol] = fundamentals
            
            # Cache it
            if ARCTIC_AVAILABLE:
                try:
                    df = pd.DataFrame([fundamentals])
                    fundamentals_lib.write(cache_key, df)
                except Exception:
                    pass
        
        except Exception as e:
            results[symbol] = {"error": str(e)}
    
    return results


def get_macro_indicators() -> Dict[str, float]:
    """
    Fetch current macroeconomic indicators
    
    Returns:
        Dict of macro indicators
    
    Tool Definition:
        name: get_macro_indicators
        description: Fetch current macroeconomic indicators (10Y yield, VIX, Dollar Index, etc.)
        parameters: {}
    """
    try:
        import yfinance as yf
        
        indicators = {}
        
        # 10-Year Treasury Yield
        try:
            tnx = yf.Ticker("^TNX")
            tnx_data = tnx.history(period="5d")
            if not tnx_data.empty:
                indicators['treasury_10y'] = tnx_data['Close'].iloc[-1] / 100
        except Exception:
            indicators['treasury_10y'] = None
        
        # VIX (Volatility Index)
        try:
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period="5d")
            if not vix_data.empty:
                indicators['vix'] = vix_data['Close'].iloc[-1]
        except Exception:
            indicators['vix'] = None
        
        # Dollar Index
        try:
            dxy = yf.Ticker("DX-Y.NYB")
            dxy_data = dxy.history(period="5d")
            if not dxy_data.empty:
                indicators['dollar_index'] = dxy_data['Close'].iloc[-1]
        except Exception:
            indicators['dollar_index'] = None
        
        # S&P 500
        try:
            spy = yf.Ticker("SPY")
            spy_data = spy.history(period="1mo")
            if not spy_data.empty:
                indicators['sp500_level'] = spy_data['Close'].iloc[-1]
                indicators['sp500_1m_return'] = (spy_data['Close'].iloc[-1] / spy_data['Close'].iloc[0] - 1)
        except Exception:
            indicators['sp500_level'] = None
            indicators['sp500_1m_return'] = None
        
        # Add market regime assessment
        if indicators.get('vix') is not None:
            if indicators['vix'] < 15:
                indicators['market_regime'] = 'low_volatility'
            elif indicators['vix'] < 25:
                indicators['market_regime'] = 'normal'
            elif indicators['vix'] < 35:
                indicators['market_regime'] = 'elevated_volatility'
            else:
                indicators['market_regime'] = 'high_stress'
        
        if indicators.get('treasury_10y') is not None:
            indicators['rate_environment'] = 'high' if indicators['treasury_10y'] > 0.04 else 'low'
        
        indicators['timestamp'] = datetime.now().isoformat()
        
        return indicators
    
    except Exception as e:
        return {"error": str(e)}


def get_sector_performance(period: str = "1mo") -> Dict[str, float]:
    """
    Get sector ETF performance
    
    Args:
        period: Time period ('1d', '5d', '1mo', '3mo', '1y')
    
    Returns:
        Dict of sector returns
    
    Tool Definition:
        name: get_sector_performance
        description: Get sector ETF returns for relative sector analysis
        parameters:
            period: string - time period (1d, 5d, 1mo, 3mo, 1y)
    """
    sector_etfs = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Financials': 'XLF',
        'Consumer Discretionary': 'XLY',
        'Consumer Staples': 'XLP',
        'Energy': 'XLE',
        'Utilities': 'XLU',
        'Real Estate': 'XLRE',
        'Materials': 'XLB',
        'Industrials': 'XLI',
        'Communication Services': 'XLC',
    }
    
    try:
        import yfinance as yf
        
        results = {}
        
        for sector, etf in sector_etfs.items():
            try:
                ticker = yf.Ticker(etf)
                data = ticker.history(period=period)
                if not data.empty and len(data) > 1:
                    ret = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1)
                    results[sector] = float(ret)
            except Exception:
                results[sector] = None
        
        return results
    
    except Exception as e:
        return {"error": str(e)}


# Tool registration
# These will be automatically registered when the module is imported
TOOLS = {
    "get_price_history": {
        "function": get_price_history,
        "description": "Fetch historical OHLCV price data for one or more stocks. Returns DataFrame with open, high, low, close, volume.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Stock ticker symbol(s) to fetch"
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format (optional)"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format (optional)"
                },
                "period": {
                    "type": "string",
                    "enum": ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
                    "description": "Time period if dates not specified"
                }
            },
            "required": ["symbols"]
        }
    },
    "get_fundamentals": {
        "function": get_fundamentals,
        "description": "Fetch fundamental financial data including valuation ratios (P/E, P/B), profitability (ROE, ROA, margins), financial health (debt ratios, current ratio), and growth metrics.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": ["string", "array"],
                    "items": {"type": "string"},
                    "description": "Stock ticker symbol(s) to fetch"
                },
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["income", "balance", "cash_flow", "ratios", "metrics"]
                    },
                    "description": "Specific metric types to fetch (optional, defaults to ratios and metrics)"
                }
            },
            "required": ["symbols"]
        }
    },
    "get_macro_indicators": {
        "function": get_macro_indicators,
        "description": "Fetch current macroeconomic indicators: 10-year Treasury yield, VIX volatility index, Dollar Index, S&P 500 level/return, and market regime assessment.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    "get_sector_performance": {
        "function": get_sector_performance,
        "description": "Get sector ETF returns for relative sector strength analysis. Covers all 11 S&P 500 sectors.",
        "parameters": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": ["1d", "5d", "1mo", "3mo", "1y"],
                    "description": "Time period for returns calculation"
                }
            },
            "required": ["period"]
        }
    }
}
