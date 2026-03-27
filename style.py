import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        /* Force high contrast for all headers and body text */
        html, body, [class*="st-"] {
            color: #1E293B; 
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #0F172A !important;
            font-weight: 700 !important;
        }

        .stApp {
            background-color: #F8FAFC;
        }
        
        /* Card Styling: White background with a subtle border */
        div[data-testid="stMetric"], div.stVerticalBlock > div > div[style*="border"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }

        /* Fixing Metric Labels (making them dark) */
        [data-testid="stMetricLabel"] {
            color: #64748B !important;
            font-size: 0.9rem !important;
        }

        /* Fix the Sidebar color if you use one */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }

        /* Clean up buttons: Use a professional Blue instead of Red */
        .stButton>button {
            background-color: #2563EB !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 600 !important;
            transition: all 0.2s ease;
        }
        
        .stButton>button:hover {
            background-color: #1D4ED8 !important;
            box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)