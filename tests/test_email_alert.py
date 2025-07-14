import pytest
from unittest.mock import patch, MagicMock
from chatbot.utils.email_alert import send_cost_alert, send_email_smtp

# === Constants ===
TEST_SUBJECT = "Test Alert"
TEST_BODY = "This is a test email from DevGenius."

# === Test: SES success ===
@patch("chatbot.utils.email_alert.boto3.client")
def test_send_cost_alert_ses_success(mock_boto_client):
    mock_ses = MagicMock()
    mock_ses.send_email.return_value = {"MessageId": "123"}
    mock_boto_client.return_value = mock_ses

    success = send_cost_alert(TEST_SUBJECT, TEST_BODY)
    assert success is True
    mock_ses.send_email.assert_called_once()

# === Test: SES failure triggers SMTP fallback success ===
@patch("chatbot.utils.email_alert.send_email_smtp", return_value=True)
@patch("chatbot.utils.email_alert.boto3.client")
def test_send_cost_alert_ses_failure_fallback_success(mock_boto_client, mock_smtp):
    mock_ses = MagicMock()
    error = Exception("Simulated SES error")
    error.response = {"Error": {"Message": "Simulated SES failure"}}
    mock_ses.send_email.side_effect = error
    mock_boto_client.return_value = mock_ses

    success = send_cost_alert(TEST_SUBJECT, TEST_BODY)
    assert success is True
    mock_smtp.assert_called_once()

# === Test: SES + SMTP failure ===
@patch("chatbot.utils.email_alert.send_email_smtp", return_value=False)
@patch("chatbot.utils.email_alert.boto3.client")
def test_send_cost_alert_total_failure(mock_boto_client, mock_smtp):
    mock_ses = MagicMock()
    error = Exception("Complete SES failure")
    error.response = {"Error": {"Message": "Fail"}}
    mock_ses.send_email.side_effect = error
    mock_boto_client.return_value = mock_ses

    success = send_cost_alert(TEST_SUBJECT, TEST_BODY)
    assert success is False
    mock_smtp.assert_called_once()

# === Test: SMTP only ===
@patch("smtplib.SMTP")
def test_send_email_smtp_success(mock_smtp_class):
    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp
    success = send_email_smtp(TEST_SUBJECT, TEST_BODY)
    assert success is True
    mock_smtp.starttls.assert_called_once()
    mock_smtp.login.assert_called_once()
    mock_smtp.sendmail.assert_called_once()

@patch("smtplib.SMTP", side_effect=Exception("SMTP failed"))
def test_send_email_smtp_failure(mock_smtp_class):
    success = send_email_smtp(TEST_SUBJECT, TEST_BODY)
    assert success is False
