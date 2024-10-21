import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

if __name__ == "__main__":
    st.sidebar.page_link("app.py", label="Homepage")
    st.sidebar.page_link("pages/infra.py", label="Infrastructure")
    st.sidebar.page_link("pages/task1.py", label="Task 1")
    st.sidebar.page_link("pages/task2.py", label="Task 2")
    st.sidebar.page_link("pages/task3.py", label="Task 3")

    # Title
    st.header("Infrastructure")

    # Introduction
    st.subheader("System Architecture")
    st.write("""
    This project uses a containerized architecture to manage data ingestion, database management, and application interface.
    Built using Docker Compose, which allows  is used manage three services:
    - **PostgreSQL database** (container for storing the data).
    - **Reader** (container for reading CSV files and importing them into PostgreSQL).
    - **Streamlit application** (container for hosting web application to present results (connected to PostgreSQL)).
    """)
    st.image("diagram.png", caption="Architecture Diagram")

    # PostgreSQL Schema Section
    st.subheader("PostgreSQL Database Schema")
    st.write("Below is the schema of the PostgreSQL database used in this system.")
    st.write("""
    - **user_consents** is linked to **accounts** through the `user_id` field.
    - **accounts** is linked to **transactions** through the `account_id` field.
    """)
    with open('init.sql', 'r') as file:
        sql_code = file.read()
    st.code(sql_code, language='sql')

    # Query
    st.subheader("Database Query")
    query = st.text_area("Enter a SQL query to run on the database:")
    if st.button("Run Query"):
        engine = create_engine('postgresql://sampatel3:Tulegatan37@postgres_db:5432/tarabutdb')
        try:
            result = pd.read_sql(query, engine)
            st.dataframe(result)
        except Exception as e:
            st.error(f"An error occurred: {e}")

