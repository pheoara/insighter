import os
import pandas as pd
import streamlit as st
from insighter.components.ui import render_header
from insighter.utils.state import navigate_to

def render_file_view():

    current_project = st.session_state.current_project
    current_file = st.session_state.current_file
    project_path = st.session_state.projects[current_project]["path"]
    file_path = os.path.join(project_path, current_file)
    
    render_header(current_file, "Viewing file data")
    
    col1, _, _ = st.columns([1, 1, 2])

    with col1:
        if st.button("← Back to Project", key="file_view_back_btn", use_container_width=True):
            navigate_to("project_chat")
    
    with st.spinner("Loading file..."):

        try:
            df = pd.read_csv(file_path)
            
            st.markdown("## Data Summary")
            metrics = st.columns(3)
            metrics[0].metric("Rows", f"{len(df):,}")
            metrics[1].metric("Columns", len(df.columns))
            
            file_size = os.path.getsize(file_path)
            size_str = f"{file_size/1024:.1f} KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f} MB"
            metrics[2].metric("File Size", size_str)
            
            st.markdown("## Data Preview")
            st.dataframe(df, use_container_width=True)
            
            st.markdown("## Column Information")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str),
                'Non-Null Count': df.count(),
                'Null Count': df.isna().sum(),
                'Unique Values': [df[col].nunique() for col in df.columns]
            })

            st.dataframe(col_info, use_container_width=True)
        
            st.markdown("### Column Types")
            cols = st.columns(3)

            for i, (col_name, col_type) in enumerate(df.dtypes.astype(str).to_dict().items()):
                
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="card" style="padding: 0.8rem; margin-bottom: 0.8rem;">
                        <p style="font-weight: 500; margin-bottom: 0.3rem;">{col_name}</p>
                        <p style="color: #666; font-size: 0.9rem;">{col_type}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error loading file: {e}")