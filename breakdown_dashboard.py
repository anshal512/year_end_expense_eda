import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# -------------------------
# PostgreSQL connection
# -------------------------
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

def get_connection():
    """Return a raw psycopg2 connection."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

def run_query(query):
    """Run SQL query and return DataFrame."""
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# -------------------------
# Streamlit Layout
# -------------------------
st.set_page_config(page_title="Personal Expense Dashboard", layout="wide")
st.title("📊 Personal Expense Dashboard")

# -------------------------
# SQL Queries
# -------------------------
# Monthly Rent
rent_query = """
SELECT 
    date_trunc('month', date::date) AS month,
    SUM(amount) AS monthly_rent
FROM combined_transactions
WHERE (transaction ILIKE '%santhosh%'
    OR transaction ILIKE '%haritha%'
    OR transaction ILIKE '%littlewonders%')
  AND (type IS NULL OR type ILIKE 'debit')
GROUP BY 1
ORDER BY 1;
"""

# Monthly Insurance
insurance_query = """
SELECT 
    date_trunc('month', date::date) AS month,
    SUM(amount) AS monthly_insurance
FROM combined_transactions
WHERE transaction ILIKE '%policy%bazaar%'
  AND (type IS NULL OR type ILIKE 'debit')
GROUP BY 1
ORDER BY 1;
"""

# Monthly Food/Swiggy
food_query = """
SELECT 
    date_trunc('month', date::date) AS month,
    SUM(amount) AS monthly_food
FROM combined_transactions
WHERE transaction ILIKE '%swiggy%'
   OR transaction ILIKE '%the veg story%'
   OR transaction ILIKE '%new taaza thindi%'
   OR transaction ILIKE '%surendra singh%'
  AND (type IS NULL OR type ILIKE 'debit')
GROUP BY 1
ORDER BY 1;
"""

# -------------------------
# Fetch DataFrames
# -------------------------
rent_df = run_query(rent_query)
insurance_df = run_query(insurance_query)
food_df = run_query(food_query)

# -------------------------
# Display Metrics
# -------------------------
st.subheader("Monthly Expenses Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Total Rent", f"₹{rent_df['monthly_rent'].sum():,.0f}")
col2.metric("Total Insurance", f"₹{insurance_df['monthly_insurance'].sum():,.0f}")
col3.metric("Total Food/Swiggy", f"₹{food_df['monthly_food'].sum():,.0f}")

# -------------------------
# Histograms
# -------------------------
st.subheader("Monthly Expense Histogram")
combined_hist_df = pd.DataFrame({
    "Month": rent_df['month'],
    "Rent": rent_df['monthly_rent'],
    "Insurance": insurance_df['monthly_insurance'],
    "Food/Swiggy": food_df['monthly_food']
})

fig = px.bar(
    combined_hist_df.melt(id_vars='Month', var_name='Category', value_name='Amount'),
    x='Month',
    y='Amount',
    color='Category',
    barmode='group',
    title="Monthly Expenses",
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Pie Chart
# -------------------------
st.subheader("Expense Distribution")
total_amounts = {
    "Rent": rent_df['monthly_rent'].sum(),
    "Insurance": insurance_df['monthly_insurance'].sum(),
    "Food/Swiggy": food_df['monthly_food'].sum()
}
pie_df = pd.DataFrame({
    "Category": total_amounts.keys(),
    "Amount": total_amounts.values()
})

fig_pie = px.pie(
    pie_df,
    names='Category',
    values='Amount',
    title='Total Expense Distribution',
    hole=0.4
)
st.plotly_chart(fig_pie, use_container_width=True)

# -------------------------
# Scrollable Tables
# -------------------------
st.subheader("Monthly Expenses Table")
combined_table = combined_hist_df.copy()
combined_table['Month'] = combined_table['Month'].dt.strftime('%Y-%m')
st.dataframe(combined_table, height=400)
