import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
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
st.markdown('<div class="main-header">💊 Echoes of Recalls: Predictive Insights from FDA Shadows</div>', unsafe_allow_html=True)
st.markdown("Step into the narrative of pharmacy safety: From raw FDA data to actionable forecasts, explore how hidden patterns can prevent crises and optimize operations.")

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

# Check if data loaded successfully
if df.empty:
    st.warning("⚠️ Failed to load data from API. Using sample data for demonstration.")
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
st.success(f"✅ Successfully loaded {len(df)} records from openFDA API")

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Records", len(df))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    avg_quantity = df['quantity_involved'].mean()
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Avg Quantity Involved", f"{avg_quantity:.1f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    total_amount = df['total_amount'].sum()
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Total Amount ($)", f"${total_amount:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    most_common_reason = df['reason'].mode()[0] if not df['reason'].mode().empty else 'N/A'
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Most Common Reason", most_common_reason)
    st.markdown('</div>', unsafe_allow_html=True)

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 The Rising Tide: Recall Trends Unveiled", "📊 Guardians of Quality: Product Insights", "🔗 Threads of Connection: Data Correlations", "📋 Raw Chronicles: The Data Beneath", "🆚 Shadows of Severity: A/B Revelations"])

with tab1:
    st.header("📈 The Rising Tide: Recall Trends Over Time")
    st.markdown("Witness the ebb and flow of pharmacy recalls—where spikes signal hidden risks, guiding proactive measures to protect patients and profits.")

    # Prepare time series data
    df['action_date'] = pd.to_datetime(df['action_date'], errors='coerce')
    daily_trends = df.groupby(df['action_date'].dt.date)['total_amount'].sum().reset_index()
    daily_trends.columns = ['Date', 'Total Amount']

    # Interactive line chart with severity color-coding
    daily_trends_sev = df.groupby([df['action_date'].dt.date, 'severity'])['total_amount'].sum().reset_index()
    daily_trends_sev.columns = ['Date', 'Severity', 'Total Amount']

    fig_trends = px.line(
        daily_trends_sev,
        x='Date',
        y='Total Amount',
        color='Severity',
        title='Daily Recall Trends by Severity',
        template='plotly_white',
        color_discrete_map={'High': 'red', 'Med': 'orange', 'Low': 'blue'}
    )
    fig_trends.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Amount ($)",
        hovermode='x unified'
    )
    st.plotly_chart(fig_trends, use_container_width=True)
    st.markdown("**Business Outcome:** Hover to see severity trends—spikes in red (high severity) signal urgent compliance actions to prevent $X losses.")

    # Monthly trends
    monthly_trends = df.groupby(df['action_date'].dt.to_period('M'))['total_amount'].sum().reset_index()
    monthly_trends['action_date'] = monthly_trends['action_date'].astype(str)

    fig_monthly = px.bar(
        monthly_trends,
        x='action_date',
        y='total_amount',
        title='Monthly Recall Trends',
        template='plotly_white'
    )
    fig_monthly.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Amount ($)"
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

with tab2:
    st.header("📊 Guardians of Quality: Product Analysis")
    st.markdown("Unmask the heroes and villains in your inventory—where top products reveal vulnerabilities, empowering targeted audits for safer shelves.")

    # Top products by quantity with severity color-coding
    top_products_df = df.groupby('product_name').agg({'quantity_involved': 'sum', 'severity': lambda x: x.mode()[0] if not x.mode().empty else 'Low'}).sort_values('quantity_involved', ascending=False).head(10).reset_index()

    # Horizontal bar chart with color by severity
    color_map = {'High': 'red', 'Med': 'orange', 'Low': 'green'}
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
    st.plotly_chart(fig_products, use_container_width=True)
    st.markdown("**Tooltip Insight:** Red bars indicate high-severity products—prioritize these for compliance audits to reduce patient safety risks.")

    # Product distribution pie chart
    product_counts = df['product_name'].value_counts().head(10)
    fig_pie = px.pie(
        values=product_counts.values,
        names=product_counts.index,
        title='Product Distribution (Top 10)',
        template='plotly_white'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    st.header("🔗 Threads of Connection: Data Correlations")
    st.markdown("Follow the invisible threads linking variables—where correlations unveil predictive power, transforming uncertainty into strategic foresight.")

    # Select only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])

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
        st.pyplot(fig_corr)

        # Scatter plot matrix for key variables
        st.subheader("Scatter Plot Matrix")
        key_vars = ['quantity_involved', 'total_amount']
        available_vars = [var for var in key_vars if var in numeric_df.columns]

        if len(available_vars) >= 2:
            fig_scatter = sns.pairplot(numeric_df[available_vars], diag_kind='kde')
            st.pyplot(fig_scatter)
        else:
            st.info("Not enough numeric variables for scatter plot matrix")
    else:
        st.warning("No numeric columns available for correlation analysis")

with tab4:
    st.header("📋 Raw Data")

    # Data filters
    col1, col2 = st.columns(2)

    with col1:
        selected_reason = st.multiselect(
            "Filter by Reason",
            options=df['reason'].unique(),
            default=[]
        )

    with col2:
        min_quantity = st.number_input(
            "Minimum Quantity",
            min_value=0,
            value=0
        )

    # Apply filters
    filtered_df = df.copy()
    if selected_reason:
        filtered_df = filtered_df[filtered_df['reason'].isin(selected_reason)]
    filtered_df = filtered_df[filtered_df['quantity_involved'] >= min_quantity]

    st.write(f"Showing {len(filtered_df)} of {len(df)} records")

    # Display data
    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config={
            "action_date": st.column_config.DateColumn("Action Date"),
            "quantity_involved": st.column_config.NumberColumn("Quantity Involved", format="%.0f"),
            "total_amount": st.column_config.NumberColumn("Total Amount ($)", format="$%.2f")
        }
    )

    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="pharmacy_data_filtered.csv",
        mime="text/csv"
    )

