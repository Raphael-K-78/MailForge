import re
from pathlib import Path

from mailforge.utils.logger import logger

ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt", ".zip",
}

_SKIP_PREFIXES = ("http://", "https://", "cid:", "mailto:", "data:")

_ATTR_PATTERN = re.compile(r'(src|href)="([^"]+)"')


def extract_inline_attachments(html, base_dir):
    """
    Scanne le HTML à la recherche de src="..."/href="..." pointant vers
    un fichier local (image, pdf, ...), le remplace par une référence cid:
    et retourne la liste des pièces jointes à embarquer.
    """

    attachments = []
    counter = {"value": 0}

    def replace(match):
        attr, value = match.group(1), match.group(2)

        if value.startswith(_SKIP_PREFIXES):
            return match.group(0)

        ext = Path(value).suffix.lower()

        if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
            return match.group(0)

        file_path = (base_dir / value).resolve()

        if not file_path.is_file():
            logger.warning(f"Pièce jointe introuvable, ignorée : {file_path}")
            return match.group(0)

        counter["value"] += 1
        content_id = f"attached_file_{counter['value']}"

        attachments.append({
            "path": file_path,
            "filename": file_path.name,
            "content_id": content_id,
        })

        return f'{attr}="cid:{content_id}"'

    new_html = _ATTR_PATTERN.sub(replace, html)

    return new_html, attachments
