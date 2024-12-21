import logging
import time
from datetime import datetime, timedelta
from typing import List

import schedule

from app.services.email_service import send_email
from app.services.firestore_service import (expire_old_reminders,
                                            get_overdue_tasks, get_reminders,
                                            reschedule_recurring_reminders,
                                            reschedule_recurring_tasks,
                                            update_reminder)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Utility Functions
def fetch_all_user_ids() -> List[str]:
    """
    Fetch all user IDs dynamically from Firestore.
    Replace this function's logic with a Firestore query to retrieve all users.
    """
    # Example: Replace with Firestore query logic
    return ["firebase_user_id_1", "firebase_user_id_2"]


# Scheduler Functions
def check_and_send_reminders():
    """
    Check reminders and send email notifications for due reminders.
    """
    try:
        user_ids = fetch_all_user_ids()
        for user_id in user_ids:
            reminders = get_reminders(user_id)
            if "error" not in reminders:
                for reminder in reminders:
                    due_date = datetime.fromisoformat(reminder["due_date"])
                    if due_date <= datetime.now() and not reminder.get("sent", False):
                        send_email(
                            recipient="recipient-email@example.com",
                            subject=f"Reminder: {reminder['title']}",
                            body=f"""Your reminder '{reminder['title']}' is due on
                            {reminder['due_date']}.""",
                        )
                        update_reminder(user_id, reminder["id"], {"sent": True})
                        logger.info(
                            f"""Sent reminder email for '{reminder['title']}'
                            to recipient."""
                        )
    except Exception as e:
        logger.error(f"Error in check_and_send_reminders: {str(e)}")


def reschedule_all_recurring_reminders():
    """
    Reschedule recurring reminders for all users.
    """
    try:
        user_ids = fetch_all_user_ids()
        for user_id in user_ids:
            reschedule_recurring_reminders(user_id)
            logger.info(f"Rescheduled recurring reminders for user {user_id}")
    except Exception as e:
        logger.error(f"Error in reschedule_all_recurring_reminders: {str(e)}")


def remove_expired_reminders():
    """
    Remove reminders older than the expiry threshold for all users.
    """
    try:
        expiry_threshold = (datetime.now() - timedelta(days=30)).isoformat()
        user_ids = fetch_all_user_ids()
        for user_id in user_ids:
            expire_old_reminders(user_id, expiry_threshold)
            logger.info(f"Expired old reminders for user {user_id}")
    except Exception as e:
        logger.error(f"Error in remove_expired_reminders: {str(e)}")


def notify_overdue_tasks():
    """
    Notify users about overdue tasks.
    """
    try:
        user_ids = fetch_all_user_ids()
        for user_id in user_ids:
            overdue_tasks = get_overdue_tasks(user_id)
            if "error" not in overdue_tasks and overdue_tasks:
                for task in overdue_tasks:
                    send_email(
                        recipient="recipient-email@example.com",
                        subject=f"Overdue Task: {task['title']}",
                        body=f"""Your task '{task['title']}' was due on
                        {task['due_date']}.\n\n"
                        f"Description: {task.get('''description',
                                                'No description provided.''')}\n"
                        f"Priority: {task.get('priority', 'No priority specified')}\n\n"
                        f"Please complete it as soon as possible.""",
                    )
                    logger.info(
                        f"Sent overdue task email for '{task['title']}' to recipient."
                    )
    except Exception as e:
        logger.error(f"Error in notify_overdue_tasks: {str(e)}")


def reschedule_all_recurring_tasks():
    """
    Reschedule recurring tasks for all users.
    """
    try:
        user_ids = fetch_all_user_ids()
        for user_id in user_ids:
            reschedule_recurring_tasks(user_id)
            logger.info(f"Rescheduled recurring tasks for user {user_id}")
    except Exception as e:
        logger.error(f"Error in reschedule_all_recurring_tasks: {str(e)}")


# Scheduling
def schedule_jobs():
    """
    Schedule all jobs using the `schedule` library.
    """
    schedule.every(1).minutes.do(check_and_send_reminders)
    schedule.every().day.at("00:00").do(reschedule_all_recurring_reminders)
    schedule.every().day.at("00:00").do(remove_expired_reminders)
    schedule.every().day.at("09:00").do(notify_overdue_tasks)
    schedule.every().day.at("00:00").do(reschedule_all_recurring_tasks)
    logger.info("All jobs scheduled successfully.")


# Main Scheduler Loop
if __name__ == "__main__":
    logger.info("Starting reminder scheduler...")
    schedule_jobs()
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error in the main scheduler loop: {str(e)}")
