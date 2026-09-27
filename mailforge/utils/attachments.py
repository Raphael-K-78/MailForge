import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from mailforge.utils.logger import logger

ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt", ".zip",
}

_REMOTE_PREFIXES = ("http://", "https://")
_SKIP_PREFIXES = ("cid:", "mailto:", "data:")

_ATTR_PATTERN = re.compile(r'(src|href)="([^"]+)"')


def extract_inline_attachments(html, base_dir):
    """
    Scanne le HTML à la recherche de src="..." (images, y compris distantes)
    et de href="..." pointant vers un fichier local, remplace la valeur par
    une référence cid: et retourne la liste des pièces jointes à embarquer.
    Les fichiers distants ne sont pas téléchargés ici : l'URL est conservée
    comme "path" et sera récupérée au moment de l'envoi.
    """

    attachments = []
    counter = {"value": 0}

    def next_content_id():
        counter["value"] += 1
        return f"attached_file_{counter['value']}"

    def replace(match):
        attr, value = match.group(1), match.group(2)

        if value.startswith(_SKIP_PREFIXES):
            return match.group(0)

        if value.startswith(_REMOTE_PREFIXES):
            if attr != "src":
                return match.group(0)

            content_id = next_content_id()
            filename = Path(urlparse(value).path).name or content_id

            attachments.append({
                "path": value,
                "filename": filename,
                "content_id": content_id,
                "remote": True,
            })

            return f'{attr}="cid:{content_id}"'

        ext = Path(value).suffix.lower()

        if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
            return match.group(0)

        file_path = (base_dir / value).resolve()

        if not file_path.is_file():
            logger.warning(f"Pièce jointe introuvable, ignorée : {file_path}")
            return match.group(0)

        content_id = next_content_id()

        attachments.append({
            "path": file_path,
            "filename": file_path.name,
            "content_id": content_id,
        })

        return f'{attr}="cid:{content_id}"'

    new_html = _ATTR_PATTERN.sub(replace, html)

    return new_html, attachments


def read_attachment_bytes(item):
    """
    Lit le contenu d'une pièce jointe, qu'elle soit locale (Path) ou
    distante (URL récupérée à la volée, jamais écrite sur disque).
    """

    if item.get("remote"):
        request = urllib.request.Request(
            item["path"],
            headers={"User-Agent": "Mozilla/5.0 (compatible; MailForge/1.0)"}
        )

        with urllib.request.urlopen(request) as response:
            return response.read(), response.headers.get_content_type()

    with open(item["path"], "rb") as f:
        return f.read(), None
