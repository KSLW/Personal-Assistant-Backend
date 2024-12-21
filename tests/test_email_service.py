from unittest.mock import patch

from app.services.email_service import send_email


def test_send_email_success():
    with patch("app.services.email_service.mailer_client.send") as mock_send:
        mock_send.return_value = None
        result = send_email("test@example.com", "Test Subject", "Test Body")
        assert result["message"] == "Email sent successfully to test@example.com"
