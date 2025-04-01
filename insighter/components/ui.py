import streamlit as st

def render_header(title, subtitle=""):
    """Renders a consistent page header"""
    st.markdown(f"""
    <div class="app-header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_card(title="", content="", padding="1rem", margin="1rem", card_class="card"):
    """Renders a card with consistent styling, returning HTML that works with st.markdown"""
    html = f"""
    <div class="{card_class}" style="padding: {padding}; margin-bottom: {margin};">
        {f"<h3>{title}</h3>" if title else ""}
        {content}
    </div>
    """
    return html