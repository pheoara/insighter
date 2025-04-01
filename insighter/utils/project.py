import os
import streamlit as st
from insighter.utils.state import BASE_PATH
import datetime
import random
import datetime

def create_project(project_name, description=""):

    project_path = os.path.join(BASE_PATH, project_name)
    os.makedirs(project_path, exist_ok=True)
    
    st.session_state.projects[project_name] = {
        "path": project_path,
        "files": [],
        "file_paths": {}, 
        "insights": {},
        "selected_insights": {}, 
        "messages": [],
        "description": description
    }
    
    return project_name

def delete_project(project_name):

    if project_name in st.session_state.projects:
        project_path = st.session_state.projects[project_name]["path"]

        try:

            for file in os.listdir(project_path):
                file_path = os.path.join(project_path, file)

                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            os.rmdir(project_path)
            
            del st.session_state.projects[project_name]
            
            return True
        
        except Exception as e:
            st.error(f"Error deleting project: {str(e)}")
            return False
        
    return False

def delete_file(project_name, file_name):

    if project_name in st.session_state.projects:
        project = st.session_state.projects[project_name]
        file_path = os.path.join(project["path"], file_name)
        json_path = file_path.replace('.csv', '.json')
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            
            if os.path.exists(json_path):
                os.remove(json_path)
            
            if file_name in project["files"]:
                project["files"].remove(file_name)
            
            if "file_paths" in project and file_name in project["file_paths"]:
                del project["file_paths"][file_name]
            
            if file_name in project["insights"]:
                del project["insights"][file_name]
            
            return True
        except Exception as e:
            st.error(f"Error deleting file: {str(e)}")
            return False
    return False


def generate_sample_alert(project_name=None, count=1):

    alert_types = [
        "Data quality issue detected in dataset",
        "Anomaly detected in recent data uploads",
        "Action required: Missing values in key columns",
        "Scheduled insight generation completed",
        "New correlation detected between variables",
        "Data drift observed in recent uploads"
    ]

    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for _ in range(count):
        alert_message = random.choice(alert_types)

        if project_name:
            alert = {
                "message": alert_message,
                "project": project_name,
                "timestamp": timestamp
            }

        else:
            alert = {
                "message": alert_message,
                "project": random.choice(list(st.session_state.projects.keys())) if st.session_state.projects else "System",
                "timestamp": timestamp
            }
        
        st.session_state.alerts.append(alert)
    
    return True

def create_custom_alert(message, project_name):
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    alert = {
        "message": message,
        "project": project_name,
        "timestamp": timestamp
    }
    
    if "alerts" not in st.session_state:
        st.session_state.alerts = []
    
    st.session_state.alerts.append(alert)
    
    return True