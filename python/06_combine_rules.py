import pandas as pd

df = pd.read_csv("data/cleaned.csv", parse_dates=["trans_time"])
df = df.sort_values(["cc_num", "trans_time"]).reset_index(drop=True)

# ---- The three rules ----
df["rule_amount"] = df["amt"] > 600

counts = (
    df.set_index("trans_time")
      .groupby("cc_num")["amt"]
      .rolling("30min")
      .count()
      .values
)
df["rule_velocity"] = counts >= 3

night_hours = [22, 23, 0, 1, 2, 3]
df["rule_night"] = df["trans_hour"].isin(night_hours) & (df["amt"] > 300)

rules = ["rule_amount", "rule_velocity", "rule_night"]
df["flag_count"] = df[rules].sum(axis=1)

# ---- Evaluation ----
total_fraud = (df["is_fraud"] == 1).sum()

def report(name, flagged):
    n = flagged.sum()
    caught = (flagged & (df["is_fraud"] == 1)).sum()
    p = caught / n * 100 if n else 0
    r = caught / total_fraud * 100
    f1 = 2 * p * r / (p + r) if (p + r) else 0
    print(f"{name:<28} flagged={n:>6} caught={caught:>5} "
          f"precision={p:5.1f}% recall={r:5.1f}% F1={f1:5.1f}")

print("EACH RULE ALONE")
report("amount > 600", df["rule_amount"])
report("velocity (3 in 30 min)", df["rule_velocity"])
report("night & amt > 300", df["rule_night"])

print("\nCOMBINATIONS")
report("any 1 or more rules", df["flag_count"] >= 1)
report("2 or more rules", df["flag_count"] >= 2)
report("all 3 rules", df["flag_count"] == 3)
report("amount OR night", df["rule_amount"] | df["rule_night"])
report("amount AND velocity", df["rule_amount"] & df["rule_velocity"])
report("night AND velocity", df["rule_night"] & df["rule_velocity"])

# ---- Save flags for Oracle and Power BI ----
df[rules] = df[rules].astype(int)
df.to_csv("data/flagged.csv", index=False)
print("\nSaved data/flagged.csv")