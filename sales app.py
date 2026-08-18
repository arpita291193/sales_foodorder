
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Filtered Sales Dashboard", layout="wide")
st.title("📊 Filtered Sales Dashboard")

# Load data
try:
    df = pd.read_csv("data/sales_data.csv")
    st.success("✅ CSV loaded successfully")

    # Region filter
    st.sidebar.header("Filter Options")
    region = st.sidebar.selectbox("Choose Region", df['region'].unique())

    # Filter data
    filtered_df = df[df['region'] == region]

    # Show filtered table
    st.subheader(f"Sales Data for Region: {region}")
    st.dataframe(filtered_df)

except Exception as e:
    st.error(f"❌ Something went wrong: {e}")

import plotly.express as px

# Bar chart: total sales by product
st.subheader("📦 Total Sales by Product")
fig = px.bar(
    filtered_df,
    x='product',
    y='total_sales',
    color='status',
    title=f"Sales Breakdown by Product in {region}"
)
st.plotly_chart(fig, use_container_width=True)

from utils.insights import generate_insight

st.subheader("🔍 AI Insight")
st.info(generate_insight(filtered_df))
