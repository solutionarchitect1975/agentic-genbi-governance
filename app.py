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

# --- 2. Custom CSS Engine (Fixes Visibility & "Jones" Aesthetic) ---
def apply_styling():
    st.markdown("""
        <style>
        /* 1. Global Reset & Typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        .stApp {
            background-color: #F8FAFC;
            font-family: 'Inter', sans-serif;
        }

        /* 2. Force High Contrast on All Text */
        h1, h2, h3, h4, p, span, label, .stMetric div {
            color: #1E293B !important;
        }

        /* 3. The Enterprise Header Bar */
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

        /* 4. KPI Tile Styling (White Cards) */
        [data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }
        [data-testid="stMetricLabel"] {
            color: #64748B !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* 5. Blue Primary Buttons (Modern UI) */
        .stButton>button {
            background-color: #2563EB !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            width: 100%;
            transition: background 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #1D4ED8 !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
        }

        /* 6. AI Chat/Bot UI bubbles */
        div[data-testid="stChatMessage"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
        }
        
        /* 7. Sidebar Cleanup */
        [data-testid="stSidebar"] {
            background-color: #F1F5F9;
            border-right: 1px solid #E2E8F0;
        }
        </style>
    """, unsafe_allow_html=True)

apply_styling()

# --- 3. Core Logic & Connections ---
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def classify_metadata_with_llm(metadata_df, source_name):
    grouped = metadata_df.groupby('TABLE_NAME')['COLUMN_NAME'].apply(list).to_dict()
    schema_context = "".join([f"Table: {k}\nCols: {', '.join(v)}\n\n" for k,v in grouped.items()])
    
    prompt = PromptTemplate.from_template(
        "You are a Data Governance Agent. Summarize PII risks for {source}. "
        "Highlight high-risk anomalies (SSN, Credit Cards) clearly.\n\nContext:\n{schema_context}"
    )
    return (prompt | llm).invoke({"source": source_name, "schema_context": schema_context}).content

@st.cache_data(ttl=300)
def get_mock_data(source):
    # Simulated data for when real connection is bypassed for UI testing
    return pd.DataFrame({
        'TABLE_NAME': ['USERS', 'ORDERS', 'SALES_HISTORY'],
        'COLUMN_NAME': ['EMAIL', 'ORDER_ID', 'SSN_HASH'],
        'DATA_TYPE': ['VARCHAR', 'INT', 'VARCHAR']
    })

# --- 4. Render UI ---

# Enterprise Header
st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 22px; font-weight: 800;">🛡️ AGENTIC GENBI</span>
            <span style="margin-left: 15px; border-left: 1px solid #334155; padding-left: 15px; opacity: 0.7; font-size: 14px;">CONTROL TOWER</span>
        </div>
        <div style="font-size: 12px; opacity: 0.8; font-weight: 600;">
            EST. 2026 | FOLSOM, CA HQ
        </div>
    </div>
""", unsafe_allow_html=True)

st.title("Dashboard")
st.caption("A cross-cloud summary of compliance across your properties")

# Governance KPI Tiles
m1, m2, m3, m4 = st.columns(4)
m1.metric("Data Sources", "2", "Active")
m2.metric("Tables Monitored", "1,772", "12 Today")
m3.metric("Compliance Rate", "64%", "-5% MoM", delta_color="inverse")
m4.metric("Risk Anomalies", "18", "Requires Action", delta_color="inverse")

st.write("")

# Visuals Section
v_col1, v_col2 = st.columns([1, 2])

with v_col1:
    with st.container(border=True):
        st.subheader("Required Attention")
        fig_pie = px.pie(
            values=[40, 23, 37], 
            names=['Expiring', 'Non-Compliant', 'No Response'], 
            hole=0.6, 
            color_discrete_sequence=['#F59E0B', '#EF4444', '#6366F1'],
            template="plotly_white"
        )
        fig_pie.update_layout(showlegend=False, margin=dict(t=20, b=20, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

with v_col2:
    with st.container(border=True):
        st.subheader("Compliance Status Overview")
        data = {'Status': ['Compliant', 'Waived', 'Non-compliant', 'Expired', 'Awaiting'], 'Value': [19, 7, 61, 3, 11]}
        fig_bar = px.bar(
            data, x='Status', y='Value', color='Status', 
            color_discrete_sequence=['#10B981', '#8B5CF6', '#EF4444', '#94A3B8', '#F59E0B'],
            template="plotly_white"
        )
        fig_bar.update_layout(showlegend=False, margin=dict(t=20, b=20, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# Deployment Section
st.subheader("Cross-Cloud Discovery & Classification")
d_col1, d_col2 = st.columns(2)

with d_col1:
    with st.container(border=True):
        st.header("❄️ Snowflake")
        st.caption("Monitoring: PROD_DINING_ROOM_DB")
        if st.button("Deploy AI Agent", key="sf_btn"):
            with st.spinner("Mapping Snowflake estate..."):
                df = get_mock_data("Snowflake") # Replace with get_snowflake_metadata()
                st.dataframe(df.style.set_properties(**{'background-color': '#F8FAFC', 'color': '#1E293B'}), use_container_width=True)
                
                with st.chat_message("assistant", avatar="🛡️"):
                    st.markdown("**AI Agent Recommendation:**")
                    st.write(classify_metadata_with_llm(df, "Snowflake"))
                
                st.button("Approve & Write-Back", key="sf_appr")

with d_col2:
    with st.container(border=True):
        st.header("🧱 Databricks")
        st.caption("Monitoring: raw_kitchen_db")
        if st.button("Deploy AI Agent", key="db_btn"):
            with st.spinner("Mapping Databricks Unity Catalog..."):
                df = get_mock_data("Databricks") # Replace with get_databricks_metadata()
                st.dataframe(df.style.set_properties(**{'background-color': '#F8FAFC', 'color': '#1E293B'}), use_container_width=True)
                
                with st.chat_message("assistant", avatar="🛡️"):
                    st.markdown("**AI Agent Recommendation:**")
                    st.write(classify_metadata_with_llm(df, "Databricks"))

                st.button("Approve & Write-Back", key="db_appr")

# --- 5. Modular Sidebar for Future Growth ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=80)
    st.title("Admin Console")
    st.info("System Status: Healthy")
    
    st.divider()
    st.write("### Governance Modules")
    if st.button("📜 Policy Management"):
        st.toast("Module Under Construction - ISO 42001 Mapping Coming Soon")
    if st.button("🔍 Audit History"):
        st.toast("Module Under Construction")