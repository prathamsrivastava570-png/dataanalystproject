# Software Requirements Specification (SRS)
**Project:** Credit Card Transaction and Fraud Pattern Analysis   **Version:** 1.0

## 1. Purpose and scope
Analytics pipeline that cleans card transaction data, flags suspicious transactions with rules, and reports how well the rules match labelled fraud. It is an offline analysis project, not a real-time system.

## 2. Users
Fraud analyst (reviews flagged transactions), project evaluator (checks reproducibility).

## 3. Functional requirements
| ID | Requirement |
|---|---|
| FR1 | Load the raw CSV and sample all transactions of 500 cards |
| FR2 | Clean the data and write a data-quality log (issue, rule applied, rows affected) |
| FR3 | Compute three rules: amount > 600; 3 transactions in 30 minutes on one card; night hours with amount > 300 |
| FR4 | Combine rules: flag when 2 or more rules fire; assign a risk tier (Clear, Low, Medium, High) |
| FR5 | Load a star schema (4 dimensions, 1 fact) into Oracle |
| FR6 | Re-implement the rules in Oracle SQL and reconcile counts with Python (0 mismatches) |
| FR7 | Calculate precision, recall and F1 against the labelled is_fraud column |
| FR8 | Provide 7 business SQL queries (JOIN, GROUP BY, CASE, LAG) |
| FR9 | Produce KPIs (JSON), 4 charts, a Jupyter notebook, a Streamlit dashboard and a Power BI report |
| FR10 | Run automated tests and save PASS/FAIL results |

## 4. Non-functional requirements
- **Reproducibility:** every step is a numbered script run from the project root.
- **Data integrity:** primary keys, foreign keys and CHECK constraints in Oracle.
- **Performance:** full pipeline runs on a laptop with 16 GB RAM in minutes.
- **Transparency:** rule-based flags, so each alert can be explained.
- **No silent data loss:** every removed row is logged.

## 5. Constraints and assumptions
Data is simulated; thresholds were chosen on the same data (so results may be optimistic); fraud is rare (0.57%), so accuracy is not used.

## 6. Acceptance criteria
At least 3 rules implemented; flagged counts compared against labelled fraud; precision and recall reported; SQL and Python counts reconcile; all tests pass.

## 7. Interfaces
Input: `fraudTrain.csv`. Outputs: cleaned/flagged CSVs, Oracle tables and views, KPI JSON, PNG charts, Power BI report, README.
