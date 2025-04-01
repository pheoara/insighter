import sqlite3
import pandas as pd
from pprint import pprint
import json
from typing import TypedDict, Dict, Any, Optional
from insighter.models.insight_agents import get_metadata_result, get_insight_questions, get_sql_queries, insights_creation
from langgraph.graph import StateGraph, END



class WorkflowState(TypedDict):
    db_connection: Optional[sqlite3.Connection]
    metadata_result: Optional[str]
    insight_questions: Optional[str]
    sql_queries: Optional[Dict[str, Any]]
    sql_queries_and_results: Optional[Dict[str, Any]]
    presentation_result: Optional[Dict[str, Any]]
    final_dict: Optional[Dict[str, Any]]
    file_path: Optional[str]



def load_csv_to_sql_node(state: WorkflowState) -> Dict[str, Any]:
    file_path = state.get("file_path", "data.csv")
    df = pd.read_csv(file_path)
    conn = sqlite3.connect(":memory:")
    df.to_sql("sales_marketing_data", conn, if_exists="replace", index=False)
    return {"db_connection": conn}



def extract_metadata_node(state: WorkflowState) -> Dict[str, Any]:
    conn = state["db_connection"]
    columns = conn.execute("PRAGMA table_info(sales_marketing_data)").fetchall()
    metadata_output = get_metadata_result(columns)

    if isinstance(metadata_output, dict):
        metadata_text = metadata_output.get("text", "")
    else:
        metadata_text = str(metadata_output)

    metadata_result = 'Table name : sales_marketing_data\n' + metadata_text
    return {"metadata_result": metadata_result}



def define_insights_node(state: WorkflowState) -> Dict[str, Any]:
    metadata_result = state["metadata_result"]
    insight_output = get_insight_questions(metadata_result)

    if isinstance(insight_output, dict):
        insight_questions = insight_output.get("text", "")
    else:
        insight_questions = str(insight_output)

    return {"insight_questions": insight_questions}



def generate_sql_node(state: WorkflowState) -> Dict[str, Any]:
    metadata_result = state["metadata_result"]
    insight_questions = state["insight_questions"]
    sql_output = get_sql_queries(metadata_result, insight_questions)

    if isinstance(sql_output, dict):
        sql_text = sql_output.get("text", "")
    else:
        sql_text = str(sql_output)

    try:
        sql_queries = json.loads(sql_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding SQL JSON: {e}")
        print(f"Received text: {sql_text}")
        raise
    return {"sql_queries": sql_queries}



def execute_sql_queries_node(state: WorkflowState) -> Dict[str, Any]:
    conn = state["db_connection"]
    sql_queries = state["sql_queries"]
    cursor = conn.cursor()

    sql_queries_and_results = json.loads(json.dumps(sql_queries))

    keys_to_process = list(sql_queries_and_results.get("sql_queries", {}).keys())

    for key in keys_to_process:
        value = sql_queries_and_results["sql_queries"][key]
        try:
            query_text = value.get("sql_query")
            if not query_text:
                 print(f"Skipping query {key}: 'sql_query' key missing or empty.")
                 if key in sql_queries_and_results["sql_queries"]:
                      del sql_queries_and_results["sql_queries"][key]
                 continue

            cursor.execute(query_text)
            result = cursor.fetchall()
            if result:
                sql_queries_and_results["sql_queries"][key]["result"] = result
            else:
                if key in sql_queries_and_results["sql_queries"]:
                     del sql_queries_and_results["sql_queries"][key]
        except Exception as e:
            print(f"Error executing query for {key} ('{value.get('sql_query', 'N/A')}'): {e}")
            if key in sql_queries_and_results["sql_queries"]:
                 del sql_queries_and_results["sql_queries"][key]

    return {"sql_queries_and_results": sql_queries_and_results}



def generate_insights_node(state: WorkflowState) -> Dict[str, Any]:
    sql_queries_and_results = state.get("sql_queries_and_results")

    if not sql_queries_and_results or not sql_queries_and_results.get("sql_queries"):
        return {"presentation_result": {"insights": {}}}

    presentation_output = insights_creation(sql_queries_and_results)

    if isinstance(presentation_output, dict):
        presentation_text = presentation_output.get("text", "")
    else:
        presentation_text = str(presentation_output)

    try:
        presentation_result = json.loads(presentation_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding presentation JSON: {e}")
        print(f"Received text: {presentation_text}")
        raise
    return {"presentation_result": presentation_result}



def present_final_insights_node(state: WorkflowState) -> Dict[str, Any]:
    sql_queries_and_results = state.get("sql_queries_and_results")
    presentation_result = state.get("presentation_result")

    final_dict = json.loads(json.dumps(sql_queries_and_results)) if sql_queries_and_results else {"sql_queries": {}}
    insights_dict = presentation_result.get("insights", {}) if presentation_result else {}

    if "sql_queries" in final_dict:
        for question_key, summary in insights_dict.items():
            if question_key in final_dict["sql_queries"]:
                final_dict["sql_queries"][question_key]["insight_summary"] = summary
    return {"final_dict": final_dict}


workflow = StateGraph(WorkflowState)

workflow.add_node("load_data", load_csv_to_sql_node)
workflow.add_node("extract_metadata", extract_metadata_node)
workflow.add_node("define_insights", define_insights_node)
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("execute_sql", execute_sql_queries_node)
workflow.add_node("generate_insights", generate_insights_node)
workflow.add_node("present_final", present_final_insights_node)

workflow.set_entry_point("load_data")
workflow.add_edge("load_data", "extract_metadata")
workflow.add_edge("extract_metadata", "define_insights")
workflow.add_edge("define_insights", "generate_sql")
workflow.add_edge("generate_sql", "execute_sql")
workflow.add_edge("execute_sql", "generate_insights")
workflow.add_edge("generate_insights", "present_final")
workflow.add_edge("present_final", END)

app = workflow.compile()


def insight_pipeline(file_path="data.csv"):
    initial_state = {"file_path": file_path}
    final_state = app.invoke(initial_state)

    print("\n" + "="*50 + "\nWorkflow Complete. Final Output:")
    pprint(final_state.get("final_dict"))
    print("\n" + "="*50 + "\n")

    db_conn = final_state.get("db_connection")
    if db_conn:
        db_conn.close()

    return final_state.get("final_dict")
