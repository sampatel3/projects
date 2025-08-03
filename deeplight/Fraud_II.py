import sys
import subprocess
import streamlit as st
import pandas as pd
import random
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import confusion_matrix, classification_report
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns

# Generate realistic transaction data
def generate_transaction_data(num_transactions=1000):
    np.random.seed(42)  # for reproducibility
    data = {
        'Transaction ID': [f'T{i}' for i in range(1, num_transactions + 1)],
        'Transaction Amount': np.random.normal(loc=500, scale=200, size=num_transactions).clip(0, 5000),  # Gaussian distribution
        'Location': np.random.choice(['Domestic', 'International'], size=num_transactions, p=[0.85, 0.15]),
        'Transaction Time': np.random.randint(0, 24, size=num_transactions),
        'Frequency': np.random.randint(1, 20, size=num_transactions),
        'IP Address': [f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}" for _ in range(num_transactions)],
        'Device': np.random.choice(['Desktop', 'Mobile', 'Tablet'], size=num_transactions),
        'Payment Method': np.random.choice(['Credit Card', 'PayPal', 'Bank Transfer'], size=num_transactions),
        'Customer Age': np.random.randint(18, 80, size=num_transactions),
        'Account Age (days)': np.random.randint(1, 3650, size=num_transactions),
        'Previous Transactions': np.random.randint(0, 100, size=num_transactions),
    }
    df = pd.DataFrame(data)

    # Create time-based and behavioral features
    df['Time Since Last Transaction'] = df['Frequency'] / (df['Transaction Time'] + 1)  # Simulate behavior patterns
    df['Transaction Amount / Account Age'] = df['Transaction Amount'] / (df['Account Age (days)'] + 1)

    return df

def main():
    df = generate_transaction_data()
    st.write("### Generated Transaction Dataset")
    st.write(df.head())

    # Preprocess data
    def preprocess_data(df):
        # One-hot encode categorical variables
        categorical_features = ['Location', 'Device', 'Payment Method']
        encoder = OneHotEncoder()
        encoded_features = encoder.fit_transform(df[categorical_features]).toarray()
        encoded_df = pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(categorical_features))
        
        # Combine with numerical features
        numerical_features = ['Transaction Amount', 'Transaction Time', 'Frequency', 'Customer Age', 
                              'Account Age (days)', 'Previous Transactions', 'Time Since Last Transaction', 
                              'Transaction Amount / Account Age']
        X = pd.concat([df[numerical_features].reset_index(drop=True), pd.DataFrame(encoded_df)], axis=1)
        
        return X

    X = preprocess_data(df)

    # --- Rules-Based Fraud Detection ---
    def rules_based_fraud_detection(row, amount_threshold=3000, location_flag=True, frequency_threshold=10):
        """ Simple rules-based approach to detect fraud based on a few key criteria. """
        if row['Transaction Amount'] > amount_threshold:
            return 1  # Fraudulent
        if location_flag and row['Location'] == 'International':
            return 1  # Fraudulent
        if row['Frequency'] > frequency_threshold:
            return 1  # Fraudulent
        return 0  # Legitimate

    # Apply the rules-based approach to the dataset
    df['Rules-Based Fraud Flag'] = df.apply(rules_based_fraud_detection, axis=1)

    st.write("### Rules-Based Fraud Detection Results")
    st.write(df[['Transaction ID', 'Transaction Amount', 'Location', 'Frequency', 'Rules-Based Fraud Flag']].head())

    # --- Machine Learning-Based (GenAI) Fraud Detection using Random Forest ---
    # Split data for training the model
    y = df['Rules-Based Fraud Flag']  # Assume rules-based flags are the target labels (for training comparison)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Standardize data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Balance the dataset using SMOTE (optional, if class imbalance exists)
    smote = SMOTE()
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)

    # Train a Random Forest classifier
    rf_model = RandomForestClassifier(random_state=42)
    rf_model.fit(X_train_balanced, y_train_balanced)

    # Predict using the trained model
    y_pred = rf_model.predict(X_test_scaled)

    # Calculate confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    # Evaluation metrics for Random Forest
    st.write("### Random Forest (GenAI) Fraud Detection - Confusion Matrix")
    fig, ax = plt.subplots()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Legitimate', 'Fraudulent'], yticklabels=['Legitimate', 'Fraudulent'], ax=ax)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    st.pyplot(fig)  # Pass the figure object here

    st.write("### Random Forest (GenAI) - Classification Report")
    report = classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraudulent'])
    st.text(report)

    # Show Fraud Counts for Both Approaches
    rules_based_fraud_count = df['Rules-Based Fraud Flag'].value_counts()
    ml_fraud_count = pd.Series(y_pred).value_counts()

    st.write("### Comparison of Fraud Detection")
    st.write("#### Rules-Based Fraud Detection:")
    st.write(rules_based_fraud_count)

    st.write("#### GenAI (Random Forest) Fraud Detection:")
    st.write(ml_fraud_count)

    # Visual comparison using Streamlit's native chart
    st.write("### Fraud Detection Comparison: Rules-Based vs GenAI")
    comparison_data = pd.DataFrame({
        'Category': ['Legitimate', 'Fraudulent'],
        'Rules-Based': rules_based_fraud_count,
        'GenAI (Random Forest)': ml_fraud_count
    })
    st.bar_chart(comparison_data.set_index('Category'))

    st.write(f"Python version: {sys.version}")
    st.write(f"Python executable: {sys.executable}")

if __name__ == '__main__':
    main()
