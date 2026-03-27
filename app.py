import streamlit as st
import snowflake.connector
from databricks import sql
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import pandas as pd
import os

# --- 1. Page Configuration & State ---
st.set_page_config(page_title="AI Governance Control Tower", page_icon="🛡️", layout="wide")

# Initialize session state for the ISO 42001 Human-in-the-Loop simulation
if "sf_scanned" not in st.session_state:
    st.session_state.sf_scanned = False
if "db_scanned" not in st.session_state:
    st.session_state.db_scanned = False

# --- 2. LLM Setup ---
# Automatically pick up the API key from secrets for LangChain
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def classify_metadata_with_llm(metadata_df, source_name):
    """Sends table and column names to the LLM to find PII anomalies dynamically."""
    
    # Dynamically group columns by their Table Name
    grouped = metadata_df.groupby('TABLE_NAME')['COLUMN_NAME'].apply(list).to_dict()
    
    # Format this into a clean string for the LLM to read
    schema_context = ""
    for table, columns in grouped.items():
        schema_context += f"Table: {table}\nColumns: {', '.join(columns)}\n\n"
        
    prompt = PromptTemplate.from_template(
        "You are a strict Data Governance AI. Review the following database tables and their columns from {source}. "
        "Identify any columns that likely contain PII (like SSNs, Credit Cards) and flag them as high-risk anomalies. "
        "Return your findings as a short, bulleted list detailing the Table Name, the specific Column Name, and why it is a risk.\n\n"
        "Schema Context to Review:\n{schema_context}"
    )
    
    chain = prompt | llm
    response = chain.invoke({"source": source_name, "schema_context": schema_context})
    return response.content

# --- 3. Connection Functions ---
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
        
        # DYNAMIC DISCOVERY: Pulls all tables and columns in whatever schema is in secrets.toml
        query = f"""
            SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE 
            FROM {db_name}.INFORMATION_SCHEMA.COLUMNS 
            WHERE UPPER(TABLE_SCHEMA) = UPPER('{schema_name}')
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Standardize column names to uppercase to prevent grouping KeyErrors
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
        # Querying the Unity Catalog System Schema
        query = "SELECT table_name, column_name, data_type FROM system.information_schema.columns WHERE table_schema = 'raw_kitchen_db'"
        df = pd.read_sql(query, connection)
        connection.close()
        # Standardize column names to match Snowflake's uppercase format for the LLM
        df.columns = [col.upper() for col in df.columns] 
        return df
    except Exception as e:
        st.error(f"Databricks Connection Error: {e}")
        return None

# --- 4. Dashboard UI ---
st.title("🛡️ Agentic GenBI: Cross-Cloud Governance")
st.markdown("Automated Discovery, AI Classification, and ISO 42001 Compliant Write-Backs.")
st.divider()

col1, col2 = st.columns(2)

# --- Snowflake Section ---
with col1:
    st.header("❄️ Snowflake (Dining Room)")
    st.caption("Monitoring: PROD_DINING_ROOM_DB")
    
    if st.button("Deploy AI Agent to Snowflake", type="primary"):
        st.session_state.sf_scanned = True
        
    if st.session_state.sf_scanned:
        with st.spinner("Agent mapping Snowflake estate..."):
            sf_df = get_snowflake_metadata()
            
            if sf_df is not None:
                if sf_df.empty:
                    st.warning("Connection succeeded, but no tables or columns were found.")
                else:
                    st.success("Metadata Extracted Successfully")
                    st.dataframe(sf_df, use_container_width=True, height=200)
                    
                    st.subheader("🚨 AI Risk Analysis")
                    with st.spinner("Analyzing semantics with LLM..."):
                        sf_anomalies = classify_metadata_with_llm(sf_df, "Snowflake")
                        st.warning(sf_anomalies)
                    
                    st.info("ISO 42001 Human-in-the-Loop Action Required")
                    if st.button("Approve & Write-Back Tags to Snowflake"):
                        st.success("✅ APPROVED: Executing `ALTER TABLE` to apply PII tags.")

# --- Databricks Section ---
with col2:
    st.header("🧱 Databricks (Kitchen)")
    st.caption("Monitoring: raw_kitchen_db")
    
    if st.button("Deploy AI Agent to Databricks", type="primary"):
        st.session_state.db_scanned = True
        
    if st.session_state.db_scanned:
        with st.spinner("Agent mapping Databricks Unity Catalog..."):
            db_df = get_databricks_metadata()
            
            if db_df is not None:
                st.success("Metadata Extracted Successfully")
                st.dataframe(db_df, use_container_width=True, height=200)
                
                st.subheader("🚨 AI Risk Analysis")
                with st.spinner("Analyzing semantics with LLM..."):
                    db_anomalies = classify_metadata_with_llm(db_df, "Databricks")
                    st.warning(db_anomalies)
                    
                st.info("ISO 42001 Human-in-the-Loop Action Required")
                if st.button("Approve & Write-Back Tags to Unity Catalog"):
                    st.success("✅ APPROVED: Executing REST API call to apply PII tags.")