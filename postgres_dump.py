import pandas as pd
from sqlalchemy import create_engine, text
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

DATA_FOLDER = "Data"  # Folder where your CSVs are
# -----------------------------

# Connect to Postgres
engine = create_engine(
    f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

# Function to truncate table
def truncate_table(table_name):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT to_regclass('{table_name}');"))
            exists = result.scalar()
            if exists is None:
                print(f"Table '{table_name}' does NOT exist. Skipping truncate.")
                return False
            conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"))
            conn.commit()
            print(f"Table '{table_name}' truncated successfully!")
            return True
    except Exception as e:
        print(f"Failed to truncate table '{table_name}': {e}")
        return False

# Function to load CSV into Postgres (no cleaning)
def load_csv_to_postgres(csv_path, table_name):
    if not os.path.exists(csv_path):
        print(f"{csv_path} does not exist!")
        return

    try:
        df = pd.read_csv(csv_path)

        # Truncate table
        truncate_table(table_name)

        # Load into Postgres
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"✅ SUCCESS: Data from {csv_path} loaded into table '{table_name}'")
    except Exception as e:
        print(f"❌ FAILURE: Could not load {csv_path} into '{table_name}': {e}")

# Find the latest CSV file for given prefix
def find_latest_csv(prefix):
    prefix = prefix.lower()
    files = [
        f for f in os.listdir(DATA_FOLDER)
        if f.lower().startswith(prefix) and f.lower().endswith('.csv')
    ]
    if not files:
        print(f"No CSV found for prefix: {prefix}")
        return None
    files.sort(reverse=True)
    return os.path.join(DATA_FOLDER, files[0])

# ---------- Load PhonePe ----------
phonepe_csv = find_latest_csv("phonepe")
if phonepe_csv:
    load_csv_to_postgres(phonepe_csv, "phonepe")

# ---------- Load GPay ----------
gpay_csv = find_latest_csv("gpay")
if gpay_csv:
    load_csv_to_postgres(gpay_csv, "gpay")

# ---------- Load HDFC Bank Statement ----------
hdfc_csv = find_latest_csv("hdfc")
if hdfc_csv:
    load_csv_to_postgres(hdfc_csv, "hdfc_bank")
