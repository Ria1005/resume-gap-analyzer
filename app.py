"""
Resume-to-Job Gap Analyzer - Main Application Entrypoint.
A five-page Streamlit website configured with top navigation.
"""

import streamlit as st
from ui_components import apply_theme

# Page configuration
st.set_page_config(
    page_title="Resume-to-Job Gap Analyzer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_theme()

# Define the 5 navigation pages
pages = [
    st.Page("views/home.py", title="Home", url_path="", default=True),
    st.Page("views/how_to_use.py", title="How to use", url_path="how-to-use"),
    st.Page(
        "views/dataset_and_preprocessing.py",
        title="Dataset and preprocessing",
        url_path="dataset-and-preprocessing",
    ),
    st.Page("views/analyzer.py", title="Analyzer", url_path="analyzer"),
    st.Page(
        "views/results_and_limits.py",
        title="Results and limits",
        url_path="results-and-limits",
    ),
]

nav = st.navigation(pages, position="top")
nav.run()
