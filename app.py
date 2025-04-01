import os
import streamlit as st
from insighter.utils.state import initialize_session_state
from insighter.styles.main import apply_custom_css
from insighter.pages.dashboard import render_dashboard
from insighter.pages.create_project import render_create_project
from insighter.pages.file_view import render_file_view
from insighter.pages.file_insights import render_file_insights
from insighter.pages.project_chat import render_project_chat
from insighter.components.sidebar import render_sidebar

# Page configuration
st.set_page_config(
    page_title="Insighter",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
apply_custom_css()

# Initialize session state
initialize_session_state()

# Render sidebar
render_sidebar()

# Main content area - route to the correct page
page = st.session_state.page
if page == "dashboard":
    render_dashboard()
elif page == "create_project":
    render_create_project()
elif page == "project_dashboard":
    # Redirect to project_chat instead
    st.session_state.page = "project_chat"
    render_project_chat()
elif page == "file_view":
    render_file_view()
elif page == "file_insights":
    # Redirect to project_chat instead and set focus to All Insights tab
    st.session_state.active_tab = "All Insights"
    st.session_state.page = "project_chat"
    render_project_chat()
elif page == "project_chat":
    render_project_chat()