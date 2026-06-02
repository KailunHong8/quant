"""
Value Stock Selection Dashboard
Goldman Sachs Institutional Investor Perspective

PURPOSE: Help investors identify companies that:
1. Deliver societal value and improve wellbeing
2. Are financially solid (Buffett criteria + quality metrics)
3. Trade at reasonable valuations

FEATURES:
- Interactive visualizations of key metrics
- Sector analysis for diversification
- Quality vs Value quadrant analysis
- Easy criteria adjustment
- Export filtered results

USAGE:
    python scripts/visualize_value_stocks.py
    
CUSTOMIZATION:
    Adjust criteria at the bottom of script and re-run
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("=" * 80)
print("VALUE STOCK SELECTION DASHBOARD")
print("Goldman Sachs Institutional Perspective")
print("=" * 80)

# ============================================================================
# PART 1: Load and Prepare Data
# ============================================================================
print("\n" + "=" * 80)
print("PART 1: Loading Stock Screening Results")
print("=" * 80)

# Find most recent scan results
import glob
import os

scan_files = glob.glob("value_stocks_*.csv")
if not scan_files:
    print("❌ No value_stocks_*.csv file found!")
    print("   Run market_scanner_full.py or stock_selection_buffett.py first")
    exit(1)

latest_file = max(scan_files, key=os.path.getmtime)
print(f"Loading: {latest_file}")

df = pd.read_csv(latest_file)
print(f"✓ Loaded {len(df)} stocks that passed basic Buffett criteria")

# Calculate additional quality metrics
print("\nCalculating institutional-grade quality metrics...")

# 1. Quality Score (0-100): ROE, ROA, Interest Coverage
df['quality_score'] = 0
df.loc[df['roe'] > 0.15, 'quality_score'] += 33  # High profitability
df.loc[df['roa'] > 0.10, 'quality_score'] += 33  # Asset efficiency
df.loc[df['interest_coverage'] > 10, 'quality_score'] += 34  # Strong coverage

# 2. Value Score (0-100): P/B, P/E, relative to sector
df['value_score'] = 0
df.loc[df['pb_ratio'] < 2.0, 'value_score'] += 33
df.loc[df['pe_ratio'] < 20, 'value_score'] += 33
df.loc[df['pb_ratio'] < 1.5, 'value_score'] += 34  # Extra for deep value

# 3. Safety Score (0-100): Leverage, liquidity, beta
df['safety_score'] = 0
df.loc[df['debt_equity'] < 0.3, 'safety_score'] += 33
df.loc[df['current_ratio'] > 2.0, 'safety_score'] += 33
df.loc[df['beta'] < 1.2, 'safety_score'] += 34  # Lower volatility

# 4. Composite Institutional Score (weighted)
df['institutional_score'] = (
    0.40 * df['quality_score'] +  # Quality is paramount
    0.30 * df['value_score'] +    # Value matters
    0.30 * df['safety_score']     # Safety for long-term
)

# 5. Societal Value Proxy (sector-based)
# Sectors that improve wellbeing: Healthcare, Consumer Staples, Utilities, Industrials
societal_sectors = {
    'Healthcare': 100,          # Direct health impact
    'Utilities': 90,            # Essential services
    'Consumer Staples': 85,     # Basic needs
    'Industrials': 75,          # Infrastructure
    'Technology': 70,           # Productivity
    'Materials': 60,            # Building blocks
    'Communication Services': 55,
    'Consumer Cyclical': 50,
    'Financials': 45,
    'Energy': 40,              # Transition concern
    'Real Estate': 35
}

df['societal_value'] = df['sector'].map(societal_sectors).fillna(50)

# 6. Final Holistic Score (Quality + Value + Safety + Societal)
df['holistic_score'] = (
    0.35 * df['institutional_score'] +
    0.35 * df['buffett_score'] / 6 * 100 +  # Buffett out of 6 -> 0-100
    0.30 * df['societal_value']
)

print(f"✓ Calculated 6 institutional metrics")
print(f"  - Quality Score (ROE, ROA, Interest Coverage)")
print(f"  - Value Score (P/B, P/E)")
print(f"  - Safety Score (Leverage, Liquidity, Beta)")
print(f"  - Institutional Score (weighted composite)")
print(f"  - Societal Value (sector-based wellbeing proxy)")
print(f"  - Holistic Score (all factors combined)")

# ============================================================================
# PART 2: Summary Statistics
# ============================================================================
print("\n" + "=" * 80)
print("PART 2: Portfolio Universe Summary")
print("=" * 80)

print(f"\nTotal stocks analyzed: {len(df)}")
print(f"Date: {df['fetch_date'].iloc[0] if 'fetch_date' in df.columns else 'N/A'}")

print(f"\nMarket Cap Distribution:")
df['market_cap_billions'] = df['market_cap'] / 1e9
print(f"  Mega Cap (>$200B):  {len(df[df['market_cap_billions'] > 200]):>3} stocks")
print(f"  Large Cap ($10-200B): {len(df[(df['market_cap_billions'] >= 10) & (df['market_cap_billions'] <= 200)]):>3} stocks")
print(f"  Mid Cap ($2-10B):   {len(df[(df['market_cap_billions'] >= 2) & (df['market_cap_billions'] < 10)]):>3} stocks")
print(f"  Small Cap (<$2B):   {len(df[df['market_cap_billions'] < 2]):>3} stocks")

print(f"\nSector Distribution:")
sector_counts = df['sector'].value_counts()
for sector, count in sector_counts.items():
    pct = count / len(df) * 100
    print(f"  {sector:<30} {count:>3} ({pct:>5.1f}%)")

print(f"\nKey Metrics (Median):")
print(f"  P/B Ratio:          {df['pb_ratio'].median():.2f}")
print(f"  P/E Ratio:          {df['pe_ratio'].median():.2f}")
print(f"  ROE:                {df['roe'].median()*100:.1f}%")
print(f"  ROA:                {df['roa'].median()*100:.1f}%")
print(f"  Debt/Equity:        {df['debt_equity'].median():.2f}")
print(f"  Current Ratio:      {df['current_ratio'].median():.2f}")
print(f"  Dividend Yield:     {df['dividend_yield'].median():.2f}%")
print(f"  Beta:               {df['beta'].median():.2f}")

# ============================================================================
# PART 3: Visualizations
# ============================================================================
print("\n" + "=" * 80)
print("PART 3: Generating Visualizations")
print("=" * 80)

fig = plt.figure(figsize=(20, 12))
fig.suptitle('Value Stock Selection Dashboard - Institutional Perspective', 
             fontsize=16, fontweight='bold', y=0.995)

# Chart 1: Quality vs Value Quadrant (THE MOST IMPORTANT)
ax1 = plt.subplot(2, 3, 1)
scatter = ax1.scatter(df['pb_ratio'], df['roe']*100, 
                     c=df['holistic_score'], s=df['market_cap_billions']*2,
                     cmap='RdYlGn', alpha=0.6, edgecolors='black', linewidth=0.5)
ax1.axhline(y=15, color='red', linestyle='--', alpha=0.5, label='ROE 15% threshold')
ax1.axvline(x=2.0, color='red', linestyle='--', alpha=0.5, label='P/B 2.0 threshold')
ax1.set_xlabel('Price-to-Book Ratio (Lower = Cheaper)', fontweight='bold')
ax1.set_ylabel('Return on Equity % (Higher = Better Quality)', fontweight='bold')
ax1.set_title('Quality vs Value Quadrant\n(Top-Left = Best: High Quality, Low Price)', 
              fontweight='bold')
ax1.set_xlim(0, min(df['pb_ratio'].quantile(0.95), 15))
ax1.set_ylim(0, min(df['roe'].quantile(0.95)*100, 50))
ax1.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax1, label='Holistic Score')
ax1.legend(loc='upper right', fontsize=8)

# Add annotations for top stocks
top_stocks = df.nlargest(5, 'holistic_score')
for _, row in top_stocks.iterrows():
    if row['pb_ratio'] < 15 and row['roe']*100 < 50:  # Only annotate if in chart bounds
        ax1.annotate(row['symbol'], 
                    (row['pb_ratio'], row['roe']*100),
                    fontsize=7, alpha=0.7)

# Chart 2: Safety vs Return (Risk-Adjusted View)
ax2 = plt.subplot(2, 3, 2)
scatter2 = ax2.scatter(df['debt_equity'], df['roa']*100, 
                      c=df['institutional_score'], s=df['market_cap_billions']*2,
                      cmap='RdYlGn', alpha=0.6, edgecolors='black', linewidth=0.5)
ax2.axhline(y=10, color='blue', linestyle='--', alpha=0.5, label='ROA 10% threshold')
ax2.axvline(x=0.5, color='blue', linestyle='--', alpha=0.5, label='D/E 0.5 threshold')
ax2.set_xlabel('Debt-to-Equity Ratio (Lower = Safer)', fontweight='bold')
ax2.set_ylabel('Return on Assets % (Higher = Efficient)', fontweight='bold')
ax2.set_title('Safety vs Efficiency\n(Bottom-Right = Best: Low Leverage, High ROA)', 
              fontweight='bold')
ax2.set_xlim(0, min(df['debt_equity'].quantile(0.95), 2.0))
ax2.set_ylim(0, min(df['roa'].quantile(0.95)*100, 30))
ax2.grid(True, alpha=0.3)
plt.colorbar(scatter2, ax=ax2, label='Institutional Score')
ax2.legend(loc='upper right', fontsize=8)

# Chart 3: Buffett Score Distribution
ax3 = plt.subplot(2, 3, 3)
buffett_counts = df['buffett_score'].value_counts().sort_index()
bars = ax3.bar(buffett_counts.index, buffett_counts.values, 
              color='steelblue', edgecolor='black', alpha=0.7)
ax3.set_xlabel('Buffett Criteria Passed (out of 6)', fontweight='bold')
ax3.set_ylabel('Number of Stocks', fontweight='bold')
ax3.set_title('Buffett Criteria Distribution\n(Higher = More Criteria Passed)', 
              fontweight='bold')
ax3.set_xticks(range(7))
ax3.grid(True, alpha=0.3, axis='y')
# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}', ha='center', va='bottom', fontsize=9)

# Chart 4: Sector Breakdown with Societal Value
ax4 = plt.subplot(2, 3, 4)
sector_data = df.groupby('sector').agg({
    'symbol': 'count',
    'societal_value': 'first'
}).sort_values('symbol', ascending=True)
colors_sector = plt.cm.RdYlGn(sector_data['societal_value'] / 100)
bars4 = ax4.barh(sector_data.index, sector_data['symbol'], 
                color=colors_sector, edgecolor='black', alpha=0.7)
ax4.set_xlabel('Number of Stocks', fontweight='bold')
ax4.set_title('Sector Distribution\n(Green = Higher Societal Value)', fontweight='bold')
ax4.grid(True, alpha=0.3, axis='x')
# Add value labels
for i, (idx, row) in enumerate(sector_data.iterrows()):
    ax4.text(row['symbol'] + 0.5, i, f"{int(row['symbol'])}", 
            va='center', fontsize=8)

# Chart 5: Valuation Distribution (P/E vs Market Cap)
ax5 = plt.subplot(2, 3, 5)
# Filter out extreme outliers for better visualization
pe_filtered = df[(df['pe_ratio'] > 0) & (df['pe_ratio'] < 50)].copy()
scatter5 = ax5.scatter(pe_filtered['market_cap_billions'], pe_filtered['pe_ratio'],
                      c=pe_filtered['holistic_score'], s=100,
                      cmap='RdYlGn', alpha=0.6, edgecolors='black', linewidth=0.5)
ax5.axhline(y=20, color='red', linestyle='--', alpha=0.5, label='P/E 20 threshold')
ax5.set_xlabel('Market Cap (Billions $)', fontweight='bold')
ax5.set_ylabel('P/E Ratio (Lower = Cheaper)', fontweight='bold')
ax5.set_title('Valuation by Size\n(Lower P/E = Better Value)', fontweight='bold')
ax5.set_xscale('log')
ax5.grid(True, alpha=0.3)
plt.colorbar(scatter5, ax=ax5, label='Holistic Score')
ax5.legend(loc='upper right', fontsize=8)

# Chart 6: Top 20 Stocks by Holistic Score
ax6 = plt.subplot(2, 3, 6)
top20 = df.nlargest(20, 'holistic_score')[['symbol', 'holistic_score', 'sector']].copy()
top20 = top20.sort_values('holistic_score', ascending=True)
colors_top20 = [plt.cm.tab20(i/20) for i in range(len(top20))]
bars6 = ax6.barh(range(len(top20)), top20['holistic_score'], 
                color=colors_top20, edgecolor='black', alpha=0.7)
ax6.set_yticks(range(len(top20)))
ax6.set_yticklabels([f"{row['symbol']} ({row['sector'][:12]})" 
                     for _, row in top20.iterrows()], fontsize=8)
ax6.set_xlabel('Holistic Score (0-100)', fontweight='bold')
ax6.set_title('Top 20 Stocks by Holistic Score\n(Quality + Value + Safety + Societal)', 
              fontweight='bold')
ax6.grid(True, alpha=0.3, axis='x')
# Add score labels
for i, score in enumerate(top20['holistic_score']):
    ax6.text(score + 1, i, f"{score:.1f}", va='center', fontsize=7)

plt.tight_layout()
output_file = f"value_stock_dashboard_{datetime.now().strftime('%Y%m%d')}.png"
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✓ Saved visualization: {output_file}")
plt.show()

# ============================================================================
# PART 4: Detailed Rankings
# ============================================================================
print("\n" + "=" * 80)
print("PART 4: Top Stock Rankings (Holistic Score)")
print("=" * 80)

print("\nTop 30 Stocks for Long-Term Portfolio:")
print("-" * 120)
print(f"{'Rank':<5} {'Symbol':<8} {'Company':<35} {'Sector':<20} {'Score':<8} {'P/B':<7} {'ROE':<7} {'D/E':<7}")
print("-" * 120)

top30 = df.nlargest(30, 'holistic_score')
for idx, (_, row) in enumerate(top30.iterrows(), 1):
    company_short = row['company_name'][:33] if len(row['company_name']) > 33 else row['company_name']
    sector_short = row['sector'][:18] if len(row['sector']) > 18 else row['sector']
    print(f"{idx:<5} {row['symbol']:<8} {company_short:<35} {sector_short:<20} "
          f"{row['holistic_score']:>6.1f}  {row['pb_ratio']:>6.2f}  "
          f"{row['roe']*100:>5.1f}%  {row['debt_equity']:>6.2f}")

# ============================================================================
# PART 5: Customizable Filtering
# ============================================================================
print("\n" + "=" * 80)
print("PART 5: Apply Your Custom Criteria")
print("=" * 80)

print("\n📝 ADJUST THESE CRITERIA BELOW AND RE-RUN:")
print("=" * 80)

# ============================================================================
# 🎯 CUSTOMIZE YOUR CRITERIA HERE
# ============================================================================

CUSTOM_CRITERIA = {
    'min_holistic_score': 60,      # 0-100, higher = better overall
    'min_buffett_score': 5,        # 0-6, number of Buffett criteria passed
    'max_pb_ratio': 5.0,           # Price-to-Book (lower = cheaper)
    'max_pe_ratio': 30,            # Price-to-Earnings (lower = cheaper)
    'min_roe': 0.10,               # 10% Return on Equity
    'min_roa': 0.06,               # 6% Return on Assets
    'max_debt_equity': 0.6,        # Debt-to-Equity ratio
    'min_current_ratio': 1.5,      # Liquidity
    'max_beta': 1.5,               # Market risk (1.0 = market average)
    'min_market_cap_billions': 5,  # Minimum company size
    'preferred_sectors': [         # Leave empty [] for all sectors
        'Healthcare',
        'Technology',
        'Industrials',
        'Consumer Staples',
        'Communication Services'
    ]
}

# ============================================================================

# Apply filters
filtered = df.copy()

filtered = filtered[filtered['holistic_score'] >= CUSTOM_CRITERIA['min_holistic_score']]
filtered = filtered[filtered['buffett_score'] >= CUSTOM_CRITERIA['min_buffett_score']]
filtered = filtered[filtered['pb_ratio'] <= CUSTOM_CRITERIA['max_pb_ratio']]
filtered = filtered[filtered['pe_ratio'] <= CUSTOM_CRITERIA['max_pe_ratio']]
filtered = filtered[filtered['roe'] >= CUSTOM_CRITERIA['min_roe']]
filtered = filtered[filtered['roa'] >= CUSTOM_CRITERIA['min_roa']]
filtered = filtered[filtered['debt_equity'] <= CUSTOM_CRITERIA['max_debt_equity']]
filtered = filtered[filtered['current_ratio'] >= CUSTOM_CRITERIA['min_current_ratio']]
filtered = filtered[filtered['beta'] <= CUSTOM_CRITERIA['max_beta']]
filtered = filtered[filtered['market_cap_billions'] >= CUSTOM_CRITERIA['min_market_cap_billions']]

if CUSTOM_CRITERIA['preferred_sectors']:
    filtered = filtered[filtered['sector'].isin(CUSTOM_CRITERIA['preferred_sectors'])]

print(f"\nFiltered Results: {len(filtered)} stocks meet your custom criteria")
print(f"(Started with {len(df)} stocks)")

if len(filtered) > 0:
    print("\n🎯 YOUR CUSTOMIZED PORTFOLIO PICKS:")
    print("-" * 120)
    print(f"{'Symbol':<8} {'Company':<35} {'Sector':<20} {'Score':<8} {'P/B':<7} {'P/E':<7} {'ROE':<7}")
    print("-" * 120)
    
    for _, row in filtered.nlargest(20, 'holistic_score').iterrows():
        company_short = row['company_name'][:33] if len(row['company_name']) > 33 else row['company_name']
        sector_short = row['sector'][:18] if len(row['sector']) > 18 else row['sector']
        print(f"{row['symbol']:<8} {company_short:<35} {sector_short:<20} "
              f"{row['holistic_score']:>6.1f}  {row['pb_ratio']:>6.2f}  "
              f"{row['pe_ratio']:>6.2f}  {row['roe']*100:>5.1f}%")
    
    # Export filtered results
    export_file = f"my_portfolio_picks_{datetime.now().strftime('%Y%m%d')}.csv"
    filtered_export = filtered.nlargest(50, 'holistic_score')
    filtered_export.to_csv(export_file, index=False)
    print(f"\n✓ Exported top 50 filtered stocks to: {export_file}")
    print(f"  Update comprehensive_analysis.py with these symbols!")
else:
    print("\n⚠ No stocks match your criteria. Try relaxing some filters.")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY & NEXT STEPS")
print("=" * 80)

print(f"""
Analysis Complete!

