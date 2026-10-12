import os, smtplib, ssl
from dotenv import load_dotenv
load_dotenv()

host = os.environ.get("SMTP_HOST")
user = os.environ.get("SMTP_USER")
pw   = os.environ.get("SMTP_PASS")

print("=" * 50)
print("TEST 2: SSL verification bypassed (diagnostic only)")
print("=" * 50)
try:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    s = smtplib.SMTP(host, 587, timeout=15)
    s.ehlo()
    s.starttls(context=context)
    s.ehlo()
    print("  handshake OK, attempting login...")
    s.login(user, pw)
    print("  ? LOGIN OK with bypass")
    s.quit()
except Exception as e:
    print(f"  ? FAILED: {type(e).__name__}: {e}")
