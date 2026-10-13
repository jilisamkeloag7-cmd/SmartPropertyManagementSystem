import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2

print("=" * 50)
print("SUPABASE DATA CHECK")
print("=" * 50)
conn = psycopg2.connect(os.environ["DATABASE_URL"], connect_timeout=10)
cur = conn.cursor()

for table in ["users", "properties", "ownerships", "leases", "payments"]:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"{table:20s}: {cur.fetchone()[0]} rows")

print()
print("Property statuses:")
cur.execute("SELECT status, COUNT(*) FROM properties GROUP BY status")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

cur.close()
conn.close()
