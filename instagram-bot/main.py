#!/usr/bin/env python3
"""
main.py - Entry point Instagram Bot dengan menu interaktif
"""
import signal
import sys

from colorama import Fore, Style, init

import config
from modules.auth import InstagramAuth
from modules.actions import BotActions
from modules.proxy import ProxyManager
from modules.logger import setup_logger
from utils.validators import (
    validate_username,
    validate_proxy,
    validate_positive_int,
)

init(autoreset=True)
logger = setup_logger("main")

# ============================================================
# Banner
# ============================================================
BANNER = f"""{Fore.CYAN}{Style.BRIGHT}
╔══════════════════════════════════════════╗
║        Instagram Bot v{config.APP_VERSION}               ║
║   Termux-Compatible   |   By: Bot System ║
╚══════════════════════════════════════════╝
{Style.RESET_ALL}"""

# ============================================================
# Helpers
# ============================================================

_auth: InstagramAuth | None = None
_actions: BotActions | None = None
_proxy_manager: ProxyManager = ProxyManager()


def _require_login() -> bool:
    """Cek apakah sudah login. Minta login jika belum."""
    if _auth is None or _actions is None:
        print(Fore.RED + "❌ Anda belum login. Silakan login terlebih dahulu.")
        return False
    return True


def _prompt(msg: str, default: str = "") -> str:
    """Tampilkan prompt dan kembalikan input pengguna."""
    try:
        value = input(f"{Fore.YELLOW}{msg}{Style.RESET_ALL} ").strip()
        return value if value else default
    except (KeyboardInterrupt, EOFError):
        return default


def _print_separator() -> None:
    print(Fore.CYAN + "─" * 44)


# ============================================================
# Menu actions
# ============================================================

def menu_login() -> None:
    global _auth, _actions
    print(Fore.CYAN + "\n── Login ──")
    username = _prompt("Username Instagram:")
    if not validate_username(username):
        print(Fore.RED + "❌ Username tidak valid.")
        return
    password = _prompt("Password:")
    if not password:
        print(Fore.RED + "❌ Password tidak boleh kosong.")
        return

    _auth = InstagramAuth()

    # Terapkan proxy jika sudah dikonfigurasi
    if config.USE_PROXY:
        proxy = _proxy_manager.get_next()
        if proxy:
            _auth.set_proxy(proxy)

    if _auth.login(username, password):
        _actions = BotActions(_auth.client)
        print(Fore.GREEN + f"✅ Login berhasil sebagai @{username}")
    else:
        _auth = None
        print(Fore.RED + "❌ Login gagal.")


def menu_logout() -> None:
    global _auth, _actions
    if _auth:
        _auth.logout()
        if _actions:
            _actions.close()
        _auth = None
        _actions = None
        print(Fore.GREEN + "✅ Logout berhasil.")
    else:
        print(Fore.YELLOW + "ℹ️  Anda belum login.")


def menu_like_user() -> None:
    if not _require_login():
        return
    username = _prompt("Username target:")
    if not validate_username(username):
        print(Fore.RED + "❌ Username tidak valid.")
        return
    count_str = _prompt("Jumlah postingan yang di-like [5]:", "5")
    count = validate_positive_int(count_str, max_val=50)
    if count is None:
        print(Fore.RED + "❌ Jumlah tidak valid.")
        return
    liked = _actions.like_user_posts(username, count)
    print(Fore.GREEN + f"✅ {liked} postingan dilike dari @{username}")


def menu_like_hashtag() -> None:
    if not _require_login():
        return
    hashtag = _prompt("Hashtag (tanpa #):")
    if not hashtag:
        print(Fore.RED + "❌ Hashtag tidak boleh kosong.")
        return
    count_str = _prompt("Jumlah postingan [10]:", "10")
    count = validate_positive_int(count_str, max_val=100)
    if count is None:
        print(Fore.RED + "❌ Jumlah tidak valid.")
        return
    liked = _actions.like_hashtag_posts(hashtag, count)
    print(Fore.GREEN + f"✅ {liked} postingan dilike dari #{hashtag}")


def menu_follow_user() -> None:
    if not _require_login():
        return
    username = _prompt("Username yang ingin di-follow:")
    if not validate_username(username):
        print(Fore.RED + "❌ Username tidak valid.")
        return
    success = _actions.follow_user(username)
    if success:
        print(Fore.GREEN + f"✅ Berhasil follow @{username}")


def menu_follow_followers() -> None:
    if not _require_login():
        return
    target = _prompt("Username akun target (ambil follower-nya):")
    if not validate_username(target):
        print(Fore.RED + "❌ Username tidak valid.")
        return
    count_str = _prompt("Jumlah follower yang di-follow [20]:", "20")
    count = validate_positive_int(count_str, max_val=200)
    if count is None:
        print(Fore.RED + "❌ Jumlah tidak valid.")
        return
    followed = _actions.follow_user_followers(target, count)
    print(Fore.GREEN + f"✅ {followed} akun berhasil di-follow")


