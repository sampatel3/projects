import streamlit as st
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix

# Generate a more varied and realistic transaction dataset
def generate_transaction_data(num_transactions=100):
    data = {
        'Transaction ID': [f'T{i}' for i in range(1, num_transactions + 1)],
        'Transaction Amount': [random.randint(100, 50000) for _ in range(num_transactions)],
        'Location': [random.choice(['Domestic', 'International']) for _ in range(num_transactions)],
        'Transaction Time': [random.randint(0, 23) for _ in range(num_transactions)],
        'Frequency': [random.randint(1, 10) for _ in range(num_transactions)],
        'IP Address': [f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}" for _ in range(num_transactions)],
        'Device': [random.choice(['Desktop', 'Mobile', 'Tablet']) for _ in range(num_transactions)],
        'Payment Method': [random.choice(['Credit Card', 'PayPal', 'Bank Transfer']) for _ in range(num_transactions)],
        'Customer Age': [random.randint(18, 80) for _ in range(num_transactions)],
        'Account Age (days)': [random.randint(1, 3650) for _ in range(num_transactions)],
        'Previous Transactions': [random.randint(0, 100) for _ in range(num_transactions)]
    }
    return pd.DataFrame(data)

# Rules-based fraud detection logic
def rules_based_fraud_detection(row, amount_threshold, location_flag, frequency_threshold, device_flag, payment_flag):
    if row['Transaction Amount'] > amount_threshold:
        return True
    if location_flag and row['Location'] == 'International':
        return True
    if row['Frequency'] > frequency_threshold:
        return True
    if device_flag and row['Device'] == 'Mobile':
        return True
    if payment_flag and row['Payment Method'] == 'PayPal':
        return True
    if row['Customer Age'] < 25 and row['Transaction Amount'] > 10000:
        return True
    if row['Account Age (days)'] < 30 and row['Transaction Amount'] > 5000:
        return True
    if row['Previous Transactions'] == 0 and row['Transaction Amount'] > 1000:
        return True
    return False

# Generate more data for training
train_df = generate_transaction_data(1000)

# Create features and labels
X = train_df[['Transaction Amount', 'Frequency', 'Transaction Time', 'Customer Age', 'Account Age (days)', 'Previous Transactions']]
y = (train_df['Transaction Amount'] > 20000) | \
    ((train_df['Transaction Amount'] > 15000) & (train_df['Location'] == 'International')) | \
    ((train_df['Device'] == 'Mobile') & (train_df['Payment Method'] == 'PayPal')) | \
    ((train_df['Customer Age'] < 25) & (train_df['Transaction Amount'] > 10000)) | \
    ((train_df['Account Age (days)'] < 30) & (train_df['Transaction Amount'] > 5000)) | \
    ((train_df['Previous Transactions'] == 0) & (train_df['Transaction Amount'] > 1000))

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)

# Streamlit UI
st.title('Fraud Detection Demo: Rules-Based vs GenAI Model')

# Sidebar for adjusting rules-based model parameters
st.sidebar.header('Rules-Based Model Parameters')
amount_threshold = st.sidebar.slider('Amount Threshold ($)', min_value=5000, max_value=50000, value=10000)
location_flag = st.sidebar.checkbox('Flag International Transactions', value=True)
frequency_threshold = st.sidebar.slider('Max Transactions per Hour', min_value=1, max_value=10, value=3)
device_flag = st.sidebar.checkbox('Flag Mobile Device Transactions', value=False)
payment_flag = st.sidebar.checkbox('Flag PayPal Transactions', value=False)

# Toggle between models
model_choice = st.radio("Choose Detection Model to Display", ('Rules-Based Model', 'GenAI Model'))

# Generate test data
df = generate_transaction_data(200)

# Apply both models to the test data
df['Rules_Based_Flag'] = df.apply(lambda row: rules_based_fraud_detection(row, amount_threshold, location_flag, frequency_threshold, device_flag, payment_flag), axis=1)
X_test = df[['Transaction Amount', 'Frequency', 'Transaction Time', 'Customer Age', 'Account Age (days)', 'Previous Transactions']]
X_test_scaled = scaler.transform(X_test)
df['GenAI_Flag'] = rf_model.predict(X_test_scaled)

# Display the resulting dataset
st.write("### Transaction Dataset with Fraud Flags")
st.write(df)

# Create comparison table
comparison_data = {
    'Model': ['Rules-Based Model', 'GenAI Model'],
    'Fraudulent Transactions': [df['Rules_Based_Flag'].sum(), df['GenAI_Flag'].sum()],
    'Legitimate Transactions': [(~df['Rules_Based_Flag']).sum(), (~df['GenAI_Flag']).sum()]
}
comparison_df = pd.DataFrame(comparison_data)

# Display comparison table
st.write("### Model Comparison")
st.write("This table shows the number of fraudulent and legitimate transactions detected by each model.")
st.write(comparison_df)

# Visualization for the selected model
st.write(f"### {model_choice} Results")

# Fraud count
fraud_count = df[f'{"Rules_Based" if model_choice == "Rules-Based Model" else "GenAI"}_Flag'].value_counts()
fraud_count_0 = fraud_count.get(False, 0)
fraud_count_1 = fraud_count.get(True, 0)

# Bar chart
fig, ax = plt.subplots()
ax.bar(['Legitimate', 'Fraudulent'], [fraud_count_0, fraud_count_1], color=['green', 'red'])
ax.set_xlabel("Transaction Type")
ax.set_ylabel("Number of Transactions")
ax.set_title(f"Fraud Flags in {model_choice}")
st.pyplot(fig)

# Confusion Matrix
cm = confusion_matrix(df[f'{"Rules_Based" if model_choice == "Rules-Based Model" else "GenAI"}_Flag'], 
                      df[f'{"Rules_Based" if model_choice == "Rules-Based Model" else "GenAI"}_Flag'])
fig, ax = plt.subplots()
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Legitimate', 'Fraudulent'], yticklabels=['Legitimate', 'Fraudulent'], ax=ax)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
ax.set_title(f'Confusion Matrix - {model_choice}')
st.pyplot(fig)

# Feature Importance (for GenAI model)
if model_choice == 'GenAI Model':
    st.write("### Feature Importance in GenAI Model")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)

    fig, ax = plt.subplots()
    sns.barplot(x='importance', y='feature', data=feature_importance, ax=ax)
    ax.set_title('Feature Importance in GenAI Model')
    st.pyplot(fig)

# Model Comparison Explanation
st.write("### Interpreting the Model Comparison")
st.write("The comparison table above shows the number of fraudulent and legitimate transactions detected by each model:")
st.write("1. Fraudulent Transactions: The number of transactions flagged as fraudulent by the model.")
st.write("2. Legitimate Transactions: The number of transactions considered legitimate by the model.")
st.write("\nCompare these numbers to understand the differences between the two approaches. The Rules-Based Model offers interpretability and easy adjustments, while the GenAI Model may capture more complex patterns in the data.")
