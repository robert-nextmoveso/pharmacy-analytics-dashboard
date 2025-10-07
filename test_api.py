import requests
from datetime import datetime, timedelta

url = 'https://api.fda.gov/drug/enforcement.json'

# Test without search
params = {'limit': 1}
print('Testing without search:')
try:
    response = requests.get(url, params=params)
    print('Status code:', response.status_code)
    if response.status_code == 200:
        data = response.json()
        print('Number of results:', len(data['results']))
    else:
        print('Response text:', response.text)
except Exception as e:
    print('Error:', e)

# Test with search and limit=300 using +TO+
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')
params = {
    'search': f'report_date:[{start_date}+TO+{end_date}]',
    'limit': 300
}
print(f'\nTesting with +TO+ and limit=300: {params["search"]}')
try:
    response = requests.get(url, params=params)
    print('Status code:', response.status_code)
    if response.status_code == 200:
        data = response.json()
        print('Number of results:', len(data['results']))
    else:
        print('Response text:', response.text)
except Exception as e:
    print('Error:', e)