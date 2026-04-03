import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
# 1. Page Configuration
st.set_page_config(page_title="Biomedical Asset Tracker", layout="wide", page_icon="🏥")

st.title("🏥 Healthcare Asset Uptime & Reliability Dashboard")
st.markdown("---")
# 2. Data Loading Function
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    
    # CLEANING STEP: Standardize column names
    df.columns = df.columns.str.strip().str.lower()
    
    # DATA SANITIZATION
    df['maint_cost_abs'] = df['maintenance_cost'].abs()
    
    # 3. Logic: Calculate Reliability Metrics
    df['calculated_mtbf'] = ((df['age'] * 8760) - df['downtime']) / df['maintenance_frequency']
    df['calculated_mttr'] = df['downtime'] / df['maintenance_frequency']
    
    # --- ADD THIS LINE: The missing health_index calculation ---
    # Calculates health as a percentage of operational uptime
    df['health_index'] = (1 - (df['downtime'] / (df['age'] * 8760))) * 100
    
    # MAPPING LOGIC: Assigning PAM Zones
    def assign_pam_zone(id_str):
        if 'MD01' in id_str: return 'Central (KCH PAM)'
        elif 'MD03' in id_str: return 'South (QECH PAM)'
        elif 'MD05' in id_str: return 'South-East (Zomba PAM)'
        else: return 'North (MZRH PAM)'
        
    df['pam_zone'] = df['device_id'].apply(assign_pam_zone)
    return df

try:
    data = load_data()
    # Logic for risk score based on uptime/reliability
    data['risk_score'] = data['calculated_mttr'] / data['calculated_mtbf']

except Exception as e:
    # --- PROFESSIONAL ERROR HANDLING ---
    st.markdown("---")
    st.error("🚨 **System Interruption Detected**")
    
    col_err1, col_err2 = st.columns([2, 1])
    
    with col_err1:
        st.warning("""
            **Possible Causes:**
            * The data source `data.csv` is missing or corrupted.
            * A required library (like `matplotlib`) is not installed.
            * There is a mismatch in the CSV column headers.
        """)
    
    with col_err2:
        st.info("💡 **BioFix Support:** If this persists, verify your local environment setup or contact the system administrator.")

    # Technical Debugger (Collapsed so it doesn't ruin the UI)
    with st.expander("Show Technical Traceback"):
        st.code(f"Runtime Error: {e}")
    
    st.stop()

else:
    # --- START OF SIDEBAR COMMAND CENTER ---
    with st.sidebar:
        # 1. User Profile & System Status
        st.markdown("### 👨‍🔧 User Profile")
        # Branding for Chief Biomedical Consultant
        st.info(f"**Frank Kasunda**\n\nChief Biomedical Consultant")
    
    # Live Timestamp for CAT timezone
    now = datetime.datetime.now()
    st.caption(f"📅 **System Date:** {now.strftime('%d %B %Y')}")
    st.caption(f"⏰ **Last Sync:** {now.strftime('%H:%M:%S')} CAT")
    
    st.markdown("---")

    # 2. Filter Options
    st.header("🔍 Filter Options")

    device_list = ["All"] + sorted(list(data['device_type'].unique()))
    selected_device = st.selectbox("Select Equipment Type", device_list)

    mfr_list = ["All"] + sorted(list(data['manufacturer'].unique()))
    selected_mfr = st.selectbox("Select Manufacturer", mfr_list)
    
    st.markdown("---")

    # 3. National PAM Pulse (Live Fleet Metrics)
    st.subheader("📡 National PAM Pulse")
    
    total_assets_count = len(data)
    overall_uptime = data['health_index'].mean()
    at_risk_count = len(data[data['health_index'] < 75])

    st.metric("Total Fleet Size", f"{total_assets_count} Units")
    st.metric(
        "National Health Index", 
        f"{overall_uptime:.1f}%", 
        delta=f"{overall_uptime - 85:.1f}% vs Target"
    )
    
    st.markdown("---")

    # 4. Operations & Exports
    st.subheader("🛠️ Operations")
    
    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Technical Audit",
        data=csv,
        file_name='PAM_Asset_Audit_Report.csv',
        mime='text/csv',
        help="Download the full technical log for Ministry of Health reporting."
    )
    
    st.caption("Reports are formatted for PAM compliance.")

# --- END OF SIDEBAR (Notice the indentation moves back to the left by one level) ---

# --- BRANDED PROFESSIONAL HEADER ---
# --- BRANDED PROFESSIONAL HEADER ---
header_col1, header_col2, header_col3 = st.columns([1, 3, 1])

with header_col1:
    # Displaying your uploaded emblem
    st.image("Healthcare asset uptime emblem.PNG", width=120)

with header_col2:
    st.markdown(f"""
        <h1 style='margin-bottom: 0; padding-top: 10px;'>Healthcare Asset Uptime & Reliability</h1>
        <p style='font-size: 1.1rem; color: #808495; margin-top: 0;'>
            Strategic PAM Intelligence | <b>BioFix Hub</b>
        </p>
    """, unsafe_allow_html=True)

