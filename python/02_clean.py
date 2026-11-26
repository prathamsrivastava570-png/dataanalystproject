"""Cleaning step. Every fix is counted and written to docs/data_quality_log.csv.
Nothing is dropped silently: removed rows are always logged with a count."""
import os
import pandas as pd

os.makedirs("docs", exist_ok=True)
os.makedirs("reports", exist_ok=True)
log = []


def note(issue, rule, rows):
    log.append({"issue": issue, "rule_applied": rule, "rows_affected": int(rows)})


df = pd.read_csv("data/sample.csv")
rows_start = len(df)

# 1. Redundant index column from the Kaggle export
df = df.drop(columns=["Unnamed: 0"])
note("Redundant index column 'Unnamed: 0'", "Dropped the column (no rows removed)", rows_start)

# 2. Column names that are reserved or ambiguous in Oracle
df = df.rename(columns={
    "trans_date_trans_time": "trans_time", "first": "first_name", "last": "last_name",
    "lat": "latitude", "long": "longitude",
    "merch_lat": "merch_latitude", "merch_long": "merch_longitude"})
note("Reserved/ambiguous column names (LONG, FIRST, LAST, ...)",
     "Renamed 7 columns, e.g. long -> longitude", rows_start)

# 3. Text standardisation
text_cols = ["merchant", "category", "first_name", "last_name", "street", "city", "job"]
changed = pd.Series(False, index=df.index)
for c in text_cols:
    s = df[c].astype(str)
    st = s.str.strip()
    changed |= (s != st)
    df[c] = st
for c, fn in [("state", str.upper), ("gender", str.upper)]:
    s = df[c].astype(str)
    st = s.str.strip().map(fn)
    changed |= (s != st)
    df[c] = st
note("Stray whitespace / inconsistent case in text columns",
     "Trimmed text; upper-cased state and gender", changed.sum())

# 4. Data types
df["trans_time"] = pd.to_datetime(df["trans_time"], errors="coerce")
df["dob"] = pd.to_datetime(df["dob"], errors="coerce")
bad_dates = df["trans_time"].isna() | df["dob"].isna()
note("Unparseable transaction or birth dates", "Removed rows with invalid dates (logged)", bad_dates.sum())
df = df[~bad_dates]

# 5. Missing required fields
required = ["trans_num", "cc_num", "trans_time", "amt", "is_fraud", "category", "merchant"]
missing = df[required].isnull().any(axis=1)
note("Missing values in required fields", "Removed rows with a missing required field (logged)", missing.sum())
df = df[~missing]

# 6. Invalid fraud label
bad_label = ~df["is_fraud"].isin([0, 1])
note("is_fraud not in {0,1}", "Removed rows with an invalid label (logged)", bad_label.sum())
df = df[~bad_label]

# 7. Duplicate transactions
dupes = df.duplicated(subset="trans_num").sum()
note("Duplicate transactions (same trans_num)", "Kept first occurrence, removed the rest", dupes)
df = df.drop_duplicates(subset="trans_num")

# 8. Invalid amounts
bad_amt = (df["amt"] <= 0).sum()
note("Zero or negative transaction amounts", "Removed rows with amt <= 0 (logged)", bad_amt)
df = df[df["amt"] > 0]

# 9. Consistency check: one card = one set of customer attributes
card_cols = ["first_name", "last_name", "gender", "dob", "job", "street", "city", "state", "zip"]
inconsistent = (df.groupby("cc_num")[card_cols].nunique().max(axis=1) > 1).sum()
note("Cards whose customer attributes change between rows", "Check only; no fix needed" if inconsistent == 0
     else "Check only; investigate", inconsistent)

# 10. Rows kept on purpose but worth reporting
df = df.sort_values(["cc_num", "trans_time"]).reset_index(drop=True)
df["trans_hour"] = df["trans_time"].dt.hour
note("Transactions in the midnight hour (00:00-00:59)", "Retained; hour 0 is a valid hour and is used by the night rule",
     (df["trans_hour"] == 0).sum())
note("Extreme amounts above 1,000 (median is about 47)", "Retained; amount rule thresholds handle them",
     (df["amt"] > 1000).sum())

# 11. Helper columns
df["trans_date"] = df["trans_time"].dt.date
df["trans_dow"] = df["trans_time"].dt.day_name()
df["age"] = (df["trans_time"] - df["dob"]).dt.days // 365

df.to_csv("data/cleaned.csv", index=False)
logdf = pd.DataFrame(log)
logdf.to_csv("docs/data_quality_log.csv", index=False)

report = f"""DATA QUALITY REPORT
Rows before cleaning:      {rows_start}
Rows after cleaning:       {len(df)}
Rows removed:              {rows_start - len(df)}
Fraud rows:                {df['is_fraud'].sum()}
Fraud rate (%):            {round(df['is_fraud'].mean() * 100, 2)}
Cards:                     {df['cc_num'].nunique()}
Date range:                {df['trans_time'].min()} to {df['trans_time'].max()}
Amount min / max:          {df['amt'].min()} / {df['amt'].max()}
"""
print(report)
print(logdf.to_string(index=False))
with open("docs/data_quality_report.txt", "w") as f:
    f.write(report)
