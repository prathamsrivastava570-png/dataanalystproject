"""Run from the project root:  python tests/test_pipeline.py
Prints PASS / FAIL / SKIP per test and saves reports/test_results.csv"""
import importlib.util
import os
import pandas as pd

os.makedirs("reports", exist_ok=True)
results = []


def check(name, condition, detail=""):
    results.append({"test": name, "status": "PASS" if condition else "FAIL", "detail": detail})
    print(f"{'PASS' if condition else 'FAIL'}  {name}  {detail}")


def skip(name, detail):
    results.append({"test": name, "status": "SKIP", "detail": detail})
    print(f"SKIP  {name}  {detail}")


df = pd.read_csv("data/flagged.csv", parse_dates=["trans_time", "dob"])

# ---- keys ----
check("No duplicate transaction keys (trans_num)", df["trans_num"].is_unique,
      f"{df['trans_num'].duplicated().sum()} duplicates")

# ---- required fields ----
required = ["trans_num", "cc_num", "trans_time", "amt", "is_fraud", "category", "merchant", "state"]
miss = int(df[required].isnull().sum().sum())
check("No missing required fields", miss == 0, f"{miss} missing cells")

# ---- value ranges ----
check("Amount is positive", (df["amt"] > 0).all(), f"min={df['amt'].min()}")
check("is_fraud only 0 or 1", df["is_fraud"].isin([0, 1]).all())
check("Hour between 0 and 23", df["trans_hour"].between(0, 23).all())
check("Latitude/longitude in valid range",
      df["latitude"].between(-90, 90).all() and df["longitude"].between(-180, 180).all())
check("Rule flags are 0/1", df[["rule_amount", "rule_velocity", "rule_night"]].isin([0, 1]).all().all())
check("flag_count equals sum of the three rules",
      (df["flag_count"] == df[["rule_amount", "rule_velocity", "rule_night"]].sum(axis=1)).all())
check("Customer age between 10 and 110", df["age"].between(10, 110).all())

# ---- star schema integrity (built exactly as the Oracle load builds it) ----
spec = importlib.util.spec_from_file_location("loader", "python/08_load_oracle.py")
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
dim_card, dim_merchant, dim_category, dim_date, fact = loader.build_tables()

check("Fact rows equal source rows", len(fact) == len(df), f"{len(fact)} vs {len(df)}")
check("Every fact row has a matching card", fact["card_key"].isin(dim_card["card_key"]).all())
check("Every fact row has a matching merchant", fact["merchant_key"].isin(dim_merchant["merchant_key"]).all())
check("Every fact row has a matching category", fact["category_key"].isin(dim_category["category_key"]).all())
check("Every fact row has a matching date", fact["date_key"].isin(dim_date["date_key"]).all())
check("No duplicate dimension keys",
      dim_card["card_key"].is_unique and dim_merchant["merchant_key"].is_unique
      and dim_category["category_key"].is_unique and dim_date["date_key"].is_unique)

# ---- Python total equals SQL total (needs Oracle; skipped if it is not reachable) ----
try:
    import oracledb
    con = oracledb.connect(user="fraud_user", password="FraudPass2026", dsn="localhost:1521/XEPDB1")
    cur = con.cursor()

    def one(sql):
        cur.execute(sql)
        return cur.fetchone()

    n, fr, amt = one("SELECT COUNT(*), SUM(is_fraud), SUM(amt) FROM fact_transaction")
    check("Row count: Python = Oracle", n == len(df), f"py={len(df)} sql={n}")
    check("Fraud count: Python = Oracle", fr == int(df["is_fraud"].sum()), f"py={int(df['is_fraud'].sum())} sql={fr}")
    check("Total amount: Python = Oracle", abs(float(amt) - float(df["amt"].sum())) < 1,
          f"py={df['amt'].sum():.2f} sql={float(amt):.2f}")
    (orph,) = one("SELECT COUNT(*) FROM fact_transaction f LEFT JOIN dim_card k ON k.card_key=f.card_key "
                  "LEFT JOIN dim_merchant m ON m.merchant_key=f.merchant_key "
                  "LEFT JOIN dim_category c ON c.category_key=f.category_key "
                  "LEFT JOIN dim_date d ON d.date_key=f.date_key "
                  "WHERE k.card_key IS NULL OR m.merchant_key IS NULL OR c.category_key IS NULL OR d.date_key IS NULL")
    check("Oracle: no orphan fact rows", orph == 0, f"{orph} orphans")
    (mm,) = one("SELECT SUM(ABS(sql_rule_amount-py_rule_amount)+ABS(sql_rule_velocity-py_rule_velocity)"
                "+ABS(sql_rule_night-py_rule_night)) FROM vw_txn_rules")
    check("SQL rules match Python rules", mm == 0, f"{mm} mismatching flags")
    con.close()
except Exception as e:
    skip("Python vs Oracle totals", f"Oracle not reachable: {str(e)[:80]}")

out = pd.DataFrame(results)
out.to_csv("reports/test_results.csv", index=False)
print(f"\n{(out.status == 'PASS').sum()} passed, {(out.status == 'FAIL').sum()} failed, {(out.status == 'SKIP').sum()} skipped")
