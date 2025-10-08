import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from scipy.stats import chi2_contingency

def fetch_pharmacy_data(limit=500, years_back=5, retries=3, backoff_factor=2):
    """
    Dynamically fetch drug enforcement reports from openFDA API with robust error handling.
    Mimics transactional pharmacy data (e.g., recalls as 'inventory events').
    Includes retry logic with exponential backoff for reliability.
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

    for attempt in range(retries):
        try:
            print(f"Attempt {attempt + 1}/{retries}: Fetching data from openFDA API...")
            response = requests.get(base_url, params=params, timeout=30)  # Added timeout
            response.raise_for_status()
            data = response.json()

            print(f"API response keys: {list(data.keys())}")
            if 'results' not in data or not data['results']:
                raise ValueError("No results found—check query params or API availability.")

            print(f"Number of results: {len(data['results'])}")
            print(f"Sample result keys: {list(data['results'][0].keys()) if data['results'] else 'No results'}")

            df = pd.json_normalize(data['results'])  # Flatten JSON to DataFrame
            print(f"DataFrame columns after normalization: {list(df.columns)}")

            # Enhanced date parsing with multiple fallbacks
            if 'report_date' in df.columns:
                df['action_date'] = pd.to_datetime(df['report_date'], errors='coerce')
                print("Date parsing from 'report_date' successful.")
            elif 'recall_initiation_date' in df.columns:
                df['action_date'] = pd.to_datetime(df['recall_initiation_date'], errors='coerce')
                print("Date parsing from 'recall_initiation_date' successful.")
            else:
                print("Warning: No date column found. Available columns: {list(df.columns)}")
                df['action_date'] = pd.NaT

            # Improved product name derivation
            if 'product_type' in df.columns:
                df['product_name'] = df['product_type'].apply(lambda x: x[0] if isinstance(x, list) and x else 'Unknown Product')
            elif 'product_description' in df.columns:
                df['product_name'] = df['product_description'].str.split().str[0].fillna('Unknown Product')
            else:
                df['product_name'] = 'Unknown Product'

            # Robust quantity handling
            df['quantity_involved'] = pd.to_numeric(df.get('product_quantity', np.nan), errors='coerce').fillna(0).astype(float)
            df['total_amount'] = df['quantity_involved'] * np.random.uniform(5, 50, len(df))  # Randomized mock pricing for realism
            df['reason'] = df.get('reason_for_recall', 'N/A').fillna('N/A')

            # Derive severity with enhanced logic
            if 'classification' in df.columns:
                df['severity'] = df['classification'].fillna('').str.extract(r'Class (\w+)')[0].map({'I': 'High', 'II': 'Med', 'III': 'Low'}).fillna('Low')
                # Boost severity based on keywords in reason
                high_keywords = ['serious', 'cgmp', 'contamination', 'death', 'injury']
                df.loc[df['reason'].str.contains('|'.join(high_keywords), case=False, na=False), 'severity'] = 'High'
            else:
                df['severity'] = 'Low'  # Default

            print(f"Successfully fetched and processed {len(df)} records from openFDA.")
            return df

        except requests.exceptions.Timeout:
            print(f"Timeout error on attempt {attempt + 1}. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
        except ValueError as e:
            print(f"Data processing error: {e}")
            break  # No retry for data issues
        except Exception as e:
            print(f"Unexpected error on attempt {attempt + 1}: {e}")

        if attempt < retries - 1:
            sleep_time = backoff_factor ** attempt
            print(f"Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)

    print("All attempts failed. Returning empty DataFrame for fallback.")
    return pd.DataFrame()

def perform_hypothesis_test(df):
    """
    Perform chi-square test for independence between 'reason' and 'severity'.
    Returns test statistic, p-value, and interpretation.
    """
    if df.empty or 'reason' not in df.columns or 'severity' not in df.columns:
        return None, None, "Insufficient data for hypothesis test."

    contingency_table = pd.crosstab(df['reason'], df['severity'])
    if contingency_table.size == 0:
        return None, None, "No valid contingency table."

    chi2, p, dof, expected = chi2_contingency(contingency_table)
    interpretation = "Significant association (p < 0.05)" if p < 0.05 else "No significant association (p >= 0.05)"
    return chi2, p, interpretation