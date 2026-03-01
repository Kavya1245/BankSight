import sqlite3
import pandas as pd

DB_PATH = "database/banksight.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ─────────────────────────────────────────────────────────────────
# CATEGORY 1 — CUSTOMER & ACCOUNT ANALYSIS
# ─────────────────────────────────────────────────────────────────

Q1 = {
    "title": "Q1 — Customers per City with Average Account Balance",
    "description": "How many customers exist per city, and what is their average account balance?",
    "sql": """
        SELECT
            c.city,
            COUNT(c.customer_id)            AS total_customers,
            ROUND(AVG(a.account_balance), 2) AS avg_balance
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        GROUP BY c.city
        ORDER BY total_customers DESC;
    """
}

Q2 = {
    "title": "Q2 — Account Type with Highest Total Balance",
    "description": "Which account type (Savings, Current, etc.) holds the highest total balance?",
    "sql": """
        SELECT
            c.account_type,
            ROUND(SUM(a.account_balance), 2)  AS total_balance,
            ROUND(AVG(a.account_balance), 2)  AS avg_balance,
            COUNT(c.customer_id)              AS total_customers
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        GROUP BY c.account_type
        ORDER BY total_balance DESC;
    """
}

Q3 = {
    "title": "Q3 — Top 10 Customers by Account Balance",
    "description": "Who are the top 10 customers by total account balance?",
    "sql": """
        SELECT
            c.customer_id,
            c.name,
            c.city,
            c.account_type,
            ROUND(a.account_balance, 2) AS account_balance
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        ORDER BY a.account_balance DESC
        LIMIT 10;
    """
}

Q4 = {
    "title": "Q4 — Customers Who Joined in 2023 with Balance > ₹1,00,000",
    "description": "Which customers opened accounts in 2023 with a balance above ₹1,00,000?",
    "sql": """
        SELECT
            c.customer_id,
            c.name,
            c.city,
            c.account_type,
            c.join_date,
            ROUND(a.account_balance, 2) AS account_balance
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        WHERE strftime('%Y', c.join_date) = '2023'
          AND a.account_balance > 100000
        ORDER BY a.account_balance DESC;
    """
}

# ─────────────────────────────────────────────────────────────────
# CATEGORY 2 — TRANSACTION BEHAVIOR
# ─────────────────────────────────────────────────────────────────

Q5 = {
    "title": "Q5 — Total Transaction Volume by Type",
    "description": "What is the total transaction volume (sum of amounts) by transaction type?",
    "sql": """
        SELECT
            txn_type                      AS transaction_type,
            COUNT(*)                      AS total_transactions,
            ROUND(SUM(amount), 2)         AS total_transaction_volume,
            ROUND(AVG(amount), 2)         AS avg_amount
        FROM transactions
        GROUP BY txn_type
        ORDER BY total_transaction_volume DESC;
    """
}

Q6 = {
    "title": "Q6 — Failed Transactions by Type",
    "description": "How many failed transactions occurred for each transaction type?",
    "sql": """
        SELECT
            txn_type                      AS transaction_type,
            COUNT(*)                      AS failed_transactions,
            ROUND(SUM(amount), 2)         AS total_failed_amount
        FROM transactions
        WHERE LOWER(status) = 'failed'
        GROUP BY txn_type
        ORDER BY failed_transactions DESC;
    """
}

Q7 = {
    "title": "Q7 — Total Number of Transactions per Type",
    "description": "What is the total number of transactions per transaction type?",
    "sql": """
        SELECT
            txn_type                      AS transaction_type,
            COUNT(*)                      AS total_transactions,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM transactions), 2) AS pct_share
        FROM transactions
        GROUP BY txn_type
        ORDER BY total_transactions DESC;
    """
}

Q8 = {
    "title": "Q8 — Accounts with 5+ High-Value Transactions (> ₹20,000)",
    "description": "Which accounts have 5 or more high-value transactions above ₹20,000?",
    "sql": """
        SELECT
            t.customer_id,
            c.name,
            c.account_type,
            COUNT(*)                AS high_value_count,
            ROUND(SUM(t.amount), 2) AS total_high_value
        FROM transactions t
        JOIN customers c ON t.customer_id = c.customer_id
        WHERE t.amount > 20000
        GROUP BY t.customer_id
        HAVING COUNT(*) >= 5
        ORDER BY high_value_count DESC;
    """
}

# ─────────────────────────────────────────────────────────────────
# CATEGORY 3 — LOAN INSIGHTS
# ─────────────────────────────────────────────────────────────────

Q9 = {
    "title": "Q9 — Average Loan Amount & Interest Rate by Loan Type",
    "description": "What is the average loan amount and interest rate by loan type?",
    "sql": """
        SELECT
            loan_type,
            COUNT(*)                          AS total_loans,
            ROUND(AVG(loan_amount), 2)        AS avg_loan_amount,
            ROUND(AVG(interest_rate), 2)      AS avg_interest_rate,
            ROUND(SUM(loan_amount), 2)        AS total_disbursed
        FROM loans
        GROUP BY loan_type
        ORDER BY avg_loan_amount DESC;
    """
}

Q10 = {
    "title": "Q10 — Customers with More Than One Active/Approved Loan",
    "description": "Which customers currently hold more than one active or approved loan?",
    "sql": """
        SELECT
            l.customer_id,
            COUNT(l.loan_id)                    AS no_of_active_loans,
            GROUP_CONCAT(l.loan_type, ' | ')    AS loan_types_held,
            ROUND(SUM(l.loan_amount), 2)        AS total_loan_amount,
            ROUND(AVG(l.interest_rate), 2)      AS avg_interest_rate
        FROM loans l
        WHERE LOWER(l.loan_status) IN ('active', 'approved')
        GROUP BY l.customer_id
        HAVING COUNT(l.loan_id) > 1
        ORDER BY no_of_active_loans DESC, total_loan_amount DESC;
    """
}

