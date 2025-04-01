import os
import json
import time
import pandas as pd
import streamlit as st
from insighter.components.ui import render_header, render_card
from insighter.utils.state import navigate_to, toggle_details
from insighter.utils.insights import run_insight_pipeline

def render_file_insights():
    current_project = st.session_state.current_project
    current_file = st.session_state.current_file
    project = st.session_state.projects[current_project]
    project_path = project["path"]
    csv_path = os.path.join(project_path, current_file)
    json_path = csv_path.replace('.csv', '.json')
    
    render_header(f"Insights: {current_file}", "View and manage data insights")
    
    col1, col2, _ = st.columns([1, 1, 2])

    with col1:
        if st.button("← Back to Project", key="insights_back_btn", use_container_width=True):
            navigate_to("project_dashboard")

    with col2:

        if st.button("View Raw Data", key="insights_view_data_btn", use_container_width=True):
            navigate_to("file_view", file=current_file)
    
    insights_data = project["insights"].get(current_file)
    
    if insights_data is None:

        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                insights_data = json.load(f)
            project["insights"][current_file] = insights_data
            st.success("Loaded existing insights")

        else:
            st.markdown("""
            <div class="card" style="text-align: center; padding: 2rem; margin-bottom: 2rem;">
                <h3>No insights available</h3>
                <p>Generate insights to discover patterns and trends in your data</p>
            </div>
            """, unsafe_allow_html=True)
            _, center, _ = st.columns([1, 2, 1])

            with center:
                if st.button("Generate Insights", key=f"generate_insights_btn_{current_file}", type="primary", use_container_width=True):

                    with st.spinner("Generating insights... This may take a few minutes."):

                        try:
                            insights_data = run_insight_pipeline(csv_path)
                            project["insights"][current_file] = insights_data
                            st.success("Insights generated successfully!")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error generating insights: {str(e)}")
                            st.info(f"Make sure the file exists and is properly formatted. Path: {csv_path}")
    

    if insights_data:
        insights = insights_data.get("sql_queries", {})

        if not insights:
            st.warning("No meaningful insights could be generated from this data.")

        else:
            selected_insights_key = f"selected_insights_{current_project}"

            if not hasattr(st.session_state, selected_insights_key):
                setattr(st.session_state, selected_insights_key, {})
            
            project_selected_insights = getattr(st.session_state, selected_insights_key)
            
            if current_file not in project_selected_insights:
                project_selected_insights[current_file] = []
            
            selected_insights = project_selected_insights[current_file]
            tab_all, tab_selected = st.tabs(["All Insights", "Selected Insights"])
            
            with tab_all:
                search_term = st.text_input("Search insights", key=f"search_insights_{current_file}", placeholder="Filter by keyword...")
                
                for key, insight in insights.items():
                    if "insight_summary" not in insight:
                        continue
                        
                    summary = insight.get("insight_summary", "")
                    question = insight.get("insight_question", "")
                    if search_term and not (search_term.lower() in summary.lower() or search_term.lower() in question.lower()):
                        continue
                        
                    with st.expander(summary, expanded=False):

                        if "insight_question" in insight:
                            st.markdown(f"""
                            <div style="padding: 0.8rem; border-radius: 4px; margin-bottom: 1rem; background: rgb(26, 28, 36);">
                                <p style="font-weight: 500; margin-bottom: 0.3rem;">Question:</p>
                                <p>{insight['insight_question']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        if "sql_query" in insight:
                            st.markdown("**SQL Query:**")
                            st.code(insight["sql_query"], language="sql")
                        
                        if "result" in insight:
                            st.markdown("**Result:**")
                            st.dataframe(pd.DataFrame(insight["result"]), use_container_width=True)
                        
                        insight_key = f"select_{current_file}_{key}_{current_project}"
                        is_selected = any(s.get('insight_summary') == insight.get('insight_summary') for s in selected_insights)
                        
                        button_label = "Selected ✓" if is_selected else "Select"
                        button_type = "secondary" if is_selected else "primary"
                        
                        if st.button(button_label, key=f"btn_{insight_key}", type=button_type, help="Add to selected insights"):

                            if not is_selected:
                                selected_insights.append(insight)
                                st.success("Added to selected insights")

                            else:
                                selected_insights = [s for s in selected_insights if s.get('insight_summary') != insight.get('insight_summary')]
                                st.info("Removed from selected insights")
                            
                            project_selected_insights[current_file] = selected_insights
                            setattr(st.session_state, selected_insights_key, project_selected_insights)
                            st.rerun()
            
            with tab_selected:
                if selected_insights:
                    st.markdown("## Selected Insights")
                    
                    for i, insight in enumerate(selected_insights):
                        st.markdown(f"""
                        <div class="insight-card" style="padding: 1rem; margin-bottom: 0.75rem; border-radius: 6px; border: 1px solid rgba(250, 250, 250, 0.2);">
                            <p style="font-weight: 500;">{i+1}. {insight['insight_summary']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    _, center, _ = st.columns([1, 2, 1])
                    
                    with center:

                        if st.button("Add Selected Insights to Chat", key=f"add_to_chat_btn_{current_file}", type="primary", use_container_width=True):
                            insight_message = "\n\n".join([
                                f"**Question:** {ins.get('insight_question', 'N/A')}\n**Summary:** {ins.get('insight_summary', 'N/A')}"

                                for ins in selected_insights
                            ])
                            
                            project["messages"].append({
                                "role": "system",
                                "content": f"Insights added from {current_file}:\n{insight_message}"
                            })
                            
                            st.success("Insights added to chat!")
                            time.sleep(1)
                            navigate_to("project_chat")
                else:
                    st.info("No insights selected. Go to the 'All Insights' tab to select some.")