import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import random
import os

# BankSight - Complete Streamlit Application

st.set_page_config(
    page_title="BankSight Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #e0e0e0;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}
.big-title { font-size: 2.2rem; font-weight: 800; color: #1a3c5e; }
.sub-title { font-size: 1.1rem; color: #4a6fa5; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# DATABASE CONNECTION

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "database", "banksight.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def run_query(sql, params=None):
    try:
        conn = get_conn()
        sql = sql.replace("%s", "?")
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        conn.close()
        return pd.DataFrame(rows, columns=cols)
    except Exception as e:
        st.error(f"Query Error: {e}")
        return pd.DataFrame()

def run_action(sql, params=None):
    try:
        conn = get_conn()
        sql = sql.replace("%s", "?")
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        return False

def safe_val(sql, default=0):
    try:
        df = run_query(sql)
        if df.empty or df.iloc[0, 0] is None:
            return default
        return df.iloc[0, 0]
    except:
        return default

# SIDEBAR

st.sidebar.markdown("## 🏦 BankSight")
st.sidebar.markdown("*Transaction Intelligence Dashboard*")
st.sidebar.markdown("---")

page = st.sidebar.radio("📌 Navigate To", [
    "🏠 Introduction",
    "📊 View Tables",
    "🔍 Filter Data",
    "✏️ CRUD Operations",
    "💰 Credit / Debit Simulation",
    "🧠 Analytical Insights",
    "👩‍💻 About Creator"
])

st.sidebar.markdown("---")
st.sidebar.markdown("**Database:** `banksight.db` (SQLite)")
st.sidebar.markdown("**Stack:** Python · SQLite · Streamlit ")

# PAGE 1 — INTRODUCTION

if page == "🏠 Introduction":

    st.markdown("<div class='big-title'>🏦 BankSight: Transaction Intelligence Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>A comprehensive banking analytics platform — customer insights, fraud detection & branch performance.</div>", unsafe_allow_html=True)
    st.markdown("---")

    # Live metrics — safe so no crash if DB not ready
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        n1 = run_query("SELECT COUNT(*) as c FROM customers")
        st.metric("👥 Customers", f"{int(n1.iloc[0,0]) if not n1.empty else 0:,}")
    with c2:
        n2 = run_query("SELECT COUNT(*) as c FROM transactions")
        st.metric("💳 Transactions", f"{int(n2.iloc[0,0]) if not n2.empty else 0:,}")
    with c3:
        n3 = run_query("SELECT ROUND(SUM(account_balance)/10000000,2) as c FROM accounts")
        st.metric("💰 Total Balance", f"₹{n3.iloc[0,0] if not n3.empty else 0} Cr")
    with c4:
        n4 = run_query("SELECT COUNT(*) as c FROM loans WHERE loan_status != 'Closed'")
        st.metric("🏠 Active Loans", f"{int(n4.iloc[0,0]) if not n4.empty else 0:,}")
    with c5:
        n5 = run_query("SELECT COUNT(*) as c FROM support_tickets WHERE status NOT IN ('Resolved','Closed')")
        st.metric("🎫 Open Tickets", f"{int(n5.iloc[0,0]) if not n5.empty else 0:,}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📌 Problem Statement")
        st.markdown("""
        Banks process millions of transactions daily with critical needs to:
        - 🔍 Understand **customer behavior** and transaction patterns
        - 🚨 Detect **fraudulent** and anomalous transactions early
        - 🏢 Evaluate **branch performance** based on transactions
        - 📊 Provide **interactive exploration** of transaction data
        - ✏️ Enable **CRUD operations** on accounts and transactions
        """)

        st.subheader("🎯 Business Use Cases")
        st.markdown("""
        - Profile customer transaction behavior to tailor banking products
        - Identify high-risk transactions and accounts for fraud prevention
        - Branch performance evaluation based on transactions and accounts
        - Enable customers and bank officials to query transaction histories
        """)

        st.subheader("🛠️ Tech Stack")
        tech = pd.DataFrame({
            "Tool":    ["Python", "SQLite", "Streamlit", "Plotly", "Pandas"],
            "Purpose": ["Data processing & scripting", "Database storage & queries",
                        "Web dashboard", "Interactive charts", "Data manipulation"]
        })
        st.dataframe(tech, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("📁 Datasets Used")
        datasets = pd.DataFrame({
            "Dataset":     ["Customers", "Accounts", "Transactions", "Loans", "Credit Cards", "Branches", "Support Tickets"],
            "Records":     ["500", "500", "10,000", "553", "557", "520", "600"],
            "Format":      ["CSV", "CSV", "CSV", "JSON", "JSON", "JSON", "JSON"],
            "Description": [
                "Customer demographics",
                "Account balances",
                "All bank transactions",
                "Loan details",
                "Credit card info",
                "Branch information",
                "Support complaints"
            ]
        })
        st.dataframe(datasets, use_container_width=True, hide_index=True)

        st.subheader("📊 Transaction Overview")
        df1 = run_query("SELECT txn_type, COUNT(*) as count, ROUND(SUM(amount),2) as total FROM transactions GROUP BY txn_type ORDER BY total DESC")
        if not df1.empty:
            fig1 = px.bar(df1, x='txn_type', y='total', color='txn_type',
                          color_discrete_sequence=px.colors.qualitative.Set2,
                          title="Transaction Volume by Type",
                          labels={'txn_type': 'Type', 'total': 'Total Amount (₹)'})
            fig1.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 More Insights at a Glance")
    col1, col2, col3 = st.columns(3)

    with col1:
        df2 = run_query("SELECT account_type, COUNT(*) as count FROM customers GROUP BY account_type")
        if not df2.empty:
            fig2 = px.pie(df2, names='account_type', values='count',
                          title="Customers by Account Type",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)

    with col2:
        df3 = run_query("SELECT loan_type, COUNT(*) as count FROM loans GROUP BY loan_type")
        if not df3.empty:
            fig3 = px.pie(df3, names='loan_type', values='count',
                          title="Loans by Type",
                          color_discrete_sequence=px.colors.qualitative.Set3)
            fig3.update_layout(height=350)
            st.plotly_chart(fig3, use_container_width=True)

    with col3:
        df4 = run_query("SELECT status, COUNT(*) as count FROM support_tickets GROUP BY status")
        if not df4.empty:
            fig4 = px.pie(df4, names='status', values='count',
                          title="Support Ticket Status",
                          color_discrete_sequence=px.colors.qualitative.Bold)
            fig4.update_layout(height=350)
            st.plotly_chart(fig4, use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 2 — VIEW TABLES
# ══════════════════════════════════════════════
elif page == "📊 View Tables":

    st.title("📊 View Tables")
    st.markdown("Browse all 7 core datasets directly from the SQLite database.")
    st.markdown("---")

    TABLE_MAP = {
        "👥 Customers":       "customers",
        "💳 Accounts":        "accounts",
        "💸 Transactions":    "transactions",
        "🏢 Branches":        "branches",
        "🏠 Loans":           "loans",
        "🎫 Support Tickets": "support_tickets",
        "💳 Credit Cards":    "credit_cards"
    }

    col1, col2 = st.columns([2, 1])
    with col1:
        selected = st.selectbox("📂 Select Table", list(TABLE_MAP.keys()))
    with col2:
        limit = st.selectbox("🔢 Rows to Show", [10, 25, 50, 100, 200, "All"])

    table = TABLE_MAP[selected]

    if limit == "All":
        df = run_query(f"SELECT * FROM {table}")
    else:
        df = run_query(f"SELECT * FROM {table} LIMIT {limit}")

    total_rows = int(safe_val(f"SELECT COUNT(*) as c FROM {table}"))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Total Records", f"{total_rows:,}")
    c2.metric("📊 Columns",       len(df.columns))
    c3.metric("👁️ Showing Now",   len(df))
    c4.metric("📁 Table",         table)

    st.markdown("---")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download as CSV", csv, f"{table}.csv", "text/csv")
    with col2:
        st.info(f"💡 Showing {len(df)} of {total_rows} total records from `{table}` table.")


# ══════════════════════════════════════════════
# PAGE 3 — FILTER DATA
# ══════════════════════════════════════════════
elif page == "🔍 Filter Data":

    st.title("🔍 Filter Data")
    st.markdown("Select any dataset, choose columns to filter, and apply multiple filters simultaneously.")
    st.markdown("---")

    TABLE_MAP = {
        "👥 Customers":       "customers",
        "💳 Accounts":        "accounts",
        "💸 Transactions":    "transactions",
        "🏢 Branches":        "branches",
        "🏠 Loans":           "loans",
        "💳 Credit Cards":    "credit_cards",
        "🎫 Support Tickets": "support_tickets"
    }

    selected = st.selectbox("📂 Select Dataset to Filter", list(TABLE_MAP.keys()))
    table = TABLE_MAP[selected]
    df = run_query(f"SELECT * FROM {table}")

    if df.empty:
        st.warning("No data found.")
        st.stop()

    st.markdown(f"**Dataset:** `{table}` &nbsp;|&nbsp; **Total Records:** {len(df)}")
    st.markdown("---")

    all_cols = df.columns.tolist()
    selected_cols = st.multiselect(
        "🎯 Choose columns to filter on (select one or more):",
        all_cols,
        default=[]
    )

    filtered = df.copy()

    if selected_cols:
        st.markdown("### 🎛️ Apply Filters")
        cols_ui = st.columns(min(len(selected_cols), 3))

        for i, col in enumerate(selected_cols):
            with cols_ui[i % 3]:
                dtype = df[col].dtype

                if dtype in ['int64', 'float64']:
                    min_val = float(df[col].min())
                    max_val = float(df[col].max())
                    if min_val == max_val:
                        st.info(f"{col}: only value {min_val}")
                    else:
                        selected_range = st.slider(
                            f"📊 {col}", min_val, max_val, (min_val, max_val),
                            key=f"slider_{col}"
                        )
                        filtered = filtered[
                            (filtered[col] >= selected_range[0]) &
                            (filtered[col] <= selected_range[1])
                        ]

                elif 'date' in col.lower() or 'time' in col.lower():
                    unique_vals = ["All"] + sorted(df[col].astype(str).unique().tolist())
                    chosen = st.selectbox(f"📅 {col}", unique_vals, key=f"date_{col}")
                    if chosen != "All":
                        filtered = filtered[filtered[col].astype(str) == chosen]

                else:
                    unique_vals = ["All"] + sorted(df[col].astype(str).unique().tolist())
                    chosen = st.selectbox(f"🔤 {col}", unique_vals, key=f"cat_{col}")
                    if chosen != "All":
                        filtered = filtered[filtered[col].astype(str) == chosen]

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("📋 Original Records", len(df))
    c2.metric("✅ Filtered Records",  len(filtered))
    c3.metric("🗑️ Filtered Out",     len(df) - len(filtered))

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    csv = filtered.to_csv(index=False)
    st.download_button("⬇️ Download Filtered Data", csv, f"{table}_filtered.csv", "text/csv")


# ══════════════════════════════════════════════
# PAGE 4 — CRUD OPERATIONS
# ══════════════════════════════════════════════
elif page == "✏️ CRUD Operations":

    st.title("✏️ CRUD Operations")
    st.markdown("Create, Read, Update and Delete records from any table in real-time.")
    st.markdown("---")

    table_choice = st.selectbox("📂 Select Table", [
        "customers", "accounts", "transactions",
        "loans", "branches", "support_tickets", "credit_cards"
    ])

    operation = st.radio("⚙️ Operation", ["➕ Create", "👁️ Read", "✏️ Update", "🗑️ Delete"], horizontal=True)
    st.markdown("---")

    # ══ CUSTOMERS ══
    if table_choice == "customers":
        if operation == "➕ Create":
            st.subheader("➕ Add New Customer")
            c1, c2 = st.columns(2)
            with c1:
                cid       = st.text_input("Customer ID (e.g. C0501)")
                name      = st.text_input("Full Name")
                gender    = st.selectbox("Gender", ["M", "F"])
                age       = st.number_input("Age", 18, 100, 30)
            with c2:
                city      = st.text_input("City")
                acc_type  = st.selectbox("Account Type", ["Savings", "Current"])
                join_date = st.date_input("Join Date", date.today())
            if st.button("✅ Add Customer", type="primary"):
                ok = run_action(
                    "INSERT INTO customers (customer_id,name,gender,age,city,account_type,join_date) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (cid, name, gender, age, city, acc_type, str(join_date))
                )
                if ok: st.success(f"✅ Customer `{cid}` added!")

        elif operation == "👁️ Read":
            st.subheader("👁️ Search Customer")
            all_custs = run_query("SELECT customer_id, name FROM customers ORDER BY customer_id")
            options = ["-- Show All --"] + [f"{r['customer_id']} — {r['name']}" for _, r in all_custs.iterrows()]
            chosen = st.selectbox("🔍 Select Customer ID", options)
            if st.button("🔍 Search", type="primary"):
                if chosen == "-- Show All --":
                    df = run_query("SELECT * FROM customers LIMIT 50")
                else:
                    cid = chosen.split(" — ")[0]
                    df = run_query("SELECT * FROM customers WHERE customer_id=%s", (cid,))
                st.dataframe(df, use_container_width=True, hide_index=True) if not df.empty else st.warning("Not found!")

        elif operation == "✏️ Update":
            st.subheader("✏️ Update Customer")
            all_custs = run_query("SELECT customer_id, name FROM customers ORDER BY customer_id")
            options = ["-- Select Customer --"] + [f"{r['customer_id']} — {r['name']}" for _, r in all_custs.iterrows()]
            chosen = st.selectbox("🔍 Select Customer ID to Update", options)
            if chosen != "-- Select Customer --":
                cid = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM customers WHERE customer_id=%s", (cid,))
                if not df.empty:
                    c1, c2 = st.columns(2)
                    with c1:
                        new_name   = st.text_input("Name", df['name'][0])
                        new_city   = st.text_input("City", df['city'][0])
                        new_age    = st.number_input("Age", 18, 100, int(df['age'][0]))
                    with c2:
                        g_list     = ["M", "F"]
                        g_idx      = g_list.index(df['gender'][0]) if df['gender'][0] in g_list else 0
                        new_gender = st.selectbox("Gender", g_list, index=g_idx)
                        t_list     = ["Savings", "Current"]
                        t_idx      = t_list.index(df['account_type'][0]) if df['account_type'][0] in t_list else 0
                        new_type   = st.selectbox("Account Type", t_list, index=t_idx)
                    if st.button("✅ Update", type="primary"):
                        ok = run_action(
                            "UPDATE customers SET name=%s,gender=%s,age=%s,city=%s,account_type=%s WHERE customer_id=%s",
                            (new_name, new_gender, new_age, new_city, new_type, cid)
                        )
                        if ok: st.success("✅ Customer updated!")
                else:
                    st.warning("⚠️ Customer not found!")

        elif operation == "🗑️ Delete":
            st.subheader("🗑️ Delete Customer")
            all_custs = run_query("SELECT customer_id, name FROM customers ORDER BY customer_id")
            options = ["-- Select Customer --"] + [f"{r['customer_id']} — {r['name']}" for _, r in all_custs.iterrows()]
            chosen = st.selectbox("🔍 Select Customer ID to Delete", options)
            if chosen != "-- Select Customer --":
                cid = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM customers WHERE customer_id=%s", (cid,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.error("⚠️ This action is permanent and cannot be undone!")
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        ok = run_action("DELETE FROM customers WHERE customer_id=%s", (cid,))
                        if ok: st.success(f"✅ Customer `{cid}` deleted!")
                else:
                    st.warning("⚠️ Customer not found!")

    # ══ ACCOUNTS ══
    elif table_choice == "accounts":
        if operation == "➕ Create":
            st.subheader("➕ Add Account Record")
            cid     = st.text_input("Customer ID")
            balance = st.number_input("Opening Balance (₹)", 1000.0, 10000000.0, 1000.0)
            if st.button("✅ Add Account", type="primary"):
                ok = run_action("INSERT INTO accounts (customer_id,account_balance,last_updated) VALUES (%s,%s,%s)",
                                (cid, balance, datetime.now()))
                if ok: st.success("✅ Account added!")

        elif operation == "👁️ Read":
            st.subheader("👁️ View Account")
            all_acc = run_query("SELECT a.customer_id, c.name FROM accounts a JOIN customers c ON a.customer_id=c.customer_id ORDER BY a.customer_id")
            opts = ["-- Show All --"] + [f"{r['customer_id']} — {r['name']}" for _, r in all_acc.iterrows()]
            chosen = st.selectbox("🔍 Select Account", opts, key="acc_read")
            if st.button("🔍 Search", type="primary"):
                if chosen == "-- Show All --":
                    df = run_query("SELECT a.*, c.name FROM accounts a JOIN customers c ON a.customer_id=c.customer_id LIMIT 50")
                else:
                    cid = chosen.split(" — ")[0]
                    df = run_query("SELECT * FROM accounts WHERE customer_id=%s", (cid,))
                st.dataframe(df, use_container_width=True, hide_index=True) if not df.empty else st.warning("Not found!")

        elif operation == "✏️ Update":
            st.subheader("✏️ Update Account Balance")
            all_acc = run_query("SELECT a.customer_id, c.name FROM accounts a JOIN customers c ON a.customer_id=c.customer_id ORDER BY a.customer_id")
            opts = ["-- Select Account --"] + [f"{r['customer_id']} — {r['name']}" for _, r in all_acc.iterrows()]
            chosen = st.selectbox("🔍 Select Account to Update", opts, key="acc_update")
            if chosen != "-- Select Account --":
                cid = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM accounts WHERE customer_id=%s", (cid,))
                if not df.empty:
                    st.info(f"Current Balance: ₹{float(df['account_balance'][0]):,.2f}")
                    new_bal = st.number_input("New Balance (₹)", 1000.0, 10000000.0, float(df['account_balance'][0]))
                    if st.button("✅ Update Balance", type="primary"):
                        ok = run_action("UPDATE accounts SET account_balance=%s, last_updated=%s WHERE customer_id=%s",
                                        (new_bal, datetime.now(), cid))
                        if ok: st.success("✅ Balance updated!")
                else:
                    st.warning("⚠️ Account not found!")

        elif operation == "🗑️ Delete":
            st.subheader("🗑️ Delete Account")
            all_acc = run_query("SELECT a.customer_id, c.name FROM accounts a JOIN customers c ON a.customer_id=c.customer_id ORDER BY a.customer_id")
            opts = ["-- Select Account --"] + [f"{r['customer_id']} — {r['name']}" for _, r in all_acc.iterrows()]
            chosen = st.selectbox("🔍 Select Account to Delete", opts, key="acc_delete")
            if chosen != "-- Select Account --":
                cid = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM accounts WHERE customer_id=%s", (cid,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.error("⚠️ Permanent action!")
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        ok = run_action("DELETE FROM accounts WHERE customer_id=%s", (cid,))
                        if ok: st.success("✅ Account deleted!")
                else:
                    st.warning("⚠️ Not found!")

    # ══ TRANSACTIONS ══
    elif table_choice == "transactions":
        if operation == "➕ Create":
            st.subheader("➕ Add Transaction")
            c1, c2 = st.columns(2)
            with c1:
                txn_id   = st.text_input("Transaction ID (e.g. T10001)")
                cid      = st.text_input("Customer ID")
                txn_type = st.selectbox("Type", ["deposit","withdrawal","transfer","purchase","online fraud"])
            with c2:
                amount   = st.number_input("Amount (₹)", 100.0, 100000.0, 1000.0)
                txn_time = st.date_input("Date", date.today())
                status   = st.selectbox("Status", ["success","failed"])
            if st.button("✅ Add Transaction", type="primary"):
                ok = run_action(
                    "INSERT INTO transactions (txn_id,customer_id,txn_type,amount,txn_time,status) VALUES (%s,%s,%s,%s,%s,%s)",
                    (txn_id, cid, txn_type, amount, str(txn_time), status)
                )
                if ok: st.success(f"✅ Transaction `{txn_id}` added!")

        elif operation == "👁️ Read":
            st.subheader("👁️ View Transactions")
            all_txn = run_query("SELECT t.txn_id, c.name, t.txn_type, t.amount, t.status FROM transactions t JOIN customers c ON t.customer_id=c.customer_id ORDER BY t.txn_id DESC LIMIT 300")
            opts = ["-- Show All (Latest 50) --"] + [f"{r['txn_id']} — {r['name']} | {r['txn_type']} ₹{r['amount']} ({r['status']})" for _, r in all_txn.iterrows()]
            chosen = st.selectbox("🔍 Select Transaction", opts, key="txn_read")
            if st.button("🔍 Search", type="primary"):
                if chosen == "-- Show All (Latest 50) --":
                    df = run_query("SELECT * FROM transactions ORDER BY txn_time DESC LIMIT 50")
                else:
                    txn_id = chosen.split(" — ")[0]
                    df = run_query("SELECT * FROM transactions WHERE txn_id=%s", (txn_id,))
                if not df.empty:
                    st.markdown(f"**{len(df)} transaction(s) found**")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.warning("No transactions found!")

        elif operation == "✏️ Update":
            st.subheader("✏️ Update Transaction")
            all_txn = run_query("SELECT t.txn_id, c.name, t.txn_type, t.amount, t.status FROM transactions t JOIN customers c ON t.customer_id=c.customer_id ORDER BY t.txn_id DESC LIMIT 300")
            opts = ["-- Select Transaction --"] + [f"{r['txn_id']} — {r['name']} | {r['txn_type']} ₹{r['amount']} ({r['status']})" for _, r in all_txn.iterrows()]
            chosen = st.selectbox("🔍 Select Transaction to Update", opts, key="txn_update")
            if chosen != "-- Select Transaction --":
                txn_id = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM transactions WHERE txn_id=%s", (txn_id,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        new_status = st.selectbox("New Status", ["Success","Failed"])
                    with c2:
                        new_amount = st.number_input("New Amount (₹)", 100.0, 100000.0, float(df['amount'][0]))
                    if st.button("✅ Update", type="primary"):
                        ok = run_action("UPDATE transactions SET status=%s, amount=%s WHERE txn_id=%s",
                                        (new_status, new_amount, txn_id))
                        if ok: st.success("✅ Transaction updated!")
                else:
                    st.warning("⚠️ Not found!")

        elif operation == "🗑️ Delete":
            st.subheader("🗑️ Delete Transaction")
            all_txn = run_query("SELECT t.txn_id, c.name, t.txn_type, t.amount, t.status FROM transactions t JOIN customers c ON t.customer_id=c.customer_id ORDER BY t.txn_id DESC LIMIT 300")
            opts = ["-- Select Transaction --"] + [f"{r['txn_id']} — {r['name']} | {r['txn_type']} ₹{r['amount']} ({r['status']})" for _, r in all_txn.iterrows()]
            chosen = st.selectbox("🔍 Select Transaction to Delete", opts, key="txn_delete")
            if chosen != "-- Select Transaction --":
                txn_id = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM transactions WHERE txn_id=%s", (txn_id,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.error("⚠️ Permanent!")
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        ok = run_action("DELETE FROM transactions WHERE txn_id=%s", (txn_id,))
                        if ok: st.success("✅ Deleted!")
                else:
                    st.warning("⚠️ Not found!")

    # ══ LOANS ══
    elif table_choice == "loans":
        if operation == "➕ Create":
            st.subheader("➕ Add Loan")
            c1, c2 = st.columns(2)
            with c1:
                cid       = st.text_input("Customer ID")
                acc_id    = st.text_input("Account ID")
                branch    = st.text_input("Branch Name")
                loan_type = st.selectbox("Loan Type", ["Personal","Business","Home","Auto","Education"])
            with c2:
                loan_amt   = st.number_input("Loan Amount (₹)", 10000, 5000000, 100000)
                interest   = st.number_input("Interest Rate (%)", 1.0, 20.0, 10.0)
                term       = st.number_input("Term (Months)", 6, 360, 60)
                start_date = st.date_input("Start Date", date.today())
                end_date   = st.date_input("End Date")
                status     = st.selectbox("Status", ["Active","Approved","Closed","Defaulted"])
            if st.button("✅ Add Loan", type="primary"):
                ok = run_action(
                    "INSERT INTO loans (customer_id,account_id,branch,loan_type,loan_amount,interest_rate,loan_term_months,start_date,end_date,loan_status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (cid, acc_id, branch, loan_type, loan_amt, interest, term, str(start_date), str(end_date), status)
                )
                if ok: st.success("✅ Loan added!")

        elif operation == "👁️ Read":
            st.subheader("👁️ View Loans")
            all_loans = run_query("SELECT l.loan_id, c.name, l.loan_type, l.loan_status FROM loans l JOIN customers c ON l.customer_id=c.customer_id ORDER BY l.loan_id")
            opts = ["-- Show All --"] + [f"{r['loan_id']} — {r['name']} | {r['loan_type']} ({r['loan_status']})" for _, r in all_loans.iterrows()]
            chosen = st.selectbox("🔍 Select Loan", opts, key="loan_read")
            if st.button("🔍 Search", type="primary"):
                if chosen == "-- Show All --":
                    df = run_query("SELECT * FROM loans LIMIT 50")
                else:
                    loan_id = chosen.split(" — ")[0]
                    df = run_query("SELECT * FROM loans WHERE loan_id=%s", (loan_id,))
                st.dataframe(df, use_container_width=True, hide_index=True) if not df.empty else st.warning("Not found!")

        elif operation == "✏️ Update":
            st.subheader("✏️ Update Loan Status")
            all_loans = run_query("SELECT l.loan_id, c.name, l.loan_type, l.loan_status FROM loans l JOIN customers c ON l.customer_id=c.customer_id ORDER BY l.loan_id")
            opts = ["-- Select Loan --"] + [f"{r['loan_id']} — {r['name']} | {r['loan_type']} ({r['loan_status']})" for _, r in all_loans.iterrows()]
            chosen = st.selectbox("🔍 Select Loan to Update", opts, key="loan_update")
            if chosen != "-- Select Loan --":
                loan_id = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM loans WHERE loan_id=%s", (loan_id,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    new_status = st.selectbox("New Status", ["Active","Approved","Closed","Defaulted"])
                    if st.button("✅ Update Status", type="primary"):
                        ok = run_action("UPDATE loans SET loan_status=%s WHERE loan_id=%s", (new_status, loan_id))
                        if ok: st.success("✅ Loan status updated!")
                else:
                    st.warning("⚠️ Not found!")

        elif operation == "🗑️ Delete":
            st.subheader("🗑️ Delete Loan")
            all_loans = run_query("SELECT l.loan_id, c.name, l.loan_type, l.loan_status FROM loans l JOIN customers c ON l.customer_id=c.customer_id ORDER BY l.loan_id")
            opts = ["-- Select Loan --"] + [f"{r['loan_id']} — {r['name']} | {r['loan_type']} ({r['loan_status']})" for _, r in all_loans.iterrows()]
            chosen = st.selectbox("🔍 Select Loan to Delete", opts, key="loan_delete")
            if chosen != "-- Select Loan --":
                loan_id = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM loans WHERE loan_id=%s", (loan_id,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.error("⚠️ Permanent!")
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        ok = run_action("DELETE FROM loans WHERE loan_id=%s", (loan_id,))
                        if ok: st.success("✅ Loan deleted!")
                else:
                    st.warning("⚠️ Not found!")

    # ══ BRANCHES ══
    elif table_choice == "branches":
        if operation == "➕ Create":
            st.subheader("➕ Add Branch")
            c1, c2 = st.columns(2)
            with c1:
                bname    = st.text_input("Branch Name")
                city     = st.text_input("City")
                manager  = st.text_input("Manager Name")
                emp      = st.number_input("Total Employees", 1, 500, 50)
            with c2:
                revenue   = st.number_input("Branch Revenue (₹)", 0.0, 50000000.0, 1000000.0)
                open_date = st.date_input("Opening Date", date.today())
                rating    = st.slider("Performance Rating (1-5)", 1, 5, 3)
            if st.button("✅ Add Branch", type="primary"):
                ok = run_action(
                    "INSERT INTO branches (branch_name,city,manager_name,total_employees,branch_revenue,opening_date,performance_rating) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (bname, city, manager, emp, revenue, str(open_date), rating)
                )
        elif operation == "👁️ Read":
            st.subheader("👁️ View Branches")
            all_br = run_query("SELECT branch_id, branch_name, city FROM branches ORDER BY branch_id")
            opts = ["-- Show All --"] + [f"{r['branch_id']} — {r['branch_name']}, {r['city']}" for _, r in all_br.iterrows()]
            chosen = st.selectbox("🔍 Select Branch", opts, key="br_read")
            if st.button("🔍 Search", type="primary"):
                if chosen == "-- Show All --":
                    df = run_query("SELECT * FROM branches LIMIT 50")
                else:
                    bid = chosen.split(" — ")[0]
                    df = run_query("SELECT * FROM branches WHERE branch_id=%s", (bid,))
                st.dataframe(df, use_container_width=True, hide_index=True) if not df.empty else st.warning("Not found!")

        elif operation == "✏️ Update":
            st.subheader("✏️ Update Branch")
            all_br = run_query("SELECT branch_id, branch_name, city FROM branches ORDER BY branch_id")
            opts = ["-- Select Branch --"] + [f"{r['branch_id']} — {r['branch_name']}, {r['city']}" for _, r in all_br.iterrows()]
            chosen = st.selectbox("🔍 Select Branch to Update", opts, key="br_update")
            if chosen != "-- Select Branch --":
                bid = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM branches WHERE branch_id=%s", (bid,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        new_manager = st.text_input("Manager Name", df['manager_name'][0])
                        new_emp     = st.number_input("Total Employees", 1, 500, int(df['total_employees'][0]))
                    with c2:
                        new_rating  = st.slider("Performance Rating", 1, 5, int(df['performance_rating'][0]))
                    if st.button("✅ Update Branch", type="primary"):
                        ok = run_action(
                            "UPDATE branches SET manager_name=%s,total_employees=%s,performance_rating=%s WHERE branch_id=%s",
                            (new_manager, new_emp, new_rating, bid)
                        )
                        if ok: st.success("✅ Branch updated!")
                else:
                    st.warning("⚠️ Not found!")

        elif operation == "🗑️ Delete":
            st.subheader("🗑️ Delete Branch")
            all_br = run_query("SELECT branch_id, branch_name, city FROM branches ORDER BY branch_id")
            opts = ["-- Select Branch --"] + [f"{r['branch_id']} — {r['branch_name']}, {r['city']}" for _, r in all_br.iterrows()]
            chosen = st.selectbox("🔍 Select Branch to Delete", opts, key="br_delete")
            if chosen != "-- Select Branch --":
                bid = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM branches WHERE branch_id=%s", (bid,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.error("⚠️ Permanent!")
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        ok = run_action("DELETE FROM branches WHERE branch_id=%s", (bid,))
                        if ok: st.success("✅ Branch deleted!")
                else:
                    st.warning("⚠️ Not found!")

    # ══ SUPPORT TICKETS ══
    # ══ SUPPORT TICKETS ══
    elif table_choice == "support_tickets":
        if operation == "➕ Create":
            st.subheader("➕ Add Support Ticket")
            c1, c2 = st.columns(2)
            with c1:
                tid     = st.text_input("Ticket ID (e.g. T00601)")
                cid     = st.text_input("Customer ID")
                acc_id  = st.text_input("Account ID")
                loan_id = st.number_input("Loan ID (0 if none)", 0, 9999, 0)
                branch  = st.text_input("Branch Name")
            with c2:
                issue    = st.text_input("Issue Category")
                desc     = st.text_area("Description")
                priority = st.selectbox("Priority", ["Low","Medium","High","Critical"])
                status   = st.selectbox("Status", ["Open","In Progress","Resolved","Closed","Escalated"])
                agent    = st.text_input("Support Agent")
                channel  = st.selectbox("Channel", ["Email","Phone","In-Person","Chat"])
                rating   = st.slider("Customer Rating", 1, 5, 3)
            if st.button("✅ Add Ticket", type="primary"):
                ok = run_action(
                    "INSERT INTO support_tickets (ticket_id,customer_id,account_id,loan_id,branch_name,issue_category,description,date_opened,date_closed,priority,status,resolution_remarks,support_agent,channel,customer_rating) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (tid, cid, acc_id, loan_id, branch, issue, desc,
                     str(date.today()), 'Not Closed', priority, status,
                     'Pending', agent, channel, rating)
                )
        elif operation == "👁️ Read":
            st.subheader("👁️ View Support Ticket")
            all_tkt = run_query("SELECT s.ticket_id, c.name, s.issue_category, s.status FROM support_tickets s JOIN customers c ON s.customer_id=c.customer_id ORDER BY s.ticket_id")
            opts = ["-- Show All --"] + [f"{r['ticket_id']} — {r['name']} | {r['issue_category']} ({r['status']})" for _, r in all_tkt.iterrows()]
            chosen = st.selectbox("🔍 Select Ticket", opts, key="tkt_read")
            if st.button("🔍 Search", type="primary"):
                if chosen == "-- Show All --":
                    df = run_query("SELECT * FROM support_tickets LIMIT 50")
                else:
                    tid = chosen.split(" — ")[0]
                    df = run_query("SELECT * FROM support_tickets WHERE ticket_id=%s", (tid,))
                st.dataframe(df, use_container_width=True, hide_index=True) if not df.empty else st.warning("Not found!")

        elif operation == "✏️ Update":
            st.subheader("✏️ Update Ticket Status")
            all_tkt = run_query("SELECT s.ticket_id, c.name, s.issue_category, s.status FROM support_tickets s JOIN customers c ON s.customer_id=c.customer_id ORDER BY s.ticket_id")
            opts = ["-- Select Ticket --"] + [f"{r['ticket_id']} — {r['name']} | {r['issue_category']} ({r['status']})" for _, r in all_tkt.iterrows()]
            chosen = st.selectbox("🔍 Select Ticket to Update", opts, key="tkt_update")
            if chosen != "-- Select Ticket --":
                tid = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM support_tickets WHERE ticket_id=%s", (tid,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        new_status  = st.selectbox("New Status", ["Open","In Progress","Resolved","Closed","Escalated"])
                        new_remarks = st.text_area("Resolution Remarks")
                    with c2:
                        new_rating = st.slider("Customer Rating", 1, 5, int(df['customer_rating'][0]))
                    if st.button("✅ Update Ticket", type="primary"):
                        ok = run_action(
                            "UPDATE support_tickets SET status=%s,resolution_remarks=%s,customer_rating=%s WHERE ticket_id=%s",
                            (new_status, new_remarks, new_rating, tid)
                        )
                        if ok: st.success("✅ Ticket updated!")
                else:
                    st.warning("⚠️ Not found!")

        elif operation == "🗑️ Delete":
            st.subheader("🗑️ Delete Ticket")
            all_tkt = run_query("SELECT s.ticket_id, c.name, s.issue_category, s.status FROM support_tickets s JOIN customers c ON s.customer_id=c.customer_id ORDER BY s.ticket_id")
            opts = ["-- Select Ticket --"] + [f"{r['ticket_id']} — {r['name']} | {r['issue_category']} ({r['status']})" for _, r in all_tkt.iterrows()]
            chosen = st.selectbox("🔍 Select Ticket to Delete", opts, key="tkt_delete")
            if chosen != "-- Select Ticket --":
                tid = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM support_tickets WHERE ticket_id=%s", (tid,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.error("⚠️ Permanent!")
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        ok = run_action("DELETE FROM support_tickets WHERE ticket_id=%s", (tid,))
                        if ok: st.success("✅ Ticket deleted!")
                else:
                    st.warning("⚠️ Not found!")

    # ══ CREDIT CARDS ══
    # ══ CREDIT CARDS ══
    elif table_choice == "credit_cards":
        if operation == "➕ Create":
            st.subheader("➕ Add Credit Card")
            c1, c2 = st.columns(2)
            with c1:
                cid       = st.text_input("Customer ID")
                acc_id    = st.text_input("Account ID")
                branch    = st.text_input("Branch Name")
                card_num  = st.text_input("Card Number (16 digits)")
                card_type = st.selectbox("Card Type", ["Business","Platinum","Gold","Silver"])
            with c2:
                network  = st.selectbox("Card Network", ["Visa","Mastercard","Rupay","Amex"])
                limit    = st.number_input("Credit Limit (₹)", 10000, 500000, 100000)
                balance  = st.number_input("Current Balance (₹)", 0.0, 500000.0, 0.0)
                issued   = st.date_input("Issued Date", date.today())
                expiry   = st.date_input("Expiry Date")
                status   = st.selectbox("Status", ["Active","Expired","Blocked"])
            if st.button("✅ Add Card", type="primary"):
                ok = run_action(
                    "INSERT INTO credit_cards (customer_id,account_id,branch,card_number,card_type,card_network,credit_limit,current_balance,issued_date,expiry_date,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (cid, acc_id, branch, card_num, card_type, network, limit, balance, str(issued), str(expiry), status)
                )
                if ok: st.success("✅ Credit card added!")

        elif operation == "👁️ Read":
            st.subheader("👁️ View Credit Cards")
            cid = st.text_input("Customer ID (leave blank for active cards)")
            if st.button("🔍 Search", type="primary"):
                if cid:
                    df = run_query("SELECT * FROM credit_cards WHERE customer_id=%s", (cid,))
                else:
                    df = run_query("SELECT * FROM credit_cards WHERE status='Active' LIMIT 50")
        elif operation == "👁️ Read":
            st.subheader("👁️ View Credit Cards")
            all_cc = run_query("SELECT cc.card_id, c.name, cc.card_type, cc.status FROM credit_cards cc JOIN customers c ON cc.customer_id=c.customer_id ORDER BY cc.card_id")
            opts = ["-- Show All --"] + [f"{r['card_id']} — {r['name']} | {r['card_type']} ({r['status']})" for _, r in all_cc.iterrows()]
            chosen = st.selectbox("🔍 Select Card", opts, key="cc_read")
            if st.button("🔍 Search", type="primary"):
                if chosen == "-- Show All --":
                    df = run_query("SELECT * FROM credit_cards LIMIT 50")
                else:
                    card_id = chosen.split(" — ")[0]
                    df = run_query("SELECT * FROM credit_cards WHERE card_id=%s", (card_id,))
                st.dataframe(df, use_container_width=True, hide_index=True) if not df.empty else st.warning("Not found!")

        elif operation == "✏️ Update":
            st.subheader("✏️ Update Card Status")
            all_cc = run_query("SELECT cc.card_id, c.name, cc.card_type, cc.status FROM credit_cards cc JOIN customers c ON cc.customer_id=c.customer_id ORDER BY cc.card_id")
            opts = ["-- Select Card --"] + [f"{r['card_id']} — {r['name']} | {r['card_type']} ({r['status']})" for _, r in all_cc.iterrows()]
            chosen = st.selectbox("🔍 Select Card to Update", opts, key="cc_update")
            if chosen != "-- Select Card --":
                card_id = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM credit_cards WHERE card_id=%s", (card_id,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    new_status  = st.selectbox("New Status", ["Active","Expired","Blocked"])
                    new_balance = st.number_input("Current Balance (₹)", 0.0, 500000.0, float(df['current_balance'][0]))
                    if st.button("✅ Update Card", type="primary"):
                        ok = run_action("UPDATE credit_cards SET status=%s, current_balance=%s WHERE card_id=%s",
                                        (new_status, new_balance, card_id))
                        if ok: st.success("✅ Card updated!")
                else:
                    st.warning("⚠️ Not found!")

        elif operation == "🗑️ Delete":
            st.subheader("🗑️ Delete Credit Card")
            all_cc = run_query("SELECT cc.card_id, c.name, cc.card_type, cc.status FROM credit_cards cc JOIN customers c ON cc.customer_id=c.customer_id ORDER BY cc.card_id")
            opts = ["-- Select Card --"] + [f"{r['card_id']} — {r['name']} | {r['card_type']} ({r['status']})" for _, r in all_cc.iterrows()]
            chosen = st.selectbox("🔍 Select Card to Delete", opts, key="cc_delete")
            if chosen != "-- Select Card --":
                card_id = chosen.split(" — ")[0]
                df = run_query("SELECT * FROM credit_cards WHERE card_id=%s", (card_id,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.error("⚠️ Permanent!")
                    if st.button("🗑️ Confirm Delete", type="primary"):
                        ok = run_action("DELETE FROM credit_cards WHERE card_id=%s", (card_id,))
                        if ok: st.success("✅ Card deleted!")
                else:
                    st.warning("⚠️ Not found!")

# ══════════════════════════════════════════════
# PAGE 5 — CREDIT / DEBIT SIMULATION
# ══════════════════════════════════════════════
elif page == "💰 Credit / Debit Simulation":

    st.title("💰 Credit / Debit Simulation")
    st.markdown("Simulate real banking deposit and withdrawal operations.")
    st.info("ℹ️ **Minimum Balance Rule:** Account must always maintain at least ₹1,000.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔍 Step 1: Check Account")
        cid = st.text_input("Enter Customer ID (e.g. C0001)")
        if st.button("🔍 Fetch Account", type="primary"):
            df = run_query(
                "SELECT c.customer_id, c.name, c.city, c.account_type, a.account_balance FROM customers c JOIN accounts a ON c.customer_id = a.customer_id WHERE c.customer_id = %s",
                (cid,)
            )
            if not df.empty:
                st.session_state['sim_customer'] = df.iloc[0].to_dict()
            else:
                st.error("❌ Customer not found!")
                if 'sim_customer' in st.session_state:
                    del st.session_state['sim_customer']

        if 'sim_customer' in st.session_state:
            c = st.session_state['sim_customer']
            st.success("✅ Account Found!")
            st.markdown(f"**👤 Name:** {c['name']}")
            st.markdown(f"**🏙️ City:** {c['city']}")
            st.markdown(f"**💳 Account Type:** {c['account_type']}")
            st.metric("💰 Current Balance", f"₹{float(c['account_balance']):,.2f}")

    with col2:
        st.subheader("💸 Step 2: Perform Transaction")

        if 'sim_customer' in st.session_state:
            c = st.session_state['sim_customer']
            current_bal = float(c['account_balance'])

            operation = st.radio("Select Operation", ["💵 Deposit", "💸 Withdraw"], horizontal=True)
            amount = st.number_input("Enter Amount (₹)", min_value=1.0, max_value=5000000.0, value=5000.0, step=100.0)

            if operation == "💵 Deposit":
                st.success(f"After deposit → ₹{(current_bal + amount):,.2f}")
            else:
                after = current_bal - amount
                if after < 1000:
                    st.error("❌ Cannot withdraw! Balance will fall below ₹1,000 minimum.")
                    st.warning(f"Max you can withdraw: ₹{max(0, current_bal - 1000):,.2f}")
                else:
                    st.success(f"After withdrawal → ₹{after:,.2f}")

            if st.button("✅ Confirm Transaction", type="primary"):
                txn_id = f"T{random.randint(10001, 99999)}"
                now    = datetime.now()

                if operation == "💵 Deposit":
                    new_bal = current_bal + amount
                    run_action("UPDATE accounts SET account_balance=%s, last_updated=%s WHERE customer_id=%s",
                               (new_bal, now, c['customer_id']))
                    run_action("INSERT INTO transactions (txn_id,customer_id,txn_type,amount,txn_time,status) VALUES (%s,%s,'deposit',%s,%s,'success')",
                               (txn_id, c['customer_id'], amount, now))
                    st.balloons()
                    st.success(f"✅ ₹{amount:,.2f} deposited! New Balance: ₹{new_bal:,.2f}")
                    st.session_state['sim_customer']['account_balance'] = new_bal

                elif operation == "💸 Withdraw":
                    if current_bal - amount < 1000:
                        st.error("❌ Transaction blocked! Minimum balance rule violated.")
                    else:
                        new_bal = current_bal - amount
                        run_action("UPDATE accounts SET account_balance=%s, last_updated=%s WHERE customer_id=%s",
                                   (new_bal, now, c['customer_id']))
                        run_action("INSERT INTO transactions (txn_id,customer_id,txn_type,amount,txn_time,status) VALUES (%s,%s,'withdrawal',%s,%s,'success')",
                                   (txn_id, c['customer_id'], amount, now))
                        st.success(f"✅ ₹{amount:,.2f} withdrawn! New Balance: ₹{new_bal:,.2f}")
                        st.session_state['sim_customer']['account_balance'] = new_bal
        else:
            st.warning("👈 Please fetch an account first on the left side.")

    if 'sim_customer' in st.session_state:
        st.markdown("---")
        st.subheader("📋 Recent Transactions")
        cid = st.session_state['sim_customer']['customer_id']
        hist = run_query(
            "SELECT txn_id, txn_type, amount, txn_time, status FROM transactions WHERE customer_id=%s ORDER BY txn_time DESC LIMIT 10",
            (cid,)
        )
        if not hist.empty:
            st.dataframe(hist, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# PAGE 6 — ANALYTICAL INSIGHTS
# ══════════════════════════════════════════════
elif page == "🧠 Analytical Insights":

    st.title("🧠 Analytical Insights")
    st.markdown("Select a category, then choose a query. Results execute live from SQLite.")
    st.markdown("---")

    CATEGORIES = {
        "1️⃣  Customer & Account Analysis": {
            "Q1 — Customers per city & avg balance": {
                "desc": "How many customers exist per city, and what is their average account balance?",
                "sql":  """
                    SELECT c.city,
                           COUNT(c.customer_id)            AS total_customers,
                           ROUND(AVG(a.account_balance),2) AS avg_balance
                    FROM customers c
                    JOIN accounts  a ON c.customer_id = a.customer_id
                    GROUP BY c.city
                    ORDER BY total_customers DESC
                    LIMIT 15
                """,
            },
            "Q2 — Account type with highest total balance": {
                "desc": "Which account type (Savings/Current) holds the highest total balance?",
                "sql":  """
                    SELECT c.account_type,
                           COUNT(c.customer_id)            AS total_customers,
                           ROUND(SUM(a.account_balance),2) AS total_balance,
                           ROUND(AVG(a.account_balance),2) AS avg_balance
                    FROM customers c
                    JOIN accounts  a ON c.customer_id = a.customer_id
                    GROUP BY c.account_type
                    ORDER BY total_balance DESC
                """,
            },
            "Q3 — Top 10 customers by account balance": {
                "desc": "Who are the top 10 customers by total account balance across all acount types?",
                "sql":  """
                    SELECT c.name,
                           c.account_type,
                           ROUND(a.account_balance,2) AS account_balance
                    FROM customers c
                    JOIN accounts  a ON c.customer_id = a.customer_id
                    ORDER BY a.account_balance DESC
                    LIMIT 10
                """,
            },
            "Q4 — 2023 joiners with balance > ₹1,00,000": {
                "desc": "Which customers opened accounts in 2023 with a balance above ₹1,00,000?",
                "sql":  """
                    SELECT c.name,
                           c.account_type,
                           c.city,
                           c.join_date,
                           ROUND(a.account_balance,2) AS account_balance
                    FROM customers c
                    JOIN accounts  a ON c.customer_id = a.customer_id
                    WHERE strftime('%Y', c.join_date) = '2023'
                      AND a.account_balance > 100000
                    ORDER BY a.account_balance DESC
                """,
            },
        },
        "2️⃣  Transaction Behavior": {
            "Q5 — Total transaction volume by type": {
                "desc": "What is the total transaction volume (sum of ₹ amounts) by transaction type?",
                "sql":  """
                    SELECT txn_type                 AS transaction_type,
                           ROUND(SUM(amount), 2)   AS total_transaction_volume
                    FROM transactions
                    GROUP BY txn_type
                    ORDER BY total_transaction_volume DESC
                """,
            },
            "Q6 — Failed transactions per type": {
                "desc": "How many failed transactions occurred for each transaction type?",
                "sql":  """
                    SELECT txn_type       AS transaction_type,
                           COUNT(*)      AS failed_transactions
                    FROM transactions
                    WHERE LOWER(status) = 'failed'
                    GROUP BY txn_type
                    ORDER BY failed_transactions DESC
                """,
            },
            "Q7 — Total number of transactions per type": {
                "desc": "What is the total number of transactions per transaction type?",
                "sql":  """
                    SELECT txn_type    AS transaction_type,
                           COUNT(*)   AS total_transactions
                    FROM transactions
                    GROUP BY txn_type
                    ORDER BY total_transactions DESC
                """,
            },
            "Q8 — Accounts with 5+ high-value transactions (>₹20K)": {
                "desc": "Which accounts have 5 or more high-value transactions above ₹20,000?",
                "sql":  """
                    SELECT c.name,
                           c.account_type,
                           COUNT(*)               AS high_value_count,
                           ROUND(SUM(t.amount),2) AS total_amount
                    FROM transactions t
                    JOIN customers    c ON t.customer_id = c.customer_id
                    WHERE t.amount > 20000
                    GROUP BY t.customer_id, c.name, c.account_type
                    HAVING COUNT(*) >= 5
                    ORDER BY high_value_count DESC
                    LIMIT 15
                """,
            },
        },
        "3️⃣  Loan Insights": {
            "Q9 — Avg loan amount & interest rate by loan type": {
                "desc": "What is the average loan amount and interest rate by loan type?",
                "sql":  """
                    SELECT loan_type,
                           COUNT(*)                    AS total_loans,
                           ROUND(AVG(loan_amount),2)   AS avg_loan_amount,
                           ROUND(AVG(interest_rate),2) AS avg_interest_rate
                    FROM loans
                    GROUP BY loan_type
                    ORDER BY avg_loan_amount DESC
                """,
            },
            "Q10 — Customers with multiple active/approved loans": {
                "desc": "Which customers currently hold more than one active or approved loan?",
                "sql":  """
                    SELECT c.name,
                           COUNT(l.loan_id)            AS active_loans,
                           ROUND(SUM(l.loan_amount),2) AS total_loan_amount
                    FROM loans    l
                    JOIN customers c ON l.customer_id = c.customer_id
                    WHERE LOWER(l.loan_status) IN ('active', 'approved')
                    GROUP BY l.customer_id, c.name
                    HAVING COUNT(l.loan_id) > 1
                    ORDER BY active_loans DESC
                    LIMIT 15
                """,
            },
            "Q11 — Top 5 customers with highest outstanding loans": {
                "desc": "Who are the top 5 customers with the highest (non-closed) outstanding loan amounts?",
                "sql":  """
                    SELECT c.name,
                           COUNT(l.loan_id)            AS loan_count,
                           ROUND(SUM(l.loan_amount),2) AS total_outstanding
                    FROM loans    l
                    JOIN customers c ON l.customer_id = c.customer_id
                    WHERE LOWER(l.loan_status) != 'closed'
                    GROUP BY l.customer_id, c.name
                    ORDER BY total_outstanding DESC
                    LIMIT 5
                """,
            },
        },
        "4️⃣  Branch & Performance": {
            "Q12 — Average loan amount per branch": {
                "desc": "What is the average loan amount disbursed per branch?",
                "sql":  """
                    SELECT branch,
                           COUNT(*)                  AS total_loans,
                           ROUND(AVG(loan_amount),2) AS avg_loan_amount
                    FROM loans
                    GROUP BY branch
                    ORDER BY avg_loan_amount DESC
                    LIMIT 10
                """,
            },
            "Q13 — Customer count by age group": {
                "desc": "How many customers exist in each age group?",
                "sql":  """
                    SELECT CASE
                               WHEN age BETWEEN 18 AND 25 THEN '18-25'
                               WHEN age BETWEEN 26 AND 35 THEN '26-35'
                               WHEN age BETWEEN 36 AND 45 THEN '36-45'
                               WHEN age BETWEEN 46 AND 55 THEN '46-55'
                               WHEN age BETWEEN 56 AND 65 THEN '56-65'
                               ELSE '65+'
                           END        AS age_group,
                           COUNT(*) AS total_customers
                    FROM customers
                    GROUP BY age_group
                    ORDER BY age_group
                """,
            },
        },
        "5️⃣  Support Tickets & Customer Experience": {
            "Q14 — Issue categories by avg resolution time": {
                "desc": "Which issue categories have the longest average resolution time?",
                "sql":  """
                    SELECT issue_category,
                           COUNT(*) AS total_tickets,
                           ROUND(AVG(
                               CAST(
                                   julianday(CASE WHEN date_closed='Not Closed' THEN NULL
                                                  ELSE date_closed END)
                                   - julianday(date_opened)
                               AS INTEGER)
                           ),2) AS avg_days_to_resolve
                    FROM support_tickets
                    WHERE date_closed != 'Not Closed'
                    GROUP BY issue_category
                    ORDER BY avg_days_to_resolve DESC
                    LIMIT 10
                """,
            },
            "Q15 — Best agents for critical tickets (rating ≥ 4)": {
                "desc": "Which support agents resolved the most critical tickets with customer rating (≥ 4)?",
                "sql":  """
                    SELECT support_agent,
                           COUNT(*)                      AS resolved_critical,
                           ROUND(AVG(customer_rating),2) AS avg_rating
                    FROM support_tickets
                    WHERE LOWER(priority) = 'critical'
                      AND LOWER(status)   IN ('resolved','closed')
                      AND customer_rating >= 4
                    GROUP BY support_agent
                    ORDER BY resolved_critical DESC
                    LIMIT 10
                """,
            },
        },
    }

    # ── Navigation ─────────────────────────────────────────────
    cat = st.selectbox("📂 Select Category", list(CATEGORIES.keys()))
    q_name = st.selectbox("📊 Select Query", list(CATEGORIES[cat].keys()))
    st.markdown("---")

    q   = CATEGORIES[cat][q_name]
    df  = run_query(q["sql"])

    st.info(f"💡 **{q['desc']}**")


    # ── QUERY RESULTS TABLE ───────────────────────────────────
    st.subheader("📋 Query Results")
    if df.empty:
        st.warning("No data returned. Check that your database is populated.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Rows returned: {len(df)}")
        st.download_button(
            "⬇️ Download CSV",
            df.to_csv(index=False),
            f"{q_name[:3].strip()}.csv",
            "text/csv"
        )

    st.markdown("---")
    st.subheader("🔍 SQL Query Used")
    st.code(q["sql"], language="sql")

elif page == "👩‍💻 About Creator":

    st.title("👩‍💻 About the Creator")
    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    with col1:
        photo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "KAVYA_S_jpg.jpeg")
        if os.path.exists(photo_path):
            st.image(photo_path, width=220)
        else:
            st.image("https://img.icons8.com/color/200/user-female-circle--v1.png", width=220)

        st.markdown("### 🏆 Skills")
        skills = ["Python", "SQL", "Streamlit", "Data Analysis",
                   "Pandas", "Plotly", "Banking Analytics",
                  "Artificial Intelligence"]
        for s in skills:
            st.markdown(f"✅ {s}")

    with col2:
        st.markdown("## 👤 KAVYA S")
        st.markdown("### 🎓 BE Biomedical Engineering · Minor in AI & DS")

        st.markdown("""
**About Me:**

I am a passionate Data Science professional specializing in
banking analytics, financial data processing, and building
interactive dashboards. This project — **BankSight** — demonstrates
my ability to work end-to-end: from raw data to a fully functional
analytics platform.

---

**🎯 Project Highlights:**
- Built a complete banking intelligence system from scratch
- Designed SQLite schema for 7 interconnected datasets
- Wrote 15 analytical SQL queries for real business insights
- Built an interactive Streamlit dashboard with 7 pages
- Implemented full CRUD for all tables
- Integrated fraud detection and credit/debit simulation
        """)

        st.markdown("---")
        st.subheader("📬 Contact Information")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("📧 **Email:** kavya22s145@gmail.com")
            st.markdown("📱 **Phone:** +91 9342677552")
            st.markdown("🌐 **LinkedIn:** [kavya-s1245](https://www.linkedin.com/in/kavya-s1245/)")
        with c2:
            st.markdown("🐙 **GitHub:** [Kavya1245](https://github.com/Kavya1245)")
            st.markdown("🏙️ **Location:** TamilNadu, India")
            st.markdown("🎓 **Education:** BE Biomedical Engg · Minor in AI & DS")

    st.markdown("---")
    st.subheader("📊 Project Summary")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📁 Datasets",      "7")
    c2.metric("🗄️ DB Tables",     "7")
    c3.metric("📝 SQL Queries",   "15")
    c4.metric("📊 App Pages",     "7")
    c5.metric("📋 Total Records", "13,230")