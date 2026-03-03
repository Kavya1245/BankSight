import pandas as pd
import json
import os
import re
from datetime import datetime


RAW_DIR     = "data/raw"
CLEANED_DIR = "data/cleaned"
os.makedirs(CLEANED_DIR, exist_ok=True)


def save_csv(df, filename):
    path = os.path.join(CLEANED_DIR, filename)
    try:
        df.to_csv(path, index=False, mode="w")
        print(f"  ✅ Saved  -> {path}  ({len(df)} rows)")
    except PermissionError:
        print(f"  ❌ Cannot write to {path}")
        print("     ➜ Please close the file if it is open in Excel or VS Code")


def load_csv(filename):
    path = os.path.join(RAW_DIR, filename)
    df = pd.read_csv(path)
    print(f"\n📂 Loaded {filename}  ({len(df)} rows, {len(df.columns)} cols)")
    return df


def load_json(filename):
    path = os.path.join(RAW_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    try:
        data = json.loads(content)
        df = pd.DataFrame(data if isinstance(data, list) else [data])
    except json.JSONDecodeError:
        try:
            records = [json.loads(line) for line in content.splitlines() if line.strip()]
            df = pd.DataFrame(records)
        except json.JSONDecodeError:
            fixed = "[" + content.replace("}\n{", "},{").replace("}\r\n{", "},{") + "]"
            data = json.loads(fixed)
            df = pd.DataFrame(data)
    print(f"\n📂 Loaded {filename}  ({len(df)} rows, {len(df.columns)} cols)")
    return df


def report(df, name):
    total_dups = df.duplicated().sum()
    missing = {}
    for col in df.columns:
        null_cnt = int(df[col].isnull().sum())
        if df[col].dtype == object:
            empty_cnt = int((df[col].fillna("").astype(str).str.strip() == "").sum()) - null_cnt
            empty_cnt = max(empty_cnt, 0)
        else:
            empty_cnt = 0
        total = null_cnt + empty_cnt
        if total > 0:
            missing[col] = {"null": null_cnt, "empty": empty_cnt, "total": total}
    total_missing = sum(v["total"] for v in missing.values())
    print(f"  🔍 {name} -- total missing: {total_missing}  |  duplicates: {total_dups}")
    if missing:
        for col, info in missing.items():
            detail = f"null={info['null']}, empty_string={info['empty']}"
            print(f"       ⚠️  {col:<35} : {info['total']} missing  ({detail})")
    else:
        print(f"       ✅ No missing values in any column")


def safe_fillna(df):
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Unknown")
    for col in df.select_dtypes(include=["float64", "int64"]).columns:
        df[col] = df[col].fillna(0)
    return df


def clean_customers():
    df = load_csv("customers.csv")
    report(df, "before")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df.drop_duplicates(subset=["customer_id"], keep="first", inplace=True)
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())
    if "gender" in df.columns:
        df["gender"] = df["gender"].str.upper().str.strip()
        df["gender"] = df["gender"].apply(
            lambda v: "M" if v in ("M", "MALE") else
                      "F" if v in ("F", "FEMALE") else "Other"
        )
    if "age" in df.columns:
        df["age"] = pd.to_numeric(df["age"], errors="coerce")
        df = df[df["age"].between(18, 100)]
    if "join_date" in df.columns:
        df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
        df["join_date"] = df["join_date"].dt.strftime("%Y-%m-%d")
    for col in ("city", "account_type"):
        if col in df.columns:
            df[col] = df[col].str.title()
    df = safe_fillna(df)
    report(df, "after ")
    save_csv(df, "customers_cleaned.csv")


