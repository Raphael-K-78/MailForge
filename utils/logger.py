import logging
import os

from logging.handlers import RotatingFileHandler

from utils.config import (
    log_max_size_mb,
    log_backup_count
)

# Création du dossier logs
os.makedirs("logs", exist_ok=True)

# Rotation infinie
class InfiniteRotatingFileHandler(RotatingFileHandler):

    def doRollover(self):

        if self.stream:
            self.stream.close()
            self.stream = None

        index = 1

        while os.path.exists(
            f"{self.baseFilename}.{index}"
        ):
            index += 1

        os.rename(
            self.baseFilename,
            f"{self.baseFilename}.{index}"
        )

        self.stream = self._open()

# Formatter
class AppFormatter(logging.Formatter):

    def format(self, record):

        prefix = (
            "[+]"
            if record.levelno == logging.INFO
            else "[-]"
        )

        return (
            f"{prefix} "
            f"{self.formatTime(record)} | "
            f"{record.levelname} | "
            f"{record.getMessage()}"
        )

formatter = AppFormatter()

# File Handler
if log_backup_count == -1:

    file_handler = InfiniteRotatingFileHandler(
        "logs/app.log",
        maxBytes=log_max_size_mb * 1024**2,
        backupCount=0,
        encoding="utf-8"
    )

else:

    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=log_max_size_mb * 1024**2,
        backupCount=log_backup_count,
        encoding="utf-8"
    )

# Console Handler
console_handler = logging.StreamHandler()

# Formatter
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        file_handler,
        console_handler
    ]
)

logger = logging.getLogger("email_app")