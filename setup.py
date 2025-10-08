#!/usr/bin/env python3
"""
Setup script for Pharmacy Analytics Project.
Installs dependencies, creates sample data, and runs basic checks.
"""

import subprocess
import sys
import pandas as pd
import numpy as np
from datetime import datetime

def install_dependencies():
    """Install required packages from requirements.txt."""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Please check requirements.txt.")
        sys.exit(1)

def create_sample_data():
    """Create and save sample CSV for reproducibility."""
    np.random.seed(42)
    sample_data = {
        'action_date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
        'product_name': np.random.choice(['Aspirin', 'Ibuprofen', 'Tylenol', 'Unknown Product'], 100),
        'quantity_involved': np.random.randint(1, 100, 100),
        'total_amount': np.random.uniform(10, 500, 100),
        'reason': np.random.choice(['Quality Issue', 'Labeling Error', 'N/A'], 100),
        'severity': np.random.choice(['High', 'Low'], 100)
    }
    df = pd.DataFrame(sample_data)
    df.to_csv('sample_pharmacy_data.csv', index=False)
    print("Sample data saved as sample_pharmacy_data.csv.")

def run_basic_check():
    """Run a basic import check."""
    try:
        import pandas as pd
        import plotly.express as px
        from api_utils import fetch_pharmacy_data
        print("Basic imports successful.")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Setting up Pharmacy Analytics Project...")
    install_dependencies()
    create_sample_data()
    run_basic_check()
    print("Setup complete! Run 'python eda_script.py' or 'streamlit run app.py' to start.")