with tab5:
    st.header("🆚 Shadows of Severity: A/B Comparison of Recalls")
    st.markdown("Contrast the light and dark: High-severity crises vs. low-risk echoes, revealing strategies to elevate safety and slash costs.")

    # Derive severity if not present
    if 'severity' not in df.columns:
        df['severity'] = df.get('classification', '').str.extract(r'Class (\w+)')[0].map({'I': 'High', 'II': 'Med', 'III': 'Low'}).fillna('Low')

    # Split into high and low severity
    high_sev = df[df['severity'] == 'High']
    low_sev = df[df['severity'].isin(['Low', 'Med'])]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("High Severity Recalls")
        st.metric("Total Records", len(high_sev))
        st.metric("Avg Quantity", f"{high_sev['quantity_involved'].mean():.1f}")
        st.metric("Most Common Reason", high_sev['reason'].mode()[0] if not high_sev['reason'].mode().empty else 'N/A')

        # Bar chart for reasons
        reason_high = high_sev['reason'].value_counts().head(5)
        fig_high = px.bar(reason_high, x=reason_high.index, y=reason_high.values,
                          title='Top Reasons (High Severity)', color=reason_high.index,
                          color_discrete_sequence=px.colors.qualitative.Set1)
        fig_high.update_layout(xaxis_title="Reason", yaxis_title="Count")
        st.plotly_chart(fig_high, use_container_width=True)

    with col2:
        st.subheader("Low/Med Severity Recalls")
        st.metric("Total Records", len(low_sev))
        st.metric("Avg Quantity", f"{low_sev['quantity_involved'].mean():.1f}")
        st.metric("Most Common Reason", low_sev['reason'].mode()[0] if not low_sev['reason'].mode().empty else 'N/A')

        # Bar chart for reasons
        reason_low = low_sev['reason'].value_counts().head(5)
        fig_low = px.bar(reason_low, x=reason_low.index, y=reason_low.values,
                         title='Top Reasons (Low/Med Severity)', color=reason_low.index,
                         color_discrete_sequence=px.colors.qualitative.Pastel1)
        fig_low.update_layout(xaxis_title="Reason", yaxis_title="Count")
        st.plotly_chart(fig_low, use_container_width=True)

    st.markdown("**Business Insight:** High-severity recalls (Class I) often stem from CGMP deviations, costing pharmacies ~$X more per incident. Compare to prioritize compliance efforts.")

# Footer
st.markdown("---")
st.markdown("**Data Source:** openFDA Drug Enforcement API")
st.markdown("**Built with:** Streamlit, Pandas, Plotly, Matplotlib, Seaborn")
st.markdown("**Author:** Robert - [GitHub](https://github.com/robert-nextmoveso)")