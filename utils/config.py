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