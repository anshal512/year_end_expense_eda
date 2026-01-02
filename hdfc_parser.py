# hdfc_parser.py
import pandas as pd
from datetime import datetime
import os

# -----------------------------
#  Path to your Excel file
# -----------------------------
xls_path = "Data/Hdfc_statement.xls"  
if not os.path.exists(xls_path):
    raise FileNotFoundError(f"{xls_path} does not exist!")

# -----------------------------
# 2 Load Excel without header to detect actual header row
# -----------------------------
df_raw = pd.read_excel(xls_path, header=None, dtype=str)

# -----------------------------
# 3 Robust header detection
# Header row must contain BOTH 'Date' and 'Narration'
# -----------------------------
header_row_idx = df_raw[
    df_raw.apply(lambda row: row.astype(str).str.contains("Date", na=False).any() and
                              row.astype(str).str.contains("Narration", na=False).any(), axis=1)
].index[0]
print("Header found at row:", header_row_idx)

# -----------------------------
# 4 Read Excel again with proper header
# -----------------------------
df = pd.read_excel(xls_path, header=header_row_idx, dtype=str)

# -----------------------------
# 5 Normalize column names (strip, lowercase)
# -----------------------------
df.columns = df.columns.str.strip().str.lower()
print("Columns detected:", df.columns.tolist())

# Standard column names for reference
date_col = 'date'
value_dt_col = 'value dt'  # if exists
numeric_cols = ['withdrawal amt.', 'deposit amt.', 'closing balance']

# -----------------------------
# 6 Drop completely empty rows
# -----------------------------
df = df.dropna(how='all')

# -----------------------------
# 7 Remove top dummy rows with all '*' or blank
# -----------------------------
df = df[~df.apply(lambda row: row.astype(str).str.match(r'^\*+$').all(), axis=1)]

# -----------------------------
# 8 Remove footer rows
# Keep only rows up to last valid 'date'
# -----------------------------
df['date_parsed'] = pd.to_datetime(df[date_col], errors='coerce')
last_valid_idx = df['date_parsed'].last_valid_index()
df = df.loc[:last_valid_idx]
df = df.drop(columns=['date_parsed'])

# -----------------------------
# 9 Clean numeric columns (remove commas, convert to float)
# -----------------------------
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "").str.strip(), errors='coerce')

# -----------------------------
# 10 Format date columns uniformly
# -----------------------------
for col in [date_col, value_dt_col]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%m-%y')

# -----------------------------
# 11 Make columns Postgres-friendly
# -----------------------------
df.columns = df.columns.str.strip() \
    .str.lower() \
    .str.replace(r'[./ ]+', '_', regex=True) \
    .str.replace(r'_+$', '', regex=True)

print("Columns after rename:", df.columns.tolist())

# -----------------------------
# 12 Save cleaned CSV with timestamp
# -----------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_csv = f"Data/hdfc_clean_{timestamp}.csv"
df.to_csv(output_csv, index=False, quoting=1)  # quoting=1 -> csv.QUOTE_ALL

print(f"\nClean CSV file created successfully: {output_csv}")
