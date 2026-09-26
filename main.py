from utils.template import (
    get_templates,
    display_templates,
    get_template_fields
)

from utils.mailer import send
from utils.logger import logger
from utils.config import TEMPLATES_DIR


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