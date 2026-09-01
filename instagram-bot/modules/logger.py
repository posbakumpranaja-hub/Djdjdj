"""
logger.py - Logging system untuk Instagram Bot
"""
import logging
import sys
from logging.handlers import RotatingFileHandler

from colorama import Fore, Style, init

import config

# Inisialisasi colorama
init(autoreset=True)


class ColorFormatter(logging.Formatter):
    """Formatter dengan warna untuk output terminal."""

    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(name: str = "instagram_bot") -> logging.Logger:
    """Buat dan kembalikan logger yang sudah dikonfigurasi."""
    logger = logging.getLogger(name)

    # Hindari duplikasi handler
    if logger.handlers:
        return logger

    level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # --- Console handler (berwarna) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(
        ColorFormatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    # --- File handler (plain text, rotating) ---
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
