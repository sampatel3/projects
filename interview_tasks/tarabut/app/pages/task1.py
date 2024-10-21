import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# database connection
engine = create_engine('postgresql://sampatel3:Tulegatan37@postgres_db:5432/tarabutdb')

# load data
@st.cache_data
def load_data():
    user_consents = pd.read_sql('SELECT * FROM user_consents', engine)
    accounts = pd.read_sql('SELECT * FROM accounts', engine)
    transactions = pd.read_sql('SELECT * FROM transactions', engine)
    return user_consents, accounts, transactions

def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        sql = file.read().strip()
    return sql

@st.cache_data
def execute_query(query):
    with engine.connect() as connection:
        result = connection.execute(text(query))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

st.sidebar.page_link("app.py", label="Homepage")
st.sidebar.page_link("pages/infra.py", label="Infrastructure")
st.sidebar.page_link("pages/task1.py", label="Task 1")
st.sidebar.page_link("pages/task2.py", label="Task 2")
st.sidebar.page_link("pages/task3.py", label="Task 3")

# user_consents, accounts, transactions = load_data()

st.header("Task 1")
st.write("Write a query to summarize each user’s activity. Think about which metrics might be most useful for our client.")

st.write("""Query summarises:
- Activity: consent status, recent transaction activity
- Accounts: types, number of accounts, open/ closed accounts, balance
- Banks: connected Banks (one or multiple)
- Transactions: number of transactions, total debit/credit amount, average transaction amount, average income

This query will help the client to identify which User's have connected primary accounts, whether they already use multiple Banks, the status of the connected accounts and the transaction activity.
 """)
sql_query = read_sql_file('task1.sql')
st.code(sql_query, language='sql')

if st.button("Run Query"):
    try:
        result_df = execute_query(sql_query)
        st.write(result_df)
    except Exception as e:
        st.error(f"An error occurred: {e}")