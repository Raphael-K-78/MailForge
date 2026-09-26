import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mailforge.utils.googleAuth import get_gmail_credentials
from mailforge.utils.logger import logger


def _build_raw_message(sender, to, subject, html):
    message = MIMEMultipart("alternative")
    message["From"] = sender
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(html, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    return {"raw": raw}


def send_via_gmail(sender, to, subject, html):
    try:
        creds = get_gmail_credentials()
        service = build("gmail", "v1", credentials=creds)

        body = _build_raw_message(sender, to, subject, html)

        response = (
            service.users()
            .messages()
            .send(userId="me", body=body)
            .execute()
        )

        logger.info(
            f"Mail envoyé à {to}"
        )

        return response

    except (HttpError, FileNotFoundError) as e:
        logger.error(
            f"Erreur lors de l'envoi à {to} : {e}"
        )

        return None
