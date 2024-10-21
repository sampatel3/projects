import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
import plotly.express as px

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

st.header("Task 2")
st.write("""Explore the transaction data using any suitable tools (queries, pivot table, data frames).
Can you identify any interesting patterns?""")

# data transformation
st.subheader("Data Load and Transformation")
st.write("""Load the 3 datasets, join on common keys and apply transformations to simplify the analysis:
- keep users where consent is active: assumption that revoked consent implies transactions are old
- keep transactions for the last 6 months: assumption that older transactions are not relevant 
""")
with st.echo():
    # load data and format keys as string
    user_consents, accounts, transactions = load_data()
    transactions['transaction_yymm'] = transactions['transaction_date'].dt.strftime('%y-%m')
    transactions['debit_amount'] = np.where(transactions['transaction_amount'] < 0, transactions['transaction_amount'], 0)
    transactions['credit_amount'] = np.where(transactions['transaction_amount'] > 0, transactions['transaction_amount'], 0)
    transactions['account_id'] = transactions['account_id'].astype(str)
    user_consents['user_id'] = user_consents['user_id'].astype(str)
    accounts['user_id'] = accounts['user_id'].astype(str)
    accounts['account_id'] = accounts['account_id'].astype(str)

    # join data and keep only active consent_status accounts - assumption
    accounts_transactions = transactions.merge(accounts, on='account_id', how='left')
    user_transactions = accounts_transactions.merge(user_consents, on='user_id', how='left')
    user_transactions = user_transactions.loc[user_transactions['consent_status'] == 'active']

    # keep only last 6 months of transactions - assumption
    most_recent_date = user_transactions['transaction_date'].max()
    user_transactions = user_transactions[user_transactions['transaction_date'] >= most_recent_date - pd.DateOffset(months=6)]


st.subheader("Analyse the monthly transactions by type for each user or account")
st.write("""Notable findings that may interest a Bank:
- High number of transactions, stable income: active users, verify connected to primary accounts
- High consecutive transactions: stable spending patterns
- For lending risk assessment:
    - High/ Stable income - high income users, lower risk, higher lending capacity
    - Stable rental payments - lower risk
    - Stable loan payments - lower risk
    - Stable utility payments - lower risk
- For marketing offers / personalisation:
    - High volume transactors at another Bank - target for account transfer
    - High average transaction amount: high net worth users, cross-sell premium services
    - High net amount transactions: high earners, target for investment products
    - High grocery payments - supermarket offers
    - High/ Stable entertainment payments - entertainment offers
    - Medical payments - health insurance offers
    - Dining payments - dine out offers
    ...
    
Further thoughts:
- Analyse type of accounts - assess whether holding large savings at another Bank
- Analyse transaction information / unstructured text - categorisation is hiding useful information e.g. where the customer is dining out/ buying groceries, if the customer is often travelling, etc.
""")
# data parameters
transaction_types = list(user_transactions['transaction_type'].unique()) + ["all"]
select_type = st.selectbox('Select Transaction Type', transaction_types, index=len(transaction_types)-1)
aggr_type = st.selectbox('Select Aggregation Key', ['account_id', 'user_id'], index=1)

st.write(f"Plots of monthly transactions-{select_type} by {aggr_type}")

transaction_volume = user_transactions.groupby(['transaction_yymm',aggr_type]).agg(
    total_transactions=('transaction_id', 'count'),
    total_transaction_amount=('transaction_amount', 'sum')
).reset_index()

transaction_type_volume = user_transactions.groupby(['transaction_yymm',aggr_type,'transaction_type']).agg(
    total_transactions=('transaction_id', 'count'),
    total_transaction_amount=('transaction_amount', 'sum')
).reset_index()

if select_type == "all":
    plot_data = transaction_volume
else:
    plot_data = transaction_type_volume[transaction_type_volume['transaction_type'] == select_type]

with st.container():
    fig = px.scatter(plot_data,
                  x='transaction_yymm',
                  y='total_transactions',
                  color=aggr_type,
                  facet_col=aggr_type,
                  labels={'transaction_yymm': 'Transaction Year-Month', 'total_transactions': 'Total Transactions'},
                  title = f'Total Transactions by {aggr_type} for {select_type}'
                  )
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with st.container():
    fig = px.scatter(plot_data,
                     x='transaction_yymm',
                     y='total_transaction_amount',
                     color=aggr_type,
                     facet_col=aggr_type,
                     labels={'transaction_yymm': 'Transaction Year-Month', 'total_transactions': 'Total Transactions'},
                     title = f'Total Transactions Amount by {aggr_type} for {select_type}'
                     )
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

# feature engineering
st.subheader("Feature Engineering")
st.write("""Generate features for customer segmentation by user id and transaction type:
- Number of transactions
- Average transaction amount
- Total transaction amount
- Total number of credit/income and debit/expense transactions
- Consecutive number of monthly transactions""")

aggregated_data = user_transactions.groupby(['user_id']).agg(
    total_transactions=('transaction_amount', 'count'),
    total_income_transactions=('transaction_amount', lambda x: (x > 0).sum()),
    total_expense_transactions=('transaction_amount', lambda x: (x < 0).sum()),
    total_transaction_amount=('transaction_amount', 'sum'),
    avg_transaction_amount=('transaction_amount', 'mean'),
).reset_index()

avg_transaction_by_type = user_transactions.groupby(['user_id', 'transaction_type']).agg(
    avg_transaction_amount=('transaction_amount', 'mean'),
    transaction_count=('transaction_amount', 'count')
).reset_index()

avg_transaction_pivot = avg_transaction_by_type.pivot(index='user_id',
                                                      columns='transaction_type',
                                                      values=['avg_transaction_amount', 'transaction_count'])

avg_transaction_pivot.columns = [f'{stat}_{trans_type}' for stat, trans_type in avg_transaction_pivot.columns]
avg_transaction_pivot = avg_transaction_pivot.reset_index()

def count_consecutive_transactions(x):
    x['consecutive_flag'] = (x['transaction_type'] != x['transaction_type'].shift()).cumsum()
    consecutive_count = x.groupby(['transaction_type', 'consecutive_flag']).size().groupby('transaction_type').sum()
    return consecutive_count / 6

consecutive_transactions = user_transactions.groupby('user_id').apply(count_consecutive_transactions, include_groups=False).reset_index()
consecutive_pivot = consecutive_transactions.pivot(index='user_id',
                                                   columns='transaction_type',
                                                   values=0)
consecutive_pivot.columns = [f'consecutive_{trans_type}_pct' for trans_type in consecutive_pivot.columns]
consecutive_pivot = consecutive_pivot.reset_index()

user_transaction_features = aggregated_data.merge(avg_transaction_pivot, on='user_id', how='left')
user_transaction_features = user_transaction_features.merge(consecutive_pivot, on='user_id', how='left')

if st.button("Run and Load to DB"):
    try:
        user_transaction_features.to_sql('user_transaction_features', engine, if_exists='replace', index=False)
        test = pd.read_sql('SELECT * FROM user_transaction_features', engine)
        st.dataframe(test)
    except Exception as e:
        st.error(f"An error occurred: {e}")
