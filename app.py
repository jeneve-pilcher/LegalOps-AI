import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------------------------------
# 1. PAGE LAYOUT & SETUP
# ----------------------------------------------------
st.set_page_config(
    page_title="LegalOps AI - Partner Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling to mimic modern B2B enterprise software
st.markdown("""
    <style>
    .metric-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E3A8A;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .alert-critical {
        background-color: #FFF5F5;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #E53E3E;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. MOCK DATA GENERATION PIPELINE
# ----------------------------------------------------
@st.cache_data
def generate_legal_pipeline_data():
    np.random.seed(42)
    n_cases = 40
    
    # Simulating data structural layout pulled from Clio + QuickBooks
    mock_data = {
        'Matter ID': [f"MAT-{1000+i}" for i in range(n_cases)],
        'Client Name': [
            f"Client {ln}" for ln in ["Acme Corp", "Global Tech", "Smith Estate", "Vanguard LLC", "Apex Logistics", "Davis Legal"] * 7
        ][:n_cases],
        'Lead Attorney': np.random.choice(['Partner Smith', 'Partner Jones', 'Associate Davis'], n_cases),
        'Practice Area': np.random.choice(['Corporate/M&A', 'Family Law', 'Personal Injury', 'Real Estate'], n_cases),
        'Unbilled WIP ($)': np.random.exponential(scale=3500, size=n_cases).round(2),
        'IOLTA Trust Balance ($)': np.random.choice([0, 1500, 5000, 12000], n_cases, p=[0.25, 0.35, 0.30, 0.10]),
        'Days Since Last Invoice': np.random.randint(5, 95, size=n_cases),
        'Upcoming Retainer Expenses ($)': np.random.choice([0, 500, 2500, 6000], n_cases, p=[0.50, 0.25, 0.15, 0.10])
    }
    
    df = pd.DataFrame(mock_data)
    
    # Dynamic Alert logic logic processing
    df['Status'] = 'Healthy'
    
    # Condition 1: Revenue leakage (Work done long ago but not billed)
    df.loc[(df['Unbilled WIP ($)'] > 4000) & (df['Days Since Last Invoice'] > 45), 'Status'] = 'WIP Leakage Risk'
    
    # Condition 2: High Compliance Overdraw Danger (Expenses outpace available escrow)
    df.loc[df['Upcoming Retainer Expenses ($)'] > df['IOLTA Trust Balance ($)'], 'Status'] = 'IOLTA Trust Deficit'
    
    return df

df = generate_legal_pipeline_data()

# ----------------------------------------------------
# 3. SIDEBAR CONTROLS (User Customization)
# ----------------------------------------------------
st.sidebar.image("https://icons8.com", width=50)
st.sidebar.title("LegalOps Operations Engine")
st.sidebar.write("Simulated Live API Stream")

practice_filter = st.sidebar.multiselect(
    "Filter by Practice Area",
    options=df['Practice Area'].unique(),
    default=df['Practice Area'].unique()
)

attorney_filter = st.sidebar.multiselect(
    "Filter by Responsible Attorney",
    options=df['Lead Attorney'].unique(),
    default=df['Lead Attorney'].unique()
)

# Apply runtime filters
filtered_df = df[(df['Practice Area'].isin(practice_filter)) & (df['Lead Attorney'].isin(attorney_filter))]

# ----------------------------------------------------
# 4. EXECUTIVE HERO BANNER & KPI CARDS
# ----------------------------------------------------
st.title("⚖️ Law Firm Revenue Protection & Trust Compliance Dashboard")
st.markdown("Automated cross-referencing engine auditing **Clio Billing** and **QuickBooks Ledger Escrow** values.")
st.write("---")

# Analytical Computations for Metrics
total_unbilled_wip = filtered_df['Unbilled WIP ($)'].sum()
critical_iolta_count = (filtered_df['Status'] == 'IOLTA Trust Deficit').sum()
leakage_wip_count = (filtered_df['Status'] == 'WIP Leakage Risk').sum()
avg_billing_cycle = int(filtered_df['Days Since Last Invoice'].mean())

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='metric-box'>
        <p style='color: #4B5563; font-size: 0.9rem; margin-bottom: 0;'>Total Unbilled WIP</p>
        <h2 style='color: #1E3A8A; margin-top: 0;'>${total_unbilled_wip:,.2f}</h2>
        <small style='color: #DC2626;'>⚠️ Revenue left on table</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Set warning color based on severity counts
    escrow_color = "#DC2626" if critical_iolta_count > 0 else "#10B981"
    st.markdown(f"""
    <div class='metric-box' style='border-left-color: {escrow_color};'>
        <p style='color: #4B5563; font-size: 0.9rem; margin-bottom: 0;'>IOLTA Trust Deficits</p>
        <h2 style='color: {escrow_color}; margin-top: 0;'>{critical_iolta_count} Cases</h2>
        <small>Disbarment Risk Level</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-box' style='border-left-color: #D97706;'>
        <p style='color: #4B5563; font-size: 0.9rem; margin-bottom: 0;'>Aging WIP Alert (>45 Days)</p>
        <h2 style='color: #D97706; margin-top: 0;'>{leakage_wip_count} Files</h2>
        <small>Needs Immediate Invoice Draft</small>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='metric-box'>
        <p style='color: #4B5563; font-size: 0.9rem; margin-bottom: 0;'>Avg. Days Since Last Bill</p>
        <h2 style='color: #1E3A8A; margin-top: 0;'>{avg_billing_cycle} Days</h2>
        <small style='color: #4B5563;'>Firm Goal: &lt; 30 Days</small>
    </div>
    """, unsafe_allow_html=True)

st.write(" ")

# ----------------------------------------------------
# 5. REAL-TIME COMPLIANCE EXCEPTION TICKER
# ----------------------------------------------------
st.subheader("🚨 Proactive Partner Action Center")
danger_zone = filtered_df[filtered_df['Status'] != 'Healthy']

if not danger_zone.empty:
    for idx, row in danger_zone.iterrows():
        if row['Status'] == 'IOLTA Trust Deficit':
            st.markdown(f"""
            <div class='alert-critical'>
                <strong>🔴 CRITICAL COMPLIANCE THREAT:</strong> {row['Matter ID']} ({row['Client Name']}) under <strong>{row['Lead Attorney']}</strong>. 
                Upcoming Ledger Fee of <strong>${row['Upcoming Retainer Expenses ($)']:,}</strong> exceeds Trust Account Balance of <strong>${row['IOLTA Trust Balance ($)']:,}</strong>.
            </div>
            """, unsafe_allow_html=True)
        elif row['Status'] == 'WIP Leakage Risk':
            st.markdown(f"""
            <div class='alert-critical' style='border-left-color: #D97706; background-color: #FFFBEB;'>
                <strong>⚠️ UNBILLED REVENUE DRIFT:</strong> {row['Matter ID']} ({row['Client Name']}) has <strong>${row['Unbilled WIP ($)']:,.2f}</strong> in unbilled hours with no client invoice sent for <strong>{row['Days Since Last Invoice']} days</strong>.
            </div>
            """, unsafe_allow_html=True)
else:
    st.success("✅ Audit Clear: Zero active compliance risks or billing anomalies detected across targeted practices.")

st.write(" ")

# ----------------------------------------------------
# 6. VISUAL CHARTS INTERFACE
# ----------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("### Unbilled Revenue Accumulation by Attorney")
    fig_wip = px.bar(
        filtered_df, 
        x='Lead Attorney', 
        y='Unbilled WIP ($)', 
        color='Practice Area',
        title="Who holds the most unbilled inventory?",
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    st.plotly_chart(fig_wip, use_container_width=True)

with chart_col2:
    st.markdown("### Retainer Health Analysis")
    fig_scatter = px.scatter(
        filtered_df,
        x='IOLTA Trust Balance ($)',
        y='Unbilled WIP ($)',
        size='Days Since Last Invoice',
        color='Status',
        hover_name='Client Name',
        title="Escrow Retainers vs. Active Unbilled WIP Work (Bubble Size = Days Idle)",
        color_discrete_map={'Healthy': '#10B981', 'WIP Leakage Risk': '#D97706', 'IOLTA Trust Deficit': '#DC2626'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ----------------------------------------------------
# 7. INTERACTIVE DRILL-DOWN DATA TABLE
# ----------------------------------------------------
st.markdown("### 🔎 Full Case File Audit Explorer")
st.write("Filter, sort, and investigate real-time client files across underlying practice infrastructure:")

# Formatting styling for visual UI dataframe presentation
styled_df = filtered_df.copy()
styled_df['Unbilled WIP ($)'] = styled_df['Unbilled WIP ($)'].map('${:,.2f}'.format)
styled_df['IOLTA Trust Balance ($)'] = styled_df['IOLTA Trust Balance ($)'].map('${:,.2f}'.format)
styled_df['Upcoming Retainer Expenses ($)'] = styled_df['Upcoming Retainer Expenses ($)'].map('${:,.2f}'.format)

st.dataframe(styled_df, use_container_width=True)
