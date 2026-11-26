# Project Synopsis

**Title:** Credit Card Transaction and Fraud Pattern Analysis
**Team:** [Name 1, Roll No], [Name 2, Roll No]   **Course:** B.Tech 2nd Year, Data Analyst Project   **College:** ABES

## 1. Problem statement
Card issuers must separate a very small number of fraudulent transactions (under 1%) from millions of normal ones. This project builds transparent, rule-based fraud flags and measures how well they find the labelled fraud.

## 2. Objectives
1. Clean and profile the transaction data and log every data-quality fix.
2. Design a star schema and load it into Oracle.
3. Implement at least three fraud rules in Python and in Oracle SQL (including a window-function velocity rule) and reconcile both.
4. Measure precision and recall against the labelled fraud.
5. Present results in a Power BI dashboard and a short report.

## 3. Data
Kaggle *Credit Card Transactions Fraud Detection Dataset* (simulated), sample of 500 cards, 662,187 transactions, 3,771 labelled fraud.

## 4. Tools
Python (pandas, matplotlib), Oracle Database XE (SQL), Power BI Desktop, Excel Power Query, Streamlit, GitHub.

## 5. Methodology
Clean -> explore -> define rules -> evaluate -> combine rules -> load to Oracle -> SQL rules and reconciliation -> dashboard -> report.

## 6. Expected outcome
A working pipeline, a precision/recall comparison of the rules, a risk-tier view (Low/Medium/High), and recommendations for fraud analysts.

## 7. Result summary
Final rule (2 or more of 3 rules): precision 64.1%, recall 42.0%, F1 50.7. 85.1% of fraud occurs between 22:00 and 03:59.
