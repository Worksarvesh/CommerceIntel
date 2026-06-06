import unittest
import pandas as pd
from src.rfm_analysis import perform_rfm

class TestRFMAnalysis(unittest.TestCase):
    def setUp(self):
        # Create a dummy DataFrame for testing with more diverse data
        data = {
            'InvoiceNo': ['536365', '536365', '536366', '536367', '536367', '536368', '536369', '536370', '536371', '536372'],
            'StockCode': ['85123A', '71053', '84406B', '84777', '22727', '22726', '22728', '22729', '22730', '22731'],
            'Description': ['WHITE HANGING HEART T-LIGHT HOLDER', 'WHITE METAL LANTERN', 'CREAM CUPID HEARTS COAT HANGER', 'GLASS STAR FROSTED T-LIGHT HOLDER', 'ALARM CLOCK BAKELIKE RED', 'ALARM CLOCK BAKELIKE GREEN', 'ALARM CLOCK BAKELIKE PINK', 'ALARM CLOCK BAKELIKE BLUE', 'ALARM CLOCK BAKELIKE YELLOW', 'ALARM CLOCK BAKELIKE ORANGE'],
            'Quantity': [6, 6, 8, 6, 4, 4, 10, 12, 1, 2],
            'InvoiceDate': ['2010-12-01 08:26:00', '2010-12-01 08:26:00', '2010-12-01 08:28:00', '2010-12-01 08:34:00', '2010-12-01 08:34:00', '2010-12-01 08:34:00', '2010-12-02 09:00:00', '2010-12-02 09:10:00', '2010-12-03 10:00:00', '2010-12-03 10:15:00'],
            'UnitPrice': [2.55, 3.39, 2.75, 4.25, 4.95, 4.95, 1.25, 1.50, 0.85, 0.99],
            'CustomerID': [17850, 17850, 17850, 17850, 17850, 17850, 17851, 17851, 17852, 17852],
            'Country': ['United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom'],
            'TotalAmount': [15.30, 20.34, 22.00, 25.50, 19.80, 19.80, 12.50, 18.00, 0.85, 1.98]
        }
        self.test_df = pd.DataFrame(data)
        self.test_df['InvoiceDate'] = pd.to_datetime(self.test_df['InvoiceDate'])
        self.test_csv_path = 'data/test_rfm.csv'
        self.test_df.to_csv(self.test_csv_path, index=False)

    def test_perform_rfm(self):
        rfm_result = perform_rfm(self.test_csv_path, output_path='data/test_rfm_output.csv')
        self.assertIsInstance(rfm_result, pd.DataFrame)
        self.assertIn('Recency', rfm_result.columns)
        self.assertIn('Frequency', rfm_result.columns)
        self.assertIn('Monetary', rfm_result.columns)
        self.assertIn('RFM_Score', rfm_result.columns)
        self.assertIn('Segment', rfm_result.columns)
        self.assertEqual(len(rfm_result), 3) # Now 3 customers in test data

    def tearDown(self):
        import os
        if os.path.exists(self.test_csv_path):
            os.remove(self.test_csv_path)
        if os.path.exists('data/test_rfm_output.csv'):
            os.remove('data/test_rfm_output.csv')

if __name__ == '__main__':
    unittest.main()
