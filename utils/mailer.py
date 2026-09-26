from utils.template import get_template_fields
from utils.mail import send_mail
from utils.logger import logger
from utils.config import MAIL_DOMAINE


def send(
    subject,
    sender_name,
    sender_email,
    recipient,
    template,
    template_data
):
    """
    Prépare et envoie un mail à partir de toutes les informations fournies.
    """

    logger.info(f"Préparation de l'envoi à {recipient}")
    logger.info(f"Template sélectionné : {template.name}")

    fields = get_template_fields(template)

    with open(template, encoding="utf-8") as f:
        html = f.read()

    for field in fields:
        value = template_data.get(field, "")

        html = html.replace(
            "{{" + field + "}}",
            str(value)
        )

    logger.info(
        f"Expéditeur : {sender_name} <{sender_email}>"
    )

    try:
        sender = f"{sender_name} <{sender_email}@{MAIL_DOMAINE}>"

        result = send_mail(
            sender=sender,
            to=recipient,
            subject=subject,
            html=html
        )

        return result

    except Exception as e:
        logger.error(
            f"Erreur lors de l'envoi à {recipient} : {e}"
        )

        return None
