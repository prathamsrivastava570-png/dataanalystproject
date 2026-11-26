import os
import sys
import oracledb
import pandas as pd

path = sys.argv[1]
con = oracledb.connect(user="fraud_user", password="FraudPass2026",
                       dsn="localhost:1521/XEPDB1")
cur = con.cursor()

text = open(path, encoding="utf-8").read()
text = "\n".join(l for l in text.splitlines() if not l.strip().startswith("--"))
os.makedirs("reports", exist_ok=True)

n = 0
for stmt in [s.strip() for s in text.split(";") if s.strip()]:
    if stmt.upper().startswith(("SELECT", "WITH")):
        n += 1
        cur.execute(stmt)
        df = pd.DataFrame(cur.fetchall(), columns=[c[0] for c in cur.description])
        print(f"\n--- result {n} ---")
        print(df.head(30).to_string(index=False))
        df.to_csv(f"reports/{os.path.basename(path)[:-4]}_q{n}.csv", index=False)
    else:
        cur.execute(stmt)
        print("OK:", " ".join(stmt.split()[:5]))
con.commit()
con.close()
