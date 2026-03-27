import streamlit as st
import snowflake.connector
from databricks import sql
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import pandas as pd
import os
import plotly.express as px
from style import apply_custom_style

# --- NEW: Header Bar Component ---
st.markdown("""
    <div class="main-header">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 24px; font-weight: 800; letter-spacing: -1px;">🛡️ AGENTIC GENBI</span>
            <span style="margin-left: 20px; opacity: 0.6; font-weight: 400;">Governance Control Tower</span>
        </div>
        <div style="font-size: 14px; opacity: 0.8;">
            v2.0 Beta | Folsom, CA HQ
        </div>
    </div>
""", unsafe_allow_html=True)
# --- 1. Page Configuration & State ---
st.set_page_config(page_title="AI Governance Control Tower", page_icon="🛡️", layout="wide")

# Inject Custom CSS
apply_custom_style()

# Initialize session state 
if "sf_scanned" not in st.session_state:
    st.session_state.sf_scanned = False
if "db_scanned" not in st.session_state:
    st.session_state.db_scanned = False

# --- 2. LLM Setup ---
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def classify_metadata_with_llm(metadata_df, source_name):
    grouped = metadata_df.groupby('TABLE_NAME')['COLUMN_NAME'].apply(list).to_dict()
    schema_context = ""
    for table, columns in grouped.items():
        schema_context += f"Table: {table}\nColumns: {', '.join(columns)}\n\n"
        
    prompt = PromptTemplate.from_template(
        "You are a strict Data Governance AI. Review the database tables and columns from {source}. "
        "Identify columns that likely contain PII (e.g., SSNs, Credit Cards) and flag them as high-risk anomalies. "
        "Return your findings as a concise, professional summary followed by a bulleted list detailing the Table Name, Column Name, and risk reason.\n\n"
        "Schema Context:\n{schema_context}"
    )
    
    chain = prompt | llm
    return chain.invoke({"source": source_name, "schema_context": schema_context}).content

# --- 3. Connection Functions (Unchanged) ---
@st.cache_data(ttl=0) 
def get_snowflake_metadata():
    try:
        conn = snowflake.connector.connect(
            user=st.secrets["snowflake"]["user"],
            password=st.secrets["snowflake"]["password"],
            account=st.secrets["snowflake"]["account"],
            database=st.secrets["snowflake"]["database"],
            schema=st.secrets["snowflake"]["schema"],
            role=st.secrets["snowflake"]["role"],
            warehouse=st.secrets["snowflake"]["warehouse"]
        )
        db_name = st.secrets['snowflake']['database'].strip()
        schema_name = st.secrets['snowflake']['schema'].strip()
        query = f"SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM {db_name}.INFORMATION_SCHEMA.COLUMNS WHERE UPPER(TABLE_SCHEMA) = UPPER('{schema_name}')"
        df = pd.read_sql(query, conn)
        conn.close()
        df.columns = [col.upper() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Snowflake Connection Error: {e}")
        return None
                    
@st.cache_data(ttl=300)
def get_databricks_metadata():
    try:
        connection = sql.connect(
            server_hostname=st.secrets["databricks"]["server_hostname"],
            http_path=st.secrets["databricks"]["http_path"],
            access_token=st.secrets["databricks"]["access_token"]
        )
        query = "SELECT table_name, column_name, data_type FROM system.information_schema.columns WHERE table_schema = 'raw_kitchen_db'"
        df = pd.read_sql(query, connection)
        connection.close()
        df.columns = [col.upper() for col in df.columns] 
        return df
    except Exception as e:
        st.error(f"Databricks Connection Error: {e}")
        return None

# --- 4. Dashboard UI: Header & KPIs ---
st.title("Dashboard")
st.caption("A summary of compliance across your data estate")

# KPI Metrics (Task 2: Governance Visuals)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("🏢 Data Sources", "2", "Active")
kpi2.metric("📄 Tables Monitored", "1,772", "12 scanned today")
kpi3.metric("✅ Compliance Rate", "64%", "-5% vs last month")
kpi4.metric("🚨 Unresolved Anomalies", "18", "Requires Action", delta_color="inverse")

st.write("") # Spacer

# Charts Section (Task 2: Governance Visuals)
chart_col1, chart_col2 = st.columns([1, 2])

# Helper function to standardize chart styling
def update_chart_theme(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1E293B'),
        margin=dict(t=10, b=10, l=10, r=10),
        template='plotly_white' # Forces white/transparent theme
    )
    return fig

with chart_col1:
    with st.container(border=True):
        st.subheader("Required Attention")
        fig = px.pie(values=[40, 23, 37], names=['Expiring', 'Non-Compliant', 'No Response'], 
                     hole=0.6, color_discrete_sequence=['#F59E0B', '#EF4444', '#6366F1'])
        st.plotly_chart(update_chart_theme(fig), use_container_width=True)

with chart_col2:
    with st.container(border=True):
        st.subheader("Compliance Status Overview")
        data = {'Status': ['Compliant', 'Waived', 'Non-compliant', 'Expired', 'Awaiting'], 'Value': [19, 7, 61, 3, 11]}
        fig2 = px.bar(data, x='Status', y='Value', color='Status', 
                      color_discrete_sequence=['#10B981', '#8B5CF6', '#EF4444', '#94A3B8', '#F59E0B'])
        st.plotly_chart(update_chart_theme(fig2), use_container_width=True)

st.divider()
# --- Discovery Section (With Clean AI Results) ---
st.subheader("Cross-Cloud Discovery")

with chart_col1:
    with st.container(border=True):
        st.subheader("Required Attention")
        # Mock Donut Chart
        fig = px.pie(values=[40, 23, 37], names=['About to expire', 'Not compliant', 'Not responsive'], hole=0.6, 
                     color_discrete_sequence=['#FFC107', '#FF5722', '#3F51B5'])
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    with st.container(border=True):
        st.subheader("Compliance Status Overview")
        # Mock Bar Chart
        data = {'Status': ['Compliant', 'Waived', 'Not compliant', 'Expired', 'Awaiting COI'], 'Value': [19, 7, 61, 3, 11]}
        fig2 = px.bar(data, x='Status', y='Value', text='Value', 
                      color='Status', color_discrete_sequence=['#00C853', '#5C6BC0', '#FF5722', '#607D8B', '#FFC107'])
        fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
# --- Inside Task 2 Visuals ---

# Donut Chart Fix
fig.update_layout(
    margin=dict(t=10, b=10, l=10, r=10),
    height=250,
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)',   # Transparent background
    font=dict(color='#1E293B')      # Darker font for percentages
)

