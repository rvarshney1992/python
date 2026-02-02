import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page Config
st.set_page_config(layout="wide", page_title="TruRisk™ Summary")

# --- CUSTOM CSS FOR HIGH-FIDELITY CARDS ---
st.markdown("""
    <style>
    /* Summary Metric Cards */
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #e9ecef;
        margin-bottom: 10px;
    }
    .risk-value { font-size: 20px; font-weight: bold; color: #1f77b4; }
    
    /* Detailed Entity Cards */
    .entity-card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .risk-border-high { border-left: 8px solid #d32f2f; }
    .risk-border-medium { border-left: 8px solid #f57c00; }
    .risk-border-low { border-left: 8px solid #fbc02d; }
    
    .label-text { color: #666; font-size: 0.8rem; margin-top: 4px; }
    .value-text { font-size: 1.4rem; font-weight: bold; }
    .trend-up { color: #1976d2; font-weight: bold; }
    .trend-down { color: #d32f2f; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING ---
def load_data():
    try:
        return pd.read_csv('data.csv')
    except Exception:
        # Initial dummy data if file is missing
        data = {
            'Entity': ['Employee Portal', 'Sales Portal', 'Inventory', 'Checkout App'],
            'Sub_Label': ['BusinessApp: Empl...', 'BusinessApp: Sale...', 'LinuxHostname', 'BusinessApp: App007'],
            'Value_Millions': [599, 175, 2, 80],
            'TruRisk_Score': [836, 786, 652, 412],
            'Risk_Appetite': [430, 300, 500, 250],
            'Trend': [219, -1, -1, -49]
        }
        return pd.DataFrame(data)

df = load_data()

# --- SIDEBAR: LIVE EDITOR ---
st.sidebar.header("Global Risk Factors")
cisa_kev = st.sidebar.number_input("CISA KEV", value=58500)
ransomware = st.sidebar.number_input("Ransomware", value=41000)
threat_actors = st.sidebar.number_input("Threat Actors", value=442)
weaponized = st.sidebar.number_input("Weaponized Vulns", value=175000)

st.sidebar.divider()
st.sidebar.subheader("Entity Data Editor")
edited_df = st.sidebar.data_editor(df, num_rows="dynamic")

if st.sidebar.button("Save Changes to CSV"):
    edited_df.to_csv('data.csv', index=False)
    st.sidebar.success("Changes saved to data.csv!")

# --- TOP SECTION: SUMMARY DASHBOARD ---
st.title("TruRisk™ Summary")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("TruRisk™ Score")
    avg_score = int(edited_df['TruRisk_Score'].mean()) if not edited_df.empty else 0
    
    # Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = avg_score,
        gauge = {
            'axis': {'range': [0, 1000]},
            'bar': {'color': "#a56215"},
            'steps': [
                {'range': [0, 500], 'color': "#eeeeee"},
                {'range': [500, 750], 'color': "#dddddd"},
                {'range': [750, 1000], 'color': "#cccccc"}
            ],
        }
    ))
    fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Risk Factor Grid
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='metric-card'>CISA KEV<br><span class='risk-value'>{cisa_kev/1000:.1f}K</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-card'>Threat Actors<br><span class='risk-value'>{threat_actors}</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'>Ransomware<br><span class='risk-value'>{ransomware/1000:.1f}K</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-card'>Weaponized<br><span class='risk-value'>{weaponized/1000:.1f}K</span></div>", unsafe_allow_html=True)

with col2:
    st.subheader("Business Entities Overview")
    # Multi-axis Chart (Value vs Score vs Appetite)
    fig_entities = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_entities.add_trace(go.Bar(
        x=edited_df['Entity'], 
        y=edited_df['Value_Millions'], 
        name="Business Value ($M)", 
        marker_color='#004baf'
    ), secondary_y=False)
    
    fig_entities.add_trace(go.Scatter(
        x=edited_df['Entity'], 
        y=edited_df['TruRisk_Score'], 
        name="TruRisk™ Score", 
        mode='lines+markers', 
        line=dict(color='red', width=3)
    ), secondary_y=True)
    
    fig_entities.add_trace(go.Scatter(
        x=edited_df['Entity'], 
        y=edited_df['Risk_Appetite'], 
        name="Risk Appetite", 
        mode='lines+markers', 
        line=dict(color='#00c4ff', dash='dash')
    ), secondary_y=True)
    
    fig_entities.update_layout(height=450, legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"))
    st.plotly_chart(fig_entities, use_container_width=True)

st.divider()

# --- BOTTOM SECTION: TOP RISKY LIST ---
st.subheader("Business Entities: Top Risky")

# Sort descending to show highest risk first
risky_df = edited_df.sort_values(by="TruRisk_Score", ascending=False)

for _, row in risky_df.iterrows():
    # Dynamic Class and Label Selection
    if row['TruRisk_Score'] > 700:
        b_class, color, lvl = "risk-border-high", "#d32f2f", "High"
    elif row['TruRisk_Score'] > 450:
        b_class, color, lvl = "risk-border-medium", "#f57c00", "Medium"
    else:
        b_class, color, lvl = "risk-border-low", "#fbc02d", "Low"

    t_arrow = "↑" if row['Trend'] > 0 else "↓"
    t_class = "trend-up" if row['Trend'] > 0 else "trend-down"

    # Card HTML Rendering
    st.markdown(f"""
        <div class="entity-card {b_class}">
            <div style="flex: 2;">
                <div style="font-size: 1.3rem; font-weight: bold; color: #333;">{row['Entity']}</div>
                <div class="label-text" style="background: #f0f0f0; display: inline-block; padding: 2px 8px; border-radius: 4px;">{row['Sub_Label']}</div>
            </div>
            <div style="flex: 1; text-align: center; border-left: 1px solid #eee;">
                <div class="value-text">${row['Value_Millions']}M</div>
                <div class="label-text">Business Value</div>
            </div>
            <div style="flex: 1; text-align: center;">
                <div style="font-size: 1.6rem; font-weight: bold; color: {color};">{row['TruRisk_Score']}</div>
                <div style="font-size: 0.8rem; font-weight: bold; color: #666;">{lvl}</div>
                <div class="label-text">0 &nbsp;&nbsp;&nbsp; 1000</div>
            </div>
            <div style="flex: 1; text-align: center;">
                <div style="font-weight: bold; font-size: 1.1rem;">{row['Risk_Appetite']}</div>
                <div class="label-text">Risk Appetite</div>
            </div>
            <div style="flex: 1; text-align: right; border-left: 1px solid #eee;">
                <div class="{t_class}" style="font-size: 1.1rem;">{t_arrow} {abs(row['Trend'])}</div>
                <div class="label-text">Since last 7 days</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

