"""
validators.py - Validasi input untuk Instagram Bot
"""
import re
from typing import Optional


def validate_username(username: str) -> bool:
    """
    Validasi username Instagram.
    Aturan: 1-30 karakter, hanya huruf/angka/titik/underscore.
    """
    if not username:
        return False
    pattern = r"^[a-zA-Z0-9._]{1,30}$"
    return bool(re.match(pattern, username))


def validate_url(url: str) -> bool:
    """Validasi URL sederhana."""
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, url, re.IGNORECASE))


def validate_proxy(proxy: str) -> bool:
    """
    Validasi format proxy.
    Format yang diterima:
      - ip:port
      - user:pass@ip:port
      - http://ip:port
      - socks5://ip:port
      - ******ip:port
    """
    if not proxy:
        return False
    # Hapus schema jika ada
    cleaned = re.sub(r"^(https?|socks[45])://", "", proxy)
    # user:pass@ip:port  atau  ip:port
    pattern = r"^(?:[^@:]+:[^@:]+@)?[\w\-.]+:\d{1,5}$"
    return bool(re.match(pattern, cleaned))


def validate_positive_int(value: str, max_val: Optional[int] = None) -> Optional[int]:
    """
    Validasi bahwa value adalah integer positif.
    Kembalikan int jika valid, None jika tidak.
    """
    try:
        n = int(value)
        if n <= 0:
            return None
        if max_val is not None and n > max_val:
            return None
        return n
    except (ValueError, TypeError):
        return None
