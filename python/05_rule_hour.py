import pandas as pd

df = pd.read_csv("data/cleaned.csv", parse_dates=["trans_time"])
total_fraud = df["is_fraud"].sum()

# 1. Fraud rate by hour of day
by_hour = df.groupby("trans_hour")["is_fraud"].agg(["count", "sum", "mean"])
by_hour["mean"] = (by_hour["mean"] * 100).round(2)
by_hour.columns = ["transactions", "fraud", "fraud_rate_%"]
print(by_hour)

# 2. Fraud rate by category
by_cat = df.groupby("category")["is_fraud"].agg(["count", "sum", "mean"])
by_cat["mean"] = (by_cat["mean"] * 100).round(2)
by_cat.columns = ["transactions", "fraud", "fraud_rate_%"]
print(by_cat.sort_values("fraud_rate_%", ascending=False))

# 3. Test: night hours, alone and combined with amount
def report(name, flagged):
    n = flagged.sum()
    caught = (flagged & (df["is_fraud"] == 1)).sum()
    p = caught / n * 100 if n else 0
    r = caught / total_fraud * 100
    print(f"{name:<28} flagged={n:>7} caught={caught:>5} precision={p:5.1f}% recall={r:5.1f}%")

night = df["trans_hour"].isin([22, 23, 0, 1, 2, 3])
print()
report("night only", night)
for t in [200, 300, 400, 500]:
    report(f"night & amt > {t}", night & (df["amt"] > t))