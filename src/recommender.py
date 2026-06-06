import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
import os

class Recommender:
    def __init__(self, data_path):
        self.df = pd.read_csv(data_path)
        self.user_item_matrix = None
        self.item_similarity = None

    def build_collaborative_filtering(self):
        print("Building Collaborative Filtering Model...")
        # Create user-item matrix
        self.user_item_matrix = self.df.pivot_table(
            index='CustomerID', 
            columns='StockCode', 
            values='Quantity', 
            aggfunc='sum'
        ).fillna(0)
        
        # Convert to sparse matrix for efficiency
        sparse_matrix = sparse.csr_matrix(self.user_item_matrix.values)
        
        # Calculate Item-Item Similarity
        self.item_similarity = cosine_similarity(sparse_matrix.T)
        self.item_similarity_df = pd.DataFrame(
            self.item_similarity, 
            index=self.user_item_matrix.columns, 
            columns=self.user_item_matrix.columns
        )
        print("Model built.")

    def get_recommendations(self, stock_code, n=5):
        if stock_code not in self.item_similarity_df.columns:
            return []
        
        similar_items = self.item_similarity_df[stock_code].sort_values(ascending=False)
        # Exclude the item itself
        recommendations = similar_items.iloc[1:n+1].index.tolist()
        return recommendations

if __name__ == "__main__":
    rec = Recommender("data/cleaned_online_retail.csv")
    rec.build_collaborative_filtering()
    # Test recommendation for a popular item
    sample_item = rec.df['StockCode'].iloc[0]
    recs = rec.get_recommendations(sample_item)
    print(f"Recommendations for {sample_item}: {recs}")
