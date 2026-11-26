import pandas as pd

df = pd.read_csv("data/fraudTrain.csv")

print("Shape:", df.shape)
print(df.dtypes)
print(df.isnull().sum())
print(df["is_fraud"].value_counts())
print("Fraud %:", round(df["is_fraud"].mean() * 100, 2))
print("Unique cards:", df["cc_num"].nunique())

cards = df["cc_num"].drop_duplicates().sample(500, random_state=42)
sample = df[df["cc_num"].isin(cards)]
sample.to_csv("data/sample.csv", index=False)

print("Sample rows:", len(sample))
print("Sample fraud rows:", sample["is_fraud"].sum())
