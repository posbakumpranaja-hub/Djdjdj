"""
proxy.py - Proxy management untuk Instagram Bot
"""
import random
from pathlib import Path
from typing import List, Optional

import requests

import config
from modules.logger import setup_logger

logger = setup_logger(__name__)

_DEFAULT_TIMEOUT = 10


class ProxyManager:
    """Mengelola daftar proxy dan rotasi otomatis."""

    def __init__(self, proxy_file: str = config.PROXY_FILE) -> None:
        self._proxy_file = proxy_file
        self._proxies: List[str] = []
        self._index: int = 0
        self._action_count: int = 0
        self._load_proxies()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_proxies(self) -> None:
        """Muat proxy dari file teks (satu per baris)."""
        path = Path(self._proxy_file)
        if not path.exists():
            logger.info("File proxy tidak ditemukan: %s", self._proxy_file)
            return
        with path.open(encoding="utf-8") as fh:
            self._proxies = [
                line.strip()
                for line in fh
                if line.strip() and not line.startswith("#")
            ]
        logger.info("%d proxy dimuat dari %s", len(self._proxies), self._proxy_file)

    def _format_proxy(self, raw: str) -> dict:
        """Ubah string proxy menjadi dict yang diterima requests/instagrapi."""
        if not raw.startswith(("http://", "https://", "socks5://")):
            raw = f"http://{raw}"
        return {"http": raw, "https": raw}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_proxy(self, proxy: str) -> None:
        """Tambahkan proxy secara manual."""
        self._proxies.append(proxy)

    def get_next(self) -> Optional[str]:
        """Ambil proxy berikutnya secara round-robin."""
        if not self._proxies:
            return None
        proxy = self._proxies[self._index % len(self._proxies)]
        self._index += 1
        return proxy

    def get_random(self) -> Optional[str]:
        """Ambil proxy acak."""
        if not self._proxies:
            return None
        return random.choice(self._proxies)

    def should_rotate(self) -> bool:
        """Cek apakah sudah waktunya rotasi proxy."""
        self._action_count += 1
        if self._action_count >= config.PROXY_ROTATION_INTERVAL:
            self._action_count = 0
            return True
        return False

    def test_proxy(self, proxy: str, timeout: int = _DEFAULT_TIMEOUT) -> bool:
        """Uji apakah proxy berfungsi. Kembalikan True jika OK."""
        try:
            resp = requests.get(
                "https://httpbin.org/ip",
                proxies=self._format_proxy(proxy),
                timeout=timeout,
            )
            ok = resp.status_code == 200
            status = "OK" if ok else f"HTTP {resp.status_code}"
            logger.debug("Proxy %s → %s", proxy, status)
            return ok
        except Exception as exc:  # noqa: BLE001
            logger.debug("Proxy %s gagal: %s", proxy, exc)
            return False

    def get_working_proxies(self) -> List[str]:
        """Kembalikan daftar proxy yang berfungsi."""
        working = [p for p in self._proxies if self.test_proxy(p)]
        logger.info("%d/%d proxy berfungsi.", len(working), len(self._proxies))
        return working

    @property
    def count(self) -> int:
        return len(self._proxies)
