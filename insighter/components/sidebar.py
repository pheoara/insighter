import streamlit as st
from insighter.utils.state import navigate_to

def render_sidebar():
    """Render the sidebar navigation"""
    with st.sidebar:
        st.markdown("<h1>Insighter</h1>", unsafe_allow_html=True)
        st.markdown("### Navigation")
        
        # Main navigation buttons
        for label, key, page in [
            ("🏠 Dashboard", "nav_dashboard", "dashboard"),
            ("➕ New Project", "nav_new_project", "create_project")
        ]:
            if st.button(label, key=key, use_container_width=True):
                navigate_to(page)
        
        # Projects list
        if st.session_state.projects:
            st.markdown("### Projects")
            for project_name in sorted(st.session_state.projects.keys()):
                if st.button(f"📁 {project_name}", key=f"proj_{project_name}", use_container_width=True):
                    navigate_to("project_chat", project=project_name)
        else:
            st.markdown("### Projects")
            st.info("No projects available")