def clean_accounts():
    df = load_csv("accounts.csv")
    report(df, "before")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df.drop_duplicates(subset=["customer_id"], keep="first", inplace=True)
    if "account_balance" in df.columns:
        df["account_balance"] = pd.to_numeric(df["account_balance"], errors="coerce")
        df = df[df["account_balance"] >= 0]
    if "last_updated" in df.columns:
        df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce")
        df["last_updated"] = df["last_updated"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["account_balance"] = df["account_balance"].fillna(0.0)
    df = safe_fillna(df)
    report(df, "after ")
    save_csv(df, "accounts_cleaned.csv")


def clean_transactions():
    df = load_csv("transactions.csv")
    report(df, "before")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df.drop_duplicates(subset=["txn_id"], keep="first", inplace=True)
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df = df[df["amount"] > 0]
    if "txn_time" in df.columns:
        df["txn_time"] = pd.to_datetime(df["txn_time"], errors="coerce")
        df["txn_time"] = df["txn_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    for col in ("status", "txn_type"):
        if col in df.columns:
            df[col] = df[col].str.strip().str.title()
    df = safe_fillna(df)
    report(df, "after ")
    save_csv(df, "transactions_cleaned.csv")


def clean_loans():
    json_path = os.path.join(RAW_DIR, "loans.json")
    csv_path  = os.path.join(RAW_DIR, "loans.csv")
    if os.path.exists(json_path):
        df = load_json("loans.json")
    elif os.path.exists(csv_path):
        df = load_csv("loans.csv")
    else:
        print("⚠️  loans file not found -- skipping")
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
        df["loan_type"] = df["loan_type"].str.strip().str.title()
    df = safe_fillna(df)
    report(df, "after ")
    save_csv(df, "loans_cleaned.csv")


def clean_credit_cards():
    json_path = os.path.join(RAW_DIR, "credit_cards.json")
    if not os.path.exists(json_path):
        print("⚠️  credit_cards.json not found -- skipping")
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
    if "card_number" in df.columns:
        df["card_number"] = df["card_number"].astype(str).apply(
            lambda v: "**** **** **** " + re.sub(r"\D", "", v)[-4:]
            if len(re.sub(r"\D", "", v)) >= 4 else "****"
        )
    df = safe_fillna(df)
    report(df, "after ")
    save_csv(df, "credit_cards_cleaned.csv")


def clean_branches():
    json_path = os.path.join(RAW_DIR, "branches.json")
    csv_path  = os.path.join(RAW_DIR, "branches.csv")
    if os.path.exists(json_path):
        df = load_json("branches.json")
    elif os.path.exists(csv_path):
        df = load_csv("branches.csv")
    else:
        print("⚠️  branches file not found -- skipping")
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
    if "performance_rating" in df.columns:
        df["performance_rating"] = df["performance_rating"].clip(1, 5)
    for str_col in ("branch_name", "city", "manager_name"):
        if str_col in df.columns:
            df[str_col] = df[str_col].str.strip().str.title()
    df = safe_fillna(df)
    report(df, "after ")
    save_csv(df, "branches_cleaned.csv")


def clean_support_tickets():
    json_path = os.path.join(RAW_DIR, "support_tickets.json")
    csv_path  = os.path.join(RAW_DIR, "support_tickets.csv")
    if os.path.exists(json_path):
        df = load_json("support_tickets.json")
    elif os.path.exists(csv_path):
        df = load_csv("support_tickets.csv")
    else:
        print("⚠️  support_tickets file not found -- skipping")
        return

    # Standardise column names first
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df.drop_duplicates(subset=["ticket_id"], keep="first", inplace=True)

    # Convert empty strings to NaN so report() counts them as missing
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].replace("", pd.NA)

    # loan_id comes as float when nulls exist in JSON — convert to numeric first
    if "loan_id" in df.columns:
        df["loan_id"] = pd.to_numeric(df["loan_id"], errors="coerce")

    # Show before report with accurate null counts
    report(df, "before")

    # loan_id: missing → 0  (means no loan is linked to this ticket)
    if "loan_id" in df.columns:
        df["loan_id"] = df["loan_id"].fillna(0).astype(int)

    # date_closed: missing → 'Not Closed'  (ticket is still open/unresolved)
    if "date_closed" in df.columns:
        df["date_closed"] = df["date_closed"].fillna("Not Closed")

    # Format date_opened
    if "date_opened" in df.columns:
        df["date_opened"] = pd.to_datetime(df["date_opened"], errors="coerce")
        df["date_opened"] = df["date_opened"].dt.strftime("%Y-%m-%d")

    # Format date_closed only for rows with actual dates (skip 'Not Closed')
    if "date_closed" in df.columns:
        mask = df["date_closed"] != "Not Closed"
        df.loc[mask, "date_closed"] = (
            pd.to_datetime(df.loc[mask, "date_closed"], errors="coerce")
            .dt.strftime("%Y-%m-%d")
        )

    # Compute resolution days (0 for open tickets)
    if "date_opened" in df.columns and "date_closed" in df.columns:
        df["resolution_days"] = (
            pd.to_datetime(df["date_closed"], errors="coerce") -
            pd.to_datetime(df["date_opened"], errors="coerce")
        ).dt.days
        df["resolution_days"] = (
            df["resolution_days"].clip(lower=0).fillna(0).astype(int)
        )

    if "customer_rating" in df.columns:
        df["customer_rating"] = pd.to_numeric(df["customer_rating"], errors="coerce")
        df["customer_rating"] = df["customer_rating"].clip(1, 5).fillna(3).astype(int)

    for str_col in ("priority", "status", "issue_category", "channel"):
        if str_col in df.columns:
            df[str_col] = df[str_col].str.strip().str.title()

    df = safe_fillna(df)
    report(df, "after ")
    save_csv(df, "support_tickets_cleaned.csv")


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("   BankSight -- Data Cleaning Pipeline")
    print("=" * 55)
    clean_customers()
    clean_accounts()
    clean_transactions()
    clean_loans()
    clean_credit_cards()
    clean_branches()
    clean_support_tickets()
    print("\n" + "=" * 55)
    print("   ✅ All datasets cleaned successfully!")
    print("=" * 55 + "\n")