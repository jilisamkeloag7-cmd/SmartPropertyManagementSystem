import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2

print("Testing Supabase connection...")
try:
    conn = psycopg2.connect(os.environ["DATABASE_URL"], connect_timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"Connected. Users in DB: {count}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
