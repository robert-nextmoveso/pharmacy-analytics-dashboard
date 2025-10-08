import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from api_utils import fetch_pharmacy_data

# Set page configuration
st.set_page_config(
    page_title="Pharmacy Analytics Dashboard",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #1f77b4;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">💊 Pharmacy Recall Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown("Analyze FDA recall data to identify trends, risks, and insights for pharmacy inventory optimization and compliance.")

# Sidebar controls
st.sidebar.markdown('<div class="sidebar-header">⚙️ Controls</div>', unsafe_allow_html=True)

# Data limit selector
data_limit = st.sidebar.slider("Data Limit", min_value=50, max_value=1000, value=300, step=50)

# Refresh data button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Cache data fetching
@st.cache_data
def load_data(limit):
    return fetch_pharmacy_data(limit=limit)

# Load data
with st.spinner("Fetching pharmacy data..."):
    df = load_data(data_limit)

# Fallback to local CSV if API fails
if df.empty:
    try:
        df = pd.read_csv('pharmacy_data/sample_pharmacy_data.csv')
        df['action_date'] = pd.to_datetime(df['action_date'])
        # Apply severity logic if needed, but CSV has it
        st.info("Loaded sample data from local CSV as API fallback.")
    except FileNotFoundError:
        st.error("No local CSV found. Please ensure sample_pharmacy_data.csv exists.")
        df = pd.DataFrame()  # Empty fallback

# Date filters in sidebar after data load
if not df.empty:
    min_date = pd.to_datetime(df['action_date']).min().date()
    max_date = pd.to_datetime(df['action_date']).max().date()
else:
    min_date = datetime.now().date() - timedelta(days=365)
    max_date = datetime.now().date()

start_date = st.sidebar.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

# Apply date filter
df['action_date'] = pd.to_datetime(df['action_date'], errors='coerce')
filtered_df = df[(df['action_date'].dt.date >= start_date) & (df['action_date'].dt.date <= end_date)].copy()

if filtered_df.empty:
    st.warning("No data in range—adjust filters")

# Check if data loaded successfully
if df.empty:
    st.warning("⚠️ Failed to load data from API. Using sample data for analysis.")
    # Create sample data as backup
    sample_data = {
        'action_date': pd.date_range('2023-01-01', periods=10, freq='D'),
        'product_name': ['Drug A', 'Drug B', 'Drug C'] * 3 + ['Drug A'],
        'quantity_involved': [100, 200, 150, 300, 250, 180, 220, 190, 160, 210],
        'total_amount': [1000, 2000, 1500, 3000, 2500, 1800, 2200, 1900, 1600, 2100],
        'reason': ['Recall', 'Defect', 'Expiration'] * 3 + ['Recall']
    }
    df = pd.DataFrame(sample_data)

# Success message
st.success(f"✅ Successfully loaded {len(filtered_df)} records from openFDA API (filtered by date range)")

# Key Metrics Row using filtered_df
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Records", len(filtered_df))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    avg_quantity = filtered_df['quantity_involved'].mean()
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Avg Quantity Involved", f"{avg_quantity:.1f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    total_amount = filtered_df['total_amount'].sum()
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Amount ($)", f"${total_amount:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    most_common_reason = filtered_df['reason'].mode()[0] if not filtered_df['reason'].mode().empty else 'N/A'
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Most Common Reason", most_common_reason)
    st.markdown('</div>', unsafe_allow_html=True)

# Main content tabs using filtered_df
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trends",
    "📊 Products",
    "🔗 Correlations",
    "📋 Raw Data",
    "🆚 Severity"
])

with tab1:
    st.header("📈 Trends")
    st.markdown("Analyze recall trends over time to identify patterns and predict future risks.")
    
    # Prepare time series data using filtered_df
    filtered_df_local = filtered_df.copy()  # Avoid modifying global
    filtered_df_local['action_date'] = pd.to_datetime(filtered_df_local['action_date'], errors='coerce')
    
    # Monthly trends for combo chart
    monthly_trends = filtered_df_local.groupby(filtered_df_local['action_date'].dt.to_period('M')).agg({
        'total_amount': 'sum',
        'quantity_involved': 'sum'
    }).reset_index()
    monthly_trends['action_date'] = monthly_trends['action_date'].astype(str)
    # Derive inventory proxy from quantity (e.g., total quantity as proxy for inventory impact)
    monthly_trends['inventory_proxy'] = monthly_trends['quantity_involved'] * np.random.uniform(10, 20, len(monthly_trends))  # Mock pricing for inventory value

    # Combo chart: line for recalls (total_amount), bar for inventory proxy
    try:
        fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add line for recalls
        fig_combo.add_trace(
            px.line(monthly_trends, x='action_date', y='total_amount', color_discrete_sequence=['blue']).data[0],
            secondary_y=False,
        )
        
        # Add bar for inventory proxy
        fig_combo.add_trace(
            px.bar(monthly_trends, x='action_date', y='inventory_proxy', color_discrete_sequence=['green']).data[0],
            secondary_y=True,
        )
        
        fig_combo.update_layout(
            title="Recall Amounts and Inventory Proxy Over Time",
            xaxis_title="Month",
            template='plotly_white'
        )
        fig_combo.update_yaxes(title_text="Recall Amount ($)", secondary_y=False)
        fig_combo.update_yaxes(title_text="Inventory Proxy ($)", secondary_y=True)
        
        st.markdown("**Alt:** Combo chart with blue line for recall amounts over months and green bars for inventory proxy values, highlighting correlations for stock management.")
        st.plotly_chart(fig_combo, use_container_width=True)
        st.markdown("This chart highlights seasonal patterns in recalls, aiding inventory planning.")
    except Exception as e:
        st.error(f"Error generating trends combo chart: {e}")

with tab2:
    st.header("📊 Products")
    st.markdown("Identify high-risk products for targeted audits and inventory management.")
    
    # Top products by quantity with severity color-coding using filtered_df
    top_products_df = filtered_df.groupby('product_name').agg({'quantity_involved': 'sum', 'severity': lambda x: x.mode()[0] if not x.mode().empty else 'low'}).sort_values('quantity_involved', ascending=False).head(10).reset_index()

    # Horizontal bar chart with color by severity
    color_map = {'high': 'red', 'medium': 'orange', 'low': 'green'}
    try:
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
        fig_products.update_layout(
            xaxis_title="Quantity Involved",
            yaxis_title="Product Name"
        )
        st.markdown("**Alt:** Horizontal bar chart of top 10 products by quantity, colored red for high severity, orange for medium, green for low.")
        st.plotly_chart(fig_products, use_container_width=True)
        st.markdown("This visualization helps prioritize audits for high-severity products to mitigate risks.")
    except Exception as e:
        st.error(f"Error generating products bar chart: {e}")

    # Product distribution pie chart
    product_counts = filtered_df['product_name'].value_counts().head(10)
    try:
        fig_pie = px.pie(
            values=product_counts.values,
            names=product_counts.index,
            title='Product Distribution (Top 10)',
            template='plotly_white'
        )
        st.markdown("**Alt:** Pie chart showing distribution of top 10 products by recall count.")
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("The pie chart illustrates the distribution of recalls across top products.")
    except Exception as e:
        st.error(f"Error generating products pie chart: {e}")

with tab3:
    st.header("🔗 Correlations")
    st.markdown("Compare high vs. low severity to uncover operational insights.")
    
    # Select only numeric columns from filtered_df
    numeric_df = filtered_df.select_dtypes(include=[np.number])

    # Correlation heatmap
    if not numeric_df.empty:
        corr = numeric_df.corr()

        fig_corr, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            corr,
            annot=True,
            cmap='coolwarm',
            center=0,
            ax=ax,
            fmt='.2f',
            square=True
        )
        ax.set_title('Correlation Heatmap of Numeric Variables')
        st.markdown("**Alt:** Heatmap of correlations between numeric variables like quantity and amount, with colors from blue (negative) to red (positive).")
        st.pyplot(fig_corr)
        st.markdown("This heatmap reveals relationships between variables, such as quantity and total amount, to inform risk assessment.")

        # Scatter plot matrix for key variables
        st.subheader("Scatter Plot Matrix")
        key_vars = ['quantity_involved', 'total_amount']
        available_vars = [var for var in key_vars if var in numeric_df.columns]

        if len(available_vars) >= 2:
            fig_scatter = sns.pairplot(numeric_df[available_vars], diag_kind='kde')
            st.markdown("**Alt:** Pairplot showing scatter between quantity involved and total amount, with KDE on diagonals.")
            st.pyplot(fig_scatter)
            st.markdown("The scatter plot matrix visualizes distributions and relationships for deeper analysis.")
        else:
            st.info("Not enough numeric variables for scatter plot matrix")
    else:
        st.warning("No numeric columns available for correlation analysis")

