import pdfplumber
import pandas as pd
import re

# -----------------------------
# PhonePe Parser
# -----------------------------
def parse_phonepe(pdf_path):
    all_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_lines.extend(text.split('\n'))

    transactions = []
    i = 0
    while i < len(all_lines):
        line = all_lines[i].strip()

        # Allow Sep + Sept
        date_match = re.match(
            r'^([A-Za-z]{3,4} \d{1,2}, \d{4})\s*(.*?)(DEBIT|CREDIT)\s*(₹[\d,]+)',
            line,
            re.I
        )

        if date_match:
            date_str = date_match.group(1)
            transaction_part = date_match.group(2).strip()
            t_type = date_match.group(3).upper()
            amount = float(date_match.group(4).replace('₹','').replace(',',''))

            # collect following detail lines
            details = []
            j = i + 1
            while j < len(all_lines) and not re.match(r'^[A-Za-z]{3,4} \d{1,2}, \d{4}', all_lines[j].strip()):
                details.append(all_lines[j].strip())
                j += 1

            full_transaction = ' '.join([transaction_part] + details).strip()

            # extract time if present
            time_match = re.search(r'(\d{1,2}:\d{2}\s*[apAP][mM])', full_transaction)
            time_str = time_match.group(1) if time_match else '12:00 AM'

            # let pandas parse month safely
            date = pd.to_datetime(f"{date_str} {time_str}", errors='coerce')

            transactions.append({
                'date': date,
                'transaction': full_transaction,
                'type': t_type,
                'amount': amount
            })

            i = j
        else:
            i += 1

    return pd.DataFrame(transactions)

# -----------------------------
# GPay Parser
# -----------------------------
def parse_gpay(pdf_path):
    all_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_lines.extend(text.split('\n'))

    transactions = []
    i = 0
    while i < len(all_lines):
        line = all_lines[i].strip()
        date_match = re.match(r'^(\d{2}[A-Za-z]{3},\d{4})\s+(.*?)(₹[\d,]+)$', line)
        if date_match:
            date_str = date_match.group(1)
            transaction_part = date_match.group(2).strip()
            amount = float(date_match.group(3).replace('₹','').replace(',',''))

            # Look for time and additional info
            details = []
            j = i + 1
            while j < len(all_lines) and not re.match(r'^\d{2}[A-Za-z]{3},\d{4}', all_lines[j].strip()):
                subline = all_lines[j].strip()
                t_match = re.match(r'(\d{2}:\d{2}[AP]M)\s*(.*)', subline)
                if t_match:
                    time_str = t_match.group(1)
                    details.append(t_match.group(2))
                else:
                    details.append(subline)
                j += 1

            # Default time if not found
            if 'time_str' not in locals():
                time_str = '12:00AM'
            date = pd.to_datetime(f"{date_str} {time_str}", format="%d%b,%Y %I:%M%p", errors='coerce')
            full_transaction = ' '.join([transaction_part] + details).strip()

            transactions.append({
                'date': date,
                'transaction': full_transaction,
                'type': 'NA',
                'amount': amount
            })

            # Reset for next loop
            if 'time_str' in locals():
                del time_str

            i = j
        else:
            i += 1

    df = pd.DataFrame(transactions)
    return df

# =========================
# Paths
# =========================
phonepe_path = "Data/phonepe_statement.pdf"
gpay_path = "Data/gpay_statement.pdf"

# Parse PDFs
phonepe_df = parse_phonepe(phonepe_path)
gpay_df = parse_gpay(gpay_path)

# Display results
print("=== PhonePe DataFrame Preview ===")
print(phonepe_df.head(20))
print("\n=== GPay DataFrame Preview ===")
print(gpay_df.head(20))

# Optional: Save CSVs with timestamp
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
phonepe_df.to_csv(f"Data/phonepe_{timestamp}.csv", index=False)
gpay_df.to_csv(f"Data/gpay_{timestamp}.csv", index=False)
print("\nCSV files created successfully!")

