import os
from dotenv import load_dotenv
load_dotenv()

from Services.email_service import EmailService

service = EmailService()
print(f"Enabled: {service.enabled}")

if service.enabled:
    print("Sending test email...")
    ok = service.send(
        to="jilisamkeloag7@gmail.com",
        subject="SPMS Test Email",
        body="This is a test from the SPMS app via Brevo API. If you see this, it works!",
    )
    print(f"Result: {'SUCCESS' if ok else 'FAILED'}")
else:
    print("Brevo not configured - check .env")
