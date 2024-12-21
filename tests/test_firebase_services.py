from unittest.mock import patch

from app.services.firestore_service import add_reminder


def test_add_reminder_success():
    user_id = "test_user"
    reminder = {"title": "Test Reminder", "due_date": "2024-12-31T10:00:00"}

    with patch("app.services.firestore_service.db.collection") as mock_db:
        mock_db.return_value.document.return_value.update.return_value = None
        result = add_reminder(user_id, reminder)
        assert result["message"] == "Reminder added successfully"
