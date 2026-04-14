"""
═══════════════════════════════════════════════════════════════════════════════
نظام تخزين قاعدة البيانات الشامل - بديل كامل لملفات JSON والملفات النصية
═══════════════════════════════════════════════════════════════════════════════

جميع البيانات تُخزن الآن في SQLite3:
- System Config (إعدادات النظام)
- Bot Data (بيانات البوتات)
- User Data (بيانات المستخدمين والإداريين)
- Messages & Content (الرسائل والمحتوى)
- Media Settings (إعدادات الوسائط)
- Files Storage (تخزين المحتوى من الملفات القديمة)
"""

import sqlite3
import os
import json
from threading import Lock
from datetime import datetime
from typing import Any, Optional, List, Dict

_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "bot_data.db")
_lock = Lock()


def _get_conn() -> sqlite3.Connection:
    """إنشاء اتصال آمن بقاعدة البيانات"""
    conn = sqlite3.connect(_DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")  # توازن بين السرعة والأمان
    return conn


def _init_database():
    """تهيئة كل جداول قاعدة البيانات"""
    with _lock:
        conn = _get_conn()
        try:
            # جدول الإعدادات النظامية
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    config_key   TEXT PRIMARY KEY,
                    config_value TEXT NOT NULL,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول بيانات البوتات المصنوعة
            conn.execute('''
                CREATE TABLE IF NOT EXISTS bot_instances (
                    bot_id       INTEGER PRIMARY KEY,
                    owner_id     INTEGER NOT NULL,
                    bot_token    TEXT UNIQUE NOT NULL,
                    bot_username TEXT UNIQUE NOT NULL,
                    bot_type     TEXT DEFAULT 'NAMERO4',
                    bot_settings JSON DEFAULT '{}',
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول المستخدمين
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id      INTEGER PRIMARY KEY,
                    username     TEXT,
                    first_name   TEXT,
                    last_name    TEXT,
                    joined_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول الإداريين والأعضاء
            conn.execute('''
                CREATE TABLE IF NOT EXISTS admins_members (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id       INTEGER NOT NULL,
                    user_id      INTEGER NOT NULL,
                    role         TEXT DEFAULT 'member',
                    added_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(bot_id, user_id),
                    FOREIGN KEY(bot_id) REFERENCES bot_instances(bot_id)
                )
            ''')
            
            # جدول الحظر والبان
            conn.execute('''
                CREATE TABLE IF NOT EXISTS banned_users (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id       INTEGER NOT NULL,
                    user_id      INTEGER NOT NULL,
                    reason       TEXT,
                    banned_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(bot_id, user_id),
                    FOREIGN KEY(bot_id) REFERENCES bot_instances(bot_id)
                )
            ''')
            
            # جدول الرسائل والمحتوى (مع دعم المحتوى العام)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS content_storage (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id       INTEGER DEFAULT 0,
                    content_key  TEXT NOT NULL,
                    content_type TEXT DEFAULT 'text',
                    content_data TEXT NOT NULL,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(bot_id, content_key)
                )
            ''')
            
            # جدول إعدادات الوسائط
            conn.execute('''
                CREATE TABLE IF NOT EXISTS media_settings (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id       INTEGER NOT NULL,
                    media_type   TEXT NOT NULL,
                    is_blocked   BOOLEAN DEFAULT 0,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(bot_id, media_type),
                    FOREIGN KEY(bot_id) REFERENCES bot_instances(bot_id)
                )
            ''')
            
            # جدول الاشتراكات والقنوات
            conn.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id       INTEGER NOT NULL,
                    channel_id   TEXT NOT NULL,
                    channel_type TEXT DEFAULT 'telegram',
                    is_required  BOOLEAN DEFAULT 1,
                    added_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(bot_id, channel_id),
                    FOREIGN KEY(bot_id) REFERENCES bot_instances(bot_id)
                )
            ''')
            
            # جدول الإحصائيات
            conn.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id       INTEGER NOT NULL,
                    total_users  INTEGER DEFAULT 0,
                    total_admins INTEGER DEFAULT 0,
                    broadcast_sent INTEGER DEFAULT 0,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(bot_id) REFERENCES bot_instances(bot_id)
                )
            ''')

            # جدول رسائل المحادثات (بديل ملفات messages/)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS bot_messages (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id       TEXT NOT NULL,
                    from_id      TEXT NOT NULL,
                    from_name    TEXT DEFAULT '',
                    from_user    TEXT DEFAULT '',
                    to_id        TEXT DEFAULT '',
                    to_user      TEXT DEFAULT '',
                    message_text TEXT DEFAULT '',
                    message_id   INTEGER DEFAULT 0,
                    direction    TEXT DEFAULT 'user->admin',
                    timestamp    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_bot_msg ON bot_messages(bot_id, timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_bot_msg_from ON bot_messages(bot_id, from_id)')

            conn.commit()
        finally:
            conn.close()


# ═══════════════════════════════════════════════════════════════════════════
# دوال نظام الإعدادات العام
# ═══════════════════════════════════════════════════════════════════════════

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
        print(f"[DB] Error reading config '{key}': {e}")
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
        print(f"[DB] Error saving config '{key}': {e}")
        return False


def delete_config(key: str) -> bool:
    """حذف إعداد من قاعدة البيانات"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute("DELETE FROM system_config WHERE config_key = ?", (key,))
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error deleting config '{key}': {e}")
        return False


def get_all_configs() -> dict:
    """جلب جميع الإعدادات"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                rows = conn.execute("SELECT config_key, config_value FROM system_config").fetchall()
                return {row[0]: row[1] for row in rows}
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error fetching all configs: {e}")
        return {}


# ═══════════════════════════════════════════════════════════════════════════
# دوال تخزين المحتوى (بديل read_file/write_file)
# ═══════════════════════════════════════════════════════════════════════════

def db_read(file_path: str, default: str = "") -> str:
    """قراءة محتوى نصي من قاعدة البيانات (بديل read_file)"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                # تأكد من البحث بـ bot_id=0 للبيانات العامة
                row = conn.execute(
                    "SELECT content_data FROM content_storage WHERE bot_id = 0 AND content_key = ? AND content_type = 'text'",
                    (file_path,)
                ).fetchone()
                return row[0] if row else default
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error reading '{file_path}': {e}")
        return default


def db_write(file_path: str, content: str) -> bool:
    """كتابة محتوى نصي في قاعدة البيانات (بديل write_file)"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                # تأكد من الكتابة بـ bot_id=0 للبيانات العامة
                conn.execute(
                    "INSERT OR REPLACE INTO content_storage (bot_id, content_key, content_type, content_data, updated_at) "
                    "VALUES (0, ?, 'text', ?, CURRENT_TIMESTAMP)",
                    (file_path, content)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error writing '{file_path}': {e}")
        return False


def db_append(file_path: str, content: str) -> bool:
    """إضافة محتوى إلى نص موجود"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                # اقرأ المحتوى الحالي مع bot_id=0
                row = conn.execute(
                    "SELECT content_data FROM content_storage WHERE bot_id = 0 AND content_key = ? AND content_type = 'text'",
                    (file_path,)
                ).fetchone()
                
                current = (row[0] if row else "") + content
                
                # اكتب المحتوى المُحدث مع bot_id=0
                conn.execute(
                    "INSERT OR REPLACE INTO content_storage (bot_id, content_key, content_type, content_data, updated_at) "
                    "VALUES (0, ?, 'text', ?, CURRENT_TIMESTAMP)",
                    (file_path, current)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error appending to '{file_path}': {e}")
        return False


def db_delete(file_path: str) -> bool:
    """حذف محتوى من قاعدة البيانات"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                # تأكد من حذف البيانات مع bot_id=0 فقط
                conn.execute("DELETE FROM content_storage WHERE bot_id = 0 AND content_key = ?", (file_path,))
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error deleting '{file_path}': {e}")
        return False


def db_exists(file_path: str) -> bool:
    """التحقق من وجود مفتاح في قاعدة البيانات"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                # تأكد من البحث بـ bot_id=0 للبيانات العامة
                row = conn.execute(
                    "SELECT 1 FROM content_storage WHERE bot_id = 0 AND content_key = ?",
                    (file_path,)
                ).fetchone()
                return row is not None
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error checking existence of '{file_path}': {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# دوال تخزين JSON (بديل read_json/write_json)
# ═══════════════════════════════════════════════════════════════════════════

def db_read_json(file_path: str, default: Optional[Dict] = None) -> Dict:
    """قراءة بيانات JSON من قاعدة البيانات (بديل read_json)"""
    if default is None:
        default = {}
    
    try:
        with _lock:
            conn = _get_conn()
            try:
                # تأكد من البحث بـ bot_id=0 للبيانات العامة
                row = conn.execute(
                    "SELECT content_data FROM content_storage WHERE bot_id = 0 AND content_key = ? AND content_type = 'json'",
                    (file_path,)
                ).fetchone()
                
                if row:
                    return json.loads(row[0])
                return default
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error reading JSON '{file_path}': {e}")
        return default


def db_write_json(file_path: str, data: Dict) -> bool:
    """كتابة بيانات JSON في قاعدة البيانات (بديل write_json)"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                # تأكد من الكتابة بـ bot_id=0 للبيانات العامة
                conn.execute(
                    "INSERT OR REPLACE INTO content_storage (bot_id, content_key, content_type, content_data, updated_at) "
                    "VALUES (0, ?, 'json', ?, CURRENT_TIMESTAMP)",
                    (file_path, json.dumps(data, ensure_ascii=False))
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error writing JSON '{file_path}': {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# دوال إدارة البيانات القائمة على الأسطر (بديل file_lines)
# ═══════════════════════════════════════════════════════════════════════════

def db_lines(file_path: str) -> List[str]:
    """قراءة أسطر من قاعدة البيانات (بديل file_lines)"""
    try:
        content = db_read(file_path, "").strip()
        return [line.strip() for line in content.split("\n") if line.strip()]
    except Exception as e:
        print(f"[DB] Error reading lines from '{file_path}': {e}")
        return []


def db_lines_write(file_path: str, lines: List[str]) -> bool:
    """كتابة أسطر في قاعدة البيانات"""
    try:
        content = "\n".join(str(line).strip() for line in lines if line.strip())
        return db_write(file_path, content)
    except Exception as e:
        print(f"[DB] Error writing lines to '{file_path}': {e}")
        return False


def db_lines_add(file_path: str, line: str) -> bool:
    """إضافة سطر جديد"""
    try:
        current_lines = db_lines(file_path)
        current_lines.append(str(line).strip())
        return db_lines_write(file_path, current_lines)
    except Exception as e:
        print(f"[DB] Error adding line to '{file_path}': {e}")
        return False


def db_lines_remove(file_path: str, line: str) -> bool:
    """إزالة سطر معين"""
    try:
        current_lines = db_lines(file_path)
        current_lines = [l for l in current_lines if l != str(line).strip()]
        return db_lines_write(file_path, current_lines)
    except Exception as e:
        print(f"[DB] Error removing line from '{file_path}': {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# دوال إدارة البوتات
# ═══════════════════════════════════════════════════════════════════════════

def db_add_bot(bot_id: int, owner_id: int, bot_token: str, bot_username: str, bot_type: str = "NAMERO4") -> bool:
    """إضافة بوت جديد"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "INSERT INTO bot_instances (bot_id, owner_id, bot_token, bot_username, bot_type) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (bot_id, owner_id, bot_token, bot_username, bot_type)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error adding bot {bot_id}: {e}")
        return False


def db_get_bot(bot_id: int) -> Optional[Dict]:
    """جلب بيانات بوت"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                row = conn.execute(
                    "SELECT * FROM bot_instances WHERE bot_id = ?",
                    (bot_id,)
                ).fetchone()
                return dict(row) if row else None
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error getting bot {bot_id}: {e}")
        return None


def db_list_bots(owner_id: int = None) -> List[Dict]:
    """قائمة بالبوتات"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                if owner_id:
                    rows = conn.execute(
                        "SELECT * FROM bot_instances WHERE owner_id = ?",
                        (owner_id,)
                    ).fetchall()
                else:
                    rows = conn.execute("SELECT * FROM bot_instances").fetchall()
                
                return [dict(row) for row in rows]
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error listing bots: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════
# دوال إدارة المستخدمين والإداريين
# ═══════════════════════════════════════════════════════════════════════════

def db_add_user(user_id: int, username: str = "", first_name: str = "", last_name: str = "") -> bool:
    """إضافة مستخدم جديد"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) "
                    "VALUES (?, ?, ?, ?)",
                    (user_id, username, first_name, last_name)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error adding user {user_id}: {e}")
        return False


def db_add_admin(bot_id: int, user_id: int, role: str = "admin") -> bool:
    """إضافة إداري/عضو للبوت"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO admins_members (bot_id, user_id, role) "
                    "VALUES (?, ?, ?)",
                    (bot_id, user_id, role)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error adding admin {user_id} to bot {bot_id}: {e}")
        return False


def db_get_admins(bot_id: int) -> List[Dict]:
    """جلب قائمة الإداريين"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                rows = conn.execute(
                    "SELECT * FROM admins_members WHERE bot_id = ? AND role = 'admin'",
                    (bot_id,)
                ).fetchall()
                return [dict(row) for row in rows]
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error getting admins for bot {bot_id}: {e}")
        return []


def db_ban_user(bot_id: int, user_id: int, reason: str = "") -> bool:
    """حظر مستخدم"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO banned_users (bot_id, user_id, reason) "
                    "VALUES (?, ?, ?)",
                    (bot_id, user_id, reason)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error banning user {user_id} in bot {bot_id}: {e}")
        return False


def db_unban_user(bot_id: int, user_id: int) -> bool:
    """فك الحظر عن مستخدم"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "DELETE FROM banned_users WHERE bot_id = ? AND user_id = ?",
                    (bot_id, user_id)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error unbanning user {user_id} in bot {bot_id}: {e}")
        return False


def db_is_banned(bot_id: int, user_id: int) -> bool:
    """التحقق من حظر المستخدم"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                row = conn.execute(
                    "SELECT 1 FROM banned_users WHERE bot_id = ? AND user_id = ?",
                    (bot_id, user_id)
                ).fetchone()
                return row is not None
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error checking ban status: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# دوال إدارة إعدادات الوسائط
# ═══════════════════════════════════════════════════════════════════════════

def db_set_media_lock(bot_id: int, media_type: str, is_blocked: bool) -> bool:
    """تعيين حالة قفل الوسائط"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO media_settings (bot_id, media_type, is_blocked, updated_at) "
                    "VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                    (bot_id, media_type, 1 if is_blocked else 0)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error setting media lock: {e}")
        return False


def db_is_media_blocked(bot_id: int, media_type: str) -> bool:
    """التحقق من قفل الوسائط"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                row = conn.execute(
                    "SELECT is_blocked FROM media_settings WHERE bot_id = ? AND media_type = ?",
                    (bot_id, media_type)
                ).fetchone()
                return bool(row[0]) if row else False
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error checking media block: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# حذف بيانات البوت كاملاً من قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════

def db_delete_bot_data(bot_dir: str) -> int:
    """حذف جميع بيانات البوت من content_storage و bot_messages"""
    deleted = 0
    try:
        prefix = bot_dir.rstrip("/") + "/"
        with _lock:
            conn = _get_conn()
            try:
                cur = conn.execute(
                    "DELETE FROM content_storage WHERE content_key = ? OR content_key LIKE ?",
                    (bot_dir, prefix + "%")
                )
                deleted += cur.rowcount
                cur2 = conn.execute(
                    "DELETE FROM bot_messages WHERE bot_id = ?",
                    (os.path.basename(bot_dir),)
                )
                deleted += cur2.rowcount
                conn.commit()
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error deleting bot data '{bot_dir}': {e}")
    return deleted


# ═══════════════════════════════════════════════════════════════════════════
# دوال رسائل المحادثات (بديل ملفات messages/)
# ═══════════════════════════════════════════════════════════════════════════

def db_save_message(bot_id: str, from_id: str, from_name: str, from_user: str,
                    to_id: str, to_user: str, text: str, message_id: int,
                    direction: str = "user->admin") -> bool:
    """حفظ رسالة محادثة مباشرة في قاعدة البيانات"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                conn.execute(
                    "INSERT INTO bot_messages "
                    "(bot_id, from_id, from_name, from_user, to_id, to_user, "
                    " message_text, message_id, direction) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(bot_id), str(from_id), from_name or "", from_user or "",
                     str(to_id), to_user or "", str(text)[:500],
                     int(message_id) if message_id else 0, direction)
                )
                conn.commit()
                return True
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error saving message: {e}")
        return False


def db_get_messages(bot_id: str, from_id: str = None, limit: int = 100) -> List[Dict]:
    """جلب رسائل البوت (اختياري: تصفية بـ from_id)"""
    try:
        with _lock:
            conn = _get_conn()
            try:
                if from_id:
                    rows = conn.execute(
                        "SELECT * FROM bot_messages WHERE bot_id = ? AND from_id = ? "
                        "ORDER BY timestamp DESC LIMIT ?",
                        (str(bot_id), str(from_id), limit)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM bot_messages WHERE bot_id = ? "
                        "ORDER BY timestamp DESC LIMIT ?",
                        (str(bot_id), limit)
                    ).fetchall()
                return [dict(row) for row in rows]
            finally:
                conn.close()
    except Exception as e:
        print(f"[DB] Error getting messages: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════
# تهيئة قاعدة البيانات عند الاستيراد
# ═══════════════════════════════════════════════════════════════════════════

_init_database()
