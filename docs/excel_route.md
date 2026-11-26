# Excel route (Power Query + pivots), using `data/load/excel_sample.csv` (about 98k rows, 75 cards)
Run `python python/10_export_powerbi.py` first. The script prints the sample's totals; use them to cross-check.

## A. Clean with Power Query
1. Excel > **Data** > **Get Data** > **From Text/CSV** > choose `excel_sample.csv` > **Transform Data**.
2. Select **trans_num** > **Home > Remove Rows > Remove Duplicates**.
3. Select text columns (category, merchant, state) > **Transform > Format > Trim** and **Clean**; for state use **Format > UPPERCASE**.
4. Set types: trans_time = Date/Time, amt = Decimal Number, is_fraud/flag_count/trans_hour = Whole Number.
5. Select all columns > **Transform > Replace Errors** > type `0` for numbers (none are expected).
6. **Close & Load**.

## B. Pivot tables (Insert > PivotTable, from the loaded table)
1. Fraud rate by category: Rows = category; Values = Sum of is_fraud and Average of is_fraud (format as %).
2. Fraud by hour: Rows = trans_hour; Values = Sum of is_fraud.
3. Risk tier summary: Rows = risk_tier; Values = Count of trans_num, Sum of is_fraud.
4. Precision of the final rule: Filter is_flagged = 1; Values = Average of is_fraud.

## C. Dashboard sheet
1. New sheet "Dashboard". Insert a column chart from pivot 1, a column chart from pivot 2, and a bar chart from pivot 3.
2. Select a pivot > **PivotTable Analyze > Insert Slicer** for category and state; **Report Connections** to link all pivots.
3. Add KPI cells using the formulas below.

## D. Cross-check formulas (put in a "Checks" sheet; table name assumed `excel_sample`)
- Rows: `=ROWS(excel_sample[trans_num])`
- Fraud count: `=SUM(excel_sample[is_fraud])`
- Total amount: `=SUM(excel_sample[amt])`
- Fraud rate: `=SUM(excel_sample[is_fraud])/ROWS(excel_sample[trans_num])`
- Flagged: `=SUM(excel_sample[is_flagged])`
- Caught fraud: `=COUNTIFS(excel_sample[is_flagged],1,excel_sample[is_fraud],1)`
- Precision: `=COUNTIFS(excel_sample[is_flagged],1,excel_sample[is_fraud],1)/SUM(excel_sample[is_flagged])`
- Pivot total check: `=GETPIVOTDATA("is_fraud",$A$3)` should equal the fraud count above.
Compare these with the totals printed by `10_export_powerbi.py` (rows, fraud, total amount, flagged).
