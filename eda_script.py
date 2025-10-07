import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from api_utils import fetch_pharmacy_data  # Import helper

# Dynamic load
df = fetch_pharmacy_data(limit=300)  # Pull fresh data
if df.empty:
    print("Fallback to sample data if API fails.")
    # Create sample data as backup
    sample_data = {
        'action_date': pd.date_range('2023-01-01', periods=10, freq='D'),
        'product_name': ['Drug A', 'Drug B', 'Drug C'] * 3 + ['Drug A'],
        'quantity_involved': [100, 200, 150, 300, 250, 180, 220, 190, 160, 210],
        'total_amount': [1000, 2000, 1500, 3000, 2500, 1800, 2200, 1900, 1600, 2100],
        'reason': ['Recall', 'Defect', 'Expiration'] * 3 + ['Recall']
    }
    df = pd.DataFrame(sample_data)

# Rest of EDA (adapt columns to API fields, e.g., 'action_date' for trends)
df['action_date'] = pd.to_datetime(df['action_date'], errors='coerce')  # Ensure datetime
daily_trends = df.groupby(df['action_date'].dt.date)['total_amount'].sum().reset_index()
fig1 = px.line(daily_trends, x='action_date', y='total_amount', title='Dynamic Recall Trends (API-Fetched)')
fig1.show()

# Top products (recalls by product)
top_products = df.groupby('product_name')['quantity_involved'].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=top_products.values, y=top_products.index, palette='viridis')
plt.title('Top Products by Quantity Involved (Dynamic Data)')
plt.savefig('top_products.png', dpi=300, bbox_inches='tight')
plt.close()

# Correlation heatmap (adapt to numerical cols like quantity, mock total_amount)
numerical_df = df.select_dtypes(include=[np.number])
corr = numerical_df.corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.title('Dynamic Data Correlations')
plt.savefig('correlations.png', dpi=300, bbox_inches='tight')
plt.close()

# Funnel chart for severity drop-offs (example: count by reason)
reason_counts = df['reason'].value_counts().reset_index()
reason_counts.columns = ['Reason', 'Count']
funnel_fig = px.funnel(reason_counts, x='Count', y='Reason', title='Recall Reasons Funnel')
funnel_fig.show()

print(f"Average quantity involved: {df['quantity_involved'].mean():.2f}")
print(f"Most common reason: {df['reason'].mode()[0] if not df['reason'].mode().empty else 'N/A'}")
# Export Plotly to HTML
fig1.write_html('trends.html')  # From trends line chart
funnel_fig.write_html('funnel.html')  # Funnel chart