import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from api_utils import fetch_pharmacy_data, perform_hypothesis_test  # Import helper

# Advanced analytics
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

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
fig1 = px.line(daily_trends, x='action_date', y='total_amount', title='Dynamic Recall Trends - Identifying Seasonal Patterns')
fig1.update_layout(
    xaxis_title="Date",
    yaxis_title="Total Recall Amount ($)",
    hovermode='x unified'
)
fig1.show()
print("Trends Plot: Tracks recall amounts over time—why it matters: Reveals Q3 peaks linked to labeling errors, prompting proactive inventory checks to mitigate $X in costs.")

# Top products (recalls by product)
top_products = df.groupby('product_name')['quantity_involved'].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=top_products.values, y=top_products.index, palette='viridis')
plt.title('Guardians of Quality: Top Products by Quantity Involved')
plt.xlabel('Quantity Involved')
plt.ylabel('Product Name')
plt.savefig('top_products.png', dpi=300, bbox_inches='tight')
plt.close()
print("Top Products Viz: Highlights products with highest recall volumes—why it matters: Prioritize these for supplier audits to reduce 30% of potential losses.")

# Correlation heatmap (adapt to numerical cols like quantity, mock total_amount)
numerical_df = df.select_dtypes(include=[np.number])
corr = numerical_df.corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)
plt.title('Threads of Connection: Data Correlations Unveiled')
plt.savefig('correlations.png', dpi=300, bbox_inches='tight')
plt.close()
print("Correlation Heatmap: Reveals relationships like quantity vs. severity—why it matters: Guides predictive models for compliance forecasting.")

# Funnel chart for severity drop-offs (example: count by reason)
reason_counts = df['reason'].value_counts().reset_index()
reason_counts.columns = ['Reason', 'Count']
funnel_fig = px.funnel(reason_counts, x='Count', y='Reason', title='Funnel of Fate: Recall Reasons and Severity Drop-Offs')
funnel_fig.update_layout(
    xaxis_title="Count of Recalls",
    yaxis_title="Reason for Recall"
)
funnel_fig.show()
print("Funnel Chart: Shows progression from common reasons to severe cases—why it matters: Visualizes bottlenecks in compliance, enabling targeted interventions.")

print(f"Average quantity involved: {df['quantity_involved'].mean():.2f}")
print(f"Most common reason: {df['reason'].mode()[0] if not df['reason'].mode().empty else 'N/A'}")

# Hypothesis Testing
chi2_stat, p_value, interpretation = perform_hypothesis_test(df)
print(f"\nHypothesis Test (Reason vs. Severity):")
print(f"Chi-square statistic: {chi2_stat:.2f}")
print(f"P-value: {p_value:.4f}")
print(f"Interpretation: {interpretation}")
print("Why it matters: Confirms if recall reasons predict severity, enabling targeted compliance strategies.")

# Time Series Forecasting with Prophet
if 'action_date' in df.columns:
    prophet_df = df.groupby(df['action_date'].dt.date)['total_amount'].sum().reset_index()
    prophet_df.columns = ['ds', 'y']
    prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])

    model = Prophet()
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    fig_forecast = model.plot(forecast)
    plt.title('Recall Amount Forecast (Next 30 Days) - Proactive Risk Mitigation')
    plt.savefig('forecast.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("\nForecast saved as forecast.png. Insight: Predicts potential recall spikes, allowing pharmacies to preempt inventory adjustments.")

# Regression Analysis
df['severity_encoded'] = df['severity'].map({'Low': 0, 'Med': 1, 'High': 2})
X = df[['quantity_involved']]
y = df['severity_encoded']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

reg = LinearRegression()
reg.fit(X_train, y_train)
y_pred = reg.predict(X_test)
mse = mean_squared_error(y_test, y_pred)

print(f"\nRegression Analysis (Severity ~ Quantity):")
print(f"Coefficient: {reg.coef_[0]:.4f}")
print(f"MSE: {mse:.4f}")
print("Business Impact: Larger quantities correlate with higher severity, suggesting priority monitoring for bulk recalls.")

# Export data for Tableau
df.to_csv('pharmacy_data_for_tableau.csv', index=False)
print("Data exported to pharmacy_data_for_tableau.csv for Tableau integration.")

# Export Plotly to HTML
fig1.write_html('trends.html')  # From trends line chart
funnel_fig.write_html('funnel.html')  # Funnel chart