import resend

from resend.exceptions import ResendError

from mailforge.utils.config import (
    resend_api_key,
    MAIL_PROVIDER
)
from mailforge.utils.gmail import send_via_gmail
from mailforge.utils.logger import logger

resend.api_key = resend_api_key


def _send_via_resend(sender, to, subject, html):
    try:
        response = resend.Emails.send({
            "from": sender,
            "to": to,
            "subject": subject,
            "html": html
        })

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

    return _send_via_resend(sender, to, subject, html)
