import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os


st.set_page_config(
        page_title="Hello",
        page_icon="👋",
)

st.title("Hello! 👋")

st.sidebar.page_link("app.py", label="Homepage")
st.sidebar.page_link("pages/infra.py", label="Infrastructure")
st.sidebar.page_link("pages/task1.py", label="Task 1")
st.sidebar.page_link("pages/task2.py", label="Task 2")
st.sidebar.page_link("pages/task3.py", label="Task 3")
