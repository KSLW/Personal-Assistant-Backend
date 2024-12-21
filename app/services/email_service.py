import logging
import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from mailersend import emails

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Validate MailerSend API key
api_key = os.getenv("MAILERSEND_API_KEY")
if not api_key:
    logger.error("MAILERSEND_API_KEY environment variable is not set.")
    raise ValueError("MAILERSEND_API_KEY environment variable is not set.")

# Initialize MailerSend client
try:
    mailer_client = emails.NewEmail(api_key)
    logger.info("MailerSend client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize MailerSend client: {str(e)}")
    raise ValueError("Failed to initialize MailerSend client") from e


def send_email(
    recipient: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, str]:
    """
    Send an email using the MailerSend API.

    Args:
        recipient (str): Recipient email address.
        subject (str): Email subject.
        body (str): Plain text email content.
        html_body (str, optional): HTML email content. Defaults to None.
        cc (List[str], optional): List of CC email addresses. Defaults to None.
        bcc (List[str], optional): List of BCC email addresses. Defaults to None.
        attachments (List[Dict[str, str]], optional): List of attachments with keys
            "content" (base64 encoded) and "filename". Defaults to None.

    Returns:
        dict: A success or error message.
    """
    try:
        email_data = {
            "from": {
                "email": os.getenv(
                    "MAILERSEND_SENDER_EMAIL", "your-verified-sender-email@example.com"
                ),
                "name": "Personal Assistant App",
            },
            "to": [{"email": recipient}],
            "subject": subject,
            "text": body,
        }

        if html_body:
            email_data["html"] = html_body
        if cc:
            email_data["cc"] = [{"email": email} for email in cc]
        if bcc:
            email_data["bcc"] = [{"email": email} for email in bcc]
        if attachments:
            email_data["attachments"] = attachments

        # Send the email
        mailer_client.send(email_data)
        logger.info(f"Email sent successfully to {recipient}")
        return {"message": f"Email sent successfully to {recipient}"}
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        return {"error": f"Failed to send email to {recipient}: {str(e)}"}