Q11 = {
    "title": "Q11 — Top 5 Customers with Highest Outstanding Loan Amounts",
    "description": "Who are the top 5 customers with the highest outstanding (non-closed) loan amounts?",
    "sql": """
        SELECT
            l.customer_id,
            COUNT(l.loan_id)                        AS number_of_loans,
            GROUP_CONCAT(l.loan_type, ' | ')        AS loan_types,
            GROUP_CONCAT(DISTINCT l.loan_status)    AS loan_statuses,
            ROUND(SUM(l.loan_amount), 2)            AS total_outstanding_amount
        FROM loans l
        WHERE LOWER(l.loan_status) != 'closed'
        GROUP BY l.customer_id
        ORDER BY total_outstanding_amount DESC
        LIMIT 5;
    """
}

# ─────────────────────────────────────────────────────────────────
# CATEGORY 4 — BRANCH & PERFORMANCE
# ─────────────────────────────────────────────────────────────────

Q12 = {
    "title": "Q12 — Average Loan Amount per Branch",
    "description": "What is the average loan amount per branch?",
    "sql": """
        SELECT
            l.branch,
            COUNT(l.loan_id)              AS total_loans,
            ROUND(AVG(l.loan_amount), 2)  AS avg_loan_amount,
            ROUND(SUM(l.loan_amount), 2)  AS total_loan_amount
        FROM loans l
        GROUP BY l.branch
        ORDER BY avg_loan_amount DESC;
    """
}

Q13 = {
    "title": "Q13 — Customer Distribution by Age Group",
    "description": "How many customers exist in each age group (18–25, 26–35, 36–45, 46–60, 60+)?",
    "sql": """
        SELECT
            CASE
                WHEN age BETWEEN 18 AND 25 THEN '18–25'
                WHEN age BETWEEN 26 AND 35 THEN '26–35'
                WHEN age BETWEEN 36 AND 45 THEN '36–45'
                WHEN age BETWEEN 46 AND 60 THEN '46–60'
                ELSE '60+'
            END AS age_group,
            COUNT(*) AS total_customers,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 2) AS pct_share
        FROM customers
        GROUP BY age_group
        ORDER BY
            CASE age_group
                WHEN '18–25' THEN 1
                WHEN '26–35' THEN 2
                WHEN '36–45' THEN 3
                WHEN '46–60' THEN 4
                ELSE 5
            END;
    """
}

# ─────────────────────────────────────────────────────────────────
# CATEGORY 5 — SUPPORT TICKETS & CUSTOMER EXPERIENCE
# ─────────────────────────────────────────────────────────────────

Q14 = {
    "title": "Q14 — Issue Categories with Longest Average Resolution Time",
    "description": "Which issue categories have the longest average resolution time (in days)?",
    "sql": """
        SELECT
            issue_category,
            COUNT(*)                              AS total_tickets,
            ROUND(AVG(resolution_days), 1)        AS avg_resolution_days,
            MAX(resolution_days)                  AS max_resolution_days,
            ROUND(AVG(customer_rating), 2)        AS avg_customer_rating
        FROM support_tickets
        WHERE resolution_days IS NOT NULL
          AND resolution_days > 0
        GROUP BY issue_category
        ORDER BY avg_resolution_days DESC;
    """
}

Q15 = {
    "title": "Q15 — Top Support Agents Resolving Critical Tickets (Rating ≥ 4)",
    "description": "Which support agents have resolved the most critical tickets with high customer ratings (≥4)?",
    "sql": """
        SELECT
            support_agent,
            COUNT(*)                       AS resolved_critical,
            ROUND(AVG(customer_rating), 2) AS avg_rating,
            ROUND(AVG(resolution_days), 1) AS avg_resolution_days
        FROM support_tickets
        WHERE LOWER(priority) = 'critical'
          AND customer_rating >= 4
          AND LOWER(status) IN ('resolved', 'closed')
        GROUP BY support_agent
        ORDER BY resolved_critical DESC
        LIMIT 10;
    """
}

# ─────────────────────────────────────────────────────────────────
# ALL QUERIES REGISTRY (used by Streamlit dropdown)
# ─────────────────────────────────────────────────────────────────

ALL_QUERIES = [Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8,
               Q9, Q10, Q11, Q12, Q13, Q14, Q15]


# ─────────────────────────────────────────────────────────────────
# RUNNER — test all queries from command line
# ─────────────────────────────────────────────────────────────────

def run_query(query_dict: dict) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(query_dict["sql"], conn)
    conn.close()
    return df


if __name__ == "__main__":
    print("=" * 60)
    print("  BankSight — Running All 15 Analytical Queries")
    print("=" * 60)

    conn = get_connection()
    errors = []

    for q in ALL_QUERIES:
        print(f"\n{'─' * 60}")
        print(f"  {q['title']}")
        print(f"  {q['description']}")
        print(f"{'─' * 60}")
        try:
            df = pd.read_sql_query(q["sql"], conn)
            if df.empty:
                print("  ⚠️  No results returned.")
            else:
                print(df.to_string(index=False))
                print(f"\n  ✅ {len(df)} row(s) returned")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            errors.append((q["title"], str(e)))

    conn.close()

    print("\n" + "=" * 60)
    if errors:
        print(f"  ⚠️  {len(errors)} query/queries had errors:")
        for title, err in errors:
            print(f"    • {title}: {err}")
    else:
        print("  ✅ All 15 queries executed successfully!")
    print("=" * 60)