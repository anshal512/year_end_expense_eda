# Year-End Personal Expense Analysis

A **personal finance dashboard and analytics tool** built using Python, PostgreSQL, and Streamlit. This project helps track, analyze, and visualize monthly expenses across multiple wallets (PhonePe, GPay) and bank accounts (HDFC).  

It includes automated PDF parsing, database ingestion, and interactive dashboards for detailed insights.

---

## Features

- **Expense Parsing**
  - Automatically extract transactions from PDF statements (PhonePe, GPay, HDFC Bank).
  - Handles both debit and credit transactions.
  - Cleans and formats dates, amounts, and transaction details.

- **Database Integration**
  - Store all transactions in PostgreSQL.
  - Unified `combined_transactions` view for easier analysis.
  - Monthly aggregation of expenses by category or vendor.

- **Streamlit Dashboards**
  - Interactive charts and tables for visualizing monthly spending.
  - Expense breakdowns by category, wallet, or merchant.
  - Pie charts, histograms, and summary statistics.
  - Scrollable tables for large datasets.

- **Automation**
  - Generate screenshots of dashboards for reports.
  - Easy configuration via `.env` for database credentials.

---
