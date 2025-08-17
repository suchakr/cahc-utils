# Sanskrit Varna Sanyoga (Sound Pattern) Analysis

Short summary

- A pipeline to extract phonetic/sound patterns from Sanskrit texts, normalize them, and apply clustering to explore stylistic groupings.

Quick start

1. Create and activate a Python virtual environment.
2. Install dependencies: `pip install -r requirements.txt` (run inside `linguistics/varna-sanyoga`).
3. Run `01_llm_pre_process.ipynb` to preprocess source texts and generate `llm_pre_processed/`.
4. Run `02_varna_sanyoga.ipynb` to extract sounds and produce `msound_raw.csv` and `msound_normalized.csv`.
5. Run `03_sound_clustering.py` to perform clustering and generate visualizations.

This project analyzes sound patterns in Sanskrit kavyas (literary works) by extracting, processing, and clustering phonetic data to identify natural groupings of texts based on their sound distributions.

## Project Overview

The project processes Sanskrit texts to extract sound patterns, normalizes the data, and applies machine learning techniques to discover inherent groupings of texts based on their phonetic characteristics.

## File Structure & Execution Order

The analysis is organized into four sequential steps, with corresponding numbered files:

1. **01_llm_pre_process.ipynb**
   - Preprocesses Sanskrit text files
   - Prepares data for sound pattern extraction
   - Input: Raw Sanskrit texts
   - Output: Processed files in `llm_pre_processed/`

2. **02_varna_sanyoga.ipynb**
   - Extracts sound patterns from preprocessed texts
   - Computes frequency distributions of sounds
   - Normalizes the sound frequencies
   - Output: `msound_raw.csv`, `msound_normalized.csv`

3. **03_sound_clustering.py**
   - Performs K-means clustering on normalized sound data
   - Applies Principal Component Analysis (PCA) for dimensionality reduction
   - Generates visualizations of clusters and sound relationships
   - Output: Cluster visualization PNGs, silhouette analysis

4. **04_feature_importance.py**
   - Analyzes the most discriminative sounds between clusters
   - Visualizes feature importance and cluster characteristics
   - Output: Feature importance visualizations

## Data Files

- **msound_raw.csv**: Raw counts of sound occurrences in each kavya
- **msound_normalized.csv**: Normalized sound frequency data (input for clustering)

## Dependencies

Required Python packages are listed in `requirements.txt`. Install with:

```bash
pip install -r requirements.txt
```

## Generated Visualizations

The scripts produce several visualizations that are stored in the project directory:

- Silhouette score analysis (`silhouette_scores.png`)
- PCA cluster visualization (`kavya_clusters_pca.png`)
- Feature vector visualization (`kavya_clusters_with_features.png`)
- Hierarchical clustering dendrogram (`kavya_dendrogram.png`)
- Cluster centers heatmap (`cluster_centers_heatmap.png`)
- Discriminative sounds analysis (`discriminative_sounds.png`, `discriminative_sounds_by_cluster.png`)
- Kavya groupings by cluster (`kavyas_by_cluster.png`)

## Detailed Analysis

For comprehensive analysis of the clustering results and their interpretations, please refer to:

- **sound_clustering_analysis.md**: In-depth analysis of sound pattern clusters, their characteristics, and implications

## Key Findings

1. Sanskrit kavyas naturally group into three main clusters based on sound patterns:
   - **Cluster 1** - Vowel-dominant works (high frequency of अ)
   - **Cluster 2** - Consonant-dominant works (high frequency of hard consonants)
   - **Cluster 3** - Works with balanced sound distribution

2. The most discriminative sounds between clusters are:
   - अ (a) - The basic vowel sound
   - प् (p) - Unvoiced labial stop
   - च् (c) - Palatal consonant
   - स् (s) - Dental sibilant
   - क् (k) - Velar stop

3. These clusters may correspond to different literary traditions, time periods, or stylistic preferences in Sanskrit literature.

## Usage

To run the main clustering analysis:

```bash
python sound_clustering.py
```

To generate feature importance visualizations:

```bash
python feature_importance.py
```

## Requirements

Required Python packages are listed in `requirements.txt`:

- pandas
- numpy
- matplotlib
- scikit-learn
- seaborn
- scipy

Install with:

```bash
pip install -r requirements.txt
```
