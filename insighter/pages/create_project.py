import time
import streamlit as st
from insighter.components.ui import render_header
from insighter.utils.state import navigate_to
from insighter.utils.project import create_project

def render_create_project():

    render_header("Create New Project", "Set up a new project to analyze your data files")
    
    with st.form("project_form"):
        st.markdown("### Project Details")
        new_project = st.text_input("Project name")
        project_description = st.text_area("Description (optional)", max_chars=200)
        submitted = st.form_submit_button("Create Project")
        
        if submitted:

            if not new_project:
                st.error("Please enter a project name")
                
            elif new_project in st.session_state.projects:
                st.error("Project already exists")

            else:
                
                with st.spinner("Creating project..."):
                    create_project(new_project, project_description)
                    
                st.success(f"Project '{new_project}' created!")
                time.sleep(1)
                navigate_to("project_dashboard", project=new_project)