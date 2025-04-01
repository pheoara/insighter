import sqlite3
import pandas as pd
import json
import streamlit as st
import matplotlib.pyplot as plt
from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END
from insighter.utils.project import create_custom_alert
from insighter.models.chat_agents import route_query, get_sql_query, get_alert, get_visualization, get_compare_insights, get_insight_details, get_casual_chat
    

class WorkflowState(TypedDict):
    user_query: str
    columns: str
    insights: str
    router_response: Optional[str]
    action: Optional[str]
    agent_response: Optional[str]
    db_connection: Optional[Any]
    metadata_result: Optional[str]



def extract_field_from_response(response: Any, field: str) -> str:
    if isinstance(response, dict):
        text = response.get("text", "")
    else:
        text = str(response)
    try:
        text = text.replace('\n\n', ' ').replace('\n', ' ')
        data = json.loads(text)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for field '{field}': {e}")
        print(f"Received text: {text}")
        return ""
    return data.get(field, "")



def load_csv_to_sql_node(state: WorkflowState) -> WorkflowState:
    print("in load_csv_to_sql_node")
    current_project = st.session_state.current_project
    project = st.session_state.projects[current_project]
    conn = sqlite3.connect(":memory:")
    
    for file_name in project.get("files", []):
        file_path = project.get("file_paths", {}).get(file_name)
        if file_path and file_path.endswith('.csv'):
            try:
                df = pd.read_csv(file_path)
                table_name = file_name.replace('.', '_').replace(' ', '_')
                df.to_sql(table_name, conn, if_exists="replace", index=False)
            except Exception as e:
                print(f"Error loading {file_name}: {e}")
    
    state["db_connection"] = conn
    return state



def extract_metadata_node(state: WorkflowState) -> WorkflowState:
    print("in extract_metadata_node")
    conn = state["db_connection"]
    if not conn:
        return state
    
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    print(f"Tables: {tables}")
    metadata = {}
    
    for table in tables:
        table_name = table[0]
        columns_info = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        metadata[table_name] = columns_info
        print(f"Table: {table_name}")
    
    
    state["columns"] = json.dumps(metadata)
    state["metadata_result"] = f"Tables: {[t[0] for t in tables]}\nColumns: {metadata}"
    return state



def route_query_node(state: WorkflowState) -> WorkflowState:
    print("in route_query_node")
    user_query = state["user_query"]
    router_response = route_query(user_query)
    state["router_response"] = str(router_response)
    action = extract_field_from_response(router_response, "action").lower().strip()
    state["action"] = action
    return state



def sql_node(state: WorkflowState) -> WorkflowState:
    print("in sql_node")
    columns = state.get("metadata_result", "")
    user_query = state["user_query"]
    sql_response = get_sql_query(user_query, columns)
    sql_query = extract_field_from_response(sql_response, "sql_query")
    state["agent_response"] = sql_query
    return state



def alert_node(state: WorkflowState) -> WorkflowState:
    print("in alert_node")
    columns = state.get("metadata_result", "")
    user_query = state["user_query"]
    insights = state["insights"]
    alert_response = get_alert(user_query, columns, insights)
    if isinstance(alert_response, dict):
        alert_text = alert_response.get("text", "")
    else:
        alert_text = str(alert_response)
    
    state["agent_response"] = alert_text
    return state



def visualization_node(state: WorkflowState) -> WorkflowState:
    print("in visualization_node")
    columns = state.get("metadata_result", "")
    user_query = state["user_query"]
    insights = state.get("insights", "")
    current_project = st.session_state.current_project

    project = st.session_state.projects[current_project]
    csv_files = [f for f in project.get("files", []) if f.endswith('.csv')]
    csv_file = ""
    if csv_files:
        csv_file = project.get("file_paths", {}).get(csv_files[0], "")
    
    viz_response = get_visualization(user_query, columns, csv_file, insights)
    viz_text = extract_field_from_response(viz_response, "visualization_code")
    print(f"Visualization Code: {viz_text}")
    state["agent_response"] = viz_text
    return state



