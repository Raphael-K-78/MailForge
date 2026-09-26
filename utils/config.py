from dotenv import load_dotenv
import os

# Chargement du .env
load_dotenv()

# Clé API Resend
resend_api_key = os.getenv("RESEND_API_KEY")

# Domaine du mail
mail_domaine = os.getenv("MAIL_DOMAINE")

# Taille max du fichier de log
log_max_size_mb = int(os.getenv("LOG_MAX_SIZE_MB", "20"))

# Nombre max de fichiers de log (-1 = pas de suppression)
log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", "32"))

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Fournisseur d'envoi (resend ou gmail)
MAIL_PROVIDER = os.getenv("MAIL_PROVIDER", "resend").strip().lower()

# Clé API Resend
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Domaine du mail
MAIL_DOMAINE = os.getenv("MAIL_DOMAINE")

# Gmail API + OAuth 2.0 (utilisés si MAIL_PROVIDER=gmail)
GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
GMAIL_TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE", "token.json")
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Logging
LOG_MAX_SIZE_MB = int(os.getenv("LOG_MAX_SIZE_MB", 20))
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 32))

# Dossier des templates
TEMPLATES_DIR = Path(os.getenv("TEMPLATES_DIR", "templates"))