with header_col3:
    # Enterprise Status Badge
    st.markdown("""
        <div style='background-color: #1e2130; border-radius: 10px; padding: 10px; border: 1px solid #3d4051; text-align: center; margin-top: 15px;'>
            <span style='color: #00ff00; font-size: 0.7rem;'>● SYSTEM LIVE</span><br>
            <b style='font-size: 0.8rem;'>Lilongwe Hub</b>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 0; margin-bottom: 25px; border: 1px solid #3d4051;'>", unsafe_allow_html=True)

if at_risk_count > 0:
    st.error(f"⚠️ {at_risk_count} Assets Below Health Target")
else:
    st.success("✅ All Systems Optimal")

# --- DATA FILTERING LOGIC (The missing piece) ---
# This creates the 'filtered_df' that your charts are looking for
filtered_df = data.copy()

if selected_device != "All":
    filtered_df = filtered_df[filtered_df['device_type'] == selected_device]

if selected_mfr != "All":
    filtered_df = filtered_df[filtered_df['manufacturer'] == selected_mfr]
# -----------------------------------------------
# 4.5 GEOSPATIAL VIEW: PAM Center Distribution
st.subheader("📍 Physical Assets Management (PAM) Distribution")

# Coordinates for Malawi's major PAM Hubs
malawi_map_data = pd.DataFrame({
    'lat': [-13.96, -15.78, -11.44, -15.38],
    'lon': [33.77, 35.00, 34.01, 35.33],
    'center': ['KCH PAM', 'QECH PAM', 'MZRH PAM', 'Zomba PAM']
})

st.map(malawi_map_data)
st.caption("Centralized PAM Centers managing the current filtered asset fleet.")
st.markdown("---")

# 5. Visualizations (Using the Filtered Data)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Reliability Matrix")
    fig_scatter = px.scatter(
        filtered_df, 
        x="calculated_mtbf", 
        y="calculated_mttr", 
        color="device_type", 
        size="maint_cost_abs", 
        hover_name="model",
        labels={"calculated_mtbf": "Reliability (MTBF)", "calculated_mttr": "Repair Time (MTTR)"},
        title="MTBF vs MTTR (Bubble size = Cost)"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_right:
    # First: The Downtime Bar Chart
    st.subheader("Downtime by Manufacturer")
    fig_bar = px.bar(
        filtered_df, 
        x="manufacturer", 
        y="downtime", 
        color="device_type",
        title="Total Downtime per Manufacturer"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Second: The Orange Health Distribution (FICO-style)
    st.subheader("Asset Health Distribution")
    fig_hist = px.histogram(
        filtered_df, 
        x="health_index", 
        nbins=10,
        title="Fleet Health Spread (High Score = Best)",
        color_discrete_sequence=['#FF8C00'] 
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# PAM ZONE PERFORMANCE SUMMARY
st.write("### 🏢 PAM Zone Performance Summary")
pam_summary = filtered_df.groupby('pam_zone').agg({
    'device_id': 'count',
    'health_index': 'mean',
    'maintenance_cost': 'sum'
}).rename(columns={'device_id': 'Total Assets', 'health_index': 'Avg Health %'})

# Styled table to highlight performance
st.table(pam_summary.style.background_gradient(subset=['Avg Health %'], cmap='RdYlGn'))

# 5.5 STRATEGIC ANALYSIS: Vendor Accountability Scorecard
st.markdown("---")
st.subheader("📊 Vendor Accountability & Performance Scorecard")

# Logic: Group by manufacturer to see who is costing the most vs performing best
vendor_stats = filtered_df.groupby('manufacturer').agg({
    'calculated_mtbf': 'mean',
    'calculated_mttr': 'mean',
    'maintenance_cost': 'sum',
    'device_id': 'count'
}).rename(columns={'device_id': 'Asset Count'})

# Calculate a custom "Performance Score" (High MTBF + Low MTTR is good)
# We normalize this to a simple index for the recruiter to see your math skills
vendor_stats['Reliability Score'] = (vendor_stats['calculated_mtbf'] / vendor_stats['calculated_mttr']).round(2)

# Displaying the scorecard
v_col1, v_col2 = st.columns([1, 2])

with v_col1:
    st.write("### Strategic KPIs")
    best_vendor = vendor_stats['Reliability Score'].idxmax()
    st.success(f"**Top Performer:** {best_vendor}")
    st.info("The Reliability Score represents the ratio of Uptime vs. Repair Speed.")

with v_col2:
    # Use a styled dataframe to highlight high costs
    st.dataframe(vendor_stats.style.background_gradient(subset=['maintenance_cost'], cmap='Reds'))

# 6. Raw Data Inspection
with st.expander("View Filtered Technical Logs"):
    st.write("Below is the asset data based on your current filters:")
    st.dataframe(filtered_df)

# --- FOOTER & BRANDING ---
st.markdown("---")
footer_col1, footer_col2 = st.columns([2, 1])

with footer_col1:
    st.caption("🔍 **Clinical Engineering Insights:** Reliability metrics are calculated based on a 24/7 (8760h) operational cycle.")
    st.write("© 2026 | Designed by **Frank Kasunda**")
    
with footer_col2:
    st.info("🚀 **Powered by BioFix Hub**")
