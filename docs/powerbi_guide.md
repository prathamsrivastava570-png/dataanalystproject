# Power BI guide (model, DAX, report)
Run `python python/10_export_powerbi.py` first. It creates `data/load/powerbi_txn.csv` (same fields as the Oracle view `vw_powerbi_txn`, 662,187 rows). Loading this CSV avoids installing the Oracle client for Power BI.

## A. Load and model (click by click)
1. Open **Power BI Desktop** > **Get data** > **Text/CSV** > choose `data/load/powerbi_txn.csv` > **Transform Data**.
2. In Power Query check types: `trans_time` = Date/Time, `trans_date` = Date, `amt` = Decimal Number, `is_fraud`, `flag_count`, `is_flagged`, `trans_hour` = Whole Number. Click **Close & Apply**.
3. Create the date table: **Modeling > New table** and enter:
   `Date Table = ADDCOLUMNS(CALENDAR(DATE(2019,1,1), DATE(2020,12,31)), "Month", FORMAT([Date], "MMM yyyy"), "YearMonth", YEAR([Date])*100 + MONTH([Date]))`
4. Select the `Month` column of Date Table > **Column tools > Sort by column** > `YearMonth` (so months sort in time order).
5. Select **Date Table** > **Table tools > Mark as date table** > choose `Date`.
6. Open **Model view**: drag `Date Table[Date]` onto `powerbi_txn[trans_date]` (one to many, single direction).
7. (Star-schema extension) You may also import the Oracle dimension exports; for the submission the flat table + date table is enough because the Oracle star schema is documented separately.

## B. DAX measures (Modeling > New measure)
```
Total Transactions = COUNTROWS(powerbi_txn)
Fraud Transactions = CALCULATE(COUNTROWS(powerbi_txn), powerbi_txn[is_fraud] = 1)
Fraud Rate % = DIVIDE([Fraud Transactions], [Total Transactions])
Total Amount = SUM(powerbi_txn[amt])
Fraud Amount = CALCULATE(SUM(powerbi_txn[amt]), powerbi_txn[is_fraud] = 1)
Fraud Amount Share = DIVIDE([Fraud Amount], [Total Amount])
Flagged Transactions = CALCULATE(COUNTROWS(powerbi_txn), powerbi_txn[is_flagged] = 1)
Caught Fraud = CALCULATE(COUNTROWS(powerbi_txn), powerbi_txn[is_flagged] = 1, powerbi_txn[is_fraud] = 1)
Precision = DIVIDE([Caught Fraud], [Flagged Transactions])
Recall = DIVIDE([Caught Fraud], [Fraud Transactions])
F1 Score = DIVIDE(2 * [Precision] * [Recall], [Precision] + [Recall])
```
One line each: totals and fraud counts; fraud rate = fraud / all; amounts and the share of money lost to fraud; flagged = transactions where 2 or more rules fired; caught = flagged transactions that were really fraud; precision = caught / flagged; recall = caught / all fraud; F1 balances both.
Set formats: Fraud Rate %, Fraud Amount Share, Precision, Recall = Percentage (1 decimal).

## C. Report layout
**Page 1 - Overview**
- Cards: Total Transactions, Fraud Transactions, Fraud Rate %, Fraud Amount.
- Line chart: Date Table[Month] vs Fraud Transactions (monthly trend).
- Bar chart: category vs Fraud Rate %.
- Slicers: Date Table[Date] (between), category.

**Page 2 - Category, State and Hour**
- Clustered column: trans_hour vs Fraud Rate % (colour night hours 22 to 3 red using conditional formatting rules).
- Bar chart: state vs Fraud Rate % (Top N filter = 10 by Fraud Rate %, with Total Transactions >= 1000 as a visual filter).
- Matrix: category (rows) x risk_tier (columns), values = Fraud Transactions.
- Slicers: state, gender.

**Page 3 - Rule Performance**
- Cards: Precision, Recall, F1 Score, Flagged Transactions.
- Column chart: risk_tier vs Fraud Rate % (Clear, Low, Medium, High).
- Table: rule comparison (type values from the notebook/SQL Q5: amount, velocity, night, 2 or more rules with flagged, precision, recall).
- Slicer: category.

**Drill-through page (hidden) - Transaction Details**
- New page > in **Visualizations > Drill through** drag `category` into "Add drill-through fields here".
- Add a table: trans_time, amt, category, state, risk_tier, is_fraud. Right-click a category on Page 1 or 2 > **Drill through** > Transaction Details.

## D. Formatting tips
- Use one accent colour (blue) and one alert colour (red) for fraud/night only; grey for everything else.
- Titles on every visual, axis titles on, font size 12 or more, no 3D or pie charts.
- Format rates as percentages and amounts with thousands separators.
- Align visuals to a grid and keep slicers in one row at the top.
- Check contrast: dark text on light background; avoid red/green pairs only.
