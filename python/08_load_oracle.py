import pandas as pd

DSN = "localhost:1521/XEPDB1"


def build_tables(path="data/flagged.csv"):
    """Split the flat flagged.csv into a star schema (4 dimensions + 1 fact)."""
    df = pd.read_csv(path, parse_dates=["trans_time", "dob"])

    card_cols = ["cc_num", "first_name", "last_name", "gender", "dob", "job",
                 "street", "city", "state", "zip", "latitude", "longitude", "city_pop"]
    assert df.groupby("cc_num")[card_cols].nunique().max().max() == 1, "card attributes change!"
    dim_card = df[card_cols].drop_duplicates(subset="cc_num").reset_index(drop=True)
    dim_card.insert(0, "card_key", dim_card.index + 1)

    dim_merchant = (df[["merchant"]].drop_duplicates()
                    .rename(columns={"merchant": "merchant_name"}).reset_index(drop=True))
    dim_merchant.insert(0, "merchant_key", dim_merchant.index + 1)

    dim_category = (df[["category"]].drop_duplicates()
                    .rename(columns={"category": "category_name"}).reset_index(drop=True))
    dim_category.insert(0, "category_key", dim_category.index + 1)

    dates = pd.Series(df["trans_time"].dt.normalize().unique()).sort_values()
    dim_date = pd.DataFrame({"full_date": dates})
    dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year_num"] = dim_date["full_date"].dt.year
    dim_date["month_num"] = dim_date["full_date"].dt.month
    dim_date["day_num"] = dim_date["full_date"].dt.day
    dim_date["day_name"] = dim_date["full_date"].dt.day_name()
    dim_date["is_weekend"] = (dim_date["full_date"].dt.dayofweek >= 5).astype(int)
    dim_date = dim_date[["date_key", "full_date", "year_num", "month_num",
                         "day_num", "day_name", "is_weekend"]]

    fact = df.merge(dim_card[["card_key", "cc_num"]], on="cc_num")
    fact = fact.merge(dim_merchant.rename(columns={"merchant_name": "merchant"}), on="merchant")
    fact = fact.merge(dim_category.rename(columns={"category_name": "category"}), on="category")
    fact["date_key"] = fact["trans_time"].dt.strftime("%Y%m%d").astype(int)
    fact = fact.rename(columns={"rule_amount": "py_rule_amount", "rule_velocity": "py_rule_velocity",
                                "rule_night": "py_rule_night", "flag_count": "py_flag_count"})
    fact = fact[["trans_num", "card_key", "merchant_key", "category_key", "date_key",
                 "trans_time", "trans_hour", "amt", "merch_latitude", "merch_longitude",
                 "is_fraud", "py_rule_amount", "py_rule_velocity", "py_rule_night",
                 "py_flag_count"]]
    assert len(fact) == len(df), "row count changed during merge"
    assert fact["trans_num"].is_unique, "duplicate trans_num"

    # dates as text; Oracle converts them with TO_DATE / TO_TIMESTAMP
    dim_card["dob"] = dim_card["dob"].dt.strftime("%Y-%m-%d")
    dim_date["full_date"] = dim_date["full_date"].dt.strftime("%Y-%m-%d")
    fact["trans_time"] = fact["trans_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return dim_card, dim_merchant, dim_category, dim_date, fact


def load(cur, sql, frame, batch=50000):
    data = frame.astype(object).where(frame.notna(), None).values.tolist()
    for i in range(0, len(data), batch):
        cur.executemany(sql, data[i:i + batch])
    print(f"loaded {len(data):>7} rows -> {sql.split()[2]}")


def main():
    import oracledb
    dim_card, dim_merchant, dim_category, dim_date, fact = build_tables()
    con = oracledb.connect(user="fraud_user", password="FraudPass2026", dsn=DSN)
    cur = con.cursor()
    load(cur, "INSERT INTO dim_card VALUES (:1,:2,:3,:4,:5,TO_DATE(:6,'YYYY-MM-DD'),"
              ":7,:8,:9,:10,:11,:12,:13,:14)", dim_card)
    load(cur, "INSERT INTO dim_merchant VALUES (:1,:2)", dim_merchant)
    load(cur, "INSERT INTO dim_category VALUES (:1,:2)", dim_category)
    load(cur, "INSERT INTO dim_date VALUES (:1,TO_DATE(:2,'YYYY-MM-DD'),:3,:4,:5,:6,:7)", dim_date)
    load(cur, "INSERT INTO fact_transaction VALUES (:1,:2,:3,:4,:5,"
              "TO_TIMESTAMP(:6,'YYYY-MM-DD HH24:MI:SS'),:7,:8,:9,:10,:11,:12,:13,:14,:15)", fact)
    con.commit()
    for t in ["dim_card", "dim_merchant", "dim_category", "dim_date", "fact_transaction"]:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"Oracle {t}: {cur.fetchone()[0]}")
    con.close()


if __name__ == "__main__":
    main()
