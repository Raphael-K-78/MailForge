import resend

from resend.exceptions import ResendError

from utils.config import resend_api_key
from utils.logger import logger

resend.api_key = resend_api_key


def send_mail(
    sender,
    to,
    subject,
    html
):
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