with tab4:
    st.header("📋 Raw Data")
    st.markdown("View and filter raw data for detailed exploration.")
    
    # Data filters on top of date-filtered data
    col1, col2 = st.columns(2)

    with col1:
        selected_reason = st.multiselect(
            "Filter by Reason",
            options=filtered_df['reason'].unique(),
            default=[]
        )

    with col2:
        min_quantity = st.number_input(
            "Minimum Quantity",
            min_value=0,
            value=0
        )

    # Apply additional filters
    raw_filtered_df = filtered_df.copy()
    if selected_reason:
        raw_filtered_df = raw_filtered_df[raw_filtered_df['reason'].isin(selected_reason)]
    raw_filtered_df = raw_filtered_df[raw_filtered_df['quantity_involved'] >= min_quantity]

    st.write(f"Showing {len(raw_filtered_df)} of {len(filtered_df)} records")

    # Display data
    st.markdown("**Alt:** Interactive data table with columns for date, product, quantity, amount, reason, and severity.")
    st.dataframe(
        raw_filtered_df,
        use_container_width=True,
        column_config={
            "action_date": st.column_config.DateColumn("Action Date"),
            "quantity_involved": st.column_config.NumberColumn("Quantity Involved", format="%.0f"),
            "total_amount": st.column_config.NumberColumn("Total Amount ($)", format="$%.2f")
        }
    )

    # Download button
    csv = raw_filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="pharmacy_data_filtered.csv",
        mime="text/csv"
    )
    
    st.markdown("This table allows for custom filtering and export of data for further analysis.")