def comparison_node(state: WorkflowState) -> WorkflowState:
    print("in comparison_node")
    insights = state.get("insights", "")
    user_query = state["user_query"]
    comp_response = get_compare_insights(user_query, insights)
    if isinstance(comp_response, dict):
        comp_text = comp_response.get("text", "")
    else:
        comp_text = str(comp_response)
    state["agent_response"] = comp_text
    return state



def insight_details_node(state: WorkflowState) -> WorkflowState:
    print("in insight_details_node")
    metadata = state.get("metadata_result", "")
    user_query = state["user_query"]
    insights = state.get("insights", "")
    details_response = get_insight_details(user_query, metadata, insights)
    if isinstance(details_response, dict):
        details_text = details_response.get("text", "")
    else:
        details_text = str(details_response)
    state["agent_response"] = details_text
    return state



def casual_chat_node(state: WorkflowState) -> WorkflowState:
    print("in casual_chat_node")
    user_query = state["user_query"]
    metadata = state.get("metadata_result", "")
    casual_response = get_casual_chat(user_query, metadata)
    if isinstance(casual_response, dict):
        casual_text = casual_response.get("text", "")
    else:
        casual_text = str(casual_response)
    state["agent_response"] = casual_text
    return state



def execute_sql_query(db_conn: sqlite3.Connection, sql_query: str) -> pd.DataFrame:
    try:
        cursor = db_conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        return df
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return pd.DataFrame()



def execute_visualization_code(viz_code: str) -> str:
    try:
        import time
        plot_name = f"plot_{int(time.time())}.png"
        viz_code = viz_code.replace('plot.png', plot_name)
        
        exec(viz_code, globals())
        return plot_name
    except Exception as e:
        print("Error executing visualization code:", e)
        return f"Error: {str(e)}"



def branch_node(state: WorkflowState) -> WorkflowState:
    action = state.get("action")
    
    if action == "sql database query":
        state = sql_node(state)
        sql_query = state.get("agent_response", "")
        if sql_query and state.get("db_connection"):
            try:
                df_result = execute_sql_query(state["db_connection"], sql_query)
                state["agent_response"] = df_result.to_string()
            except Exception as e:
                state["agent_response"] = f"Error executing SQL: {str(e)}"
        return state
    
    elif action == "alert":

        state = alert_node(state)
        alert_text = state.get("agent_response", "")
        
        if alert_text:
            current_project = st.session_state.current_project
            create_custom_alert(
                message=alert_text,
                project_name=current_project
            )
            state["agent_response"] = alert_text
        return state
    
    elif action == "visualization":

        state = visualization_node(state)
        viz_code = state.get("agent_response", "")
        if viz_code:
            result = execute_visualization_code(viz_code)
            state["agent_response"] = result
        return state
    
    elif action == "comparison":
        return comparison_node(state)
    
    elif action == "insight details":
        return insight_details_node(state)
    
    elif action == "chat":
        return casual_chat_node(state)

    else:
        state["agent_response"] = "I'm not sure how to process that request."
        return state



def create_chat_workflow() -> StateGraph:
    """Create and return the chat workflow graph"""
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("load_data", load_csv_to_sql_node)
    workflow.add_node("extract_metadata", extract_metadata_node)
    workflow.add_node("route", route_query_node)
    workflow.add_node("branch", branch_node)
    
    workflow.set_entry_point("load_data")
    workflow.add_edge("load_data", "extract_metadata")
    workflow.add_edge("extract_metadata", "route")
    workflow.add_edge("route", "branch")
    workflow.add_edge("branch", END)
    
    return workflow.compile()



def process_chat_query(user_query: str, selected_insights: dict = None) -> str:

    state: WorkflowState = {
        "user_query": user_query,
        "columns": "",
        "insights": json.dumps(selected_insights) if selected_insights else "",
        "router_response": None,
        "action": None,
        "agent_response": None,
        "db_connection": None,
        "metadata_result": None
    }

    workflow = create_chat_workflow()
    final_state = workflow.invoke(state)

    if final_state.get("db_connection"):
        final_state["db_connection"].close()
    
    return final_state.get("agent_response", "Sorry, I couldn't process that request.") 