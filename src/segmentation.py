import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import os
# import jobutils (not needed)
import pickle

def perform_clustering(rfm_path, output_dir="docs/plots", model_path="models/kmeans_model.pkl"):
    rfm = pd.read_csv(rfm_path)
    # Use log transformation to handle skewness
    rfm_log = rfm[['Recency', 'Frequency', 'Monetary']].apply(np.log1p, axis=1)
    
    # Scale data
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)
    
    # Elbow Method
    sse = []
    for k in range(1, min(11, len(rfm_scaled) + 1)):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(rfm_scaled)
        sse.append(kmeans.inertia_)
    
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(sse) + 1), sse, marker="o")
    plt.title('Elbow Method for Optimal K')
    plt.xlabel('Number of Clusters')
    plt.ylabel('SSE')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f"{output_dir}/elbow_method.png")
    plt.close()
    
    # Final Model (K=4 for demonstration)
    k = 4
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)
    
    # Save Model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump({'model': kmeans, 'scaler': scaler}, f)
    
    # Visualization: Clusters
    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=rfm, x='Recency', y='Monetary', hue='Cluster', palette='viridis')
    plt.title('Customer Clusters: Recency vs Monetary')
    plt.savefig(f"{output_dir}/clusters_scatter.png")
    plt.close()
    
    rfm.to_csv("data/segmented_customers.csv", index=False)
    print(f"Segmentation complete. Model saved to {model_path}")
    return rfm

if __name__ == "__main__":
    perform_clustering("data/rfm_data.csv")
