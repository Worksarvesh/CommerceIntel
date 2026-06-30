"""Collaborative and content-based recommendation engines."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import PROCESSED_DATA_DIR, RECOMMENDATIONS_FILE, TOP_N_RECOMMENDATIONS


class RecommendationEngine:
    """Hybrid recommendation system combining collaborative and content-based filtering."""

    def __init__(self, transactions: pd.DataFrame):
        self.transactions = transactions
        self.user_item_matrix: pd.DataFrame | None = None
        self.item_similarity: np.ndarray | None = None
        self.product_catalog: pd.DataFrame | None = None
        self.product_ids: list[str] = []
        self._build_models()

    def _build_models(self) -> None:
        purchases = self.transactions.copy()
        self.user_item_matrix = (
            purchases.groupby(["customer_id", "stock_code"])["quantity"]
            .sum()
            .unstack(fill_value=0)
        )

        self.product_catalog = (
            purchases.groupby(["stock_code", "description", "category"], as_index=False)
            .agg(total_revenue=("revenue", "sum"))
            .sort_values("total_revenue", ascending=False)
        )
        self.product_ids = self.product_catalog["stock_code"].tolist()

        descriptions = self.product_catalog["description"].fillna("") + " " + self.product_catalog["category"].fillna("")
        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(descriptions)
        self.item_similarity = cosine_similarity(tfidf_matrix)

    def collaborative_recommendations(
        self, customer_id: int, top_n: int = TOP_N_RECOMMENDATIONS
    ) -> list[dict]:
        """Recommend products using user-based collaborative filtering."""
        if self.user_item_matrix is None:
            return []

        if customer_id not in self.user_item_matrix.index:
            return self.popular_recommendations(top_n)

        user_vector = self.user_item_matrix.loc[customer_id]
        purchased = set(user_vector[user_vector > 0].index)

        user_similarity = self.user_item_matrix.dot(user_vector)
        user_similarity = user_similarity / (
            np.linalg.norm(self.user_item_matrix, axis=1) * np.linalg.norm(user_vector) + 1e-9
        )

        scores: dict[str, float] = defaultdict(float)
        similar_users = user_similarity.sort_values(ascending=False).head(20).index
        for similar_user in similar_users:
            if similar_user == customer_id:
                continue
            weight = user_similarity[similar_user]
            neighbor_items = self.user_item_matrix.loc[similar_user]
            for product_id, qty in neighbor_items[neighbor_items > 0].items():
                if product_id not in purchased:
                    scores[product_id] += weight * qty

        return self._format_recommendations(scores, "collaborative", top_n)

    def content_based_recommendations(
        self, product_id: str, top_n: int = TOP_N_RECOMMENDATIONS
    ) -> list[dict]:
        """Recommend similar products using content-based filtering."""
        if self.product_catalog is None or self.item_similarity is None:
            return []

        if product_id not in self.product_ids:
            return self.popular_recommendations(top_n)

        idx = self.product_ids.index(product_id)
        sim_scores = list(enumerate(self.item_similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1 : top_n + 1]

        scores = {self.product_ids[i]: score for i, score in sim_scores}
        return self._format_recommendations(scores, "content_based", top_n)

    def hybrid_recommendations(
        self, customer_id: int, top_n: int = TOP_N_RECOMMENDATIONS
    ) -> list[dict]:
        """Blend collaborative and content-based scores."""
        collab = self.collaborative_recommendations(customer_id, top_n * 2)
        if not collab:
            return self.popular_recommendations(top_n)

        last_purchases = (
            self.transactions[self.transactions["customer_id"] == customer_id]
            .sort_values("invoice_date", ascending=False)["stock_code"]
            .unique()[:3]
        )

        content_scores: dict[str, float] = defaultdict(float)
        for product_id in last_purchases:
            for rec in self.content_based_recommendations(product_id, top_n):
                content_scores[rec["stock_code"]] += rec["score"]

        hybrid_scores: dict[str, float] = defaultdict(float)
        for rec in collab:
            hybrid_scores[rec["stock_code"]] += 0.6 * rec["score"]
        for product_id, score in content_scores.items():
            hybrid_scores[product_id] += 0.4 * score

        return self._format_recommendations(hybrid_scores, "hybrid", top_n)

    def popular_recommendations(self, top_n: int = TOP_N_RECOMMENDATIONS) -> list[dict]:
        """Fallback popularity-based recommendations."""
        if self.product_catalog is None:
            return []
        top = self.product_catalog.head(top_n)
        return [
            {
                "stock_code": row.stock_code,
                "description": row.description,
                "category": row.category,
                "score": float(row.total_revenue),
                "method": "popular",
            }
            for row in top.itertuples()
        ]

    def _format_recommendations(
        self, scores: dict[str, float], method: str, top_n: int
    ) -> list[dict]:
        if self.product_catalog is None or not scores:
            return []

        catalog = self.product_catalog.set_index("stock_code")
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        results = []
        for stock_code, score in ranked:
            if stock_code not in catalog.index:
                continue
            row = catalog.loc[stock_code]
            results.append(
                {
                    "stock_code": stock_code,
                    "description": row["description"],
                    "category": row["category"],
                    "score": float(score),
                    "method": method,
                }
            )
        return results


def generate_sample_recommendations(
    transactions: pd.DataFrame, sample_size: int = 50
) -> pd.DataFrame:
    """Generate recommendation examples for sample customers."""
    engine = RecommendationEngine(transactions)
    customer_ids = transactions["customer_id"].drop_duplicates().head(sample_size).tolist()

    rows = []
    for customer_id in customer_ids:
        for rec in engine.hybrid_recommendations(customer_id, top_n=5):
            rows.append({"customer_id": customer_id, **rec})

    df = pd.DataFrame(rows)
    df.to_csv(RECOMMENDATIONS_FILE, index=False)
    return df
