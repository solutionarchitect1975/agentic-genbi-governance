import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        /* 1. The Header Bar (Fixes "Headless" feel) */
        .main-header {
            background-color: #0F172A;
            padding: 1.5rem 2rem;
            margin: -6rem -5rem 2rem -5rem; /* Forces header to span full width */
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* 2. Page & Text Basics */
        .stApp { background-color: #F8FAFC; }
        
        h1, h2, h3 { color: #1E293B !important; font-weight: 700 !important; }
        
        /* 3. The "Bot UI" & Result Container Fix */
        div[data-testid="stChatMessage"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            color: #1E293B !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        }
        
        /* Ensures the text inside the AI result is readable */
        div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] li {
            color: #334155 !important;
        }

        /* 4. Button Refinement (No more red) */
        .stButton>button {
            background-color: #2563EB !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            width: 100%;
            font-weight: 600 !important;
        }
        
        /* 5. Metrics styling */
        [data-testid="stMetric"] {
            background-color: white !important;
            border: 1px solid #E2E8F0 !important;
            padding: 15px !important;
            border-radius: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)