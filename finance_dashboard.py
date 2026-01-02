import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
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
engine = create_engine(
    f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

st.set_page_config(
    page_title="Expense Reconciliation Dashboard",
    layout="wide"
)

st.title("💰 Expense Reconciliation Dashboard")
st.write("Bank vs Wallet Spend Analytics")

# -----------------------------
# Load Queries
# -----------------------------

# Monthly Reconciliation
monthly_q = """
WITH hdfc AS (
    SELECT 
        date_trunc('month', to_date(date, 'DD-MM-YY'))::date AS month,
        SUM(withdrawal_amt) AS bank_expense
    FROM hdfc_bank
    WHERE withdrawal_amt IS NOT NULL
    GROUP BY 1
),
wallets AS (
    SELECT 
        date_trunc('month', date::date)::date AS month,
        SUM(amount) AS wallet_expense
    FROM (
        SELECT date, amount FROM gpay
        UNION ALL
        SELECT date, amount FROM phonepe
    ) t
    GROUP BY 1
)
SELECT 
    COALESCE(hdfc.month, wallets.month) AS month,
    bank_expense,
    wallet_expense,
    (bank_expense - wallet_expense) AS difference
FROM hdfc
FULL OUTER JOIN wallets USING (month)
ORDER BY month;
"""
monthly_df = pd.read_sql(monthly_q, engine)

# PIE CHART DATA
pie_q = """
WITH bank AS (
    SELECT SUM(withdrawal_amt) total_bank
    FROM hdfc_bank
    WHERE withdrawal_amt IS NOT NULL
),
wallet AS (
    SELECT SUM(amount) total_wallet
    FROM (
        SELECT amount FROM gpay
        UNION ALL
        SELECT amount FROM phonepe
    ) t
)
SELECT
    'Bank (HDFC)' AS source,
    total_bank AS amount
FROM bank
UNION ALL
SELECT
    'Wallets (GPay + PhonePe)',
    total_wallet
FROM wallet;
"""
pie_df = pd.read_sql(pie_q, engine)

# WALLET HISTOGRAM QUERY
hist_q = """
SELECT amount
FROM (
    SELECT amount FROM gpay
    UNION ALL
    SELECT amount FROM phonepe
) t;
"""
hist_df = pd.read_sql(hist_q, engine)

# AVG MONTHLY EXPENSE
avg_q = """
WITH wallets AS (
    SELECT 
        date_trunc('month', date::date)::date AS month,
        SUM(amount) AS total_wallet
    FROM (
        SELECT date, amount FROM gpay
        UNION ALL
        SELECT date, amount FROM phonepe
    ) t
    GROUP BY 1
)
SELECT 
    AVG(total_wallet) AS avg_monthly_wallet_spend,
    MAX(total_wallet) AS max_wallet_spend,
    MIN(total_wallet) AS min_wallet_spend
FROM wallets;
"""
avg_df = pd.read_sql(avg_q, engine)

# -----------------------------
# KPI ROW
# -----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("📉 Avg Monthly Wallet Spend", f"₹{round(avg_df['avg_monthly_wallet_spend'][0],2)}")
col2.metric("🔥 Highest Month Wallet Spend", f"₹{round(avg_df['max_wallet_spend'][0],2)}")
col3.metric("🧊 Lowest Month Wallet Spend", f"₹{round(avg_df['min_wallet_spend'][0],2)}")

# -----------------------------
# Monthly Reconciliation Table
# -----------------------------
st.subheader("📆 Monthly Bank vs Wallet Expense Comparison")

st.dataframe(monthly_df, use_container_width=True)

# -----------------------------
# Charts Row
# -----------------------------
left, right = st.columns(2)

# PIE CHART
with left:
    st.subheader("🥧 Expense Share — Bank vs Wallets")
    st.plotly_chart(
        {
            "data": [{
                "labels": pie_df["source"],
                "values": pie_df["amount"],
                "type": "pie"
            }],
            "layout": {"height": 400}
        }
    )

# LINE TREND
with right:
    st.subheader("📈 Monthly Trend")
    st.line_chart(
        monthly_df.set_index("month")[["bank_expense", "wallet_expense"]]
    )

# -----------------------------
# Histogram
# -----------------------------
st.subheader("📊 Wallet Transaction Distribution (Histogram)")
st.bar_chart(hist_df["amount"])

st.success("Dashboard Loaded Successfully 🚀")
