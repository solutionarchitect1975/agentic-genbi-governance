import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        /* Main background and typography */
        .stApp {
            background-color: #F4F7F6;
            font-family: 'Inter', sans-serif;
        }
        
        /* Card-like containers for metrics and charts */
        div[data-testid="stMetric"], div.stApp > header, .stAlert {
            background-color: #FFFFFF;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid #EAEAEA;
        }

        /* Top Header adjustment */
        div.block-container {
            padding-top: 2rem;
        }

        /* Alternate row colors for native Streamlit dataframes */
        [data-testid="stDataFrame"] div[data-testid="stTableRegion"] {
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #EAEAEA;
        }
        
        /* Bot UI Message Styling */
        div[data-testid="stChatMessage"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)