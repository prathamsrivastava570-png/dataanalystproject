import getpass
import oracledb

DSN = "localhost:1521/XEPDB1"
syspw = getpass.getpass("Oracle SYSTEM password (the one you set at install): ")

con = oracledb.connect(user="system", password=syspw, dsn=DSN)
cur = con.cursor()
try:
    cur.execute("DROP USER fraud_user CASCADE")
except oracledb.DatabaseError:
    pass  # user did not exist yet
cur.execute("CREATE USER fraud_user IDENTIFIED BY FraudPass2026 "
            "DEFAULT TABLESPACE USERS QUOTA UNLIMITED ON USERS")
cur.execute("GRANT CONNECT, RESOURCE, CREATE VIEW TO fraud_user")
con.close()
print("User fraud_user created")

con = oracledb.connect(user="fraud_user", password="FraudPass2026", dsn=DSN)
cur = con.cursor()
text = open("sql/01_schema.sql", encoding="utf-8").read()
for stmt in [s.strip() for s in text.split(";") if s.strip()]:
    cur.execute(stmt)
    print("OK:", " ".join(stmt.split()[:3]))
con.close()
print("Schema created")
