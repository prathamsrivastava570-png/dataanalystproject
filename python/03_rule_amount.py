import pandas as pd

df = pd.read_csv("data/cleaned.csv")

# 1. Compare amounts: fraud (1) vs normal (0)
print(df.groupby("is_fraud")["amt"].describe().round(2))

# 2. Test different thresholds
total_fraud = df["is_fraud"].sum()
print("\nThreshold | Flagged | Caught fraud | Precision % | Recall %")
for t in [200, 300, 400, 500, 600, 800, 1000]:
    flagged = df["amt"] > t
    caught = (flagged & (df["is_fraud"] == 1)).sum()
    n = flagged.sum()
    precision = caught / n * 100 if n else 0
    recall = caught / total_fraud * 100
    print(f"{t:>9} | {n:>7} | {caught:>12} | {precision:>11.1f} | {recall:>8.1f}")