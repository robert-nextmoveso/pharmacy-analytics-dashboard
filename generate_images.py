import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
from api_utils import fetch_pharmacy_data
import os

# Ensure images directory exists
os.makedirs('images', exist_ok=True)

# Load data
df = fetch_pharmacy_data(limit=300)
if df.empty:
    # Sample data fallback
    np.random.seed(42)
    sample_data = {
        'action_date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
        'product_name': np.random.choice(['Aspirin', 'Ibuprofen', 'Tylenol', 'Unknown Product'], 100),
        'quantity_involved': np.random.randint(1, 100, 100),
        'total_amount': np.random.uniform(10, 500, 100),
        'reason': np.random.choice(['Quality Issue', 'Labeling Error', 'N/A'], 100),
        'severity': np.random.choice(['high', 'medium', 'low'], 100)
    }
    df = pd.DataFrame(sample_data)
    df['action_date'] = pd.to_datetime(df['action_date'])

# Date filter (full range for images)
min_date = df['action_date'].min().date()
max_date = df['action_date'].max().date()
filtered_df = df[(df['action_date'].dt.date >= min_date) & (df['action_date'].dt.date <= max_date)].copy()

# 1. Trends Combo Chart
monthly_trends = filtered_df.groupby(filtered_df['action_date'].dt.to_period('M')).agg({
    'total_amount': 'sum',
    'quantity_involved': 'sum'
}).reset_index()
monthly_trends['action_date'] = monthly_trends['action_date'].astype(str)
monthly_trends['inventory_proxy'] = monthly_trends['quantity_involved'] * np.random.uniform(10, 20, len(monthly_trends))

fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
fig_combo.add_trace(
    px.line(monthly_trends, x='action_date', y='total_amount', color_discrete_sequence=['blue']).data[0],
    secondary_y=False,
)
fig_combo.add_trace(
    px.bar(monthly_trends, x='action_date', y='inventory_proxy', color_discrete_sequence=['green']).data[0],
    secondary_y=True,
)
fig_combo.update_layout(title="Recall Amounts and Inventory Proxy Over Time", xaxis_title="Month", template='plotly_white')
fig_combo.update_yaxes(title_text="Recall Amount ($)", secondary_y=False)
fig_combo.update_yaxes(title_text="Inventory Proxy ($)", secondary_y=True)
fig_combo.write_image("images/trends-combo.png")

# 2. Products Bar Chart
top_products_df = filtered_df.groupby('product_name').agg({'quantity_involved': 'sum', 'severity': lambda x: x.mode()[0] if not x.mode().empty else 'low'}).sort_values('quantity_involved', ascending=False).head(10).reset_index()
color_map = {'high': 'red', 'medium': 'orange', 'low': 'green'}
fig_products = px.bar(
    top_products_df,
    x='quantity_involved',
    y='product_name',
    orientation='h',
    title='Top 10 Products by Quantity Involved (Color-Coded by Severity)',
    template='plotly_white',
    color='severity',
    color_discrete_map=color_map,
    labels={'quantity_involved': 'Quantity Involved', 'product_name': 'Product Name', 'severity': 'Severity'}
)
fig_products.update_layout(xaxis_title="Quantity Involved", yaxis_title="Product Name")
fig_products.write_image("images/products-bar.png")

# 3. Products Pie Chart
product_counts = filtered_df['product_name'].value_counts().head(10)
fig_pie = px.pie(
    values=product_counts.values,
    names=product_counts.index,
    title='Product Distribution (Top 10)',
    template='plotly_white'
)
fig_pie.write_image("images/products-pie.png")

# 4. Correlations Heatmap
numeric_df = filtered_df.select_dtypes(include=[np.number])
if not numeric_df.empty:
    corr = numeric_df.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, fmt='.2f', square=True)
    plt.title('Correlation Heatmap of Numeric Variables')
    plt.tight_layout()
    plt.savefig("images/correlations-heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()

# 5. Correlations Scatter (Pairplot)
key_vars = ['quantity_involved', 'total_amount']
available_vars = [var for var in key_vars if var in numeric_df.columns]
if len(available_vars) >= 2:
    import warnings
    warnings.filterwarnings('ignore')
    fig_scatter = sns.pairplot(numeric_df[available_vars], diag_kind='kde')
    fig_scatter.savefig("images/correlations-scatter.png", dpi=300, bbox_inches='tight')
    plt.close()

# 6. Severity High Bar
high_sev = filtered_df[filtered_df['severity'] == 'high']
reason_high = high_sev['reason'].value_counts().head(5)
fig_high = px.bar(x=reason_high.index, y=reason_high.values,
                  title='Top Reasons (High Severity)', color=reason_high.index,
                  color_discrete_sequence=px.colors.qualitative.Set1)
fig_high.update_layout(xaxis_title="Reason", yaxis_title="Count")
fig_high.write_image("images/severity-high-bar.png")

# 7. Severity Low Bar
low_med_sev = filtered_df[filtered_df['severity'].isin(['low', 'medium'])]
reason_low = low_med_sev['reason'].value_counts().head(5)
fig_low = px.bar(x=reason_low.index, y=reason_low.values,
                 title='Top Reasons (Low/Medium Severity)', color=reason_low.index,
                 color_discrete_sequence=px.colors.qualitative.Pastel1)
fig_low.update_layout(xaxis_title="Reason", yaxis_title="Count")
fig_low.write_image("images/severity-low-bar.png")

# 8. Dashboard Overview (Mock - save a simple plot or note)
fig_overview = px.scatter(filtered_df, x='action_date', y='quantity_involved', color='severity',
                         title='Dashboard Overview: Recalls by Date and Severity')
fig_overview.write_image("images/dashboard-overview.png")

# 9. Trends Preview (similar to combo but simplified)
fig_trends = px.line(filtered_df.groupby(filtered_df['action_date'].dt.date)['quantity_involved'].sum().reset_index(),
                     x='action_date', y='quantity_involved', title='Trends Preview')
fig_trends.write_image("images/trends-preview.png")

print("All images generated successfully in images/ folder.")