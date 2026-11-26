"""KPIs -> reports/kpis.json and 4 charts -> reports/charts/*.png"""
import json
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/flagged.csv", parse_dates=["trans_time"])
os.makedirs("reports/charts", exist_ok=True)

# Assumption: final rule = flagged when 2 or more of the 3 rules fire.
# Assumption: precision/recall are measured against the labelled is_fraud column.
total = len(df)
fraud = int(df["is_fraud"].sum())
flagged = df["flag_count"] >= 2
caught = int((flagged & (df["is_fraud"] == 1)).sum())
precision = caught / flagged.sum()
recall = caught / fraud

kpis = {
    "total_transactions": total,
    "fraud_transactions": fraud,
    "fraud_rate_pct": round(fraud / total * 100, 2),
    "total_amount": round(float(df["amt"].sum()), 2),
    "fraud_amount": round(float(df.loc[df["is_fraud"] == 1, "amt"].sum()), 2),
    "avg_fraud_amount": round(float(df.loc[df["is_fraud"] == 1, "amt"].mean()), 2),
    "avg_normal_amount": round(float(df.loc[df["is_fraud"] == 0, "amt"].mean()), 2),
    "flagged_transactions": int(flagged.sum()),
    "caught_fraud": caught,
    "precision_pct": round(precision * 100, 1),
    "recall_pct": round(recall * 100, 1),
    "f1": round(2 * precision * recall / (precision + recall) * 100, 1),
    "night_share_of_fraud_pct": round(
        df.loc[(df["is_fraud"] == 1) & df["trans_hour"].isin([22, 23, 0, 1, 2, 3])].shape[0] / fraud * 100, 1),
}
with open("reports/kpis.json", "w") as f:
    json.dump(kpis, f, indent=2)
print(json.dumps(kpis, indent=2))

BLUE, RED, GREY = "#2b6cb0", "#c53030", "#a0aec0"

# Chart 1: monthly trend
m = df.groupby(df["trans_time"].dt.to_period("M").astype(str))["is_fraud"].sum()
plt.figure(figsize=(10, 4.5))
plt.plot(m.index, m.values, marker="o", color=BLUE)
plt.title("Fraud transactions per month")
plt.xlabel("Month")
plt.ylabel("Fraud transactions")
plt.xticks(rotation=60)
plt.tight_layout()
plt.savefig("reports/charts/1_monthly_trend.png", dpi=150)
plt.close()

# Chart 2: fraud rate by state (top 10, "region" = customer state)
s = df.groupby("state")["is_fraud"].agg(["mean", "count"])
s = s[s["count"] >= 1000].sort_values("mean", ascending=False).head(10)
plt.figure(figsize=(9, 4.5))
plt.bar(s.index, s["mean"] * 100, color=BLUE)
plt.title("Fraud rate by state (top 10, states with 1,000+ transactions)")
plt.xlabel("State")
plt.ylabel("Fraud rate (%)")
plt.tight_layout()
plt.savefig("reports/charts/2_fraud_rate_by_state.png", dpi=150)
plt.close()

# Chart 3: fraud rate by category
c = df.groupby("category")["is_fraud"].mean().sort_values() * 100
plt.figure(figsize=(9, 5.5))
plt.barh(c.index, c.values, color=BLUE)
plt.title("Fraud rate by merchant category")
plt.xlabel("Fraud rate (%)")
plt.ylabel("Category")
plt.tight_layout()
plt.savefig("reports/charts/3_fraud_rate_by_category.png", dpi=150)
plt.close()

# Chart 4: problem area = night hours
h = df.groupby("trans_hour")["is_fraud"].mean() * 100
colors = [RED if x in [22, 23, 0, 1, 2, 3] else GREY for x in h.index]
plt.figure(figsize=(10, 4.5))
plt.bar(h.index, h.values, color=colors)
plt.title("Fraud rate by hour of day (night hours 22:00-03:59 in red)")
plt.xlabel("Hour of day")
plt.ylabel("Fraud rate (%)")
plt.xticks(range(24))
plt.tight_layout()
plt.savefig("reports/charts/4_fraud_rate_by_hour.png", dpi=150)
plt.close()
print("Saved 4 charts to reports/charts/")
