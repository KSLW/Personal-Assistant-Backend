from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app, get_current_user
from app.models import Reminder
from app.main import Dict

client = TestClient(app)

# Override the dependency for get_current_user
app.dependency_overrides[get_current_user] = lambda: {"uid": "mock_user_id"}

# Test for creating a reminder

def add_reminder(user_id: str, reminder: Reminder) -> Dict:
    try:
        user_ref = db.collection("users").document(user_id)
        user_data = user_ref.get()

        if not user_data.exists:
            user_ref.set({"reminders": []})

        reminder_data = reminder.model_dump()  # Updated method
        reminder_data.update(
            {
                "id": db.collection("users").document().id,
                "sent": False,
            }
        )
        user_ref.update({"reminders": firestore.ArrayUnion([reminder_data])})
        logger.info(f"Added reminder for user: {user_id}")
        return {"message": "Reminder added successfully", "reminder": reminder_data}
    except Exception as e:
        logger.error(f"Failed to add reminder for user {user_id}: {str(e)}")
        return {"error": f"Failed to add reminder: {str(e)}"}


@patch("app.services.firestore_service.add_reminder")
def test_create_reminder(mock_add_reminder):
    mock_add_reminder.return_value = {
        "message": "Reminder added successfully",
        "reminder": {
            "title": "Meeting",
            "due_date": "2024-12-31T10:00:00",
            "sent": False,
            "recurring": False,
            "id": "mock_reminder_id",
        },
    }

    headers = {"Authorization": "Bearer mock_token"}
    data = {"title": "Meeting", "due_date": "2024-12-31T10:00:00"}
    response = client.post("/reminders", json=data, headers=headers)

    assert response.status_code == 200

    # Extract the response JSON and ignore the 'id' field
    response_json = response.json()
    assert response_json["message"] == "Reminder added successfully"
    assert response_json["reminder"]["title"] == "Meeting"
    assert response_json["reminder"]["due_date"] == "2024-12-31T10:00:00"
    assert response_json["reminder"]["sent"] is False
    assert response_json["reminder"]["recurring"] is False