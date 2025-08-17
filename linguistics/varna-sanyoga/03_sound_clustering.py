#%%
#!/usr/bin/env python3
# Sound clustering for Sanskrit kavyas based on sound patterns
# This script analyzes the normalized sound frequencies in kavyas and clusters them

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import seaborn as sns
from matplotlib.ticker import MaxNLocator
import matplotlib.cm as cm

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

# Determine optimal number of clusters using silhouette scores
sil_scores = []
K_range = range(2, 10)  # Try cluster sizes from 2 to 9
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    sil_score = silhouette_score(X_scaled, labels)
    sil_scores.append(sil_score)
    print(f"K={k}, Silhouette Score: {sil_score:.4f}")

# Plot silhouette scores to find optimal number of clusters
plt.figure(figsize=(10, 6))
plt.plot(K_range, sil_scores, 'o-')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score vs. Number of Clusters')
plt.grid(True)
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  # Force integer ticks on x-axis
plt.savefig('silhouette_scores.png', dpi=300, bbox_inches='tight')

# Choose optimal number of clusters based on the highest silhouette score
optimal_k = K_range[np.argmax(sil_scores)]
print(f"\nOptimal number of clusters based on silhouette score: {optimal_k}")

# Perform K-means clustering with the optimal number of clusters
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
labels = kmeans.fit_predict(X_scaled)

# Apply PCA for dimensionality reduction to visualize in 2D
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Percentage of variance explained by each principal component
explained_variance = pca.explained_variance_ratio_
print(f"\nVariance explained by PC1: {explained_variance[0]:.4f}")
print(f"Variance explained by PC2: {explained_variance[1]:.4f}")
print(f"Total variance explained: {sum(explained_variance):.4f}")

# Create a DataFrame for plotting
plot_df = pd.DataFrame({
    'PC1': X_pca[:, 0],
    'PC2': X_pca[:, 1],
    'Cluster': labels,
    'Kavya': kavya_names
})

# Create the plot
plt.figure(figsize=(12, 8))

# Plot each cluster with a different color
for cluster in range(optimal_k):
    cluster_data = plot_df[plot_df['Cluster'] == cluster]
    plt.scatter(
        cluster_data['PC1'], 
        cluster_data['PC2'], 
        s=80, 
        alpha=0.8, 
        label=f'Cluster {cluster+1}'
    )

# Add labels to points
for i, row in plot_df.iterrows():
    plt.annotate(
        row['Kavya'], 
        (row['PC1'], row['PC2']),
        fontsize=9,
        alpha=0.9,
        xytext=(5, 5),
        textcoords='offset points'
    )
    
plt.xlabel(f'Principal Component 1 ({explained_variance[0]:.1%} variance)')
plt.ylabel(f'Principal Component 2 ({explained_variance[1]:.1%} variance)')
plt.title('Clusters of Sanskrit Kavyas based on Sound Patterns')
plt.legend(title='Clusters')
plt.grid(True, alpha=0.3)
plt.savefig('kavya_clusters_pca.png', dpi=300, bbox_inches='tight')

# Analyze what makes each cluster unique
# Get the cluster centers in the original feature space
centers = kmeans.cluster_centers_

# Inverse transform the centers to get back to the original scale
centers_original = scaler.inverse_transform(centers)

# Create a DataFrame with the original feature names to analyze cluster centers
centers_df = pd.DataFrame(centers_original, columns=X.columns)

# Display the top 5 most dominant sounds for each cluster
print("\nTop 5 most dominant sounds in each cluster:")
for i in range(optimal_k):
    print(f"\nCluster {i+1}:")
    top_sounds = centers_df.iloc[i].sort_values(ascending=False).head(5)
    print(top_sounds)

# Create a heatmap of cluster centers to visualize key differentiating sounds
plt.figure(figsize=(15, 10))
sns.heatmap(centers_df, cmap='viridis', annot=False, cbar_kws={'label': 'Normalized Sound Frequency'})
plt.title('Sound Patterns in Each Cluster')
plt.xlabel('Sounds')
plt.ylabel('Cluster')
plt.savefig('cluster_centers_heatmap.png', dpi=300, bbox_inches='tight')

# Show and save the plot of kavya representations in the feature space of the top 2 principal components
plt.figure(figsize=(14, 10))

# Create a scatter plot with color-coded clusters and sized by distance from cluster center
for cluster in range(optimal_k):
    cluster_data = plot_df[plot_df['Cluster'] == cluster]
    plt.scatter(
        cluster_data['PC1'], 
        cluster_data['PC2'], 
        s=100, 
        alpha=0.8, 
        label=f'Cluster {cluster+1}'
    )

# Add labels with line connections
for i, row in plot_df.iterrows():
    plt.annotate(
        row['Kavya'], 
        (row['PC1'], row['PC2']),
        fontsize=10,
        xytext=(8, 0),
        textcoords='offset points',
        ha='left',
        va='center',
        bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='gray')
    )

# Add feature vectors (eigenvectors scaled by eigenvalues)
feature_names = X.columns
pca_components = pca.components_
feature_vectors = np.transpose(pca.components_)
feature_importance = np.abs(feature_vectors)

# Find top 10 most important features based on magnitude in PC space
top_features_idx = np.argsort(np.sum(feature_importance, axis=1))[-10:]
top_features = [feature_names[i] for i in top_features_idx]

scaling_factor = 5  # Adjust this value to scale the arrows appropriately
for i in top_features_idx:
    plt.arrow(0, 0, 
              pca_components[0, i] * scaling_factor, 
              pca_components[1, i] * scaling_factor, 
              head_width=0.2, 
              head_length=0.2, 
              fc='red', 
              ec='red', 
              alpha=0.5)
    plt.text(pca_components[0, i] * scaling_factor * 1.1, 
             pca_components[1, i] * scaling_factor * 1.1, 
             feature_names[i], 
             fontsize=9, 
             color='darkred', 
             ha='center', 
             va='center',
             bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.8))

plt.xlabel(f'Principal Component 1 ({explained_variance[0]:.1%} variance)')
plt.ylabel(f'Principal Component 2 ({explained_variance[1]:.1%} variance)')
plt.title('Kavya Clusters with Top Contributing Sound Features')
plt.legend(title='Clusters')
plt.grid(True, alpha=0.3)
plt.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
plt.axvline(x=0, color='gray', linestyle='--', alpha=0.3)
plt.savefig('kavya_clusters_with_features.png', dpi=300, bbox_inches='tight')

# Additional Analysis: Hierarchical Clustering
from scipy.cluster.hierarchy import dendrogram, linkage
from matplotlib import pyplot as plt

# Perform hierarchical clustering
linked = linkage(X_scaled, method='ward')

# Plot the dendrogram
plt.figure(figsize=(15, 10))
dendrogram(linked, 
           orientation='top', 
           labels=kavya_names,
           distance_sort=True,
           show_leaf_counts=True)
plt.title('Hierarchical Clustering of Sanskrit Kavyas based on Sound Patterns')
plt.xlabel('Kavyas')
plt.ylabel('Distance')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('kavya_dendrogram.png', dpi=300, bbox_inches='tight')

print("\nAnalysis complete. Check the output images for visualization.")

# %%
