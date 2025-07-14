import os
import time
import json
import smtplib
import hashlib
import boto3
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from botocore.exceptions import ClientError
from chatbot.utils.constants import (
    ALERT_EMAIL_FROM,
    ALERT_EMAIL_TO,
    AWS_REGION,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD
)

# Memory cache to prevent duplicate alerts
_ALERT_CACHE = {}

# === Helper: SHA1 digest of body ===
def _hash_body(body: str) -> str:
    return hashlib.sha1(body.encode("utf-8")).hexdigest()


# === SES Sender with retry ===
def send_email_ses(subject: str, body: str) -> bool:
    try:
        ses = boto3.client("ses", region_name=AWS_REGION)
        ses.send_email(
            Source=ALERT_EMAIL_FROM,
            Destination={"ToAddresses": [ALERT_EMAIL_TO]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}}
            }
        )
        print("[✅ SES] Email sent successfully.")
        return True

    except ClientError as ses_error:
        print(f"[❌ SES Failed] {ses_error.response['Error']['Message']}")
        return False


# === SMTP Fallback Sender ===
def send_email_smtp(subject: str, body: str) -> bool:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = ALERT_EMAIL_FROM
    msg["To"] = ALERT_EMAIL_TO

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(ALERT_EMAIL_FROM, ALERT_EMAIL_TO, msg.as_string())
        print("[✅ SMTP] Email sent via fallback.")
        return True
    except Exception as e:
        print(f"[❌ SMTP Failed] {str(e)}")
        return False


# === Public: Cost Alert Sender ===
def send_cost_alert(subject: str, body: str, dedup_window_minutes: int = 15) -> bool:
    if not ALERT_EMAIL_FROM or not ALERT_EMAIL_TO:
        print("[⚠️ ENV] Missing required email environment variables.")
        return False

    digest = _hash_body(body)
    now = datetime.utcnow()

    # Check deduplication cache
    if digest in _ALERT_CACHE:
        last_sent = _ALERT_CACHE[digest]
        if now - last_sent < timedelta(minutes=dedup_window_minutes):
            print("[🛑 Dedup] Skipping duplicate alert.")
            return False

    print("[🔔 Alert] Sending cost alert...")

    # Try SES first
    if send_email_ses(subject, body):
        _ALERT_CACHE[digest] = now
        return True

    # Fallback to SMTP
    if send_email_smtp(subject, body):
        _ALERT_CACHE[digest] = now
        return True

    print("[❌ Alert Failed] Both SES and SMTP failed.")
    return False
