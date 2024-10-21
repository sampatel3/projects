import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples

# database connection
engine = create_engine('postgresql://sampatel3:Tulegatan37@postgres_db:5432/tarabutdb')

st.sidebar.page_link("app.py", label="Homepage")
st.sidebar.page_link("pages/infra.py", label="Infrastructure")
st.sidebar.page_link("pages/task1.py", label="Task 1")
st.sidebar.page_link("pages/task2.py", label="Task 2")
st.sidebar.page_link("pages/task3.py", label="Task 3")

st.header("Task 3")
st.write("""Based on the above two analysis, create a simple segmentation of users that will help customer acquisition for our client.
Ensure that the segmentation is adequate for our main objective and justify the criteria you use.
Feel free to use any method for segmentation you find convenient (e.g. rules based on your previous analysis or any other technique you might find suitable)""")

st.subheader("Unsupervised Clustering - K-means")
st.write("K-Means clustering to segment users based on their transactional features/ behaviour. Other clustering algorithms were looked at e.g. DBSCAN, Hierarchical Clustering. K-Means was chosen due to its simplicity and ease of interpretation.")

st.write("""Based on using all transaction features and 3 clusters (based on Elbow plot), there are notable differences between the clusters (especially cluster 3 versus 1,2):
- cluster 3 looks to be high income and low spenders - maybe skewed by deposit payment
- cluster 1 looks to be high spenders

Further thoughts:
- In general, this approach doesn't work so well - too many irrelevant features and not enough data to make meaningful clusters. It would be more appropriate to use logical reasoning to create clusters for specific targeting as described in Task 2.
""")

columns = pd.read_sql('SELECT * FROM user_transaction_features', engine).columns
kmeans_features = st.multiselect('Select Features for K-Means Clustering', columns, default=columns)
kmeans_features = ['user_id'] + kmeans_features
optimal_k = st.number_input('Enter the optimal number of clusters (K)', min_value=2, max_value=10, value=3, step=1)
user_transaction_features = pd.read_sql('SELECT * FROM user_transaction_features', engine)[kmeans_features]

features = user_transaction_features.drop(columns=['user_id'])  # Exclude user_id
features.fillna(0, inplace=True)  # Handle missing values if any
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

kmeans = KMeans(n_clusters=optimal_k, random_state=42)
user_transaction_features['cluster'] = kmeans.fit_predict(scaled_features)
user_transaction_features['cluster_discrete'] = user_transaction_features['cluster'].astype(str)

pca = PCA(n_components=2)
reduced_data = pca.fit_transform(scaled_features)

with st.container():
    fig = px.scatter(x=reduced_data[:, 0], y=reduced_data[:, 1], color=user_transaction_features['cluster_discrete'],
                     labels={'x': 'PCA Component 1', 'y': 'PCA Component 2'},
                     title="K-Means Clustering Visualization (2D using PCA)")
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

silhouette_vals = silhouette_samples(scaled_features, user_transaction_features['cluster'])
user_transaction_features['silhouette_score'] = silhouette_vals
user_transaction_features = user_transaction_features.sort_values(by='silhouette_score', ascending=True)

with st.container():
    fig = px.bar(user_transaction_features,
                 x='silhouette_score',
                 y=user_transaction_features.index,
                 color='cluster_discrete',
                 orientation='h',
                 title='Silhouette Plot for K-Means Clustering',
                 labels={'silhouette_score': 'Silhouette Score', 'index': 'Cluster Members'},
                 template='plotly_white')
    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))  # Add border to bars
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

X = user_transaction_features.drop(columns=['user_id', 'cluster'])  # Features
X.fillna(0, inplace=True)
y = user_transaction_features['cluster']  # Target variable
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X, y)
feature_importances = rf_model.feature_importances_
importance_df = pd.DataFrame({'feature': X.columns, 'importance': feature_importances}).sort_values(by='importance', ascending=False)

with st.container():
    fig = px.bar(importance_df,
                 x='feature',
                 y='importance',
                 title='Feature Importance from Random Forest',
                 labels={'feature': 'Features', 'importance': 'Importance'},
                 template='plotly_white')
    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

cluster_summary = user_transaction_features.groupby('cluster_discrete').mean(numeric_only = True).reset_index()
feature_list = cluster_summary.columns[1:]
select_feature = st.selectbox('Select Feature', feature_list, index=0)
with st.container():
    fig = px.bar(cluster_summary,
                 x='cluster_discrete',
                 y=select_feature,
                 title=f'Average {select_feature} by Cluster',
                 labels={'cluster_discrete': 'Cluster', select_feature: f'Average {select_feature}'},
                 color='cluster_discrete',
                 template='plotly_white')
    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))  # Add border to bars
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

