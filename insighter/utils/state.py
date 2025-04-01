import os
import streamlit as st
import json

BASE_PATH = "projects"

def initialize_session_state():
    os.makedirs(BASE_PATH, exist_ok=True)
    
    if "alerts" not in st.session_state:
        st.session_state.alerts = []

    if "projects" not in st.session_state:
        st.session_state.projects = {}
    
        for project_name in os.listdir(BASE_PATH):

            project_path = os.path.join(BASE_PATH, project_name)

            if os.path.isdir(project_path):
                files = [f for f in os.listdir(project_path) if f.endswith(".csv")]
                
                file_paths = {}
                for file in files:
                    file_paths[file] = os.path.join(project_path, file)
                
                insights = {}
                for file in files:
                    json_path = os.path.join(project_path, file.replace('.csv', '.json'))
                    if os.path.exists(json_path):
                        try:
                            with open(json_path, 'r') as f:
                                insights[file] = json.load(f)
                        except Exception as e:
                            print(f"Error loading insights for {file}: {e}")
                
                st.session_state.projects[project_name] = {
                    "path": project_path,
                    "files": files,
                    "file_paths": file_paths,
                    "insights": insights,
                    "selected_insights": {},
                    "messages": []
                }
    else: 
        for project_name, project in st.session_state.projects.items():
            
            if "file_paths" not in project:

                project["file_paths"] = {}

                for file in project.get("files", []):
                    project["file_paths"][file] = os.path.join(project["path"], file)
            
            if "selected_insights" not in project:
                project["selected_insights"] = {}
                
            for file in project.get("files", []):

                if file not in project.get("insights", {}):

                    json_path = os.path.join(project["path"], file.replace('.csv', '.json'))

                    if os.path.exists(json_path):

                        try:

                            with open(json_path, 'r') as f:

                                if "insights" not in project:
                                    project["insights"] = {}
                                project["insights"][file] = json.load(f)

                        except Exception as e:
                            print(f"Error loading insights for {file}: {e}")
    
    default_values = {
        "page": "dashboard",
        "current_project": None, 
        "current_file": None,
        "show_details_flags": {},
        "processing": False,
        "ai_thinking": False,
        "selected_insights": {},
        "confirm_delete_project": None,
        "confirm_delete_file": None,
        "active_tab": "Chat"
    }
    
    for state_var, default_val in default_values.items():

        if state_var not in st.session_state:
            st.session_state[state_var] = default_val

def navigate_to(page, project=None, file=None):
    st.session_state.page = page

    if project is not None:
        st.session_state.current_project = project
        
    if file is not None:
        st.session_state.current_file = file
    st.rerun()

def toggle_details(file, insight_key):

    key = f"{file}_{insight_key}"
    st.session_state.show_details_flags[key] = not st.session_state.show_details_flags.get(key, False) 