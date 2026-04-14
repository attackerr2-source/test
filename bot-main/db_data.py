"""
نظام ادارة البيانات الشامل - Database-First Architecture
جميع البيانات تُخزن في قاعدة البيانات جزء من الملفات الخارجية
"""

import sqlite3
import json
import os
from threading import Lock
from datetime import datetime
from typing import Any, Optional, List, Dict

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "bot_data.db")
_lock = Lock()


def _get_conn() -> sqlite3.Connection:
    """الحصول على اتصال قاعدة البيانات مع تمكين WAL mode"""
    conn = sqlite3.connect(_DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db():
    """إنشاء جميع الجداول المطلوبة"""
    conn = _get_conn()
    try:
        cursor = conn.cursor()
        
        # ════════════════════════════════════════════════════════════════
        # 1. نظام الإعدادات العام (System Configuration)
        # ════════════════════════════════════════════════════════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                config_key   TEXT PRIMARY KEY,
                config_value TEXT NOT NULL,
                data_type    TEXT DEFAULT 'string',
                updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ════════════════════════════════════════════════════════════════
        # 2. بيانات البوتات (Bot Information)
        # ════════════════════════════════════════════════════════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bots (
                bot_id          TEXT PRIMARY KEY,
                bot_type        TEXT NOT NULL,
                owner_id        TEXT NOT NULL,
                token           TEXT NOT NULL,
                username        TEXT,
                is_active       BOOLEAN DEFAULT 1,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ════════════════════════════════════════════════════════════════
        # 3. إعدادات البوت (Bot Settings)
        # ════════════════════════════════════════════════════════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_settings (
                bot_id              TEXT PRIMARY KEY,
                settings_json       TEXT NOT NULL,
                wellcome_message    TEXT,
                info_message        TEXT,
                update_channel      TEXT,
                admin_notification  BOOLEAN DEFAULT 1,
                updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(bot_id) REFERENCES bots(bot_id)
            )
        ''')
        
        # ════════════════════════════════════════════════════════════════
        # 4. المستخدمين (Users)
        # ════════════════════════════════════════════════════════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id         TEXT NOT NULL,
                bot_id          TEXT NOT NULL,
                username        TEXT,
                first_name      TEXT,
                last_name       TEXT,
                is_admin        BOOLEAN DEFAULT 0,
                is_banned       BOOLEAN DEFAULT 0,
                message_count   INTEGER DEFAULT 0,
                joined_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(user_id, bot_id),
                FOREIGN KEY(bot_id) REFERENCES bots(bot_id)
            )
        ''')
        
        # ════════════════════════════════════════════════════════════════
        # 5. قوائم الحظر (Ban Lists)
        # ════════════════════════════════════════════════════════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ban_list (
                user_id     TEXT NOT NULL,
                bot_id      TEXT NOT NULL,
                reason      TEXT,
                banned_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(user_id, bot_id),
                FOREIGN KEY(bot_id) REFERENCES bots(bot_id)
            )
        ''')
        
        # ════════════════════════════════════════════════════════════════
        # 6. المسؤولين والأدمن (Admins)
        # ════════════════════════════════════════════════════════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                user_id     TEXT NOT NULL,
                bot_id      TEXT NOT NULL,
                permissions TEXT DEFAULT 'all',
                added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(user_id, bot_id),
                FOREIGN KEY(bot_id) REFERENCES bots(bot_id)
            )
        ''')
        
        # ════════════════════════════════════════════════════════════════
        # 7. الرسائل والبث (Messages & Broadcasts)
        # ════════════════════════════════════════════════════════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id          TEXT NOT NULL,
                message_text    TEXT NOT NULL,
                message_type    TEXT,
                sender_id       TEXT,
                recipient_id    TEXT,
                is_broadcast    BOOLEAN DEFAULT 0,
                broadcast_count INTEGER DEFAULT 0,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(bot_id) REFERENCES bots(bot_id)
            )
        ''')
        
        # ════════════════════════════════════════════════════════════════
        # 8. قنوات الاشتراك الإجباري (Subscription Channels)
        # ════════════════════════════════════════════════════════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscription_channels (
                channel_id  TEXT NOT NULL,
                bot_id      TEXT NOT NULL,
                channel_url TEXT NOT NULL,
                channel_name TEXT,
                is_active   BOOLEAN DEFAULT 1,
                added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(channel_id, bot_id),
                FOREIGN KEY(bot_id) REFERENCES bots(bot_id)
            )
        ''')
        
        # ════════════════════════════════════════════════════════════════
        # 9. الأزرار والقوائم (Buttons & Keyboards)
        # ════════════════════════════════════════════════════════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keyboards (
                keyboard_id         INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id              TEXT NOT NULL,
                keyboard_name       TEXT,
                keyboard_json       TEXT NOT NULL,
                keyboard_type       TEXT,
                created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(bot_id) REFERENCES bots(bot_id)
            )
        ''')
        
        # ════════════════════════════════════════════════════════════════
        # 10. البيانات الإحصائية (Statistics)
        # ════════════════════════════════════════════════════════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                stat_id             INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id              TEXT NOT NULL,
                total_users         INTEGER DEFAULT 0,
                total_messages      INTEGER DEFAULT 0,
                total_broadcasts    INTEGER DEFAULT 0,
                total_admins        INTEGER DEFAULT 0,
                recorded_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(bot_id) REFERENCES bots(bot_id)
            )
        ''')
        
        # ════════════════════════════════════════════════════════════════
        # 11. السجلات والأن لوجات (Logs)
        # ════════════════════════════════════════════════════════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id      TEXT NOT NULL,
                log_level   TEXT,
                log_message TEXT,
                log_data    TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(bot_id) REFERENCES bots(bot_id)
            )
        ''')
        
        conn.commit()
        print("✅ جميع الجداول تم إنشاؤها بنجاح")
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════════
# دوال الإعدادات العام (System Config)
# ════════════════════════════════════════════════════════════════════════════

def get_config(key: str, default: str = "") -> str:
    """قراءة إعداد من قاعدة البيانات"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                row = conn.execute(
                    "SELECT config_value FROM system_config WHERE config_key = ?",
                    (key,)
                ).fetchone()
                return str(row[0]) if row else default
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] خطأ في قراءة {key}: {e}")
        return default


def set_config(key: str, value: str) -> bool:
    """حفظ إعداد في قاعدة البيانات"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO system_config (config_key, config_value, updated_at) "
                    "VALUES (?, ?, CURRENT_TIMESTAMP)",
                    (key, str(value))
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] خطأ في حفظ {key}: {e}")
        return False


# ════════════════════════════════════════════════════════════════════════════
# دوال البيانات العامة (Generic Data Operations)
# ════════════════════════════════════════════════════════════════════════════

def get_json_data(table: str, key_name: str, key_value: str, json_column: str) -> dict:
    """قراءة بيانات JSON من جدول معين"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                row = conn.execute(
                    f"SELECT {json_column} FROM {table} WHERE {key_name} = ?",
                    (key_value,)
                ).fetchone()
                if row and row[0]:
                    return json.loads(row[0])
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] خطأ في قراءة {table}: {e}")
    return {}


def set_json_data(table: str, key_name: str, key_value: str, json_column: str, data: dict) -> bool:
    """حفظ بيانات JSON في جدول معين"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                json_str = json.dumps(data, ensure_ascii=False)
                conn.execute(
                    f"INSERT OR REPLACE INTO {table} ({key_name}, {json_column}, updated_at) "
                    f"VALUES (?, ?, CURRENT_TIMESTAMP)",
                    (key_value, json_str)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] خطأ في حفظ {table}: {e}")
        return False


# ════════════════════════════════════════════════════════════════════════════
# دوال البيانات النصية (Text/List Operations)
# ════════════════════════════════════════════════════════════════════════════

def get_list_from_table(table: str, column: str, where_clause: str = None, where_value: str = None) -> list:
    """قراءة قائمة من جدول"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                if where_clause and where_value:
                    rows = conn.execute(
                        f"SELECT {column} FROM {table} WHERE {where_clause} = ?",
                        (where_value,)
                    ).fetchall()
                else:
                    rows = conn.execute(f"SELECT {column} FROM {table}").fetchall()
                return [str(row[0]) for row in rows if row[0]]
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] خطأ في قراءة قائمة من {table}: {e}")
        return []


def add_to_list(table: str, column: str, value: str, where_clause: str = None, where_value: str = None) -> bool:
    """إضافة عنصر لقائمة"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    f"INSERT INTO {table} ({column}{', ' + where_clause if where_clause else ''}) "
                    f"VALUES (?{', ?' if where_clause else ''})",
                    (value, where_value) if where_clause else (value,)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] خطأ في الإضافة إلى {table}: {e}")
        return False


def remove_from_list(table: str, key_column: str, key_value: str) -> bool:
    """حذف عنصر من قائمة"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(f"DELETE FROM {table} WHERE {key_column} = ?", (key_value,))
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] خطأ في الحذف من {table}: {e}")
        return False


# ════════════════════════════════════════════════════════════════════════════
# دوال خاصة للبيانات الشائعة
# ════════════════════════════════════════════════════════════════════════════

def get_bot_settings(bot_id: str) -> dict:
    """جلب إعدادات البوت"""
    return get_json_data("bot_settings", "bot_id", bot_id, "settings_json")


def set_bot_settings(bot_id: str, settings: dict) -> bool:
    """حفظ إعدادات البوت"""
    return set_json_data("bot_settings", "bot_id", bot_id, "settings_json", settings)


def get_users_count(bot_id: str) -> int:
    """عدد المستخدمين"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                row = conn.execute(
                    "SELECT COUNT(*) FROM users WHERE bot_id = ? AND is_banned = 0",
                    (bot_id,)
                ).fetchone()
                return row[0] if row else 0
            finally:
                conn.close()
    except Exception:
        return 0


def get_admins_list(bot_id: str) -> list:
    """قائمة الأدمن"""
    return get_list_from_table("admins", "user_id", "bot_id", bot_id)


def get_ban_list(bot_id: str) -> list:
    """قائمة المحظورين"""
    return get_list_from_table("ban_list", "user_id", "bot_id", bot_id)


def add_admin(bot_id: str, user_id: str) -> bool:
    """إضافة أدمن"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO admins (bot_id, user_id) VALUES (?, ?)",
                    (bot_id, user_id)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception:
        return False


def remove_admin(bot_id: str, user_id: str) -> bool:
    """حذف أدمن"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "DELETE FROM admins WHERE bot_id = ? AND user_id = ?",
                    (bot_id, user_id)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception:
        return False


def ban_user(bot_id: str, user_id: str, reason: str = "") -> bool:
    """حظر مستخدم"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO ban_list (bot_id, user_id, reason) VALUES (?, ?, ?)",
                    (bot_id, user_id, reason)
                )
                conn.execute(
                    "UPDATE users SET is_banned = 1 WHERE bot_id = ? AND user_id = ?",
                    (bot_id, user_id)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception:
        return False


def unban_user(bot_id: str, user_id: str) -> bool:
    """إزالة الحظر"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "DELETE FROM ban_list WHERE bot_id = ? AND user_id = ?",
                    (bot_id, user_id)
                )
                conn.execute(
                    "UPDATE users SET is_banned = 0 WHERE bot_id = ? AND user_id = ?",
                    (bot_id, user_id)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception:
        return False


# ════════════════════════════════════════════════════════════════════════════
# تهيئة قاعدة البيانات
# ════════════════════════════════════════════════════════════════════════════

# تشغيل عند الاستيراد
try:
    _init_db()
except Exception as e:
    print(f"[DB] خطأ في تهيئة قاعدة البيانات: {e}")
