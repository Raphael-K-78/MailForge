import base64
import mimetypes
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mailforge.utils.googleAuth import get_gmail_credentials
from mailforge.utils.logger import logger


def _build_mime_part(item, inline):
    with open(item["path"], "rb") as f:
        data = f.read()

    ctype, _ = mimetypes.guess_type(str(item["path"]))
    maintype, subtype = ctype.split("/", 1) if ctype else ("application", "octet-stream")

    if maintype == "image":
        part = MIMEImage(data, _subtype=subtype)
    else:
        part = MIMEApplication(data, _subtype=subtype)

    filename = item.get("filename", item["path"].name)

    if inline:
        part.add_header("Content-ID", f"<{item['content_id']}>")
        part.add_header("Content-Disposition", "inline", filename=filename)
    else:
        part.add_header("Content-Disposition", "attachment", filename=filename)

    return part


def _build_raw_message(sender, to, subject, html, inline_attachments=None, attachments=None):
    inline_attachments = inline_attachments or []
    attachments = attachments or []

    message = MIMEMultipart("mixed")
    message["From"] = sender
    message["To"] = to
    message["Subject"] = subject

    body = MIMEMultipart("alternative")
    body.attach(MIMEText(html, "html", "utf-8"))

    if inline_attachments:
        related = MIMEMultipart("related")
        related.attach(body)

        for item in inline_attachments:
            related.attach(_build_mime_part(item, inline=True))

        message.attach(related)
    else:
        message.attach(body)

    for item in attachments:
        message.attach(_build_mime_part(item, inline=False))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    return {"raw": raw}


def send_via_gmail(sender, to, subject, html, inline_attachments=None, attachments=None):
    try:
        creds = get_gmail_credentials()
        service = build("gmail", "v1", credentials=creds)

        body = _build_raw_message(
            sender, to, subject, html,
            inline_attachments=inline_attachments,
            attachments=attachments
        )

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
