import streamlit as st

def apply_custom_css():
    """Apply custom CSS styling to the application"""
    st.markdown(
        """
        <style>
        /* Main layout */
        [data-testid="stMainBlockContainer"] {
            padding: 1.5rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Typography */
        h1, h2, h3, [data-testid="stMarkdownContainer"] h1, 
        [data-testid="stMarkdownContainer"] h2, 
        [data-testid="stMarkdownContainer"] h3 {
            font-weight: 600 !important;
            letter-spacing: -0.5px;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }
        
        /* Card styles */
        .card, .project-card, .insight-card, .file-card {
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(250, 250, 250, 0.2);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .card:hover, .project-card:hover {
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
            transform: translateY(-2px);
        }
        
        .project-card {
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .project-card h3 {
            margin-top: 0 !important;
            margin-bottom: 0.5rem !important;
        }
        
        .project-stats {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        /* App header */
        .app-header {
            padding: 0 1.5rem 0.5rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(67, 97, 238, 0.2);
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] .stButton button {
            width: 100%;
            text-align: left;
            padding: 0.5rem 0.75rem;
            margin-bottom: 0.4rem;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 4px !important;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        /* Form elements */
        [data-testid="stFileUploader"] {
            padding: 1rem;
            border-radius: 6px;
            border: 1px dashed rgba(250, 250, 250, 0.2);
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid rgba(250, 250, 250, 0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            border-radius: 4px 4px 0 0;
            border: 1px solid rgba(250, 250, 250, 0.1);
            border-bottom: none;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            border: 1px solid rgba(250, 250, 250, 0.1);
            border-top: none;
            border-radius: 0 0 4px 4px;
            padding: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )