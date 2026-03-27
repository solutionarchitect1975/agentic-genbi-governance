import streamlit as st
from style import apply_custom_style

st.set_page_config(page_title="Policy Management", page_icon="📜", layout="wide")
apply_custom_style()

st.title("📜 Policy Management")
st.caption("Manage compliance rules, tag definitions, and RBAC.")

st.warning("🚧 **Under Construction:** The Policy Management module is currently in development. Future updates will allow administrators to map custom compliance frameworks (HIPAA, GDPR) to LLM detection rules here.")

# Mock visual for future state
with st.container(border=True):
    st.subheader("Active Rulesets (Preview)")
    st.data_editor(
        data={"Rule ID": ["R-001", "R-002"], "Framework": ["ISO 42001", "HIPAA"], "Status": [True, False]},
        disabled=True,
        use_container_width=True
    )