from typing import Dict, List, Optional

from fastapi import Body, Depends, FastAPI, HTTPException, Query
from fastapi.security import HTTPBearer
from firebase_admin import auth
from firebase_admin.auth import verify_id_token
from pydantic import BaseModel

from services.firestore_service import add_reminder, add_task, get_reminders, update_reminder

app = FastAPI(
    title="Personal Assistant Backend API",
    description="""API for managing reminders, tasks, and user authentication in the Personal
    Assistant app.""",
    version="1.0.0",
)

security = HTTPBearer()


# Dependency for Authentication
def get_current_user(token: str = Depends(security)):
    """
    Validate Firebase ID token and return user info.
    """
    try:
        decoded_token = verify_id_token(token.credentials)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# Pydantic Models for Validation
class Reminder(BaseModel):
    title: str
    due_date: str
    recurring: bool = False
    recurrence_interval: Optional[str] = None


class Task(BaseModel):
    title: str
    due_date: str
    priority: Optional[str] = "Medium"
    category: Optional[str] = None
    recurring: bool = False
    recurrence_interval: Optional[str] = None


# User Management Endpoints
@app.post(
    "/users",
    tags=["Users"],
    summary="Create a new user",
    description="Creates a new user in Firebase Authentication.",
)
def create_user(email: str = Body(...), password: str = Body(...)):
    """
    Create a new user in Firebase Authentication.

    Args:
        email (str): User's email address.
        password (str): User's password.

    Returns:
        dict: User creation status and details.
    """
    try:
        user = auth.create_user(email=email, password=password)
        return {
            "message": "User created successfully",
            "uid": user.uid,
            "email": user.email,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")


@app.get(
    "/users",
    tags=["Users"],
    summary="Get user details",
    description="Retrieve user details from Firebase Authentication by email.",
)
def get_user(email: str = Query(...)):
    """
    Retrieve user details from Firebase Authentication.

    Args:
        email (str): User's email address.

    Returns:
        dict: User details.
    """
    try:
        user = auth.get_user_by_email(email)
        return {"uid": user.uid, "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error retrieving user: {str(e)}")


# Reminder Endpoints
@app.post(
    "/reminders",
    tags=["Reminders"],
    summary="Create a reminder",
    description="Creates a new reminder for the authenticated user.",
    response_model=Dict,
)
def create_reminder(
    user_id: str = Depends(get_current_user), reminder: Reminder = Body(...)
):
    """
    Create a reminder for the authenticated user.

    Args:
        user_id (str): Authenticated user's ID.
        reminder (Reminder): Reminder details.

    Returns:
        dict: Created reminder details.
    """
    result = add_reminder(user_id["uid"], reminder.dict())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get(
    "/reminders",
    tags=["Reminders"],
    summary="Retrieve all reminders",
    description="Fetches all reminders for the authenticated user.",
    response_model=List[Dict],
)
def retrieve_reminders(user_id: str = Depends(get_current_user)):
    """
    Retrieve all reminders for the authenticated user.

    Args:
        user_id (str): Authenticated user's ID.

    Returns:
        list: List of reminders.
    """
    reminders = get_reminders(user_id["uid"])
    if isinstance(reminders, dict) and "error" in reminders:
        raise HTTPException(status_code=404, detail=reminders["error"])
    return reminders


@app.put(
    "/reminders/{reminder_id}",
    tags=["Reminders"],
    summary="Update a reminder",
    description="Updates the details of a specific reminder.",
    response_model=Dict,
)
def modify_reminder(
    reminder_id: str,
    user_id: str = Depends(get_current_user),
    updates: dict = Body(...),
):
    """
    Update a specific reminder for the authenticated user.

    Args:
        reminder_id (str): Reminder ID.
        user_id (str): Authenticated user's ID.
        updates (dict): Reminder updates.

    Returns:
        dict: Update status.
    """
    result = update_reminder(user_id["uid"], reminder_id, updates)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# Task Endpoints
@app.post(
    "/tasks",
    tags=["Tasks"],
    summary="Create a task",
    description="Creates a new task for the authenticated user.",
    response_model=Dict,
)
def create_task(user_id: str = Depends(get_current_user), task: Task = Body(...)):
    """
    Create a new task for the authenticated user.

    Args:
        user_id (str): Authenticated user's ID.
        task (Task): Task details.

    Returns:
        dict: Created task details.
    """
    return add_task(user_id["uid"], task.dict())
