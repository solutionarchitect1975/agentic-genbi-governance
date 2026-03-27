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

# --- 2. Integrated CSS Engine (High-Contrast "Jones" Theme) ---
def apply_enterprise_styling():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }

        /* Force High Contrast Text */
        h1, h2, h3, h4, p, span, label, .stMetric div { color: #1E293B !important; }

        /* Dark Enterprise Header */
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
        [data-testid="stMetric"], .stVerticalBlock > div > div[style*="border"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }

        /* Alternating Row Colors for Dataframes */
        [data-testid="stDataFrame"] div[data-testid="stTableRegion"] { border-radius: 8px; overflow: hidden; }

        /* Blue Primary Buttons */
        .stButton>button {
            background-color: #2563EB !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            width: 100%;
            transition: all 0.3s ease;
        }
        .stButton>button:hover { background-color: #1D4ED8 !important; transform: translateY(-1px); }

        /* AI Chat/Bot UI */
        div[data-testid="stChatMessage"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

apply_enterprise_styling()

# --- 3. Core AI & Connection Logic ---
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
llm = ChatOpenAI(model="gpt-4o", temperature=0)

@st.cache_data(ttl=0) 
def get_snowflake_metadata():
    try:
        conn = snowflake.connector.connect(**st.secrets["snowflake"])
        db, schema = st.secrets['snowflake']['database'], st.secrets['snowflake']['schema']
        query = f"SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM {db}.INFORMATION_SCHEMA.COLUMNS WHERE UPPER(TABLE_SCHEMA) = UPPER('{schema}')"
        df = pd.read_sql(query, conn)
        conn.close()
        df.columns = [col.upper() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Snowflake Error: {e}"); return None
                    
@st.cache_data(ttl=300)
def get_databricks_metadata():
    try:
        conn = sql.connect(**st.secrets["databricks"])
        query = "SELECT table_name, column_name, data_type FROM system.information_schema.columns WHERE table_schema = 'raw_kitchen_db'"
        df = pd.read_sql(query, conn)
        conn.close()
        df.columns = [col.upper() for col in df.columns] 
        return df
    except Exception as e:
        st.error(f"Databricks Error: {e}"); return None

def get_real_time_risks(sf_df, db_df):
    """Aggregates metadata and uses LLM to identify multi-cloud risks."""
    context = ""
    if sf_df is not None: context += f"--- Snowflake Metadata ---\n{sf_df.head(20).to_string()}\n"
    if db_df is not None: context += f"--- Databricks Metadata ---\n{db_df.head(20).to_string()}\n"
    
    prompt = PromptTemplate.from_template(
        "You are a Data Governance Agent. Review metadata for PII risks. "
        "Return ONLY a pipe-separated table: Source | Table | Column | Risk | Reason. "
        "Risk levels: High, Medium. \n\nContext:\n{context}"
    )
    response = llm.invoke(prompt.format(context=context))
    try:
        lines = [line.strip() for line in response.content.split('\n') if '|' in line and '---' not in line and 'Source' not in line]
        parsed = [l.split('|') for l in lines]
        return pd.DataFrame([p for p in parsed if len(p) == 5], columns=["Source", "Table", "Column", "Risk", "Reason"])
    except: return pd.DataFrame()

# --- 4. Dashboard UI Rendering ---

# Header Bar
st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 22px; font-weight: 800; letter-spacing: -1px;">🛡️ AGENTIC GENBI</span>
            <span style="margin-left: 15px; border-left: 1px solid #334155; padding-left: 15px; opacity: 0.7; font-size: 13px; font-weight: 400;">GOVERNANCE CONTROL TOWER</span>
        </div>
        <div style="font-size: 11px; opacity: 0.8; font-weight: 600;">EST. 2026 | FOLSOM, CA HQ</div>
    </div>
""", unsafe_allow_html=True)

st.title("Dashboard")
st.caption("Automated Multi-Cloud Discovery & ISO 42001 Compliance Monitoring")

# KPI Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Data Sources", "2", "Active")
m2.metric("Tables Monitored", "1,772", "12 Today")
m3.metric("Compliance Rate", "64%", "-5%", delta_color="inverse")
m4.metric("Risk Anomalies", "18", "Requires Action", delta_color="inverse")

# Visuals Row
v_col1, v_col2 = st.columns([1, 2])
chart_style = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', template='plotly_white', margin=dict(t=10, b=10, l=10, r=10))

with v_col1:
    with st.container(border=True):
        st.subheader("Required Attention")
        fig_pie = px.pie(values=[40, 23, 37], names=['Expiring', 'Non-Compliant', 'No Response'], hole=0.6, color_discrete_sequence=['#F59E0B', '#EF4444', '#6366F1'])
        fig_pie.update_layout(**chart_style, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

with v_col2:
    with st.container(border=True):
        st.subheader("Compliance Status Overview")
        fig_bar = px.bar(x=['Compliant', 'Waived', 'Non-compliant', 'Expired', 'Awaiting'], y=[19, 7, 61, 3, 11], color=['C','W','N','E','A'], color_discrete_sequence=['#10B981', '#8B5CF6', '#EF4444', '#94A3B8', '#F59E0B'])
        fig_bar.update_layout(**chart_style, showlegend=False, xaxis_title=None, yaxis_title="Records")
        st.plotly_chart(fig_bar, use_container_width=True)

# Centralized Risk Scorecard
st.write("")
st.subheader("🚨 Centralized Risk Scorecard")
if st.button("🚀 Run Global Risk Assessment", type="primary"):
    sf_meta = get_snowflake_metadata()
    db_meta = get_databricks_metadata()
    st.session_state.risk_df = get_real_time_risks(sf_meta, db_meta)

if "risk_df" in st.session_state and not st.session_state.risk_df.empty:
    with st.container(border=True):
        st.dataframe(st.session_state.risk_df.style.applymap(lambda x: 'background-color: #FEE2E2; color: #991B1B; font-weight: bold;' if x == 'High' else '', subset=['Risk']), use_container_width=True, hide_index=True)
        st.caption("AI Agent aggregated findings across Snowflake Horizon and Unity Catalog.")

st.divider()

# Cloud Discovery Section
st.subheader("Cloud Discovery Agents")
d_col1, d_col2 = st.columns(2)

with d_col1:
    with st.container(border=True):
        st.header("❄️ Snowflake")
        if st.button("Deploy Snowflake Agent"):
            df = get_snowflake_metadata()
            if df is not None:
                st.dataframe(df.head(10), use_container_width=True)
                with st.chat_message("assistant", avatar="🛡️"):
                    st.write("Snowflake estate mapped. Found potential PII in `SALES` schema.")

with d_col2:
    with st.container(border=True):
        st.header("🧱 Databricks")
        if st.button("Deploy Databricks Agent"):
            df = get_databricks_metadata()
            if df is not None:
                st.dataframe(df.head(10), use_container_width=True)
                with st.chat_message("assistant", avatar="🛡️"):
                    st.write("Unity Catalog scanned. Anomalies detected in `RAW_KITCHEN` database.")

# Sidebar Admin Console
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=60)
    st.title("Admin Console")
    st.info("System Status: Healthy")
    st.divider()
    st.write("### Modules")
    if st.button("📜 Policy Management"): st.toast("Under Construction")
    if st.button("🔍 Audit History"): st.toast("Under Construction")