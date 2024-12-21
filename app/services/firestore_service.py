import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Union, Optional

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")

# Initialize Firestore
db = firestore.client()

# Utility Functions


def parse_iso_date(date_str: str) -> datetime:
    try:
        return datetime.fromisoformat(date_str)
    except ValueError as e:
        logger.error(f"Invalid ISO date format: {date_str}")
        raise ValueError(f"Invalid ISO date format: {date_str}") from e


def get_user_data(user_id: str) -> Union[Dict, str]:
    try:
        user_ref = db.collection("users").document(user_id)
        user_data = user_ref.get()
        if not user_data.exists:
            logger.warning(f"User not found: {user_id}")
            return "User not found"
        logger.info(f"Retrieved data for user: {user_id}")
        return user_data.to_dict()
    except Exception as e:
        logger.error(f"Failed to retrieve user data for {user_id}: {str(e)}")
        return "Error retrieving user data"

# Pydantic Models


class ReminderModel(BaseModel):
    title: str
    due_date: str
    recurring: Optional[bool] = False
    recurrence_interval: Optional[str] = None


class TaskModel(BaseModel):
    title: str
    due_date: str
    priority: Optional[str] = None
    category: Optional[str] = None
    recurring: Optional[bool] = False
    recurrence_interval: Optional[str] = None

# Shared Functions


def update_collection(user_id: str, collection: str, updates: List[Dict]):
    try:
        user_ref = db.collection("users").document(user_id)
        user_ref.update({collection: updates})
        logger.info(f"Updated {collection} for user: {user_id}")
    except Exception as e:
        logger.error(f"Failed to update {collection} for user {user_id}: {str(e)}")

# Reminder Functions


def get_reminders(user_id: str) -> Union[List, Dict]:
    user_data = get_user_data(user_id)
    if isinstance(user_data, str):
        return {"error": user_data}
    logger.info(f"Retrieved reminders for user: {user_id}")
    return user_data.get("reminders", [])


def add_reminder(user_id: str, reminder: Union[Dict, ReminderModel]) -> Dict:
    try:
        user_ref = db.collection("users").document(user_id)
        user_data = user_ref.get()

        if not user_data.exists:
            user_ref.set({"reminders": []})

        # Use .model_dump() if the reminder is a Pydantic model; otherwise, leave it as is
        reminder_data = reminder.model_dump() if isinstance(reminder, ReminderModel) else reminder
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


def update_reminder(user_id: str, reminder_id: str, updates: Dict) -> Dict:
    try:
        user_data = get_user_data(user_id)

        if isinstance(user_data, str):
            return {"error": user_data}

        reminders = user_data.get("reminders", [])
        updated_reminders = [
            {**reminder, **updates} if reminder["id"] == reminder_id else reminder
            for reminder in reminders
        ]
        update_collection(user_id, "reminders", updated_reminders)
        return {"message": "Reminder updated successfully"}
    except Exception as e:
        logger.error(
            f"Failed to update reminder {reminder_id} for user {user_id}: {str(e)}"
        )
        return {"error": f"Failed to update reminder: {str(e)}"}
    

def reschedule_recurring_reminders(user_id: str) -> Dict:
    try:
        user_data = get_user_data(user_id)

        if isinstance(user_data, str):
            return {
                "message": f"No reminders found for user {user_id}. Skipping rescheduling."
            }

        reminders = user_data.get("reminders", [])
        updated_reminders = []
        for reminder in reminders:
            if reminder.get("recurring", False) and reminder.get("sent", False):
                due_date = parse_iso_date(reminder["due_date"])
                if reminder["recurrence_interval"] == "daily":
                    new_due_date = due_date + timedelta(days=1)
                elif reminder["recurrence_interval"] == "weekly":
                    new_due_date = due_date + timedelta(weeks=1)
                elif reminder["recurrence_interval"] == "monthly":
                    new_due_date = due_date + timedelta(days=30)
                else:
                    continue

                updated_reminders.append(
                    {**reminder, "due_date": new_due_date.isoformat(), "sent": False}
                )
            else:
                updated_reminders.append(reminder)

        update_collection(user_id, "reminders", updated_reminders)
        return {"message": "Recurring reminders rescheduled"}
    except Exception as e:
        logger.error(f"Failed to reschedule reminders for user {user_id}: {str(e)}")
        return {"error": f"Failed to reschedule reminders: {str(e)}"}

# Task Functions


def get_tasks(user_id: str) -> Union[List, Dict]:
    user_data = get_user_data(user_id)
    if isinstance(user_data, str):
        return {"error": user_data}
    return user_data.get("tasks", [])


def add_task(user_id: str, task: TaskModel) -> Dict:
    try:
        user_ref = db.collection("users").document(user_id)
        user_data = user_ref.get()

        if not user_data.exists:
            user_ref.set({"tasks": []})

        task_data = task.dict()
        task_data.update(
            {
                "id": db.collection("users").document().id,
                "status": "Pending",
            }
        )
        user_ref.update({"tasks": firestore.ArrayUnion([task_data])})
        return {"message": "Task added successfully", "task": task_data}
    except Exception as e:
        logger.error(f"Failed to add task for user {user_id}: {str(e)}")
        return {"error": f"Failed to add task: {str(e)}"}
    

def search_tasks(user_id: str, query: str) -> Union[List, Dict]:
    try:
        tasks = get_tasks(user_id)
        if isinstance(tasks, dict) and "error" in tasks:
            return tasks

        query_lower = query.lower()
        filtered_tasks = [
            task
            for task in tasks
            if query_lower in task["title"].lower()
            or query_lower in task.get("description", "").lower()
            or query_lower in task.get("category", "").lower()
        ]
        return filtered_tasks
    except Exception as e:
        logger.error(f"Failed to search tasks for user {user_id}: {str(e)}")
        return {"error": str(e)}
