import unittest
import pandas as pd
from api_utils import fetch_pharmacy_data

class TestDataProcessing(unittest.TestCase):

    def test_fetch_pharmacy_data_non_empty(self):
        df = fetch_pharmacy_data(limit=5)
        self.assertFalse(df.empty, "DataFrame should not be empty")

    def test_fetch_pharmacy_data_columns(self):
        df = fetch_pharmacy_data(limit=5)
        expected_columns = ['action_date', 'product_name', 'quantity_involved', 'total_amount', 'reason']
        for col in expected_columns:
            self.assertIn(col, df.columns, f"Column {col} should be present")

    def test_quantity_involved_numeric(self):
        df = fetch_pharmacy_data(limit=5)
        self.assertTrue(pd.api.types.is_numeric_dtype(df['quantity_involved']), "quantity_involved should be numeric")

    def test_total_amount_numeric(self):
        df = fetch_pharmacy_data(limit=5)
        self.assertTrue(pd.api.types.is_numeric_dtype(df['total_amount']), "total_amount should be numeric")

    def test_action_date_datetime(self):
        df = fetch_pharmacy_data(limit=5)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['action_date']), "action_date should be datetime")

if __name__ == '__main__':
    unittest.main()