📊 Dashboard saved: {output_file}
📁 Filtered picks: {export_file if len(filtered) > 0 else 'N/A'}

Top Picks Summary:
  1. {top30.iloc[0]['symbol']:<6} - {top30.iloc[0]['company_name'][:40]} (Score: {top30.iloc[0]['holistic_score']:.1f})
  2. {top30.iloc[1]['symbol']:<6} - {top30.iloc[1]['company_name'][:40]} (Score: {top30.iloc[1]['holistic_score']:.1f})
  3. {top30.iloc[2]['symbol']:<6} - {top30.iloc[2]['company_name'][:40]} (Score: {top30.iloc[2]['holistic_score']:.1f})

Sector Diversification:
  Top Sectors: {', '.join(sector_counts.head(3).index.tolist())}

Next Steps:
  1. Review the dashboard visualization
  2. Adjust CUSTOM_CRITERIA in this script if needed
  3. Re-run to generate new filtered list
  4. Update comprehensive_analysis.py with selected symbols
  5. Run comprehensive_analysis.py for deep portfolio analysis

💡 Investment Philosophy (Goldman Sachs Approach):
  - Quality > Quantity: ROE >15%, ROA >10%
  - Reasonable Valuation: P/B <2.0, P/E <20
  - Financial Safety: D/E <0.5, Current Ratio >1.5
  - Societal Impact: Healthcare, Tech, Industrials preferred
  - Long-term mindset: Hold winners, compound returns
""")

print("=" * 80)
print("✓ Analysis Complete!")
print("=" * 80)

