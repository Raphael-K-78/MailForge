import resend

from resend.exceptions import ResendError

from jinja2 import Template

from dotenv import load_dotenv

import os

from pathlib import Path

# load .env
load_dotenv()

# API
resend.api_key = os.getenv("RESEND_API_KEY")

# Mail
mail_from = os.getenv("MAIL_FROM")

# Nom
name = os.getenv("MAIL_NAME")

# Mail de test
mail_test = os.getenv("MAIL_TEST", "").split(",")
prenom_test = os.getenv("PRENOM_TEST", "").split(",")
subject_test = os.getenv("SUBJECT_TEST")


# Liste des templates
dossier = Path("templates")

templates = []

for fichier in dossier.iterdir():
    if fichier.is_file():
        templates.append(fichier)
        nom = fichier.stem.replace("_", " ")
        print(f"[+]Template {nom} Chargé")


# Envoi des mails

for i in range(len(mail_test)):
    fichier = templates[1]
    with open(fichier, encoding="utf-8") as f:
        template = Template(f.read())

    html = template.render(
        prenom=prenom_test[i]
    )
    try:
        r = resend.Emails.send({
            "from": f"{name} <{mail_from}>",
            "to": mail_test[i],
            "subject": subject_test,
            "html": html
        })
        print(f"[+] Mail envoyé à {mail_test[i]}")

    except ResendError as e:

        print(f"[-] Erreur pour {mail_test[i]} : {e}")