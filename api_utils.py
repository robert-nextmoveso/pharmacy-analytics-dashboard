import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_pharmacy_data(limit=500, years_back=5):
    """
    Dynamically fetch drug enforcement reports from openFDA API.
    Mimics transactional pharmacy data (e.g., recalls as 'inventory events').
    """
    base_url = "https://api.fda.gov/drug/enforcement.json"
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=years_back*365)).strftime('%Y-%m-%d')
    
    # Dynamic query: Filter by date and limit
    params = {
        'search': f'report_date:[{start_date} TO {end_date}]',  # Date range for recency
        'limit': limit,
        'skip': 0  # Pagination start
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Error handling
        data = response.json()

        print(f"API response keys: {list(data.keys())}")
        if 'results' not in data:
            raise ValueError("No results found—check query params.")

        print(f"Number of results: {len(data['results'])}")
        print(f"Sample result keys: {list(data['results'][0].keys()) if data['results'] else 'No results'}")

        df = pd.json_normalize(data['results'])  # Flatten JSON to DataFrame
        print(f"DataFrame columns after normalization: {list(df.columns)}")

        # Corrected date parsing using proper field
        if 'report_date' in df.columns:
            df['action_date'] = pd.to_datetime(df['report_date'], errors='coerce')
            print("Date parsing from 'report_date' successful.")
        else:
            print("Warning: 'report_date' column not found. Available columns: {list(df.columns)}")
            df['action_date'] = pd.NaT  # Not a Time

        if 'product_type' in df.columns:
            df['product_name'] = df['product_type'].apply(lambda x: x[0] if isinstance(x, list) and x else 'Unknown')
        else:
            df['product_name'] = 'Unknown'

        df['quantity_involved'] = pd.to_numeric(df.get('product_quantity', 0), errors='coerce').fillna(0).astype(float)
        df['total_amount'] = df['quantity_involved'] * 10  # Mock pricing for analysis
        df['reason'] = df.get('reason_for_recall', 'N/A')  # For funnel stages

        print(f"Fetched {len(df)} records dynamically from openFDA.")
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")
        return pd.DataFrame()  # Graceful fallback