import logging
import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import auth, credentials, firestore
from firebase_admin.exceptions import FirebaseError

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred_path = os.getenv("FIREBASE_CREDENTIALS")
    if not cred_path:
        logger.error("FIREBASE_CREDENTIALS environment variable not set.")
        raise ValueError("FIREBASE_CREDENTIALS environment variable not set.")

    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
        raise

# Initialize Firestore
try:
    db = firestore.client()
    logger.info("Firestore client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Firestore client: {str(e)}")
    raise


def create_user(email: str, password: str) -> dict:
    """
    Create a new user in Firebase Authentication.

    Args:
        email (str): The email of the new user.
        password (str): The password of the new user.

    Returns:
        dict: User details if successful or an error message if failed.
    """
    try:
        user = auth.create_user(email=email, password=password)
        logger.info(f"User created successfully: {email}")
        return {
            "uid": user.uid,
            "email": user.email,
            "message": "User created successfully",
        }
    except FirebaseError as e:
        logger.error(f"Failed to create user {email}: {str(e)}")
        return {"error": f"Failed to create user: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error while creating user {email}: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


def verify_user(email: str) -> dict:
    """
    Verify if a user exists in Firebase Authentication by email.

    Args:
        email (str): The email of the user.

    Returns:
        dict: User details if the user exists or an error message if not.
    """
    try:
        user = auth.get_user_by_email(email)
        logger.info(f"User verified successfully: {email}")
        return {
            "uid": user.uid,
            "email": user.email,
            "message": "User verified successfully",
        }
    except FirebaseError as e:
        logger.error(f"Failed to verify user {email}: {str(e)}")
        return {"error": f"Failed to verify user: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error while verifying user {email}: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


def delete_user(uid: str) -> dict:
    """
    Delete a user from Firebase Authentication.

    Args:
        uid (str): The UID of the user to delete.

    Returns:
        dict: A success message if successful or an error message if failed.
    """
    try:
        auth.delete_user(uid)
        logger.info(f"User deleted successfully: {uid}")
        return {"message": "User deleted successfully"}
    except FirebaseError as e:
        logger.error(f"Failed to delete user {uid}: {str(e)}")
        return {"error": f"Failed to delete user: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error while deleting user {uid}: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}
