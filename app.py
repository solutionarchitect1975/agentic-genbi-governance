import streamlit as st
import snowflake.connector
from databricks import sql
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import pandas as pd
import os
import plotly.express as px

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Agentic GenBI | Governance Tower", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Custom CSS Engine (Enterprise UI) ---
def apply_styling():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        .stApp {
            background-color: #F8FAFC;
            font-family: 'Inter', sans-serif;
        }

        /* High Contrast Text */
        h1, h2, h3, h4, p, span, label, .stMetric div {
            color: #1E293B !important;
        }

        /* Enterprise Header Bar */
        .main-header {
            background-color: #0F172A;
            padding: 1.2rem 2rem;
            margin: -6rem -5rem 2rem -5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: white !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .main-header span { color: white !important; }

        /* KPI & Card Styling */
        [data-testid="stMetric"], .risk-card {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }

        /* Risk Level Badges */
        .badge-high { background-color: #FEE2E2; color: #991B1B; padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 12px; }
        .badge-med { background-color: #FEF3C7; color: #92400E; padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 12px; }

        /* Primary Buttons */
        .stButton>button {
            background-color: #2563EB !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

apply_styling()

# --- 3. Data & Logic ---
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def get_combined_risks():
    """Generates a centralized risk scorecard from both environments."""
    return pd.DataFrame([
        {"Source": "❄️ Snowflake", "Table": "SALES_HISTORY", "Column": "SSN_HASH", "Risk": "High", "Reason": "Likely unmasked PII"},
        {"Source": "❄️ Snowflake", "Table": "USERS", "Column": "EMAIL", "Risk": "Medium", "Reason": "Contact information"},
        {"Source": "🧱 Databricks", "Table": "RAW_KITCHEN", "Column": "CREDIT_CARD", "Risk": "High", "Reason": "PCI Compliance Breach"},
        {"Source": "🧱 Databricks", "Table": "EMPLOYEES", "Column": "DOB", "Risk": "Medium", "Reason": "Age-related PII"}
    ])

# --- 4. Render UI ---

# Header
st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 22px; font-weight: 800;">🛡️ AGENTIC GENBI</span>
            <span style="margin-left: 15px; border-left: 1px solid #334155; padding-left: 15px; opacity: 0.7; font-size: 14px;">CONTROL TOWER</span>
        </div>
        <div style="font-size: 12px; opacity: 0.8; font-weight: 600;">EST. 2026 | FOLSOM, CA HQ</div>
    </div>
""", unsafe_allow_html=True)

st.title("Dashboard")
st.caption("A summary of compliance across your multi-cloud data estate")

# KPI Section
m1, m2, m3, m4 = st.columns(4)
m1.metric("Data Sources", "2", "Active")
m2.metric("Tables Monitored", "1,772", "12 Today")
m3.metric("Compliance Rate", "64%", "-5%", delta_color="inverse")
m4.metric("Risk Anomalies", "18", "Requires Action", delta_color="inverse")

# Visuals Section
v_col1, v_col2 = st.columns([1, 2])
with v_col1:
    with st.container(border=True):
        st.subheader("Required Attention")
        fig_pie = px.pie(values=[40, 23, 37], names=['Expiring', 'Non-Compliant', 'No Response'], hole=0.6, 
                         color_discrete_sequence=['#F59E0B', '#EF4444', '#6366F1'], template="plotly_white")
        fig_pie.update_layout(showlegend=False, margin=dict(t=20, b=20, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

with v_col2:
    with st.container(border=True):
        st.subheader("Compliance Status Overview")
        data = {'Status': ['Compliant', 'Waived', 'Non-compliant', 'Expired', 'Awaiting'], 'Value': [19, 7, 61, 3, 11]}
        fig_bar = px.bar(data, x='Status', y='Value', color='Status', 
                         color_discrete_sequence=['#10B981', '#8B5CF6', '#EF4444', '#94A3B8', '#F59E0B'], template="plotly_white")
        fig_bar.update_layout(showlegend=False, margin=dict(t=20, b=20, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

# --- NEW: Centralized Risk Scorecard ---
st.write("")
st.subheader("🚨 Centralized Risk Scorecard")
with st.container(border=True):
    risk_df = get_combined_risks()
    
    # Custom styling for the scorecard table
    def style_risk(val):
        color = '#991B1B' if val == 'High' else '#92400E'
        bg = '#FEE2E2' if val == 'High' else '#FEF3C7'
        return f'background-color: {bg}; color: {color}; font-weight: bold; border-radius: 4px;'

    st.dataframe(
        risk_df.style.applymap(style_risk, subset=['Risk'])
        .set_properties(**{'background-color': '#FFFFFF', 'color': '#1E293B', 'border-color': '#E2E8F0'}),
        use_container_width=True,
        hide_index=True
    )
    st.caption("AI Agent aggregated findings from Snowflake Horizon and Databricks Unity Catalog.")

st.divider()

# Discovery Section
st.subheader("Cross-Cloud Discovery & Classification")
d_col1, d_col2 = st.columns(2)

with d_col1:
    with st.container(border=True):
        st.header("❄️ Snowflake")
        if st.button("Deploy AI Agent", key="sf_btn"):
            st.info("Discovery Active: Scanning PROD_DINING_ROOM_DB...")
            # Logic for metadata and LLM classification would go here

with d_col2:
    with st.container(border=True):
        st.header("🧱 Databricks")
        if st.button("Deploy AI Agent", key="db_btn"):
            st.info("Discovery Active: Scanning raw_kitchen_db...")
            # Logic for metadata and LLM classification would go here

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=60)
    st.title("Admin Console")
    st.divider()
    st.write("### Modules")
    st.button("📜 Policy Management")
    st.button("🔍 Audit History")