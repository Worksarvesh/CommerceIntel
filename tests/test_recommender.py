import unittest
import pandas as pd
import os
from src.recommender import Recommender

class TestRecommender(unittest.TestCase):
    def setUp(self):
        # Create a dummy DataFrame for testing
        data = {
            'InvoiceNo': ['536365', '536365', '536366', '536367', '536367', '536368', '536368'],
            'StockCode': ['85123A', '71053', '84406B', '84777', '22727', '22726', '85123A'],
            'Description': ['WHITE HANGING HEART T-LIGHT HOLDER', 'WHITE METAL LANTERN', 'CREAM CUPID HEARTS COAT HANGER', 'GLASS STAR FROSTED T-LIGHT HOLDER', 'ALARM CLOCK BAKELIKE RED', 'ALARM CLOCK BAKELIKE GREEN', 'WHITE HANGING HEART T-LIGHT HOLDER'],
            'Quantity': [6, 6, 8, 6, 4, 4, 1],
            'InvoiceDate': ['2010-12-01 08:26:00', '2010-12-01 08:26:00', '2010-12-01 08:28:00', '2010-12-01 08:34:00', '2010-12-01 08:34:00', '2010-12-01 08:34:00', '2010-12-01 08:34:00'],
            'UnitPrice': [2.55, 3.39, 2.75, 4.25, 4.95, 4.95, 2.55],
            'CustomerID': [17850, 17850, 17850, 17850, 17850, 17850, 17851],
            'Country': ['United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom'],
            'TotalAmount': [15.30, 20.34, 22.00, 25.50, 19.80, 19.80, 2.55]
        }
        self.test_df = pd.DataFrame(data)
        self.test_csv_path = 'data/test_recommender.csv'
        self.test_df.to_csv(self.test_csv_path, index=False)

    def test_build_collaborative_filtering(self):
        recommender = Recommender(self.test_csv_path)
        recommender.build_collaborative_filtering()
        self.assertIsNotNone(recommender.user_item_matrix)
        self.assertIsNotNone(recommender.item_similarity)
        self.assertIsInstance(recommender.item_similarity_df, pd.DataFrame)

    def test_get_recommendations(self):
        recommender = Recommender(self.test_csv_path)
        recommender.build_collaborative_filtering()
        # Test with an item that has similar items
        recommendations = recommender.get_recommendations('85123A', n=2)
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), 2)
        # Test with an item not in the dataset
        recommendations_none = recommender.get_recommendations('NONEXISTENT_ITEM')
        self.assertEqual(len(recommendations_none), 0)

    def tearDown(self):
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)

if __name__ == '__main__':
    unittest.main()
