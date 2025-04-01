import time
import streamlit as st
from insighter.components.ui import render_header
from insighter.utils.state import navigate_to
from insighter.utils.project import generate_sample_alert

def render_dashboard():
    render_header("Insighter", "Analyze your data with AI-powered insights and chat with your datasets")
    
    st.markdown("## System Alerts")
    
    if st.session_state.alerts:
        col1, col2, _ = st.columns([1, 1, 3])


        with col1:
            if st.button("Generate Test Alert", key="gen_test_alert", use_container_width=True):
                generate_sample_alert(count=1)
                st.rerun()
                

        with col2:
            if st.button("Clear All Alerts", key="clear_alerts", use_container_width=True):
                st.session_state.alerts = []
                st.success("All alerts cleared!")
                st.rerun()
        

        for i, alert in enumerate(st.session_state.alerts):
            bg_color = "rgba(70, 130, 180, 0.1)"  
            border_color = "#4682B4"
            cols = st.columns([10, 2])


            with cols[0]:
                st.markdown(f"""
                <div style="background: {bg_color}; 
                     border-left: 3px solid {border_color}; 
                     padding: 0.8rem; margin-bottom: 0.8rem; border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p style="margin: 0; font-weight: 500;">{alert.get('message', 'System Alert')}</p>
                            <p style="margin: 0; font-size: 0.8rem; opacity: 0.7;">Project: {alert.get('project', 'System')}</p>
                        </div>
                        <p style="margin: 0; font-size: 0.8rem; opacity: 0.7;">{alert.get('timestamp', 'Today')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)


            with cols[1]:

                if st.button("Dismiss", key=f"dismiss_alert_{i}", use_container_width=True):
                    st.session_state.alerts.pop(i)
                    st.success("Alert dismissed")
                    st.rerun()

    else:
        st.markdown("""
        <div style="padding: 1rem; border: 1px dashed #cccccc; border-radius: 4px; text-align: center; margin-bottom: 1rem;">
            <p>No system alerts at this time</p>
        </div>
        """, unsafe_allow_html=True)
        

        if st.button("Generate Sample Alert", key="gen_sample_alert", use_container_width=False):
            generate_sample_alert(count=1)
            st.success("Sample alert generated!")
            st.rerun()
    

    st.markdown("## Your Projects")
    

    if st.session_state.projects:
        cols = st.columns(3)


        for i, project_name in enumerate(sorted(st.session_state.projects.keys())):
            project = st.session_state.projects[project_name]


            with cols[i % 3]:
                st.markdown(f"""
                <div class="project-card">
                    <h3>{project_name}</h3>
                    <div class="project-stats">
                        <p><strong>{len(project['files'])}</strong> files</p>
                        <p>Last updated: {time.strftime("%Y-%m-%d")}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                

                if st.button("Open Project", key=f"dash_open_{project_name}", type="primary", use_container_width=True):
                    navigate_to("project_chat", project=project_name)


    else:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 2rem;">
            <h3>No projects yet</h3>
            <p>Create your first project to get started with data analysis</p>
        </div>
        """, unsafe_allow_html=True)


        if st.button("Create Your First Project", key="dash_create_first_project", type="primary"):
            navigate_to("create_project")
    

    st.markdown("## Quick Start Guide")
    cols = st.columns(3)
    steps = [
        ("1. Create a Project", "Start by creating a new project to organize your data files and insights"),
        ("2. Upload Data", "Upload CSV files to your project for analysis"),
        ("3. Generate Insights", "Analyze your data to discover patterns and insights")
    ]
    
    for i, col in enumerate(cols):

        with col:
            st.markdown(f"""
            <div class="card">
                <h3>{steps[i][0]}</h3>
                <p>{steps[i][1]}</p>
            </div>
            """, unsafe_allow_html=True)