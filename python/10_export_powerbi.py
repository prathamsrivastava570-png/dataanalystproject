"""Exports a flat Power BI table (same fields as Oracle view vw_powerbi_txn) and a 100k-row Excel sample."""
import os
import pandas as pd

df = pd.read_csv("data/flagged.csv", parse_dates=["trans_time"])
os.makedirs("data/load", exist_ok=True)

tier = {0: "Clear", 1: "Low", 2: "Medium", 3: "High"}
out = pd.DataFrame({
    "trans_num": df["trans_num"],
    "trans_time": df["trans_time"],
    "trans_date": df["trans_time"].dt.strftime("%Y-%m-%d"),
    "year_num": df["trans_time"].dt.year,
    "month_num": df["trans_time"].dt.month,
    "day_name": df["trans_time"].dt.day_name(),
    "trans_hour": df["trans_hour"],
    "amt": df["amt"],
    "is_fraud": df["is_fraud"],
    "category": df["category"],
    "merchant": df["merchant"],
    "state": df["state"],
    "gender": df["gender"],
    "rule_amount": df["rule_amount"],
    "rule_velocity": df["rule_velocity"],
    "rule_night": df["rule_night"],
    "flag_count": df["flag_count"],
    "risk_tier": df["flag_count"].map(tier),
    "is_flagged": (df["flag_count"] >= 2).astype(int),
})
out.to_csv("data/load/powerbi_txn.csv", index=False)
print("powerbi_txn.csv rows:", len(out))

# Excel sample: all transactions of 75 cards (keeps every card's history intact)
cards = df["cc_num"].drop_duplicates().sample(75, random_state=7)
ex = out[df["cc_num"].isin(cards)]
ex.to_csv("data/load/excel_sample.csv", index=False)
print("excel_sample.csv rows:", len(ex), "| fraud:", int(ex["is_fraud"].sum()),
      "| total amount:", round(ex["amt"].sum(), 2), "| flagged:", int(ex["is_flagged"].sum()))
