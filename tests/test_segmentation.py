import unittest
import pandas as pd
import os
from src.segmentation import perform_clustering

class TestSegmentation(unittest.TestCase):
    def setUp(self):
        # Create a dummy RFM DataFrame for testing
        data = {
            'CustomerID': [1, 2, 3, 4, 5],
            'Recency': [10, 50, 100, 10, 200],
            'Frequency': [5, 10, 2, 8, 1],
            'Monetary': [100, 200, 50, 150, 20]
        }
        self.test_rfm_df = pd.DataFrame(data)
        self.test_rfm_path = 'data/test_rfm_for_segmentation.csv'
        self.test_rfm_df.to_csv(self.test_rfm_path, index=False)
        self.model_output_path = 'models/test_kmeans_model.pkl'
        self.plot_output_dir = 'docs/plots/test_segmentation'

    def test_perform_clustering(self):
        segmented_df = perform_clustering(self.test_rfm_path, output_dir=self.plot_output_dir, model_path=self.model_output_path)
        self.assertIsInstance(segmented_df, pd.DataFrame)
        self.assertIn('Cluster', segmented_df.columns)
        self.assertEqual(len(segmented_df), 5)
        self.assertTrue(os.path.exists(self.model_output_path))
        self.assertTrue(os.path.exists(os.path.join(self.plot_output_dir, 'elbow_method.png')))
        self.assertTrue(os.path.exists(os.path.join(self.plot_output_dir, 'clusters_scatter.png')))

    def tearDown(self):
        import shutil
        if os.path.exists(self.test_rfm_path):
            os.remove(self.test_rfm_path)
        if os.path.exists('data/segmented_customers.csv'):
            os.remove('data/segmented_customers.csv')
        if os.path.exists(self.model_output_path):
            os.remove(self.model_output_path)
        if os.path.exists(self.plot_output_dir):
            shutil.rmtree(self.plot_output_dir)

if __name__ == '__main__':
    unittest.main()
