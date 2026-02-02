import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page Config
st.set_page_config(layout="wide", page_title="TruRisk Summary")

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #e9ecef;
    }
    .risk-value {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING & SIDEBAR ---
def load_data():
    return pd.read_csv('data.csv')

st.sidebar.header("Global Risk Factors")
cisa_kev = st.sidebar.number_input("CISA KEV", value=58500)
ransomware = st.sidebar.number_input("Ransomware", value=41000)
threat_actors = st.sidebar.number_input("Threat Actors", value=442)
weaponized = st.sidebar.number_input("Weaponized Vulns", value=175000)

st.sidebar.divider()
st.sidebar.subheader("Edit Entity Data")
df = load_data()
# This allows you to edit the CSV data directly in the app
edited_df = st.sidebar.data_editor(df, num_rows="dynamic")

# --- MAIN LAYOUT ---
st.title("TruRisk™ Summary")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("TruRisk™ Score")
    
    # Calculate an average score based on the data
    avg_score = int(edited_df['TruRisk_Score'].mean())
    
    # Gauge Chart
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = avg_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Low", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [0, 1000], 'tickwidth': 1},
            'bar': {'color': "#a56215"},
            'steps': [
                {'range': [0, 499], 'color': "#eeeeee"},
                {'range': [500, 699], 'color': "#dddddd"},
                {'range': [700, 849], 'color': "#cccccc"},
                {'range': [850, 1000], 'color': "#bbbbbb"}
            ],
        }
    ))
    fig_gauge.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Risk Factor Cards
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='metric-card'>CISA KEV<br><span class='risk-value'>{cisa_kev/1000:.1f}K</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-card'>Threat Actors<br><span class='risk-value'>{threat_actors}</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'>Ransomware<br><span class='risk-value'>{ransomware/1000:.1f}K</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-card'>Weaponized<br><span class='risk-value'>{weaponized/1000:.1f}K</span></div>", unsafe_allow_html=True)

with col2:
    st.subheader("Business Entities")
    
    # Multi-axis Chart
    fig_entities = make_subplots(specs=[[{"secondary_y": True}]])

    # Bars for Business Value
    fig_entities.add_trace(
        go.Bar(x=edited_df['Entity'], y=edited_df['Value_Millions'], name="Business Value ($M)", marker_color='#004baf'),
        secondary_y=False,
    )

    # Line for TruRisk Score
    fig_entities.add_trace(
        go.Scatter(x=edited_df['Entity'], y=edited_df['TruRisk_Score'], name="TruRisk™ Score", mode='lines+markers', line=dict(color='red', width=3)),
        secondary_y=True,
    )

    # Line for Risk Appetite
    fig_entities.add_trace(
        go.Scatter(x=edited_df['Entity'], y=edited_df['Risk_Appetite'], name="Risk Appetite", mode='lines+markers', line=dict(color='#00c4ff', dash='dash')),
        secondary_y=True,
    )

    fig_entities.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500
    )
    
    fig_entities.update_yaxes(title_text="Business Value ($)", secondary_y=False)
    fig_entities.update_yaxes(title_text="TruRisk Score", range=[0, 1000], secondary_y=True)

    st.plotly_chart(fig_entities, use_container_width=True)

# Save Button
if st.sidebar.button("Save Changes to CSV"):
    edited_df.to_csv('data.csv', index=False)

    st.sidebar.success("Saved!")