with tab5:
    st.header("🆚 Severity")
    st.markdown("Examine recall severity levels to prioritize high-impact events. Break down common reasons for recalls by severity to inform prevention strategies.")
    
    # Use centralized severity (already lowercase)
    # Split into high and low/medium severity using filtered_df
    high_sev = filtered_df[filtered_df['severity'] == 'high']
    low_med_sev = filtered_df[filtered_df['severity'].isin(['low', 'medium'])]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("High Severity Recalls")
        st.metric("Total Records", len(high_sev))
        st.metric("Avg Quantity", f"{high_sev['quantity_involved'].mean():.1f}")
        st.metric("Most Common Reason", high_sev['reason'].mode()[0] if not high_sev['reason'].mode().empty else 'N/A')

        # Bar chart for reasons
        reason_high = high_sev['reason'].value_counts().head(5)
        try:
            fig_high = px.bar(x=reason_high.index, y=reason_high.values,
                              title='Top Reasons (High Severity)', color=reason_high.index,
                              color_discrete_sequence=px.colors.qualitative.Set1)
            fig_high.update_layout(xaxis_title="Reason", yaxis_title="Count")
            st.markdown("**Alt:** Bar chart of top 5 reasons for high-severity recalls, colored distinctly.")
            st.plotly_chart(fig_high, use_container_width=True)
            st.markdown("This chart shows the most frequent reasons for high-severity recalls, helping to focus prevention efforts.")
        except Exception as e:
            st.error(f"Error generating high severity chart: {e}")

    with col2:
        st.subheader("Low/Medium Severity Recalls")
        st.metric("Total Records", len(low_med_sev))
        st.metric("Avg Quantity", f"{low_med_sev['quantity_involved'].mean():.1f}")
        st.metric("Most Common Reason", low_med_sev['reason'].mode()[0] if not low_med_sev['reason'].mode().empty else 'N/A')

        # Bar chart for reasons
        reason_low = low_med_sev['reason'].value_counts().head(5)
        try:
            fig_low = px.bar(x=reason_low.index, y=reason_low.values,
                             title='Top Reasons (Low/Medium Severity)', color=reason_low.index,
                             color_discrete_sequence=px.colors.qualitative.Pastel1)
            fig_low.update_layout(xaxis_title="Reason", yaxis_title="Count")
            st.markdown("**Alt:** Bar chart of top 5 reasons for low/medium-severity recalls, in pastel colors.")
            st.plotly_chart(fig_low, use_container_width=True)
            st.markdown("Comparing reasons across severity levels reveals patterns for operational improvements.")
        except Exception as e:
            st.error(f"Error generating low/medium severity chart: {e}")

    st.markdown("High-severity recalls often involve critical issues like CGMP deviations, enabling prioritization of compliance measures.")

# Footer
st.markdown("---")
st.markdown("**Data Source:** openFDA Drug Enforcement API")
st.markdown("**Built with:** Streamlit, Pandas, Plotly, Matplotlib, Seaborn")
st.markdown("**Author:** Robert - [GitHub](https://github.com/robert-nextmoveso)")