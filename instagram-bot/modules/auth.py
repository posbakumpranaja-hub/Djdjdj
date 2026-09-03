"""
auth.py - Autentikasi Instagram menggunakan instagrapi
"""
import json
import logging
from pathlib import Path

from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    ChallengeRequired,
    LoginRequired,
    TwoFactorRequired,
)

import config
from modules.logger import setup_logger

logger = setup_logger(__name__)


class InstagramAuth:
    """Mengelola autentikasi dan session Instagram."""

    def __init__(self) -> None:
        self.client = Client()
        self._configure_client()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _configure_client(self) -> None:
        """Terapkan pengaturan default pada client."""
        self.client.delay_range = [
            int(config.DELAY_BETWEEN_REQUESTS),
            int(config.DELAY_BETWEEN_REQUESTS * 2),
        ]

    def _save_session(self) -> None:
        """Simpan session ke file."""
        try:
            self.client.dump_settings(config.SESSION_FILE)
            logger.debug("Session tersimpan di %s", config.SESSION_FILE)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gagal menyimpan session: %s", exc)

    def _load_session(self) -> bool:
        """Muat session dari file jika tersedia. Kembalikan True jika berhasil."""
        session_path = Path(config.SESSION_FILE)
        if not session_path.exists():
            return False
        try:
            self.client.load_settings(config.SESSION_FILE)
            logger.info("Session dimuat dari %s", config.SESSION_FILE)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gagal memuat session: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def login(self, username: str, password: str) -> bool:
        """
        Login ke Instagram.

        Urutan: coba session → login baru.
        Kembalikan True jika berhasil.
        """
        # Coba session yang tersimpan terlebih dahulu
        if self._load_session():
            try:
                self.client.login(username, password)
                logger.info("Login berhasil menggunakan session: %s", username)
                return True
            except LoginRequired:
                logger.info("Session kadaluarsa, mencoba login ulang...")

        # Login baru
        try:
            self.client.login(username, password)
            self._save_session()
            logger.info("Login berhasil: %s", username)
            return True

        except BadPassword:
            logger.error("Username atau password salah untuk: %s", username)
        except TwoFactorRequired:
            code = input("Masukkan kode 2FA: ").strip()
            try:
                self.client.login(username, password, verification_code=code)
                self._save_session()
                logger.info("Login 2FA berhasil: %s", username)
                return True
            except Exception as exc:  # noqa: BLE001
                logger.error("Login 2FA gagal: %s", exc)
        except ChallengeRequired:
            logger.error(
                "Challenge required. Selesaikan verifikasi di aplikasi Instagram."
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Login gagal: %s", exc)

        return False

    def logout(self) -> None:
        """Logout dari Instagram."""
        try:
            self.client.logout()
            logger.info("Logout berhasil.")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Logout error: %s", exc)

    def set_proxy(self, proxy: str) -> None:
        """Set proxy pada client."""
        self.client.set_proxy(proxy)
        logger.info("Proxy diset: %s", proxy)