# Bar Chart Fix
fig2.update_layout(
    margin=dict(t=10, b=10, l=10, r=10),
    height=250,
    showlegend=False,
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=False, color='#1E293B'),
    yaxis=dict(showgrid=True, gridcolor='#E2E8F0', color='#1E293B'),
    font=dict(color='#1E293B')
)
st.divider()

# --- 5. Data Estate Scanners (Task 1: Bot UI & Alternating Rows) ---
st.subheader("Cross-Cloud Discovery & Classification")
col1, col2 = st.columns(2)

# --- Snowflake Section ---
with col1:
    with st.container(border=True):
        st.header("❄️ Snowflake")
        st.caption("Environment: PROD_DINING_ROOM_DB")
        
        if st.button("Deploy AI Agent", key="sf_btn", type="primary", use_container_width=True):
            st.session_state.sf_scanned = True
            
        if st.session_state.sf_scanned:
            with st.spinner("Agent mapping Snowflake estate..."):
                sf_df = get_snowflake_metadata()
                
                if sf_df is not None and not sf_df.empty:
                    # Apply alternating row colors using Pandas Styler
                    st.dataframe(sf_df.style.apply(lambda x: ['background: #f8f9fa' if i % 2 == 0 else '' for i in range(len(x))], axis=0), use_container_width=True, height=200)
                    
                    st.markdown("##### 🤖 AI Risk Analysis")
                    with st.spinner("Analyzing semantics with LLM..."):
                        sf_anomalies = classify_metadata_with_llm(sf_df, "Snowflake")
                        # Bot UI
                        with st.chat_message("ai", avatar="🛡️"):
                            st.write(sf_anomalies)
                    
                    st.info("ISO 42001 Human-in-the-Loop Action Required", icon="ℹ️")
                    if st.button("Approve & Write-Back Tags", key="sf_approve", use_container_width=True):
                        st.success("✅ APPROVED: Executing `ALTER TABLE` to apply PII tags natively in Snowflake Horizon.")

# --- Databricks Section ---
with col2:
    with st.container(border=True):
        st.header("🧱 Databricks")
        st.caption("Environment: raw_kitchen_db")
        
        if st.button("Deploy AI Agent", key="db_btn", type="primary", use_container_width=True):
            st.session_state.db_scanned = True
            
        if st.session_state.db_scanned:
            with st.spinner("Agent mapping Databricks Unity Catalog..."):
                db_df = get_databricks_metadata()
                
                if db_df is not None and not db_df.empty:
                    # Apply alternating row colors using Pandas Styler
                    st.dataframe(db_df.style.apply(lambda x: ['background: #f8f9fa' if i % 2 == 0 else '' for i in range(len(x))], axis=0), use_container_width=True, height=200)
                    
                    st.markdown("##### 🤖 AI Risk Analysis")
                    with st.spinner("Analyzing semantics with LLM..."):
                        db_anomalies = classify_metadata_with_llm(db_df, "Databricks")
                        # Bot UI
                        with st.chat_message("ai", avatar="🛡️"):
                            st.write(db_anomalies)
                        
                    st.info("ISO 42001 Human-in-the-Loop Action Required", icon="ℹ️")
                    if st.button("Approve & Write-Back Tags", key="db_approve", use_container_width=True):
                        st.success("✅ APPROVED: Executing REST API call to apply PII tags natively in Unity Catalog.")