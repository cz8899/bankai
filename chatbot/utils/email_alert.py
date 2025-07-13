# chatbot/utils/email_alert.py

import boto3
import smtplib
import os
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
        return True
    except Exception as e:
        print(f"[SMTP Fallback Failed] {str(e)}")
        return False


def send_cost_alert(subject: str, body: str) -> bool:
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
        print("[INFO] SES email sent successfully.")
        return True

    except ClientError as ses_error:
        print(f"[SES Failed] {ses_error.response['Error']['Message']}")
        print("[INFO] Attempting SMTP fallback...")
        return send_email_smtp(subject, body)
