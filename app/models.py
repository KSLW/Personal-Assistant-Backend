from pydantic import BaseModel, EmailStr
from typing import Optional

# User Model


class User(BaseModel):
    email: EmailStr
    password: str

# Reminder Model


class Reminder(BaseModel):
    title: str
    due_date: str  # ISO 8601 format (e.g., "2024-12-31T10:00:00")
    recurring: Optional[bool] = False
    recurrence_interval: Optional[str] = None  # Options: "daily", "weekly", "monthly"
    description: Optional[str] = None

# Task Model


class Task(BaseModel):
    title: str
    due_date: str  # ISO 8601 format
    priority: Optional[str] = None  # Options: "low", "medium", "high"
    category: Optional[str] = None
    recurring: Optional[bool] = False
    recurrence_interval: Optional[str] = None  # Options: "daily", "weekly", "monthly"
    description: Optional[str] = None
    status: Optional[str] = "Pending"  # Default status

# Email Model


class EmailRequest(BaseModel):
    recipient: EmailStr
    subject: str
    body: str
    html_body: Optional[str] = None
