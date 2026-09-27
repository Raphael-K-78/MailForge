from mailforge.utils.template import get_template_fields, render_template
from mailforge.utils.mail import send_mail
from mailforge.utils.attachments import extract_inline_attachments
from mailforge.utils.logger import logger
from mailforge.utils.config import MAIL_DOMAINE


def send(
    subject,
    sender_name,
    sender_email,
    recipient,
    template,
    template_data,
    attachments=None
):
    """
    Prépare et envoie un mail à partir de toutes les informations fournies.
    """

    logger.info(f"Préparation de l'envoi à {recipient}")
    logger.info(f"Template sélectionné : {template.name}")

    get_template_fields(template)

    html = render_template(template, template_data)

    html, inline_attachments = extract_inline_attachments(html, template.parent)

    logger.info(
        f"Expéditeur : {sender_name} <{sender_email}>"
    )

    try:
        sender = f"{sender_name} <{sender_email}@{MAIL_DOMAINE}>"

        result = send_mail(
            sender=sender,
            to=recipient,
            subject=subject,
            html=html,
            inline_attachments=inline_attachments,
            attachments=[
                {"path": path, "filename": path.name}
                for path in (attachments or [])
            ]
        )

        return result

    except Exception as e:
        logger.error(
            f"Erreur lors de l'envoi à {recipient} : {e}"
        )

        return None
