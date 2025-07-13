# tests/test_email_alert.py

import pytest
from unittest.mock import patch
from chatbot.utils.email_alert import send_cost_alert


def test_send_cost_alert_success_ses(monkeypatch):
    mock_ses = lambda **kwargs: type("MockSES", (), {
        "send_email": lambda self, **kw: {"MessageId": "12345"}
    })()
    monkeypatch.setattr("boto3.client", mock_ses)

    result = send_cost_alert("Test Subject", "Test Body")
    assert result is True


def test_send_cost_alert_fallback_smtp(monkeypatch):
    class SESFail:
        def send_email(self, **kwargs):
            raise Exception("Simulated SES failure")

    monkeypatch.setattr("boto3.client", lambda *args, **kwargs: SESFail())

    monkeypatch.setattr("chatbot.utils.email_alert.send_email_smtp", lambda s, b: True)
    result = send_cost_alert("Fallback Test", "This should use SMTP")
    assert result is True
