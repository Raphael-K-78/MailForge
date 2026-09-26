import resend

from resend.exceptions import ResendError
from jinja2 import Template
from dotenv import load_dotenv

import os
import sys

from pathlib import Path


# Configuration
load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

mail_from = os.getenv("MAIL_FROM")
mail_name = os.getenv("MAIL_NAME")

mail_test = [
    mail.strip()
    for mail in os.getenv("MAIL_TEST", "").split(",")
    if mail.strip()
]

prenom_test = [
    prenom.strip()
    for prenom in os.getenv("PRENOM_TEST", "").split(",")
    if prenom.strip()
]

subject_test = os.getenv("SUBJECT_TEST")

dossier = Path("templates")


def get_templates():
    templates = []

    for fichier in dossier.iterdir():

        if fichier.is_file() and fichier.suffix == ".html":
            templates.append(fichier)

    return templates

def show_templates(templates):
    print()
    for i, fichier in enumerate(templates, start=1):
        nom = fichier.stem.replace("_", " ")
        print(f"[{i}] {nom}")
    print()


def send_mail(to, prenom, subject, template_file):
    try:
        with open(template_file, encoding="utf-8") as f:
            template = Template(f.read())
        html = template.render(
            prenom=prenom
        )
        resend.Emails.send({
            "from": f"{mail_name} <{mail_from}>",
            "to": to,
            "subject": subject,
            "html": html
        })
        print(f"[+] Mail envoyé à {to}")

        return True

    except ResendError as e:

        print(f"[-] Erreur pour {to} : {e}")

        return False

def dev_mode(template_file):

    print()
    print("[DEV] Mode test activé")
    print(f"[DEV] {len(mail_test)} destinataire(s)")
    print()

    for i, mail in enumerate(mail_test):

        if i >= len(prenom_test):
            print(
                f"[-] Aucun prénom correspondant pour {mail}"
            )
            continue

        send_mail(
            to=mail,
            prenom=prenom_test[i],
            subject=subject_test,
            template_file=template_file
        )

def main():
    templates = get_templates()
    if not templates:
        print("[-] Aucun template trouvé.")
        return
    
    print("[+] Templates chargés :")
    show_templates(templates)
    choix = input("Choisissez un template : ")
    try:
        choix = int(choix)
        template_file = templates[choix - 1]

    except (ValueError, IndexError):

        print("[-] Template invalide.")
        return

    print()
    print(f"[+] Template sélectionné : {template_file.stem}")
    print()



    if len(sys.argv) > 1 and sys.argv[1].lower() == "dev":

        dev_mode(template_file)

    else:

        print("[+] Mode production")
        print("[!] Aucun destinataire configuré.")
        print("[!] Ajoute ici ta logique d'envoi réelle.")


if __name__ == "__main__":
    main()