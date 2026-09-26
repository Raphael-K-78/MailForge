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

# Clé API Resend
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Domaine du mail
MAIL_DOMAINE = os.getenv("MAIL_DOMAINE")

# Logging
LOG_MAX_SIZE_MB = int(os.getenv("LOG_MAX_SIZE_MB", 20))
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 32))

# Dossier des templates
TEMPLATES_DIR = Path(os.getenv("TEMPLATES_DIR", "templates"))