import streamlit as st
import time
import os
import json
import pandas as pd
from insighter.components.ui import render_header
from insighter.utils.state import navigate_to
from insighter.utils.ai_client import get_client
from insighter.pipelines.chat import process_chat_query
from insighter.utils.project import delete_project, delete_file
from insighter.utils.insights import run_insight_pipeline

def render_project_chat():
    """Render the project chat page with enhanced capabilities and dashboard functionality"""
    current_project = st.session_state.current_project
    project = st.session_state.projects[current_project]
    client = get_client()
    
    if "file_paths" not in project:
        project["file_paths"] = {}
    
    if "selected_insights" not in project:
        project["selected_insights"] = {}
    
    insights_key = f"insights_{current_project}"
    selected_insights_key = f"selected_insights_{current_project}"
    

    if hasattr(st.session_state, selected_insights_key):
        project["selected_insights"] = getattr(st.session_state, selected_insights_key)

    else:
        setattr(st.session_state, selected_insights_key, project["selected_insights"])
    
    if "insights" not in project:
        project["insights"] = {}
    
    if hasattr(st.session_state, insights_key):
        project["insights"] = getattr(st.session_state, insights_key)

    else:
        setattr(st.session_state, insights_key, project["insights"])
    
    render_header(f"Project: {current_project}", "Chat, explore files, and analyze insights")
    
    col1, col2, _ = st.columns([1, 1, 3])

    with col1:

        if st.button("🏠 Dashboard", key="proj_dashboard_btn", use_container_width=True):
            navigate_to("dashboard")

    with col2:

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
    
    active_tab = st.session_state.get("active_tab", "Chat")
    tab_options = ["Chat", "Files", "All Insights", "Selected Insights", "Settings"]
    active_index = tab_options.index(active_tab) if active_tab in tab_options else 0
    
    chat_tab, files_tab, insights_tab, selected_insights_tab, settings_tab = st.tabs(tab_options)
    
    if hasattr(st.session_state, 'generate_insights_for') and st.session_state.generate_insights_for:
        file_to_analyze = st.session_state.generate_insights_for

        if file_to_analyze in project["files"] and (project["insights"].get(file_to_analyze) is None):

            with st.spinner(f"Generating insights for {file_to_analyze}... This may take a few minutes."):

                try:
                    
                    csv_path = project["file_paths"].get(file_to_analyze)

                    if csv_path and os.path.exists(csv_path):
                        insights_data = run_insight_pipeline(csv_path)
                        project["insights"][file_to_analyze] = insights_data
                        st.success("Insights generated successfully!")

                    else:
                        st.error(f"File not found: {csv_path}")

                except Exception as e:
                    st.error(f"Error generating insights: {str(e)}")
        
        st.session_state.generate_insights_for = None
    
    with chat_tab:
        chat_container = st.container()

        with chat_container:
            
            if project["messages"]:
                
                for message in project["messages"]:
                    role = message["role"]
                    content = message["content"]
                    
                    if role == "user":
                        with st.chat_message("user", avatar="👤"):
                            st.write(content)

                    elif role == "assistant":

                        with st.chat_message("assistant", avatar="🤖"):

                            if content.endswith('.png') and os.path.exists(content):
                                st.image(content)

                            else:
                                st.write(content)
            else:
                st.info("No messages yet. Start the conversation by asking a question below.")

    with files_tab:
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
                            project["file_paths"][file.name] = file_path
                            project["insights"][file.name] = None
                            st.success(f"Uploaded {file.name}")

                        else:
                            st.info(f"{file.name} already exists")
        
        if project["files"]:
            st.markdown("### Your Files")

            for file in project["files"]:
                st.markdown(f"""
                <div style="padding: 0.5rem; border-radius: 4px; margin-bottom: 0.5rem; font-size: 1rem; 
                            border: 1px solid rgba(49, 51, 63, 0.2); background-color: #1e1e1e;">
                    <span style="margin-top: 0; margin-bottom: 0.5rem;">{file}</span>
                </div>
                """, unsafe_allow_html=True)
                
                view_btn, gen_insights_btn, delete_btn = st.columns(3)
                
                with view_btn:

                    if st.button("View", key=f"view_file_{file}_{current_project}", use_container_width=True):
                        navigate_to("file_view", file=file)
                        
                with gen_insights_btn:

                    if st.button("Generate Insights", key=f"gen_insight_{file}_{current_project}", use_container_width=True):

                        with st.spinner(f"Generating insights for {file}... This may take a few minutes."):

                            try:

                                csv_path = project["file_paths"].get(file)
                                
                                if csv_path and os.path.exists(csv_path):
                                    insights_data = run_insight_pipeline(csv_path)
                                    project["insights"][file] = insights_data
                                    
                                    json_path = csv_path.replace('.csv', '.json')

                                    with open(json_path, 'w') as f:
                                        json.dump(insights_data, f)
                                        
                                    st.success("Insights generated successfully!")
                                    st.session_state.active_tab = "All Insights"

                                    st.rerun()

                                else:
                                    st.error(f"File not found: {csv_path}")
                                    
                            except Exception as e:
                                st.error(f"Error generating insights: {str(e)}")
                                st.info(f"Make sure the file exists and is properly formatted.")
                
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
    
    with insights_tab:
        st.markdown("## All Insights")
        
        has_insights = False

        for file in project["files"]:

            if project["insights"].get(file):
                has_insights = True
                break

            else:
                json_path = os.path.join(project["path"], file.replace('.csv', '.json'))

                if os.path.exists(json_path):

                    try:

                        with open(json_path, 'r') as f:
                            insights_data = json.load(f)
                            project["insights"][file] = insights_data
                            has_insights = True

                    except Exception as e:
                        st.error(f"Error loading insights from {json_path}: {e}")
                
        if has_insights:
            file_options = [file for file in project["files"] if project["insights"].get(file)]

            if file_options:
                selected_file = st.selectbox("Select a file to view insights", file_options, key="view_insight_file_select")
                
                insights_data = project["insights"].get(selected_file, {})

                if insights_data:
                    insights = insights_data.get("sql_queries", {})

                    if insights:

                        if selected_file not in project["selected_insights"]:
                            project["selected_insights"][selected_file] = []
                            
                        search_term = st.text_input("Search insights", key=f"search_insights_{selected_file}", 
                                                  placeholder="Filter by keyword...")
                        
                        for key, insight in insights.items():
                            if "insight_summary" not in insight:
                                continue
                                
                            summary = insight.get("insight_summary", "")
                            question = insight.get("question", "") or insight.get("insight_question", "")
                            if search_term and not (search_term.lower() in summary.lower() or search_term.lower() in question.lower()):
                                continue
                                
                            with st.expander(summary, expanded=False):
                                question_text = insight.get("question", "") or insight.get("insight_question", "")

                                if question_text:
                                    st.markdown("**Question:**")
                                    st.code(question_text, language="text")
                                
                                query = insight.get("query", "") or insight.get("sql_query", "")

                                if query:
                                    st.markdown("**SQL Query:**")
                                    st.code(query, language="sql")
                                
                                if "result" in insight:
                                    st.markdown("**Result:**")

                                    try:
                                        result_data = insight["result"]
                                        df = pd.DataFrame(result_data)
                                        st.dataframe(df, use_container_width=True)

                                    except Exception as e:
                                        st.write("Error displaying result:", e)

                                
                                insight_id = str(hash(summary))
                                
                                is_selected = any(s.get('insight_summary') == insight.get('insight_summary') 
                                               for s in project["selected_insights"].get(selected_file, []))
                                
                                button_label = "Selected ✓" if is_selected else "Select"
                                button_type = "secondary" if is_selected else "primary"
                                
                                if st.button(button_label, key=f"btn_select_{selected_file}_{key}", 
                                           help="Add to selected insights"):
                                    if not is_selected:
        
                                        if selected_file not in project["selected_insights"]:
                                            project["selected_insights"][selected_file] = []
                                        
                                        insight_copy = insight.copy()
                                        insight_copy["id"] = insight_id
                                        project["selected_insights"][selected_file].append(insight_copy)
                                        
                                        st.success("Added to selected insights")

                                    else:
                                        project["selected_insights"][selected_file] = [
                                            s for s in project["selected_insights"].get(selected_file, [])
                                            if s.get('insight_summary') != insight.get('insight_summary')
                                        ]
                                        st.info("Removed from selected insights")
                                    
                                    setattr(st.session_state, selected_insights_key, project["selected_insights"])
                                    st.rerun()
                    else:
                        st.info(f"No insights found for {selected_file}. Generate insights for this file first.")
                else:
                    st.info(f"No insights found for {selected_file}. Generate insights for this file first.")
        else:
            st.info("No insights available. Go to the Files tab to generate insights for your files.")
    
    with selected_insights_tab:
        st.markdown("## Selected Insights")
        
        has_selected = False
        total_selected = 0
        
        for file, insights in project["selected_insights"].items():
            total_selected += len(insights)

            if insights:
                has_selected = True
        
        if has_selected:
            st.markdown(f"### {total_selected} insights selected")
            
            for file, insights in project["selected_insights"].items():
                
                if insights:
                    st.markdown(f"#### From {file}")
                    
                    for i, insight in enumerate(insights):
                        st.markdown(f"""
                        <div style="padding: 1rem; margin-bottom: 0.75rem; border-radius: 6px; border: 1px solid rgba(250, 250, 250, 0.2);">
                            <p style="font-weight: 500;">{i+1}. {insight.get('insight_summary', 'No summary available')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("Remove", key=f"remove_{file}_{i}", type="secondary"):
                            project["selected_insights"][file].pop(i)
                            setattr(st.session_state, selected_insights_key, project["selected_insights"])
                            st.rerun()
        else:
            st.info("No insights selected. Go to the All Insights tab to select insights.")
    
    with settings_tab:

        model_choice = st.selectbox(
            "Model",
            ["gpt-3.5-turbo", "gpt-4"],
            index=0 if project.get("model") != "gpt-4" else 1,
            key=f"model_select_{current_project}"
        )
        project["model"] = model_choice

        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, 
                             help="Higher values make output more random, lower values more deterministic",
                             key=f"temp_slider_{current_project}")
        project["temperature"] = temperature
        
        if project["messages"] and st.button("Clear Chat History", key=f"clear_chat_{current_project}"):
            project["messages"] = []
            st.rerun()
        
        with st.expander("💡 Pro Tip: Creating Alerts", expanded=False):
            st.markdown("""
            You can ask the AI to create alerts for your data. Try phrases like:
            - "Create an alert when sales drop below 1000"
            - "Alert me if customer complaints exceed 5% of total feedback"
            - "Create an alert for monthly revenue targets"
            - "Notify me about inventory levels below threshold"
            
            Alerts will appear on the main dashboard for easy monitoring.
            """)
    
    if active_tab != st.session_state.get("active_tab"):
        st.session_state.active_tab = active_tab
    
    chat_input_placeholder = "Waiting for AI response..." if st.session_state.ai_thinking else "Ask about your data or create alerts..."

    
    if prompt := st.chat_input(chat_input_placeholder, key="chat_input", disabled=st.session_state.ai_thinking):

        project["messages"].append({"role": "user", "content": prompt})
        
        create_alert = any(phrase in prompt.lower() for phrase in [
            "create alert", "create an alert", "set up alert", "set up an alert", 
            "add alert", "add an alert", "make alert", "make an alert", "notify me"
        ])
        
        has_selected_insights = any(insights for insights in project.get("selected_insights", {}).values())

        if has_selected_insights and len(prompt.split()) < 5 and not any(keyword in prompt.lower() for keyword in ["compare", "explain", "tell me about", "insight"]):
            system_msg = "Note: The user has selected insights. Their message might be referring to those insights."
            project["messages"].append({"role": "system", "content": system_msg})
        
        if create_alert:
            system_msg = "Note: The user wants to create an alert. Respond with a simple, direct alert message."
            project["messages"].append({"role": "system", "content": system_msg})
        
        st.session_state.ai_thinking = True
        st.rerun()
    
    if st.session_state.ai_thinking and project["messages"] and project["messages"][-1]["role"] == "user":

        with chat_tab:

            with st.chat_message("assistant", avatar="🤖"):
                try:
                    user_query = project["messages"][-1]["content"]

                    last_conversations = []

                    for msg in reversed(project["messages"][:-1]): 

                        if msg["role"] in ["user", "assistant"]:

                            last_conversations.append(f"{msg['role'].title()}: {msg['content']}")

                            if len(last_conversations) >= 4: 
                                break
                    
                    if last_conversations:
                        conversation_context = "\n".join(reversed(last_conversations))
                        user_query = f"Previous conversation:\n{conversation_context}\n\nCurrent question: {user_query}"
                    
                    all_insights = {}
                
                    for file, selected_insights_list in project.get("selected_insights", {}).items():
                        for i, insight in enumerate(selected_insights_list):
                            insight_key = f"selected_{file}_{i}"
                            all_insights[insight_key] = {
                                "insight_question": insight.get('question', '') or insight.get('insight_question', ''),
                                "insight_summary": insight.get('insight_summary', ''),
                                "insight_query": insight.get('query', '') or insight.get('sql_query', ''),
                                "insight_data": insight.get('result', {}),
                                "is_selected": True,
                                "file_name": file,
                                "selection_order": i
                            }
                            
                    response = process_chat_query(
                        user_query=user_query,
                        selected_insights=all_insights
                    )
                    
                    if response.endswith('.png') and os.path.exists(response):
                        st.image(response)
                    else:
                        st.write(response)
                    
                    project["messages"].append({"role": "assistant", "content": response})
                    
                except Exception as e:

                    st.error(f"Error: {e}")
                    
                    project["messages"].append({
                        "role": "system", 
                        "content": f"❌ Error: Could not generate response. {str(e)}"
                    })
                
                finally:

                    st.session_state.ai_thinking = False
        
        st.rerun()