def menu_unfollow_user() -> None:
    if not _require_login():
        return
    username = _prompt("Username yang ingin di-unfollow:")
    if not validate_username(username):
        print(Fore.RED + "❌ Username tidak valid.")
        return
    success = _actions.unfollow_user(username)
    if success:
        print(Fore.GREEN + f"✅ Berhasil unfollow @{username}")


def menu_unfollow_non_followers() -> None:
    if not _require_login():
        return
    limit_str = _prompt("Maksimum unfollow [50]:", "50")
    limit = validate_positive_int(limit_str, max_val=500)
    if limit is None:
        print(Fore.RED + "❌ Jumlah tidak valid.")
        return
    unfollowed = _actions.unfollow_non_followers(limit)
    print(Fore.GREEN + f"✅ {unfollowed} akun non-follower di-unfollow")


def menu_comment_user() -> None:
    if not _require_login():
        return
    username = _prompt("Username target:")
    if not validate_username(username):
        print(Fore.RED + "❌ Username tidak valid.")
        return
    count_str = _prompt("Jumlah postingan yang dikomentari [3]:", "3")
    count = validate_positive_int(count_str, max_val=20)
    if count is None:
        print(Fore.RED + "❌ Jumlah tidak valid.")
        return
    commented = _actions.comment_on_user_posts(username, count=count)
    print(Fore.GREEN + f"✅ {commented} komentar berhasil dikirim ke @{username}")


def menu_comment_hashtag() -> None:
    if not _require_login():
        return
    hashtag = _prompt("Hashtag (tanpa #):")
    if not hashtag:
        print(Fore.RED + "❌ Hashtag tidak boleh kosong.")
        return
    count_str = _prompt("Jumlah postingan [5]:", "5")
    count = validate_positive_int(count_str, max_val=30)
    if count is None:
        print(Fore.RED + "❌ Jumlah tidak valid.")
        return
    commented = _actions.comment_on_hashtag(hashtag, count=count)
    print(Fore.GREEN + f"✅ {commented} komentar pada #{hashtag}")


def menu_add_proxy() -> None:
    proxy = _prompt("Masukkan proxy (format: ip:port atau http://ip:port):")
    if not validate_proxy(proxy):
        print(Fore.RED + "❌ Format proxy tidak valid.")
        return
    _proxy_manager.add_proxy(proxy)
    print(Fore.GREEN + f"✅ Proxy ditambahkan: {proxy}")


def menu_stats() -> None:
    if not _require_login():
        return
    stats = _actions.get_stats()
    print(Fore.CYAN + "\n── Statistik Bot ──")
    for key, val in stats.items():
        print(f"  {key.capitalize():<15}: {Fore.WHITE}{val}")
    _print_separator()


# ============================================================
# Main menu
# ============================================================

MENU_ITEMS = [
    ("1", "Login", menu_login),
    ("2", "Logout", menu_logout),
    ("", "", None),  # separator
    ("3", "Like postingan user", menu_like_user),
    ("4", "Like postingan hashtag", menu_like_hashtag),
    ("", "", None),
    ("5", "Follow user", menu_follow_user),
    ("6", "Follow followers dari akun tertentu", menu_follow_followers),
    ("7", "Unfollow user", menu_unfollow_user),
    ("8", "Unfollow non-followers", menu_unfollow_non_followers),
    ("", "", None),
    ("9", "Komen di postingan user", menu_comment_user),
    ("10", "Komen di postingan hashtag", menu_comment_hashtag),
    ("", "", None),
    ("11", "Tambah proxy", menu_add_proxy),
    ("12", "Lihat statistik", menu_stats),
    ("", "", None),
    ("0", "Keluar", None),
]


def print_menu() -> None:
    print(BANNER)
    for key, label, _ in MENU_ITEMS:
        if key == "":
            print()
        else:
            print(f"  {Fore.CYAN}[{key}]{Style.RESET_ALL} {label}")
    _print_separator()


def graceful_shutdown(signum, frame) -> None:  # noqa: ANN001
    """Handle Ctrl+C / SIGTERM dengan bersih."""
    print(Fore.YELLOW + "\n⚠️  Menerima sinyal shutdown...")
    if _actions:
        _actions.close()
    if _auth:
        _auth.logout()
    print(Fore.GREEN + "✅ Bot dihentikan dengan bersih.")
    sys.exit(0)


def main() -> None:
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    while True:
        print_menu()
        choice = _prompt("Pilih menu [0-12]:").strip()

        action_fn = None
        for key, _, fn in MENU_ITEMS:
            if key == choice:
                action_fn = fn
                break

        if choice == "0":
            graceful_shutdown(None, None)

        if action_fn is None:
            print(Fore.RED + "❌ Pilihan tidak valid. Coba lagi.")
        else:
            try:
                action_fn()
            except Exception as exc:  # noqa: BLE001
                logger.error("Error saat menjalankan aksi: %s", exc)


if __name__ == "__main__":
    main()
