from pathlib import Path

from utils.config import mail_domaine
from utils.logger import logger
from utils.mail import send_mail
from utils.template import (
    get_templates,
    display_templates,
    get_template_fields,
    render_template
)


# Liste des templates
templates_dir = Path("templates")

templates = get_templates(
    templates_dir
)

if not templates:
    logger.error("Aucun template trouvé")
    exit()


# Informations du mail
subject = input(
    "Sujet du mail : "
).strip()

sender_name = input(
    "Nom de l'expéditeur : "
).strip()

sender_username = input(
    "Identifiant personnel du mail : "
).strip()

recipient = input(
    "Destinataire du mail : "
).strip()


# Affichage et choix du template
display_templates(templates)

template_number = int(
    input("\nChoix du Template : ")
)

template_file = templates[
    template_number - 1
]

logger.info(
    f"Template sélectionné : {template_file.name}"
)


# Champs du template
fields = get_template_fields(
    template_file
)


# Données du template
data = {}

for field in fields:
    data[field] = input(
        f"{field} : "
    )


# Génération du HTML
html = render_template(
    template_file,
    data
)


# Adresse de l'expéditeur
sender = (
    f"{sender_name} "
    f"<{sender_username}@{mail_domaine}>"
)

logger.info(
    f"Expéditeur : {sender}"
)


# Envoi du mail
send_mail(
    sender=sender,
    to=recipient,
    subject=subject,
    html=html
)