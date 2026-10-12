import os, smtplib, ssl
from dotenv import load_dotenv
load_dotenv()

host = os.environ.get("SMTP_HOST")
user = os.environ.get("SMTP_USER")
pw   = os.environ.get("SMTP_PASS")

print("=" * 50)
print("TEST 1: TLS 1.2 handshake with custom ciphers")
print("=" * 50)
try:
    context = ssl.create_default_context()
    context.set_ciphers("DEFAULT@SECLEVEL=1")

    s = smtplib.SMTP(host, 587, timeout=15)
    s.ehlo()
    s.starttls(context=context)
    s.ehlo()
    print("  handshake OK, attempting login...")
    s.login(user, pw)
    print("  ? LOGIN OK with TLS 1.2")
    s.quit()
except Exception as e:
    print(f"  ? FAILED: {type(e).__name__}: {e}")
