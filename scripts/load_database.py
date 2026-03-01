import pandas as pd
import sqlite3
import os

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
CLEANED_DIR = "data/cleaned"
DB_PATH     = "database/banksight.db"

os.makedirs("database", exist_ok=True)

# ─────────────────────────────────────────────
# Connect to SQLite
# ─────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("  BankSight — Database Creation & Loading")
print("=" * 60)

# ─────────────────────────────────────────────
# Enable foreign keys
# ─────────────────────────────────────────────
cursor.execute("PRAGMA foreign_keys = ON;")

# ─────────────────────────────────────────────
# Drop existing tables (clean slate)
# ─────────────────────────────────────────────
TABLES = [
    "support_tickets", "credit_cards", "loans",
    "transactions", "accounts", "branches", "customers"
]
for t in TABLES:
    cursor.execute(f"DROP TABLE IF EXISTS {t};")
conn.commit()
print("\n🗑️  Dropped existing tables (if any)")

# ─────────────────────────────────────────────
# CREATE TABLES
# ─────────────────────────────────────────────

cursor.executescript("""

-- 1. CUSTOMERS
CREATE TABLE IF NOT EXISTS customers (
    customer_id   TEXT PRIMARY KEY,
    name          TEXT,
    gender        TEXT,
    age           INTEGER,
    city          TEXT,
    account_type  TEXT,
    join_date     TEXT
);

-- 2. ACCOUNTS
CREATE TABLE IF NOT EXISTS accounts (
    customer_id      TEXT PRIMARY KEY,
    account_balance  REAL,
    last_updated     TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 3. TRANSACTIONS
CREATE TABLE IF NOT EXISTS transactions (
    txn_id       TEXT PRIMARY KEY,
    customer_id  TEXT,
    txn_type     TEXT,
    amount       REAL,
    txn_time     TEXT,
    status       TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 4. LOANS
CREATE TABLE IF NOT EXISTS loans (
    loan_id          INTEGER PRIMARY KEY,
    customer_id      TEXT,
    account_id       TEXT,
    branch           TEXT,
    loan_type        TEXT,
    loan_amount      REAL,
    interest_rate    REAL,
    loan_term_months INTEGER,
    start_date       TEXT,
    end_date         TEXT,
    loan_status      TEXT
);

-- 5. CREDIT CARDS
CREATE TABLE IF NOT EXISTS credit_cards (
    card_id          INTEGER PRIMARY KEY,
    customer_id      TEXT,
    account_id       TEXT,
    branch           TEXT,
    card_number      TEXT,
    card_type        TEXT,
    card_network     TEXT,
    credit_limit     REAL,
    current_balance  REAL,
    issued_date      TEXT,
    expiry_date      TEXT,
    status           TEXT
);

-- 6. BRANCHES
CREATE TABLE IF NOT EXISTS branches (
    branch_id          INTEGER PRIMARY KEY,
    branch_name        TEXT,
    city               TEXT,
    manager_name       TEXT,
    total_employees    INTEGER,
    branch_revenue     REAL,
    opening_date       TEXT,
    performance_rating INTEGER
);

-- 7. SUPPORT TICKETS
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id           TEXT PRIMARY KEY,
    customer_id         TEXT,
    account_id          TEXT,
    loan_id             TEXT,
    branch_name         TEXT,
    issue_category      TEXT,
    description         TEXT,
    date_opened         TEXT,
    date_closed         TEXT,
    priority            TEXT,
    status              TEXT,
    resolution_remarks  TEXT,
    support_agent       TEXT,
    channel             TEXT,
    customer_rating     INTEGER,
    resolution_days     INTEGER
);

""")
conn.commit()
print("✅ All tables created successfully\n")

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────

def load_table(csv_file: str, table_name: str, required_cols: list = None):
    path = os.path.join(CLEANED_DIR, csv_file)
    if not os.path.exists(path):
        print(f"  ⚠️  {csv_file} not found — skipping {table_name}")
        return

    df = pd.read_csv(path)

    # Lowercase column names for consistency
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Keep only columns that exist in the DB schema
    if required_cols:
        df = df[[c for c in required_cols if c in df.columns]]

    df.to_sql(table_name, conn, if_exists="append", index=False)
    print(f"  📥 Loaded {table_name:<20} ← {csv_file}  ({len(df)} rows)")


print("Loading cleaned data into SQLite...\n")

load_table("customers_cleaned.csv", "customers", [
    "customer_id", "name", "gender", "age", "city", "account_type", "join_date"
])

load_table("accounts_cleaned.csv", "accounts", [
    "customer_id", "account_balance", "last_updated"
])

load_table("transactions_cleaned.csv", "transactions", [
    "txn_id", "customer_id", "txn_type", "amount", "txn_time", "status"
])

load_table("loans_cleaned.csv", "loans", [
    "loan_id", "customer_id", "account_id", "branch", "loan_type",
    "loan_amount", "interest_rate", "loan_term_months",
    "start_date", "end_date", "loan_status"
])

load_table("credit_cards_cleaned.csv", "credit_cards", [
    "card_id", "customer_id", "account_id", "branch", "card_number",
    "card_type", "card_network", "credit_limit", "current_balance",
    "issued_date", "expiry_date", "status"
])

load_table("branches_cleaned.csv", "branches", [
    "branch_id", "branch_name", "city", "manager_name",
    "total_employees", "branch_revenue", "opening_date", "performance_rating"
])

load_table("support_tickets_cleaned.csv", "support_tickets", [
    "ticket_id", "customer_id", "account_id", "loan_id", "branch_name",
    "issue_category", "description", "date_opened", "date_closed",
    "priority", "status", "resolution_remarks", "support_agent",
    "channel", "customer_rating", "resolution_days"
])

conn.commit()

# ─────────────────────────────────────────────
# VERIFY ROW COUNTS
# ─────────────────────────────────────────────
print("\n" + "─" * 60)
print("  📊 Row Count Verification")
print("─" * 60)

for table in ["customers", "accounts", "transactions", "loans",
              "credit_cards", "branches", "support_tickets"]:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<25} → {count} rows")

conn.close()

print("\n" + "=" * 60)
print(f"  ✅ Database ready at: {DB_PATH}")
print("=" * 60)