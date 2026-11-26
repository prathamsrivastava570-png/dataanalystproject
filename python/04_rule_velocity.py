import pandas as pd

df = pd.read_csv("data/cleaned.csv", parse_dates=["trans_time"])
df = df.sort_values(["cc_num", "trans_time"]).reset_index(drop=True)

is_fraud = df["is_fraud"].values == 1
total_fraud = is_fraud.sum()

print("Window | Min txns | Flagged | Caught fraud | Precision % | Recall %")
for w in [10, 30, 60]:
    # For each transaction: how many transactions did the SAME card make
    # in the last w minutes (including this one)?
    counts = (
        df.set_index("trans_time")
          .groupby("cc_num")["amt"]
          .rolling(f"{w}min")
          .count()
          .values
    )
    for k in [2, 3, 4]:
        flagged = counts >= k
        n = flagged.sum()
        caught = (flagged & is_fraud).sum()
        precision = caught / n * 100 if n else 0
        recall = caught / total_fraud * 100
        print(f"{w:>5}m | {k:>8} | {n:>7} | {caught:>12} | {precision:>11.1f} | {recall:>8.1f}")