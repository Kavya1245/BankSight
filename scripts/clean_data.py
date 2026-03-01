import pandas as pd
import json
import os
import re
from datetime import datetime

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
RAW_DIR     = "data/raw"
CLEANED_DIR = "data/cleaned"
os.makedirs(CLEANED_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────

def save_csv(df: pd.DataFrame, filename: str):
    path = os.path.join(CLEANED_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  ✅ Saved  → {path}  ({len(df)} rows)")

def load_csv(filename: str) -> pd.DataFrame:
    path = os.path.join(RAW_DIR, filename)
    df = pd.read_csv(path)
    print(f"\n📂 Loaded {filename}  ({len(df)} rows, {len(df.columns)} cols)")
    return df

def load_json(filename: str) -> pd.DataFrame:
    path = os.path.join(RAW_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # Try standard JSON first
    try:
        data = json.loads(content)
        df = pd.DataFrame(data if isinstance(data, list) else [data])
    except json.JSONDecodeError:
        # Try newline-delimited JSON (one object per line)
        try:
            records = [json.loads(line) for line in content.splitlines() if line.strip()]
            df = pd.DataFrame(records)
        except json.JSONDecodeError:
            # Try wrapping multiple objects as an array
            fixed = "[" + content.replace("}\n{", "},{").replace("}\r\n{", "},{") + "]"
            data = json.loads(fixed)
            df = pd.DataFrame(data)

    print(f"\n📂 Loaded {filename}  ({len(df)} rows, {len(df.columns)} cols)")
    return df

def report(df: pd.DataFrame, name: str):
    print(f"  🔍 {name} — nulls: {df.isnull().sum().sum()}  |  "
          f"duplicates: {df.duplicated().sum()}")

# ─────────────────────────────────────────────
# 1. CUSTOMERS  (customers.csv)
# ─────────────────────────────────────────────
def clean_customers():
    df = load_csv("customers.csv")
    report(df, "before")

    # Standardise column names to snake_case
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Drop duplicate customer IDs (keep first)
    df.drop_duplicates(subset=["customer_id"], keep="first", inplace=True)

    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())

    # Normalise gender → 'M' / 'F' / 'Other'
    if "gender" in df.columns:
        df["gender"] = df["gender"].str.upper().str.strip()
        df["gender"] = df["gender"].apply(
            lambda v: "M" if v in ("M", "MALE") else
                      "F" if v in ("F", "FEMALE") else "Other"
        )

    # Age: drop rows where age is missing or unrealistic
    if "age" in df.columns:
        df["age"] = pd.to_numeric(df["age"], errors="coerce")
        df = df[df["age"].between(18, 100)]

    # Parse join_date
    if "join_date" in df.columns:
        df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
        df["join_date"] = df["join_date"].dt.strftime("%Y-%m-%d")

    # Title-case city & account_type
    for col in ("city", "account_type"):
        if col in df.columns:
            df[col] = df[col].str.title()

    # Fill remaining nulls
    df.fillna("Unknown", inplace=True)

    report(df, "after ")
    save_csv(df, "customers_cleaned.csv")

# ─────────────────────────────────────────────
# 2. ACCOUNTS  (accounts.csv)
# ─────────────────────────────────────────────
def clean_accounts():
    df = load_csv("accounts.csv")
    report(df, "before")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df.drop_duplicates(subset=["customer_id"], keep="first", inplace=True)

    # account_balance must be numeric and >= 0
    if "account_balance" in df.columns:
        df["account_balance"] = pd.to_numeric(df["account_balance"], errors="coerce")
        df = df[df["account_balance"] >= 0]

    # Parse last_updated
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
        df["last_updated"] = df["last_updated"].dt.strftime("%Y-%m-%d %H:%M:%S")

    df.fillna({"account_balance": 0.0}, inplace=True)

    report(df, "after ")
    save_csv(df, "accounts_cleaned.csv")

# ─────────────────────────────────────────────
# 3. TRANSACTIONS  (transactions.csv)
# ─────────────────────────────────────────────
def clean_transactions():
    df = load_csv("transactions.csv")
    report(df, "before")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df.drop_duplicates(subset=["txn_id"], keep="first", inplace=True)

    # Amount must be positive
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df = df[df["amount"] > 0]

    # Parse txn_time
    if "txn_time" in df.columns:
        df["txn_time"] = pd.to_datetime(df["txn_time"], errors="coerce")
        df["txn_time"] = df["txn_time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Normalise status & txn_type to title case
    for col in ("status", "txn_type"):
        if col in df.columns:
            df[col] = df[col].str.strip().str.title()

    df.fillna("Unknown", inplace=True)

    report(df, "after ")
    save_csv(df, "transactions_cleaned.csv")

# ─────────────────────────────────────────────
# 4. LOANS  (loans.json or loans.csv)
# ─────────────────────────────────────────────
def clean_loans():
    json_path = os.path.join(RAW_DIR, "loans.json")
    csv_path  = os.path.join(RAW_DIR, "loans.csv")

    if os.path.exists(json_path):
        df = load_json("loans.json")
    elif os.path.exists(csv_path):
        df = load_csv("loans.csv")
    else:
        print("⚠️  loans file not found — skipping")
        return

    report(df, "before")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df.drop_duplicates(subset=["loan_id"], keep="first", inplace=True)

    for num_col in ("loan_amount", "interest_rate", "loan_term_months"):
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

    for date_col in ("start_date", "end_date"):
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df[date_col] = df[date_col].dt.strftime("%Y-%m-%d")

    if "loan_status" in df.columns:
        df["loan_status"] = df["loan_status"].str.strip().str.title()
    if "loan_type" in df.columns:
        df["loan_type"]   = df["loan_type"].str.strip().str.title()

    df.fillna("Unknown", inplace=True)

    report(df, "after ")
    save_csv(df, "loans_cleaned.csv")

# ─────────────────────────────────────────────
# 5. CREDIT CARDS  (credit_cards.json)
# ─────────────────────────────────────────────
def clean_credit_cards():
    json_path = os.path.join(RAW_DIR, "credit_cards.json")
    if not os.path.exists(json_path):
        print("⚠️  credit_cards.json not found — skipping")
        return

    df = load_json("credit_cards.json")
    report(df, "before")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df.drop_duplicates(subset=["card_id"], keep="first", inplace=True)

    for num_col in ("credit_limit", "current_balance"):
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

    for date_col in ("issued_date", "expiry_date"):
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df[date_col] = df[date_col].dt.strftime("%Y-%m-%d")

    for str_col in ("card_type", "card_network", "status"):
        if str_col in df.columns:
            df[str_col] = df[str_col].str.strip().str.title()

    # Mask card number — keep last 4 digits only
    if "card_number" in df.columns:
        df["card_number"] = df["card_number"].astype(str).apply(
            lambda v: "**** **** **** " + re.sub(r"\D", "", v)[-4:]
            if len(re.sub(r"\D", "", v)) >= 4 else "****"
        )

    df.fillna("Unknown", inplace=True)

    report(df, "after ")
    save_csv(df, "credit_cards_cleaned.csv")

# ─────────────────────────────────────────────
# 6. BRANCHES  (branches.json or branches.csv)
# ─────────────────────────────────────────────
def clean_branches():
    json_path = os.path.join(RAW_DIR, "branches.json")
    csv_path  = os.path.join(RAW_DIR, "branches.csv")

    if os.path.exists(json_path):
        df = load_json("branches.json")
    elif os.path.exists(csv_path):
        df = load_csv("branches.csv")
    else:
        print("⚠️  branches file not found — skipping")
        return

    report(df, "before")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df.drop_duplicates(subset=["branch_id"], keep="first", inplace=True)

    for num_col in ("total_employees", "branch_revenue", "performance_rating"):
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

    if "opening_date" in df.columns:
        df["opening_date"] = pd.to_datetime(df["opening_date"], errors="coerce")
        df["opening_date"] = df["opening_date"].dt.strftime("%Y-%m-%d")

    # Rating must be 1–5
    if "performance_rating" in df.columns:
        df["performance_rating"] = df["performance_rating"].clip(1, 5)

    for str_col in ("branch_name", "city", "manager_name"):
        if str_col in df.columns:
            df[str_col] = df[str_col].str.strip().str.title()

    df.fillna("Unknown", inplace=True)

    report(df, "after ")
    save_csv(df, "branches_cleaned.csv")

# ─────────────────────────────────────────────
# 7. SUPPORT TICKETS  (support_tickets.json or .csv)
# ─────────────────────────────────────────────
def clean_support_tickets():
    json_path = os.path.join(RAW_DIR, "support_tickets.json")
    csv_path  = os.path.join(RAW_DIR, "support_tickets.csv")

    if os.path.exists(json_path):
        df = load_json("support_tickets.json")
    elif os.path.exists(csv_path):
        df = load_csv("support_tickets.csv")
    else:
        print("⚠️  support_tickets file not found — skipping")
        return

    report(df, "before")

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df.drop_duplicates(subset=["ticket_id"], keep="first", inplace=True)

    for date_col in ("date_opened", "date_closed"):
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df[date_col] = df[date_col].dt.strftime("%Y-%m-%d")

    # Compute resolution days
    if "date_opened" in df.columns and "date_closed" in df.columns:
        df["resolution_days"] = (
            pd.to_datetime(df["date_closed"], errors="coerce") -
            pd.to_datetime(df["date_opened"], errors="coerce")
        ).dt.days
        df["resolution_days"] = df["resolution_days"].clip(lower=0)

    if "customer_rating" in df.columns:
        df["customer_rating"] = pd.to_numeric(df["customer_rating"], errors="coerce")
        df["customer_rating"] = df["customer_rating"].clip(1, 5)

    for str_col in ("priority", "status", "issue_category", "channel"):
        if str_col in df.columns:
            df[str_col] = df[str_col].str.strip().str.title()

    df.fillna("Unknown", inplace=True)

    report(df, "after ")
    save_csv(df, "support_tickets_cleaned.csv")

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  BankSight — Data Cleaning Pipeline")
    print("=" * 60)

    clean_customers()
    clean_accounts()
    clean_transactions()
    clean_loans()
    clean_credit_cards()
    clean_branches()
    clean_support_tickets()

    print("\n" + "=" * 60)
    print("  ✅ All datasets cleaned! Files saved to data/cleaned/")
    print("=" * 60)