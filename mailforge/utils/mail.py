import resend

from resend.exceptions import ResendError

from mailforge.utils.config import (
    resend_api_key,
    MAIL_PROVIDER
)
from mailforge.utils.gmail import send_via_gmail
from mailforge.utils.logger import logger

resend.api_key = resend_api_key


def _build_resend_attachments(inline_attachments, attachments):
    result = []

    for item in (inline_attachments or []) + (attachments or []):
        with open(item["path"], "rb") as f:
            content = f.read()

        entry = {
            "filename": item.get("filename", item["path"].name),
            "content": list(content)
        }

        if item.get("content_id"):
            entry["content_id"] = item["content_id"]

        result.append(entry)

    return result


def _send_via_resend(sender, to, subject, html, inline_attachments=None, attachments=None):
    try:
        payload = {
            "from": sender,
            "to": to,
            "subject": subject,
            "html": html
        }

        resend_attachments = _build_resend_attachments(inline_attachments, attachments)

        if resend_attachments:
            payload["attachments"] = resend_attachments

        response = resend.Emails.send(payload)

        logger.info(
            f"Mail envoyé à {to}"
        )

        return response

    except ResendError as e:
        logger.error(
            f"Erreur lors de l'envoi à {to} : {e}"
        )

        return None


def send_mail(
    sender,
    to,
    subject,
    html,
    inline_attachments=None,
    attachments=None
):
    if MAIL_PROVIDER == "gmail":
        return send_via_gmail(
            sender, to, subject, html,
            inline_attachments=inline_attachments,
            attachments=attachments
        )

    return _send_via_resend(
        sender, to, subject, html,
        inline_attachments=inline_attachments,
        attachments=attachments
    )
