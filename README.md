# 🏦 BankSight: Transaction Intelligence Dashboard

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-red?logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-3-lightblue?logo=sqlite)
![Plotly](https://img.shields.io/badge/Plotly-6.0.1-purple?logo=plotly)
![Pandas](https://img.shields.io/badge/Pandas-2.2.3-green?logo=pandas)

> A comprehensive banking analytics platform for customer insights, fraud detection, transaction analysis, and branch performance — built end-to-end with Python, SQLite, and Streamlit.

---

## 📌 Table of Contents

- [Problem Statement](#-problem-statement)
- [Project Objectives](#-project-objectives)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Datasets](#-datasets)
- [Features](#-features)
- [SQL Queries & Insights](#-sql-queries--insights)
- [Installation & Setup](#-installation--setup)
- [How to Run](#-how-to-run)
- [Live Demo](#-live-demo)
- [Screenshots](#-screenshots)
- [Creator](#-creator)

---

## 📌 Problem Statement

Banks process millions of transactions daily and need intelligent systems to:
- Understand **customer behavior** and demographic patterns
- Detect **fraudulent** and anomalous transactions early
- Evaluate **branch performance** based on loans and transactions
- Enable **interactive data exploration** with filtering and CRUD capabilities
- Provide **actionable SQL-driven insights** for business decisions

---

## 🎯 Project Objectives

| # | Objective |
|---|-----------|
| 1 | Clean and preprocess 7 raw banking datasets |
| 2 | Design and load a relational SQLite database |
| 3 | Write 15 real-world analytical SQL queries |
| 4 | Build a 7-page interactive Streamlit dashboard |
| 5 | Deploy the application on Streamlit Cloud |

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Core programming language |
| SQLite | 3 | Lightweight relational database |
| Streamlit | 1.45.1 | Interactive web dashboard |
| Plotly | 6.0.1 | Interactive data visualizations |
| Pandas | 2.2.3 | Data manipulation & transformation |

---

## 📁 Project Structure

```
BankSight/
├── app.py                    # Main Streamlit application (7 pages)
├── requirements.txt          # Python dependencies
├── KAVYA_S_jpg.jpeg          # Creator photo
├── README.md                 # Project documentation
│
├── database/
│   └── banksight.db          # SQLite database (7 tables, 13,230+ records)
│
├── data/
│   ├── raw/                  # Original uncleaned CSV/JSON datasets
│   └── cleaned/              # Cleaned datasets ready for DB loading
│
└── scripts/
    ├── clean_data.py         # Data cleaning & preprocessing
    ├── load_database.py      # Database creation & data loading
    └── queries.py            # 15 analytical SQL queries
```

---

## 📊 Datasets

| Dataset | Records | Format | Description |
|---------|---------|--------|-------------|
| Customers | 500 | CSV | Customer demographics (name, age, city, gender) |
| Accounts | 500 | CSV | Account balances and types |
| Transactions | 10,000 | CSV | All banking transactions |
| Loans | 553 | JSON | Loan details and status |
| Credit Cards | 557 | JSON | Credit card information |
| Branches | 520 | JSON | Branch performance data |
| Support Tickets | 600 | JSON | Customer complaints and resolutions |
| **Total** | **13,230+** | | |

---

## ✨ Features

### 🏠 1. Introduction Page
- Live KPI metrics (customers, transactions, total balance, active loans, open tickets)
- Problem statement and business use cases
- Transaction overview bar chart
- Pie charts: account types, loan types, support ticket status

### 📊 2. View Tables
- Browse all 7 database tables interactively
- Row limit selector: 10, 25, 50, 100, 200, All
- Live record count and column info
- CSV download button

### 🔍 3. Filter Data
- Select any of 7 datasets to filter
- Multi-column filtering simultaneously
- Numeric columns → range sliders
- Categorical columns → dropdown selectors
- Date columns → value selectors
- Live metrics: Original / Filtered / Filtered Out records
- Download filtered results as CSV

### ✏️ 4. CRUD Operations
Full **Create / Read / Update / Delete** for all 7 tables:
- `customers` — dropdown selector for safe update/delete
- `accounts` — balance management
- `transactions` — status and amount updates
- `loans` — loan status tracking
- `branches` — manager and rating updates
- `support_tickets` — ticket resolution workflow
- `credit_cards` — card status management

### 💰 5. Credit / Debit Simulation
- Fetch any customer account by Customer ID
- Perform **Deposit** or **Withdrawal** operations
- Live balance preview before confirmation
- Enforces **₹1,000 minimum balance** rule
- Automatically logs transaction to database
- Recent transaction history table (last 10)

### 🧠 6. Analytical Insights (15 SQL Queries)
Organized into 5 categories — each with a results table + Plotly visualization:

| Category | Queries |
|----------|---------|
| Customer & Account Analysis | Q1 – Q4 |
| Transaction Behavior | Q5 – Q8 |
| Loan Insights | Q9 – Q11 |
| Branch & Performance | Q12 – Q13 |
| Support Tickets & Experience | Q14 – Q15 |

### 👩‍💻 7. About Creator
- Creator photo, bio, skills
- Contact details (email, phone, LinkedIn, GitHub)
- Project summary metrics

---

## 🔍 SQL Queries & Insights

| Query | Question |
|-------|----------|
| **Q1** | How many customers exist per city, and what is their average account balance? |
| **Q2** | Which account type holds the highest total balance? |
| **Q3** | Who are the top 10 customers by account balance? |
| **Q4** | Which customers joined in 2023 with balance > ₹1,00,000? |
| **Q5** | What is the total transaction volume by transaction type? |
| **Q6** | How many failed transactions occurred per type? |
| **Q7** | What is the total number of transactions per type? |
| **Q8** | Which accounts have 5+ high-value transactions above ₹20,000? |
| **Q9** | What is the average loan amount and interest rate by loan type? |
| **Q10** | Which customers hold more than one active/approved loan? |
| **Q11** | Who are the top 5 customers with the highest outstanding loans? |
| **Q12** | What is the average loan amount per branch? |
| **Q13** | How many customers exist in each age group? |
| **Q14** | Which issue categories have the longest average resolution time? |
| **Q15** | Which support agents resolved the most critical tickets with rating ≥ 4? |

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Kavya1245/BankSight.git
cd BankSight
```

### 2. Create a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up the Database
```bash
# Step 1 — Clean the raw data
python scripts/clean_data.py

# Step 2 — Load data into SQLite
python scripts/load_database.py
```

---

## ▶️ How to Run

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🌐 Live Demo

🔗 **[Click here to view the live app](https://kavya1245-banksight.streamlit.app)**

> Deployed on Streamlit Cloud — no installation required.

---

## 📸 Screenshots

| Page | Description |
|------|-------------|
| 🏠 Introduction | KPI metrics + charts |
| 📊 View Tables | Interactive table browser |
| 🔍 Filter Data | Multi-column filtering |
| ✏️ CRUD Operations | Full database operations |
| 💰 Credit/Debit Sim | Live banking simulation |
| 🧠 Analytical Insights | 15 SQL queries + charts |
| 👩‍💻 About Creator | Profile and contact info |

---

## 👩‍💻 Creator

**KAVYA S**
BE Biomedical Engineering · Minor in AI & Data Science

| Contact | Details |
|---------|---------|
| 📧 Email | kavya22s145@gmail.com |
| 📱 Phone | +91 9342677552 |
| 🌐 LinkedIn | [kavya-s1245](https://www.linkedin.com/in/kavya-s1245/) |
| 🐙 GitHub | [Kavya1245](https://github.com/Kavya1245) |
| 🏙️ Location | Tamil Nadu, India |

---

## 📄 License

This project is created for academic purposes as part of a Data Science course project evaluation.

---

⭐ **If you found this project helpful, please give it a star on GitHub!**