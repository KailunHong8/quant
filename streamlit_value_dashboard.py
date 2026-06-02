"""
Interactive Value Stock Selection Dashboard
Built with Streamlit - Goldman Sachs Institutional Perspective

FEATURES:
- 📊 Interactive charts (Quality vs Value quadrants)
- 🎛️ Real-time filtering with sliders
- 💾 Export filtered results with one click
- 🎨 Beautiful, professional UI
- 🔄 Live updates as you adjust criteria

USAGE:
    streamlit run streamlit_value_dashboard.py
    
REQUIREMENTS:
    pip install streamlit plotly
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import glob
import os

# Page config
st.set_page_config(
    page_title="Value Stock Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #1f77b4;
    }
    .stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD DATA
# ============================================================================

@st.cache_data
def load_latest_scan():
    """Load most recent value stocks CSV"""
    scan_files = glob.glob("value_stocks_*.csv")
    if not scan_files:
        st.error("❌ No value_stocks_*.csv file found! Run market_scanner_full.py first.")
        st.stop()
    
    latest_file = max(scan_files, key=os.path.getmtime)
    df = pd.read_csv(latest_file)
    
    # Calculate enhanced metrics
    df['market_cap_billions'] = df['market_cap'] / 1e9
    
    # Quality Score (0-100)
    df['quality_score'] = 0
    df.loc[df['roe'] > 0.15, 'quality_score'] += 33
    df.loc[df['roa'] > 0.10, 'quality_score'] += 33
    df.loc[df['interest_coverage'] > 10, 'quality_score'] += 34
    
    # Value Score (0-100)
    df['value_score'] = 0
    df.loc[df['pb_ratio'] < 2.0, 'value_score'] += 33
    df.loc[df['pe_ratio'] < 20, 'value_score'] += 33
    df.loc[df['pb_ratio'] < 1.5, 'value_score'] += 34
    
    # Safety Score (0-100)
    df['safety_score'] = 0
    df.loc[df['debt_equity'] < 0.3, 'safety_score'] += 33
    df.loc[df['current_ratio'] > 2.0, 'safety_score'] += 33
    df.loc[df['beta'].fillna(1.0) < 1.2, 'safety_score'] += 34
    
    # Institutional Score
    df['institutional_score'] = (
        0.40 * df['quality_score'] +
        0.30 * df['value_score'] +
        0.30 * df['safety_score']
    )
    
    # Societal Value (sector-based)
    societal_sectors = {
        'Healthcare': 100, 'Utilities': 90, 'Consumer Staples': 85,
        'Industrials': 75, 'Technology': 70, 'Materials': 60,
        'Communication Services': 55, 'Consumer Cyclical': 50,
        'Financials': 45, 'Financial Services': 45, 'Energy': 40, 
        'Real Estate': 35
    }
    df['societal_value'] = df['sector'].map(societal_sectors).fillna(50)
    
    # Holistic Score
    df['holistic_score'] = (
        0.35 * df['institutional_score'] +
        0.35 * df['buffett_score'] / 6 * 100 +
        0.30 * df['societal_value']
    )
    
    return df, latest_file

# Load data
with st.spinner('Loading stock data...'):
    df, source_file = load_latest_scan()

# ============================================================================
# HEADER
# ============================================================================

st.title("📊 Interactive Value Stock Dashboard")
st.markdown("### Goldman Sachs Institutional Perspective")
st.markdown("---")

# Summary metrics in columns
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Stocks", len(df))
with col2:
    st.metric("Median P/B", f"{df['pb_ratio'].median():.2f}")
with col3:
    st.metric("Median ROE", f"{df['roe'].median()*100:.1f}%")
with col4:
    st.metric("Avg Quality", f"{df['quality_score'].mean():.0f}/100")
with col5:
    st.metric("Data Source", source_file.split('_')[-1].replace('.csv', ''))

st.markdown("---")

# ============================================================================
# SIDEBAR - FILTERING CONTROLS
# ============================================================================

st.sidebar.header("🎛️ Filter Criteria")
st.sidebar.markdown("Adjust sliders to filter stocks in real-time")

# Holistic Score
min_holistic = st.sidebar.slider(
    "Min Holistic Score",
    min_value=0,
    max_value=100,
    value=55,
    step=5,
    help="Combined quality + value + safety + societal impact"
)

# Buffett Score
min_buffett = st.sidebar.slider(
    "Min Buffett Criteria Passed",
    min_value=0,
    max_value=6,
    value=4,
    step=1,
    help="Out of 6 Buffett value criteria"
)

# Valuation
st.sidebar.subheader("📉 Valuation")
max_pb = st.sidebar.slider("Max P/B Ratio", 0.0, 10.0, 5.0, 0.5)
max_pe = st.sidebar.slider("Max P/E Ratio", 0.0, 50.0, 30.0, 5.0)

# Quality
st.sidebar.subheader("💎 Quality")
min_roe = st.sidebar.slider("Min ROE %", 0.0, 30.0, 8.0, 1.0) / 100
min_roa = st.sidebar.slider("Min ROA %", 0.0, 20.0, 6.0, 1.0) / 100

# Safety
st.sidebar.subheader("🛡️ Safety")
max_de = st.sidebar.slider("Max Debt/Equity", 0.0, 2.0, 0.6, 0.1)
min_cr = st.sidebar.slider("Min Current Ratio", 0.0, 5.0, 1.5, 0.1)
max_beta = st.sidebar.slider("Max Beta", 0.0, 3.0, 1.5, 0.1)

# Size
st.sidebar.subheader("📏 Company Size")
min_market_cap = st.sidebar.slider(
    "Min Market Cap ($B)",
    0.0,
    100.0,
    5.0,
    5.0
)

# Sectors
st.sidebar.subheader("🏢 Sectors")
all_sectors = sorted(df['sector'].dropna().unique())
selected_sectors = st.sidebar.multiselect(
    "Select Sectors (empty = all)",
    all_sectors,
    default=[]
)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Quick Presets:**")
if st.sidebar.button("🏆 High Quality"):
    min_roe = 0.15
    min_roa = 0.10
    max_de = 0.3
    st.sidebar.info("Preset applied! Refresh page to see.")

if st.sidebar.button("💰 Deep Value"):
    max_pb = 2.0
    max_pe = 15.0
    st.sidebar.info("Preset applied! Refresh page to see.")

if st.sidebar.button("🌍 Societal Impact"):
    selected_sectors = ['Healthcare', 'Technology', 'Industrials', 'Utilities']
    st.sidebar.info("Preset applied! Refresh page to see.")

# ============================================================================
# APPLY FILTERS
# ============================================================================

filtered_df = df.copy()

# Apply all filters
filtered_df = filtered_df[filtered_df['holistic_score'] >= min_holistic]
filtered_df = filtered_df[filtered_df['buffett_score'] >= min_buffett]
filtered_df = filtered_df[filtered_df['pb_ratio'] <= max_pb]
filtered_df = filtered_df[filtered_df['pe_ratio'] <= max_pe]
filtered_df = filtered_df[filtered_df['roe'] >= min_roe]
filtered_df = filtered_df[filtered_df['roa'] >= min_roa]
filtered_df = filtered_df[filtered_df['debt_equity'] <= max_de]
filtered_df = filtered_df[filtered_df['current_ratio'] >= min_cr]
filtered_df = filtered_df[filtered_df['beta'].fillna(1.0) <= max_beta]
filtered_df = filtered_df[filtered_df['market_cap_billions'] >= min_market_cap]

if selected_sectors:
    filtered_df = filtered_df[filtered_df['sector'].isin(selected_sectors)]

# Sort by holistic score
filtered_df = filtered_df.sort_values('holistic_score', ascending=False)

# ============================================================================
# MAIN DISPLAY
# ============================================================================

st.header(f"📋 Filtered Results: {len(filtered_df)} stocks")
if len(filtered_df) == 0:
    st.warning("⚠️ No stocks match your criteria. Try relaxing some filters.")
    st.stop()

# Export button
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="💾 Download Filtered Stocks as CSV",
    data=csv,
    file_name=f"my_portfolio_picks_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
    mime="text/csv"
)

st.markdown("---")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

# Tab layout for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Quality vs Value", "🏢 Sector Analysis", "📈 Rankings", "📋 Full Data"])

with tab1:
    st.subheader("Quality vs Value Quadrant Analysis")
    st.markdown("**Goal:** Find stocks in the **top-left** corner (High Quality, Low Price)")
    
    # Interactive scatter plot
    fig = px.scatter(
        filtered_df,
        x='pb_ratio',
        y='roe',
        size='market_cap_billions',
        color='holistic_score',
        hover_name='symbol',
        hover_data={
            'company_name': True,
            'sector': True,
            'pb_ratio': ':.2f',
            'roe': ':.1%',
            'pe_ratio': ':.1f',
            'holistic_score': ':.1f',
            'market_cap_billions': ':.1f'
        },
        labels={
            'pb_ratio': 'Price-to-Book (Lower = Cheaper)',
            'roe': 'Return on Equity (Higher = Better)',
            'holistic_score': 'Holistic Score'
        },
        color_continuous_scale='RdYlGn',
        title="Quality (ROE) vs Value (P/B)"
    )
    
    # Add threshold lines
    fig.add_hline(y=0.15, line_dash="dash", line_color="red", 
                  annotation_text="ROE 15% threshold")
    fig.add_vline(x=2.0, line_dash="dash", line_color="red",
                  annotation_text="P/B 2.0 threshold")
    
    fig.update_layout(height=600, hovermode='closest')
    fig.update_yaxes(tickformat='.0%')
    st.plotly_chart(fig, use_container_width=True)
    
    # Second chart: Safety vs Efficiency
    st.subheader("Safety vs Efficiency Analysis")
    st.markdown("**Goal:** Find stocks in the **bottom-right** corner (Low Leverage, High ROA)")
    
    fig2 = px.scatter(
        filtered_df,
        x='debt_equity',
        y='roa',
        size='market_cap_billions',
        color='institutional_score',
        hover_name='symbol',
        hover_data={
            'company_name': True,
            'sector': True,
            'debt_equity': ':.2f',
            'roa': ':.1%',
            'current_ratio': ':.2f',
            'institutional_score': ':.1f'
        },
        labels={
            'debt_equity': 'Debt-to-Equity (Lower = Safer)',
            'roa': 'Return on Assets (Higher = Efficient)',
            'institutional_score': 'Institutional Score'
        },
        color_continuous_scale='RdYlGn',
        title="Safety (Low Debt) vs Efficiency (ROA)"
    )
    
    fig2.add_hline(y=0.10, line_dash="dash", line_color="blue")
    fig2.add_vline(x=0.5, line_dash="dash", line_color="blue")
    fig2.update_layout(height=600)
    fig2.update_yaxes(tickformat='.0%')
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Sector Distribution & Analysis")
    
    # Sector breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        sector_counts = filtered_df['sector'].value_counts().reset_index()
        sector_counts.columns = ['Sector', 'Count']
        
        fig3 = px.bar(
            sector_counts,
            x='Count',
            y='Sector',
            orientation='h',
            title="Stocks per Sector",
            color='Count',
            color_continuous_scale='Blues'
        )
        fig3.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Average quality by sector
        sector_quality = filtered_df.groupby('sector').agg({
            'holistic_score': 'mean',
            'symbol': 'count'
        }).reset_index()
        sector_quality.columns = ['Sector', 'Avg Score', 'Count']
        sector_quality = sector_quality.sort_values('Avg Score', ascending=False)
        
        fig4 = px.bar(
            sector_quality,
            x='Avg Score',
            y='Sector',
            orientation='h',
            title="Average Holistic Score by Sector",
            color='Avg Score',
            color_continuous_scale='RdYlGn',
            hover_data={'Count': True}
        )
        fig4.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Societal impact vs quality scatter
    st.subheader("Societal Impact vs Quality")
    fig5 = px.scatter(
        filtered_df,
        x='societal_value',
        y='quality_score',
        size='market_cap_billions',
        color='sector',
        hover_name='symbol',
        hover_data={'company_name': True},
        title="Societal Impact vs Quality Score",
        labels={
            'societal_value': 'Societal Value Score (Sector-based)',
            'quality_score': 'Quality Score (ROE, ROA, Interest Coverage)'
        }
    )
    fig5.update_layout(height=600)
    st.plotly_chart(fig5, use_container_width=True)

with tab3:
    st.subheader("🏆 Top Stock Rankings")
    
    # Display mode selector
    view_mode = st.radio(
        "View:",
        ["Top 20", "Top 50", "All Filtered"],
        horizontal=True
    )
    
    display_count = {'Top 20': 20, 'Top 50': 50, 'All Filtered': len(filtered_df)}[view_mode]
    display_df = filtered_df.head(display_count)
    
    # Create ranking table
    st.markdown(f"### Top {min(display_count, len(filtered_df))} Stocks by Holistic Score")
    
    # Format for display
    display_table = display_df[[
        'symbol', 'company_name', 'sector', 'holistic_score',
        'pb_ratio', 'pe_ratio', 'roe', 'roa', 'debt_equity',
        'buffett_score', 'market_cap_billions'
    ]].copy()
    
    display_table['roe'] = display_table['roe'].apply(lambda x: f"{x*100:.1f}%")
    display_table['roa'] = display_table['roa'].apply(lambda x: f"{x*100:.1f}%")
    display_table['holistic_score'] = display_table['holistic_score'].apply(lambda x: f"{x:.1f}")
    display_table['pb_ratio'] = display_table['pb_ratio'].apply(lambda x: f"{x:.2f}")
    display_table['pe_ratio'] = display_table['pe_ratio'].apply(lambda x: f"{x:.1f}")
    display_table['debt_equity'] = display_table['debt_equity'].apply(lambda x: f"{x:.2f}")
    display_table['market_cap_billions'] = display_table['market_cap_billions'].apply(lambda x: f"${x:.1f}B")
    
    display_table.columns = [
        'Symbol', 'Company', 'Sector', 'Holistic Score',
        'P/B', 'P/E', 'ROE', 'ROA', 'D/E', 'Buffett Score', 'Market Cap'
    ]
    
    st.dataframe(display_table, use_container_width=True, hide_index=True)
    
    # Top 5 detailed cards
    st.markdown("### 🎯 Top 5 Picks - Detailed View")
    
    for idx, row in filtered_df.head(5).iterrows():
        with st.expander(f"#{filtered_df.index.get_loc(idx)+1}: {row['symbol']} - {row['company_name']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Holistic Score", f"{row['holistic_score']:.1f}/100")
                st.metric("P/B Ratio", f"{row['pb_ratio']:.2f}")
                st.metric("P/E Ratio", f"{row['pe_ratio']:.1f}")
            
            with col2:
                st.metric("ROE", f"{row['roe']*100:.1f}%")
                st.metric("ROA", f"{row['roa']*100:.1f}%")
                st.metric("Debt/Equity", f"{row['debt_equity']:.2f}")
            
            with col3:
                st.metric("Buffett Score", f"{row['buffett_score']}/6")
                st.metric("Sector", row['sector'])
                st.metric("Market Cap", f"${row['market_cap_billions']:.1f}B")

with tab4:
    st.subheader("📋 Complete Filtered Data")
    st.markdown(f"Showing all {len(filtered_df)} stocks that match your criteria")
    
    # Full data table with all columns
    st.dataframe(
        filtered_df[[
            'symbol', 'company_name', 'sector', 'industry',
            'holistic_score', 'quality_score', 'value_score', 'safety_score',
            'pb_ratio', 'pe_ratio', 'roe', 'roa', 'debt_equity', 'current_ratio',
            'interest_coverage', 'buffett_score', 'market_cap_billions', 'beta'
        ]],
        use_container_width=True,
        hide_index=True
    )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("### 💡 Investment Philosophy")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Quality First**
    - ROE > 15%
    - ROA > 10%
    - Low leverage
    - Strong cash flow
    """)

with col2:
    st.markdown("""
    **Reasonable Valuation**
    - P/B < 2.0
    - P/E < 20
    - PEG < 1.5
    - Compare to sector
    """)

with col3:
    st.markdown("""
    **Societal Value**
    - Healthcare (wellness)
    - Technology (productivity)
    - Industrials (infrastructure)
    - Utilities (essential services)
    """)

st.markdown("---")
st.caption(f"Data source: {source_file} | Dashboard built with Streamlit | © 2026 Quant Toolkit")

