import time
import os
import streamlit as st
from insighter.components.ui import render_header
from insighter.utils.state import navigate_to
from insighter.utils.project import delete_project, delete_file, generate_sample_alert

def render_project_dashboard():
    current_project = st.session_state.current_project
    project = st.session_state.projects[current_project]
    
    render_header(f"Project: {current_project}", "Manage files and view insights")
    
    col1, col2, col3, col4, _ = st.columns([1, 1, 1, 1, 1])

    with col1:

        if st.button("💬 Chat with Project", key="proj_chat_btn", type="primary", use_container_width=True):
            navigate_to("project_chat")

    with col2:

        if st.button("🏠 Dashboard", key="proj_dashboard_btn", use_container_width=True):
            navigate_to("dashboard")

    with col3:

        if st.button("🔔 Create Alert", key="proj_gen_alert_btn", use_container_width=True):
            generate_sample_alert(current_project)
            st.success("Alert generated for this project!")
            st.rerun()

    with col4:

        if st.button("🗑️ Delete Project", key="proj_delete_btn", type="secondary", use_container_width=True):

            if st.session_state.get("confirm_delete_project") == current_project:

                if delete_project(current_project):
                    st.session_state.pop("confirm_delete_project", None)
                    st.success(f"Project '{current_project}' deleted successfully!")
                    time.sleep(1)
                    navigate_to("dashboard")

            else:
                st.session_state["confirm_delete_project"] = current_project
                st.warning(f"Click 'Delete Project' again to confirm deletion of '{current_project}'")
                st.rerun()
    
    if "confirm_delete_project" in st.session_state and st.session_state["confirm_delete_project"] == current_project:
        st.info("Click 'Delete Project' again to confirm deletion or proceed with other actions to cancel.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## Files")
        
        with st.expander("Upload New Files", expanded=not bool(project["files"])):
            st.markdown("Upload CSV files to analyze and extract insights")
            uploaded_files = st.file_uploader(
                "Choose CSV files",
                accept_multiple_files=True,
                type=["csv"],
                key=f"uploader_{current_project}"
            )
            
            if uploaded_files:

                with st.spinner("Processing uploads..."):

                    for file in uploaded_files:

                        file_path = os.path.join(project["path"], file.name)

                        if file.name not in project["files"]:
                            with open(file_path, "wb") as f:
                                f.write(file.getbuffer())
                            project["files"].append(file.name)
                            project["insights"][file.name] = None
                            st.success(f"Uploaded {file.name}")

                        else:
                            st.info(f"{file.name} already exists")
        
        if project["files"]:

            st.markdown("### Your Files")

            for file in project["files"]:
                st.markdown(f"""
                <div class="file-card">
                    <span style="margin-top: 0; margin-bottom: 0.5rem;">{file}</span>
                </div>
                """, unsafe_allow_html=True)
            
                view_btn, analyze_btn, delete_btn = st.columns(3)
                
                with view_btn:

                    if st.button("View", key=f"view_file_{file}_{current_project}", use_container_width=True):
                        navigate_to("file_view", file=file)
                        
                with analyze_btn:

                    if st.button("Analyze", key=f"analyze_file_{file}_{current_project}", use_container_width=True):
                        navigate_to("file_insights", file=file)
                
                with delete_btn:

                    delete_key = f"delete_file_{file}_{current_project}"
                    if st.button("Delete", key=delete_key, use_container_width=True):

                        if st.session_state.get("confirm_delete_file") == delete_key:

                            if delete_file(current_project, file):

                                st.session_state.pop("confirm_delete_file", None)
                                st.success(f"File '{file}' deleted successfully!")
                                time.sleep(1)
                                st.rerun()
                        else:

                            st.session_state["confirm_delete_file"] = delete_key
                            st.warning(f"Click 'Delete' again to confirm deletion of '{file}'")
                            st.rerun()
                
                st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
        else:
            st.info("No files yet. Upload files to get started.")
    
    with col2:

        st.markdown("## Project Overview")
        st.markdown(f"""
        <div class="card" style="padding: 1rem; margin-bottom: 1rem;">
            <p><strong>Files:</strong> {len(project["files"])}</p>
            <p><strong>Last activity:</strong> {time.strftime("%Y-%m-%d")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if project["files"]:

            st.markdown("### Recent Insights")
            insights_available = False
            
            for file in project["files"]:

                insights_data = project["insights"].get(file)
                
                if insights_data:
                    insights_available = True
                    insights_content = ""

                    for key in list(insights_data.get('sql_queries', {}).keys())[:2]:
                        
                        if "insight_summary" in insights_data['sql_queries'][key]:
                            insights_content += f"• {insights_data['sql_queries'][key]['insight_summary']}<br>"
                    
                    st.markdown(f"""
                    <div class="card" style="padding: 0.8rem; margin-bottom: 0.8rem;">
                        <h3>{file}</h3>
                        {insights_content}
                    </div>
                    """, unsafe_allow_html=True)
            
            if not insights_available:
                st.info("No insights generated yet")