# Sound Pattern Clustering Analysis of Sanskrit Kavyas

This document presents the results of clustering analysis performed on the normalized sound frequencies of various Sanskrit kavyas. The analysis reveals how different literary works cluster based on their phonetic patterns.

## Methodology

1. **Data Source**: The analysis uses `msound_normalized.csv`, which contains normalized frequencies of Sanskrit sounds for various kavyas.

2. **Preprocessing**:
   - Each kavya is represented as a vector of sound frequencies
   - Data was standardized to give equal weight to each sound

3. **Analysis Techniques**:
   - K-means clustering to group kavyas with similar sound patterns
   - Principal Component Analysis (PCA) for dimensionality reduction and visualization
   - Silhouette analysis for determining the optimal number of clusters
   - Hierarchical clustering to understand relationships between kavyas

## Key Findings

### Optimal Number of Clusters

Based on silhouette score analysis, the optimal number of clusters was determined to be 3. This suggests that Sanskrit kavyas in our dataset naturally fall into three distinct phonetic groups based on their sound usage patterns.

### Cluster Characteristics

#### Cluster 1 - Vowel-Dominant Kavyas

Most distinctive sounds:

- a (short a) - Very high frequency (16.26%)
- p - 7.70%
- s - 6.65%
- v - 6.60%
- t - 6.00%

This cluster features kavyas with high usage of the basic vowel 'a' and moderate usage of consonants like 'p' and 's'. These works likely have a more flowing, open sound quality with many open syllables.

#### Cluster 2 - Consonant-Dominant Kavyas

Most distinctive sounds:

- p - 12.30%
- k - 8.01%
- s - 7.83%
- v - 7.12%
- d - 6.34%

Works in this cluster feature higher usage of hard consonants like 'p' and 'k', giving them a more staccato, rhythmic quality.

#### Cluster 3 - Balanced Kavyas

Most distinctive sounds:

- p - 10.06%
- s - 9.79%
- v - 8.83%
- t - 8.19%
- k - 7.07%

These kavyas show a more balanced distribution between various sounds, with slightly higher frequencies of labial and dental consonants.

### Principal Component Analysis

The first two principal components explain approximately 40.24% of the total variance in the dataset:

- PC1: 24.00% of variance
- PC2: 16.25% of variance

This suggests that there are multiple dimensions of variation in sound patterns that cannot be captured in just two dimensions, but the primary patterns are visible in our visualization.

### Hierarchical Relationships

The dendrogram from hierarchical clustering reveals sub-groups within the main clusters, showing more nuanced relationships between kavyas. Some works that are distant in the K-means clustering appear closely related in the hierarchical analysis, suggesting subtle phonetic similarities.

## Practical Implications

1. **Literary Style Classification**: The clusters may reflect different stylistic traditions or periods in Sanskrit literature.

2. **Authorship Analysis**: Works by the same author or school may show similar sound patterns, suggesting potential use for authorship attribution.

3. **Phonetic Evolution**: The clustering may reveal how sound patterns evolved over time or differed across regions.

4. **Reading Experience**: The distinct sound patterns likely create different auditory experiences for listeners, affecting the emotional impact and reception of the works.

## Conclusion

This analysis demonstrates that Sanskrit kavyas can be meaningfully grouped based on their sound patterns. The three distinct clusters identified suggest fundamental phonetic styles in Sanskrit literature, potentially reflecting different poetic traditions, time periods, or author preferences.

The visualization of these clusters through PCA allows us to see relationships between different works based on their sound profiles, providing a new quantitative lens for analyzing Sanskrit literature.

## Future Directions

1. **Expand the Dataset**: Include more kavyas to strengthen the analysis and potentially reveal additional clusters.

2. **Temporal Analysis**: Add chronological data to see if sound patterns evolved over time.

3. **Meter Analysis**: Correlate sound patterns with metrical structures to understand their relationship.

4. **Content Analysis**: Examine whether sound patterns correlate with thematic content (e.g., do romantic works use different sound patterns than philosophical ones?).

5. **Cross-Language Comparison**: Apply similar analysis to kavyas in other Indian languages to explore broader phonetic patterns in Indian literature.

## Visualization Gallery

Below are the key visualizations produced during the analysis. Each provides a unique perspective on the sound patterns and clusters of Sanskrit kavyas.

### Determining Optimal Clusters

The silhouette score analysis helped determine the optimal number of clusters. This shows how well-separated the clusters are, with higher scores indicating better-defined clusters. Three clusters were found to be optimal

![Silhouette Score Analysis](silhouette_scores.png)

### Kavya Clusters in PCA Space

The 2D visualization of kavyas clustered based on their sound patterns:

![Kavya Clusters PCA](kavya_clusters_pca.png)

### Kavya Clusters with Feature Vectors

Visualization showing the influence of different sounds on the clustering:

![Kavya Clusters with Features](kavya_clusters_with_features.png)

### Hierarchical Clustering of Kavyas

Dendrogram showing relationships between different kavyas:

![Kavya Dendrogram](kavya_dendrogram.png)

### Sound Patterns in Clusters

Heatmap of cluster centers showing characteristic sound patterns:

![Cluster Centers Heatmap](cluster_centers_heatmap.png)

### Most Discriminative Sounds

Bar chart showing sounds that best differentiate between clusters:

![Discriminative Sounds](discriminative_sounds.png)

### Discriminative Sounds by Cluster

Heatmap showing how discriminative sounds vary across clusters:

![Discriminative Sounds by Cluster](discriminative_sounds_by_cluster.png)

### Kavyas Grouped by Cluster

Visual representation of kavyas in each cluster:

![Kavyas by Cluster](kavyas_by_cluster.png)

## Interactive Exploration

For a more interactive exploration of these clusters, you can run the provided scripts and modify parameters to investigate specific aspects:

1. **Adjusting Cluster Count**: Try different numbers of clusters in `03_sound_clustering.py` by modifying the `optimal_k` variable
2. **Exploring Feature Importance**: Adjust the number of top features displayed in `04_feature_importance.py`
3. **Custom Visualizations**: The scripts can be modified to generate additional visualizations focused on specific sounds or kavyas of interest
