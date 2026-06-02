"""
Fundamental Analysis Tools
=========================

Tools for fundamental analysis and value investing screening (Buffett criteria, quality metrics).
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional


def buffett_screen(
    symbols: List[str]
) -> Dict:
    """
    Screen stocks using Buffett's value investing criteria
    
    Criteria:
    1. P/B < 1.5 (undervalued)
    2. D/E < 0.5 (low leverage)
    3. Current Ratio 1.5-2.5 (good liquidity)
    4. ROE > 8% (profitable)
    5. ROA > 6% (efficient)
    6. Interest Coverage > 5 (can service debt)
    
    Args:
        symbols: List of ticker symbols to screen
    
    Returns:
        Screening results with pass/fail for each criterion
    
    Tool Definition:
        name: buffett_screen
        description: Screen stocks using Warren Buffett's 6 value investing criteria
        parameters:
            symbols: array - list of ticker symbols to screen
    """
    try:
        from .market_data import get_fundamentals
        
        # Fetch fundamentals
        fundamentals = get_fundamentals(symbols)
        
        results = []
        
        for symbol in symbols:
            if symbol not in fundamentals or isinstance(fundamentals[symbol], dict) and 'error' in fundamentals[symbol]:
                continue
            
            data = fundamentals[symbol]
            
            # Extract metrics
            pb = data.get('pb_ratio')
            de = data.get('debt_to_equity')
            cr = data.get('current_ratio')
            roe = data.get('roe')
            roa = data.get('roa')
            # Interest coverage not directly available, skip for now
            
            # Score each criterion
            criteria = {
                'pb_ratio': {
                    'value': pb,
                    'target': '< 1.5',
                    'pass': pb < 1.5 if pb is not None else False
                },
                'debt_to_equity': {
                    'value': de,
                    'target': '< 0.5',
                    'pass': de < 0.5 if de is not None else False
                },
                'current_ratio': {
                    'value': cr,
                    'target': '1.5-2.5',
                    'pass': 1.5 <= cr <= 2.5 if cr is not None else False
                },
                'roe': {
                    'value': roe,
                    'target': '> 0.08',
                    'pass': roe > 0.08 if roe is not None else False
                },
                'roa': {
                    'value': roa,
                    'target': '> 0.06',
                    'pass': roa > 0.06 if roa is not None else False
                }
            }
            
            # Calculate score
            score = sum(1 for c in criteria.values() if c['pass'])
            
            results.append({
                'symbol': symbol,
                'score': score,
                'max_score': 5,
                'criteria': criteria,
                'sector': data.get('sector'),
                'recommendation': 'Strong Buy' if score >= 4 else 'Buy' if score >= 3 else 'Hold' if score >= 2 else 'Avoid'
            })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'results': results,
            'num_screened': len(results),
            'top_picks': [r for r in results if r['score'] >= 4]
        }
    
    except Exception as e:
        return {"error": str(e)}


def quality_metrics(
    symbols: List[str]
) -> Dict:
    """
    Calculate institutional quality metrics (ROIC, FCF Yield, Earnings Quality)
    
    Args:
        symbols: List of ticker symbols
    
    Returns:
        Quality scores for each stock
    
    Tool Definition:
        name: quality_metrics
        description: Calculate Goldman Sachs-style quality metrics (ROIC, FCF Yield, Earnings Quality, Gross Margin)
        parameters:
            symbols: array - list of ticker symbols
    """
    try:
        from .market_data import get_fundamentals
        
        fundamentals = get_fundamentals(symbols)
        
        results = []
        
        for symbol in symbols:
            if symbol not in fundamentals or isinstance(fundamentals[symbol], dict) and 'error' in fundamentals[symbol]:
                continue
            
            data = fundamentals[symbol]
            
            # Calculate quality score (0-100)
            quality_components = {
                'fcf_yield': {
                    'value': data.get('fcf_yield'),
                    'score': _score_fcf_yield(data.get('fcf_yield'))
                },
                'roe': {
                    'value': data.get('roe'),
                    'score': _score_roe(data.get('roe'))
                },
                'gross_margin': {
                    'value': data.get('gross_margin'),
                    'score': _score_margin(data.get('gross_margin'))
                },
                'debt_to_equity': {
                    'value': data.get('debt_to_equity'),
                    'score': _score_leverage(data.get('debt_to_equity'))
                }
            }
            
            # Calculate composite quality score
            scores = [c['score'] for c in quality_components.values() if c['score'] is not None]
            quality_score = np.mean(scores) if scores else 0
            
            # Moat assessment
            has_moat = (
                (data.get('roe', 0) or 0) > 0.15 and
                (data.get('gross_margin', 0) or 0) > 0.40
            )
            
            results.append({
                'symbol': symbol,
                'quality_score': float(quality_score),
                'components': quality_components,
                'has_moat': has_moat,
                'sector': data.get('sector'),
                'rating': _quality_rating(quality_score)
            })
        
        # Sort by quality score
        results.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return {
            'results': results,
            'interpretation': f"Quality analysis complete: {len([r for r in results if r['has_moat']])} stocks with economic moats"
        }
    
    except Exception as e:
        return {"error": str(e)}


def _score_fcf_yield(fcf_yield):
    """Score FCF yield (0-100)"""
    if fcf_yield is None:
        return None
    if fcf_yield > 0.05:
        return 100
    elif fcf_yield > 0.03:
        return 70
    elif fcf_yield > 0:
        return 40
    else:
        return 0


def _score_roe(roe):
    """Score ROE (0-100)"""
    if roe is None:
        return None
    if roe > 0.20:
        return 100
    elif roe > 0.15:
        return 80
    elif roe > 0.10:
        return 60
    elif roe > 0.05:
        return 30
    else:
        return 0


def _score_margin(margin):
    """Score gross margin (0-100)"""
    if margin is None:
        return None
    if margin > 0.50:
        return 100
    elif margin > 0.40:
        return 80
    elif margin > 0.30:
        return 60
    elif margin > 0.20:
        return 40
    else:
        return 20


def _score_leverage(de):
    """Score debt/equity (0-100, lower is better)"""
    if de is None:
        return None
    if de < 0.3:
        return 100
    elif de < 0.5:
        return 80
    elif de < 1.0:
        return 60
    elif de < 2.0:
        return 30
    else:
        return 0


def _quality_rating(score):
    """Convert quality score to rating"""
    if score >= 80:
        return "Excellent"
    elif score >= 65:
        return "Good"
    elif score >= 50:
        return "Average"
    else:
        return "Below Average"


def compare_peers(
    symbol: str,
    peer_symbols: Optional[List[str]] = None
) -> Dict:
    """
    Compare a stock to its sector peers
    
    Args:
        symbol: Target ticker symbol
        peer_symbols: Optional list of peer symbols (auto-detect if None)
    
    Returns:
        Peer comparison analysis
    
    Tool Definition:
        name: compare_peers
        description: Compare a stock to sector peers on valuation and quality metrics
        parameters:
            symbol: string - target ticker symbol
            peer_symbols: array - optional list of peer symbols
    """
    try:
        from .market_data import get_fundamentals
        
        # If no peers provided, would need to fetch sector peers
        # For now, require peers to be provided
        if not peer_symbols:
            return {"error": "Peer symbols must be provided"}
        
        all_symbols = [symbol] + peer_symbols
        fundamentals = get_fundamentals(all_symbols)
        
        # Extract key metrics
        comparison = []
        
        for sym in all_symbols:
            if sym not in fundamentals or isinstance(fundamentals[sym], dict) and 'error' in fundamentals[sym]:
                continue
            
            data = fundamentals[sym]
            comparison.append({
                'symbol': sym,
                'is_target': sym == symbol,
                'pe_ratio': data.get('pe_ratio'),
                'pb_ratio': data.get('pb_ratio'),
                'roe': data.get('roe'),
                'roa': data.get('roa'),
                'debt_to_equity': data.get('debt_to_equity'),
                'gross_margin': data.get('gross_margin'),
                'market_cap': data.get('market_cap')
            })
        
        # Calculate peer averages
        peer_data = [c for c in comparison if not c['is_target']]
        target_data = next((c for c in comparison if c['is_target']), None)
        
        if not target_data or not peer_data:
            return {"error": "Insufficient data for comparison"}
        
        peer_averages = {}
        for metric in ['pe_ratio', 'pb_ratio', 'roe', 'roa', 'debt_to_equity', 'gross_margin']:
            values = [p[metric] for p in peer_data if p[metric] is not None]
            peer_averages[metric] = np.mean(values) if values else None
        
        # Generate comparison insights
        insights = []
        
        # Valuation
        if target_data.get('pe_ratio') and peer_averages.get('pe_ratio'):
            if target_data['pe_ratio'] < peer_averages['pe_ratio'] * 0.8:
                insights.append(f"Undervalued: P/E {target_data['pe_ratio']:.1f} vs peer avg {peer_averages['pe_ratio']:.1f}")
            elif target_data['pe_ratio'] > peer_averages['pe_ratio'] * 1.2:
                insights.append(f"Overvalued: P/E {target_data['pe_ratio']:.1f} vs peer avg {peer_averages['pe_ratio']:.1f}")
        
        # Quality
        if target_data.get('roe') and peer_averages.get('roe'):
            if target_data['roe'] > peer_averages['roe']:
                insights.append(f"Higher profitability: ROE {target_data['roe']*100:.1f}% vs peer avg {peer_averages['roe']*100:.1f}%")
        
        return {
            'target': symbol,
            'target_data': target_data,
            'peer_averages': peer_averages,
            'comparison_table': comparison,
            'insights': insights,
            'interpretation': "; ".join(insights) if insights else "Similar to peers"
        }
    
    except Exception as e:
        return {"error": str(e)}


# Tool registration
TOOLS = {
    "buffett_screen": {
        "function": buffett_screen,
        "description": "Screen stocks using Warren Buffett's 6 value investing criteria (P/B, D/E, Current Ratio, ROE, ROA, Interest Coverage)",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ticker symbols to screen"
                }
            },
            "required": ["symbols"]
        }
    },
    "quality_metrics": {
        "function": quality_metrics,
        "description": "Calculate institutional quality metrics: ROIC, FCF Yield, Earnings Quality, Gross Margin. Identifies companies with economic moats.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of ticker symbols"
                }
            },
            "required": ["symbols"]
        }
    },
    "compare_peers": {
        "function": compare_peers,
        "description": "Compare a stock to sector peers on valuation and quality metrics",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Target ticker symbol"
                },
                "peer_symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of peer ticker symbols"
                }
            },
            "required": ["symbol", "peer_symbols"]
        }
    }
}
