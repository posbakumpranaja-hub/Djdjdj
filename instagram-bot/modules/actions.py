"""
actions.py - Semua aksi bot Instagram (like, follow, comment, unfollow, dll.)
"""
import random
import sqlite3
import time
from typing import List, Optional

from instagrapi import Client
from instagrapi.exceptions import ClientError

import config
from modules.logger import setup_logger

logger = setup_logger(__name__)


class BotActions:
    """
    Semua aksi bot: like, follow, unfollow, comment, scrape followers, dll.
    Setiap aksi dilengkapi dengan rate-limiting dan pencatatan ke database.
    """

    def __init__(self, client: Client) -> None:
        self.client = client
        self._db = self._init_db()

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    def _init_db(self) -> sqlite3.Connection:
        """Inisialisasi database SQLite untuk tracking."""
        conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS followed (
                username TEXT PRIMARY KEY,
                user_id  TEXT,
                ts       INTEGER DEFAULT (strftime('%s','now'))
            );
            CREATE TABLE IF NOT EXISTS liked (
                media_id TEXT PRIMARY KEY,
                username TEXT,
                ts       INTEGER DEFAULT (strftime('%s','now'))
            );
            CREATE TABLE IF NOT EXISTS commented (
                media_id TEXT,
                comment  TEXT,
                ts       INTEGER DEFAULT (strftime('%s','now'))
            );
            CREATE TABLE IF NOT EXISTS unfollowed (
                username TEXT PRIMARY KEY,
                ts       INTEGER DEFAULT (strftime('%s','now'))
            );
            """
        )
        conn.commit()
        return conn

    def _record(self, table: str, **kwargs) -> None:
        """Simpan satu baris ke tabel database."""
        cols = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?"] * len(kwargs))
        try:
            self._db.execute(
                f"INSERT OR REPLACE INTO {table} ({cols}) VALUES ({placeholders})",
                list(kwargs.values()),
            )
            self._db.commit()
        except sqlite3.Error as exc:
            logger.warning("DB error pada tabel %s: %s", table, exc)

    def _already_done(self, table: str, key_col: str, value: str) -> bool:
        """Cek apakah aksi sudah pernah dilakukan."""
        row = self._db.execute(
            f"SELECT 1 FROM {table} WHERE {key_col} = ?", (value,)
        ).fetchone()
        return row is not None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _delay(self, extra: float = 0.0) -> None:
        """Tunggu sesuai konfigurasi delay + jitter acak."""
        base = config.DELAY_BETWEEN_ACTIONS
        jitter = random.uniform(0.5, 1.5)
        time.sleep(base * jitter + extra)

    def _safe_call(self, func, *args, **kwargs):
        """Jalankan panggilan API dengan error handling standar."""
        try:
            result = func(*args, **kwargs)
            self._delay()
            return result
        except ClientError as exc:
            logger.error("Instagram API error: %s", exc)
        except Exception as exc:  # noqa: BLE001
            logger.error("Error tak terduga: %s", exc)
        return None

    # ------------------------------------------------------------------
    # User helpers
    # ------------------------------------------------------------------

    def _get_user_id(self, username: str) -> Optional[str]:
        """Ambil user ID dari username."""
        try:
            user = self.client.user_info_by_username(username)
            return str(user.pk)
        except Exception as exc:  # noqa: BLE001
            logger.error("Tidak dapat menemukan user '%s': %s", username, exc)
            return None

    # ------------------------------------------------------------------
    # LIKE
    # ------------------------------------------------------------------

    def like_user_posts(self, username: str, count: int = 5) -> int:
        """Like sejumlah postingan terbaru dari seorang user."""
        user_id = self._get_user_id(username)
        if not user_id:
            return 0

        medias = self._safe_call(self.client.user_medias, user_id, count)
        if not medias:
            return 0

        liked = 0
        for media in medias:
            media_id = str(media.pk)
            if self._already_done("liked", "media_id", media_id):
                logger.debug("Sudah dilike: %s", media_id)
                continue
            result = self._safe_call(self.client.media_like, media_id)
            if result:
                self._record("liked", media_id=media_id, username=username)
                liked += 1
                logger.info("✅ Like media %s dari @%s", media_id, username)
            else:
                logger.warning("⚠️  Gagal like media %s", media_id)

        logger.info("Total like: %d/%d untuk @%s", liked, count, username)
        return liked

    def like_hashtag_posts(self, hashtag: str, count: int = 10) -> int:
        """Like postingan dari hashtag tertentu."""
        medias = self._safe_call(self.client.hashtag_medias_recent, hashtag, count)
        if not medias:
            return 0

        liked = 0
        for media in medias:
            media_id = str(media.pk)
            if self._already_done("liked", "media_id", media_id):
                continue
            result = self._safe_call(self.client.media_like, media_id)
            if result:
                username = media.user.username if media.user else "unknown"
                self._record("liked", media_id=media_id, username=username)
                liked += 1
                logger.info("✅ Like #%s media %s", hashtag, media_id)

        logger.info("Total like hashtag #%s: %d/%d", hashtag, liked, count)
        return liked

    # ------------------------------------------------------------------
    # FOLLOW / UNFOLLOW
    # ------------------------------------------------------------------

    def follow_user(self, username: str) -> bool:
        """Follow seorang user."""
        if self._already_done("followed", "username", username):
            logger.info("Sudah follow @%s sebelumnya.", username)
            return False

        user_id = self._get_user_id(username)
        if not user_id:
            return False

        result = self._safe_call(self.client.user_follow, int(user_id))
        if result:
            self._record("followed", username=username, user_id=user_id)
            logger.info("✅ Follow @%s", username)
            return True

        logger.warning("⚠️  Gagal follow @%s", username)
        return False

    def follow_user_followers(self, target_username: str, count: int = 20) -> int:
        """Follow follower dari akun tertentu."""
        user_id = self._get_user_id(target_username)
        if not user_id:
            return 0

        followers = self._safe_call(
            self.client.user_followers, int(user_id), amount=count
        )
        if not followers:
            return 0

        followed = 0
        for uid, user_short in followers.items():
            username = user_short.username
            if self.follow_user(username):
                followed += 1
            if followed >= count:
                break

        logger.info(
            "Total follow followers @%s: %d/%d", target_username, followed, count
        )
        return followed

    def unfollow_user(self, username: str) -> bool:
        """Unfollow seorang user."""
        user_id = self._get_user_id(username)
        if not user_id:
            return False

        result = self._safe_call(self.client.user_unfollow, int(user_id))
        if result:
            self._record("unfollowed", username=username)
            logger.info("✅ Unfollow @%s", username)
            return True

        logger.warning("⚠️  Gagal unfollow @%s", username)
        return False

    def unfollow_non_followers(self, limit: int = 50) -> int:
        """Unfollow akun yang tidak follow balik."""
        cur = self._db.execute("SELECT username FROM followed")
        followed_list = [row[0] for row in cur.fetchall()]

        me = self.client.account_info()
        my_id = str(me.pk)

        my_followers = self._safe_call(
            self.client.user_followers, int(my_id), amount=5000
        )
        follower_usernames = (
            {u.username for u in my_followers.values()} if my_followers else set()
        )

        unfollowed = 0
        for username in followed_list:
            if unfollowed >= limit:
                break
            if username not in follower_usernames:
                if self.unfollow_user(username):
                    unfollowed += 1

        logger.info("Total unfollow non-followers: %d", unfollowed)
        return unfollowed

    # ------------------------------------------------------------------
    # COMMENT
    # ------------------------------------------------------------------

    def comment_on_user_posts(
        self,
        username: str,
        comments: Optional[List[str]] = None,
        count: int = 3,
    ) -> int:
        """Komen pada postingan terbaru seorang user."""
        if comments is None:
            comments = config.DEFAULT_COMMENTS

        user_id = self._get_user_id(username)
        if not user_id:
            return 0

        medias = self._safe_call(self.client.user_medias, user_id, count)
        if not medias:
            return 0

        commented = 0
        for media in medias:
            media_id = str(media.pk)
            comment_text = random.choice(comments)
            result = self._safe_call(
                self.client.media_comment, media_id, comment_text
            )
            if result:
                self._record(
                    "commented", media_id=media_id, comment=comment_text
                )
                commented += 1
                logger.info(
                    "✅ Komentar '%s' pada media %s @%s",
                    comment_text,
                    media_id,
                    username,
                )

        return commented

    def comment_on_hashtag(
        self,
        hashtag: str,
        comments: Optional[List[str]] = None,
        count: int = 5,
    ) -> int:
        """Komen pada postingan dari hashtag tertentu."""
        if comments is None:
            comments = config.DEFAULT_COMMENTS

        medias = self._safe_call(self.client.hashtag_medias_recent, hashtag, count)
        if not medias:
            return 0

        commented = 0
        for media in medias:
            media_id = str(media.pk)
            comment_text = random.choice(comments)
            result = self._safe_call(
                self.client.media_comment, media_id, comment_text
            )
            if result:
                self._record(
                    "commented", media_id=media_id, comment=comment_text
                )
                commented += 1
                logger.info("✅ Komentar pada #%s media %s", hashtag, media_id)

        return commented

    # ------------------------------------------------------------------
    # STATS
    # ------------------------------------------------------------------

    def get_stats(self) -> dict:
        """Kembalikan statistik aksi yang telah dilakukan."""
        stats: dict = {}
        for table in ("followed", "liked", "commented", "unfollowed"):
            row = self._db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            stats[table] = row[0] if row else 0
        return stats

    def close(self) -> None:
        """Tutup koneksi database."""
        self._db.close()
