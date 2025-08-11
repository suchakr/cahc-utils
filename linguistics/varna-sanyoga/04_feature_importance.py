#!/usr/bin/env python3
# Feature importance visualization for Sanskrit kavya sound clusters
# This script analyzes which sounds are most important in distinguishing between kavya clusters

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import seaborn as sns

# Load the data
data = pd.read_csv('msound_normalized.csv')

# this is needed to ensure the column names are in IAST format and redered properly by matplotlib
iast_col_str = "kavya, a, ā, i, ī, u, ū, ṛ, e, ai, o, au, k, kh, g, gh, ṅ, c, ch, j, jh, ñ, ṭ, ṭh, ḍ, ḍh, ṇ, t, th, d, dh, n, p, ph, b, bh, m, y, r, l, v, ś, ṣ, s, h"
iast_cols = iast_col_str.split(", ")
data.columns = iast_cols

# The first column contains kavya names which we'll use as labels
kavya_names = data['kavya'].values
# The rest of the columns are sound frequencies
X = data.drop('kavya', axis=1)

# Standardize the data (important for clustering)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Perform K-means clustering with 3 clusters (based on previous analysis)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
labels = kmeans.fit_predict(X_scaled)

# Create a DataFrame with the cluster labels
kavya_df = pd.DataFrame({'kavya': kavya_names, 'cluster': labels})

# Get the cluster centers in the original feature space
centers = kmeans.cluster_centers_
centers_original = scaler.inverse_transform(centers)
centers_df = pd.DataFrame(centers_original, columns=X.columns)

# Find the most discriminative features (sounds)
# Calculate the variance of each sound across cluster centers
feature_variance = pd.DataFrame({
    'sound': X.columns,
    'variance': np.var(centers_original, axis=0)
})

# Sort features by variance (higher variance means more discriminative)
top_features = feature_variance.sort_values(by='variance', ascending=False).head(15)

# Create a bar plot of the most discriminative features
plt.figure(figsize=(12, 8))
sns.barplot(x='sound', y='variance', data=top_features)
plt.title('Top 15 Most Discriminative Sounds Between Kavya Clusters', fontsize=16)
plt.xlabel('Sound', fontsize=14)
plt.ylabel('Variance Across Clusters', fontsize=14)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('discriminative_sounds.png', dpi=300, bbox_inches='tight')

# Create a heatmap showing the most discriminative sounds by cluster
plt.figure(figsize=(15, 8))
top_sound_cols = top_features['sound'].tolist()
sns.heatmap(centers_df[top_sound_cols], annot=True, fmt=".3f", cmap="YlGnBu",
            yticklabels=["Cluster 1", "Cluster 2", "Cluster 3"])
plt.title('Top 15 Most Discriminative Sounds by Cluster', fontsize=16)
plt.xlabel('Sound', fontsize=14)
plt.ylabel('Cluster', fontsize=14)
plt.tight_layout()
plt.savefig('discriminative_sounds_by_cluster.png', dpi=300, bbox_inches='tight')

# Create a visualization showing kavyas by cluster
# Sort the DataFrame by cluster
kavya_df_sorted = kavya_df.sort_values('cluster')

# Create a DataFrame with the original data and cluster labels
full_df = pd.DataFrame(X.values, index=kavya_names, columns=X.columns)
full_df['cluster'] = labels

# Calculate the average sound frequencies for each cluster
cluster_means = full_df.groupby('cluster').mean()

# Create a visualization showing the distribution of kavyas in each cluster
plt.figure(figsize=(12, 8))
for i, cluster_id in enumerate(np.sort(kavya_df['cluster'].unique())):
    kavyas_in_cluster = kavya_df[kavya_df['cluster'] == cluster_id]['kavya'].values
    y_positions = np.arange(len(kavyas_in_cluster)) + i * (len(kavya_df) / 3 + 1)
    plt.barh(y_positions, np.ones(len(kavyas_in_cluster)), height=0.8, 
             color=f'C{i}', alpha=0.7, label=f'Cluster {i+1}')
    for j, y in enumerate(y_positions):
        plt.text(0.1, y, kavyas_in_cluster[j], va='center', fontsize=10)

plt.yticks([])
plt.xlabel('Kavya Groups by Cluster')
plt.title('Kavyas Grouped by Sound Pattern Clusters', fontsize=16)
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig('kavyas_by_cluster.png', dpi=300, bbox_inches='tight')

# Analyze top 5 sounds for each cluster
print("Top 5 most prominent sounds in each cluster:")
for i in range(3):
    print(f"\nCluster {i+1}:")
    top_sounds = centers_df.iloc[i].nlargest(5)
    print(top_sounds)

print("\nAnalysis complete. Check the output images for visualization.")
