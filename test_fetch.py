import sys
sys.path.insert(0, '.')
from api_utils import fetch_pharmacy_data
df = fetch_pharmacy_data(limit=10)
print(f'Empty: {df.empty}')
if not df.empty:
    print(f'Shape: {df.shape}')
    print(f'Columns: {list(df.columns)}')