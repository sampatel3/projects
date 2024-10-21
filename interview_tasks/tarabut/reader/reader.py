import pandas as pd
from sqlalchemy import create_engine

# accounts_url = "https://drive.google.com/file/d/1XtUY-zIDKZYFellrRT_HCGU1NL0y2_yL/view?usp=drive_link"
# user_consents_url = "https://drive.google.com/file/d/1SGaGeyEcYxrQW0FYXzKCC48nndkdIUg4/view?usp=drive_link"
# transactions_url = "https://drive.google.com/file/d/1wGtAVKhD4g6Ii_iNnCnWAkYs6uPk_YCq/view?usp=drive_link"
accounts_url = "accounts.csv"
user_consents_url = "users.csv"
transactions_url = "transaction.csv"

# read data
user_consents_data = pd.read_csv(user_consents_url)
accounts_data = pd.read_csv(accounts_url)
transactions_data = pd.read_csv(transactions_url)

# convert numeric columns to float
accounts_data['account_balance'] = accounts_data['account_balance'].str.replace(',', '').astype(float)
transactions_data['transaction_amount'] = transactions_data['transaction_amount'].str.replace(',', '').astype(float)
transactions_data['transaction_date'] = pd.to_datetime(transactions_data['transaction_date'], format='%d/%m/%Y')

# database connection
engine = create_engine('postgresql://sampatel3:Tulegatan37@postgres_db:5432/tarabutdb')

# insert data into PostgreSQL
user_consents_data.to_sql('user_consents', engine, if_exists='replace', index=False)
accounts_data.to_sql('accounts', engine, if_exists='replace', index=False)
transactions_data.to_sql('transactions', engine, if_exists='replace', index=False)

print("Data successfully inserted into PostgreSQL")

