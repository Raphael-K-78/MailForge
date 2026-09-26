from utils.template import (
    get_templates,
    display_templates,
    get_template_fields
)

from utils.mail import send_mail
from utils.logger import logger
from utils.config import (
    TEMPLATES_DIR,
    MAIL_DOMAINE
)


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


def main():
    logger.info("=== Démarrage de l'envoi d'un mail ===")

    print("=== Envoi d'un mail ===\n")

    subject = input("Sujet du mail : ")
    sender_name = input("Nom de l'expéditeur : ")
    sender_email = input("Identifiant personnel du mail : ")
    recipient = input("Destinataire du mail : ")

    logger.info(f"Sujet : {subject}")
    logger.info(f"Nom de l'expéditeur : {sender_name}")
    logger.info(f"Identifiant personnel du mail : {sender_email}")
    logger.info(f"Destinataire : {recipient}")

    templates = get_templates(TEMPLATES_DIR)

    if not templates:
        logger.error(
            f"Aucun template trouvé dans : {TEMPLATES_DIR}"
        )
        print("[-] Aucun template disponible.")
        return

    logger.info(
        f"{len(templates)} template(s) trouvé(s)"
    )

    display_templates(templates)

    while True:
        try:
            choice = int(input("Template : "))

            if 1 <= choice <= len(templates):
                break

            print("[-] Template invalide.")
            logger.warning("Numéro de template invalide.")

        except ValueError:
            print("[-] Veuillez entrer un numéro.")
            logger.warning(
                "Entrée invalide pour le choix du template."
            )

    template_file = templates[choice - 1]

    logger.info(
        f"Template sélectionné : {template_file.name}"
    )

    fields = get_template_fields(template_file)

    template_data = {}

    if fields:
        print("\nDonnées du template :")

        for field in fields:
            value = input(f"{field} : ")
            template_data[field] = value

    else:
        logger.info(
            "Aucun champ dynamique dans le template"
        )

    send(
        subject=subject,
        sender_name=sender_name,
        sender_email=sender_email,
        recipient=recipient,
        template=template_file,
        template_data=template_data
    )

    logger.info("=== Fin de l'envoi ===")


if __name__ == "__main__":
    main()