# To run the project:

### Requirements
- Docker
https://docs.docker.com/desktop/install/mac-install/
- PostgreSQL 
`brew install postgresql@15`

### Run locally
- Clone the repository
- Go to the project directory
- Run `docker-compose up --build`
- Web app available locally here: http://0.0.0.0:8501/

# Tarabut Task Description

Analytics and SQL Case Study
You are working for an open banking company and need to analyze user activity. Your task is to get an understanding of the data and create a segmentation of users based on their activity and engagement.
The main objective is identiying interesting opportunities for customer acquisition for our client, a large Saudi bank.

### Data Tables
You are provided with three tables: user_consents, accounts, and transactions.
You can find the data for this exercise in XLS and CSV format here:
https://drive.google.com/drive/folders/16VH_3utdhMFX6IIL-DQBhdT6UtYBT1CE

1. User Consents (user_consents):
   user_id (INT): Unique identifier for each user.
   consent_id (INT): Unique identifier for each consent.
   consent_granted_date (DATE): Date when the user granted consent.
   consent_status (VARCHAR): Status of the consent (e.g., "active", "revoked").

2. Accounts (accounts):
   account_id (INT): Unique identifier for each account.
   user_id (INT): Identifier for the user who owns the account.
   account_type (VARCHAR): Type of account (e.g., "current", "savings").
   account_status (VARCHAR): Status of the account (e.g., "open", "closed").
   account_balance (DECIMAL): Current balance of the account.
   bank_name (VARCHAR): Name of the bank holding the account.

3. Transactions (transactions):
   transaction_id (INT): Unique identifier for each transaction.
   account_id (INT): Identifier for the account associated with the transaction.
   transaction_amount (DECIMAL): Amount of the transaction.
   transaction_date (DATE): Date of the transaction.
   transaction_type (VARCHAR): Type of transaction (e.g., "income", "rent").

### Tasks

1. User Activity Summary
   Write a query to summarize each user’s activity.
   Think about which metrics might be most useful for our client.

2. Transaction Trends
   Explore the transaction data using any suitable tools (queries, pivot table, data frames).
   Can you identify any interesting patterns?

3. User Segmentation
   Based on the above two analysis, create a simple segmentation of users that will help customer acquisition for our client.
   Ensure that the segmentation is adequate for our main objective and justify the criteria you use.
   Feel free to use any method for segmentation you find convenient (e.g. rules based on your previous analysis or any other technique you might find suitable)

Note: the sample data in this exercise is small for the sake of simplicity but assume that each user in our data represents many users with similar behaviour. Feel free to assume these behaviours can be extrapolated reasonably, as if the sample were larger.

### Expectations:
The specific SQL dialect is not important, but correct joining of tables is expected, ensuring the right granularity of the data.
Explanation of the segmentation logic and thought process.
TIP: You can use https://sqliteonline.com/ to load the files into tables and execute SQL, if you find it convenient.