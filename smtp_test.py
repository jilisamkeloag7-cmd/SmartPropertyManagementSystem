import os, smtplib, ssl
from dotenv import load_dotenv
load_dotenv()

print("=" * 50)
print("SMTP DIAGNOSTIC")
print("=" * 50)

host = os.environ.get("SMTP_HOST", "").strip()
port = os.environ.get("SMTP_PORT", "587").strip()
user = os.environ.get("SMTP_USER", "").strip()
pw   = os.environ.get("SMTP_PASS", "").strip()

print(f"Host: [{host}]")
print(f"Port: [{port}]")
print(f"User: [{user}]")
print(f"Pass length: {len(pw)} chars")
print(f"Pass repr: {repr(pw)}")
print()

# ---- Attempt 1: port 587 with STARTTLS
print("--- ATTEMPT 1: port 587 + STARTTLS ---")
try:
    s = smtplib.SMTP(host, int(port), timeout=15)
    s.ehlo()
    ctx = ssl.create_default_context()
    s.starttls(context=ctx)
    s.ehlo()
    print("  handshake OK, attempting login...")
    s.login(user, pw)
    print("  LOGIN OK on 587")
    s.quit()
except Exception as e:
    print(f"  FAILED on 587: {type(e).__name__}: {e}")

print()

# ---- Attempt 2: port 465 with SSL (implicit)
print("--- ATTEMPT 2: port 465 + SSL ---")
try:
    ctx = ssl.create_default_context()
    s2 = smtplib.SMTP_SSL(host, 465, timeout=15, context=ctx)
    print("  SSL handshake OK, attempting login...")
    s2.login(user, pw)
    print("  LOGIN OK on 465")
    s2.quit()
except Exception as e:
    print(f"  FAILED on 465: {type(e).__name__}: {e}")

print()
print("Diagnostic complete.")
