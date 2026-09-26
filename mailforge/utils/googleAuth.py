from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from mailforge.utils.config import (
    GMAIL_CREDENTIALS_FILE,
    GMAIL_TOKEN_FILE,
    GMAIL_SCOPES
)
from mailforge.utils.logger import logger


def get_gmail_credentials():
    """
    Récupère des credentials OAuth 2.0 valides pour l'API Gmail.

    - Lit le token existant dans token.json s'il y en a un.
    - Le rafraîchit s'il est expiré.
    - Sinon lance le flow OAuth (ouverture navigateur) via credentials.json
      et sauvegarde le nouveau token dans token.json.
    """

    token_path = Path(GMAIL_TOKEN_FILE)
    credentials_path = Path(GMAIL_CREDENTIALS_FILE)

    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(
            str(token_path),
            GMAIL_SCOPES
        )

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        logger.info("Rafraîchissement du token Gmail")
        creds.refresh(Request())

    else:
        if not credentials_path.exists():
            logger.error(
                f"Fichier credentials introuvable : {credentials_path}"
            )
            raise FileNotFoundError(
                f"Fichier credentials introuvable : {credentials_path}. "
                "Télécharge-le depuis Google Cloud Console (client OAuth 2.0)."
            )

        logger.info("Nouvelle autorisation Gmail requise, ouverture du navigateur")

        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            GMAIL_SCOPES
        )
        creds = flow.run_local_server(port=0)

    token_path.write_text(creds.to_json(), encoding="utf-8")
    logger.info(f"Token Gmail sauvegardé dans {token_path}")

    return creds
