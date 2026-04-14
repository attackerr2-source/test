"""
Database Configuration and Management
قاعدة البيانات الرئيسية - SQLite
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
from threading import Lock
import config

class DatabaseManager:
    """
    مدير قاعدة البيانات الرئيسي
    يدير جميع عمليات قاعدة البيانات بشكل آمن ومتزامن
    """
    
    def __init__(self, db_path: str = "bot_data.db"):
        self.db_path = db_path
        self.lock = Lock()
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """الحصول على اتصال آمن بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """إنشاء جداول قاعدة البيانات الأساسية"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # جدول المستخدمين
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    is_banned INTEGER DEFAULT 0,
                    is_admin INTEGER DEFAULT 0,
                    last_activity TIMESTAMP
                )
            ''')
            
            # جدول البوتات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bots (
                    bot_id TEXT PRIMARY KEY,
                    bot_name TEXT NOT NULL,
                    bot_token TEXT NOT NULL UNIQUE,
                    bot_type TEXT,
                    creator_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    settings TEXT
                )
            ''')
            
            # جدول الإدارة
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    admin_id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    added_by INTEGER,
                    permissions TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # جدول الإذاعات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS broadcasts (
                    broadcast_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER,
                    message_text TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    successful_count INTEGER DEFAULT 0,
                    failed_count INTEGER DEFAULT 0,
                    total_users INTEGER,
                    FOREIGN KEY (admin_id) REFERENCES admins(admin_id)
                )
            ''')
            
            # جدول الرسائل
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    bot_id TEXT,
                    message_text TEXT,
                    message_type TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_forwarded INTEGER DEFAULT 0,
                    forwarded_to INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (bot_id) REFERENCES bots(bot_id)
                )
            ''')
            
            # جدول الإعدادات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id TEXT NOT NULL,
                    setting_key TEXT NOT NULL,
                    setting_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(bot_id, setting_key),
                    FOREIGN KEY (bot_id) REFERENCES bots(bot_id)
                )
            ''')
            
            # جدول السجل (Logs)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id TEXT,
                    user_id INTEGER,
                    action TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bot_id) REFERENCES bots(bot_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # جدول اعدادات النظام العامة
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    config_key TEXT PRIMARY KEY,
                    config_value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # إنشاء الفهارس لتسريع الاستعلامات
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_id ON bots(bot_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_admin_id ON admins(admin_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_message_time ON messages(sent_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_time ON logs(timestamp)')
            
            conn.commit()
            conn.close()
    
    # ============ عمليات المستخدمين ============
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None) -> bool:
        """إضافة مستخدم جديد"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO users 
                    (user_id, username, first_name, last_name, last_activity)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error adding user: {e}")
                return False
            finally:
                conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """الحصول على بيانات مستخدم"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
            finally:
                conn.close()
    
    def update_user_activity(self, user_id: int) -> None:
        """تحديث آخر نشاط للمستخدم"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE users SET last_activity = CURRENT_TIMESTAMP, 
                    message_count = message_count + 1 WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
            finally:
                conn.close()
    
    def get_all_users(self) -> List[Dict]:
        """الحصول على جميع المستخدمين"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM users WHERE is_banned = 0 ORDER BY joined_at DESC')
                return [dict(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    def ban_user(self, user_id: int) -> bool:
        """حظر مستخدم"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
                conn.commit()
                return True
            finally:
                conn.close()
    
    def unban_user(self, user_id: int) -> bool:
        """فك الحظر عن مستخدم"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
                conn.commit()
                return True
            finally:
                conn.close()
    
    def is_user_banned(self, user_id: int) -> bool:
        """التحقق من حظر المستخدم"""
        user = self.get_user(user_id)
        return user['is_banned'] == 1 if user else False
    
    def get_users_count(self) -> int:
        """الحصول على عدد المستخدمين"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT COUNT(*) FROM users WHERE is_banned = 0')
                return cursor.fetchone()[0]
            finally:
                conn.close()
    
    # ============ عمليات الأدمنية ============
    
    def add_admin(self, user_id: int, added_by: int = None, permissions: str = None) -> bool:
        """إضافة أدمن"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO admins (user_id, added_by, permissions)
                    VALUES (?, ?, ?)
                ''', (user_id, added_by, permissions or 'all'))
                cursor.execute('UPDATE users SET is_admin = 1 WHERE user_id = ?', (user_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error adding admin: {e}")
                return False
            finally:
                conn.close()
    
    def remove_admin(self, user_id: int) -> bool:
        """حذف أدمن"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
                cursor.execute('UPDATE users SET is_admin = 0 WHERE user_id = ?', (user_id,))
                conn.commit()
                return True
            finally:
                conn.close()
    
    def is_admin(self, user_id: int) -> bool:
        """التحقق من كون المستخدم أدمن"""
        # check config-defined admin and developer IDs first
        if user_id == getattr(config, "DEVELOPER_ID", None):
            return True
        if str(user_id) in [str(x) for x in getattr(config, "ADMIN_IDS", [])]:
            return True

        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT admin_id FROM admins WHERE user_id = ?', (user_id,))
                return cursor.fetchone() is not None
            finally:
                conn.close()
    
    def get_all_admins(self) -> List[Dict]:
        """الحصول على جميع الأدمنية"""
        config_admins = []
        developer_id = getattr(config, "DEVELOPER_ID", None)
        if developer_id is not None:
            config_admins.append({
                "user_id": developer_id,
                "added_by": None,
                "permissions": "all",
                "username": getattr(config, "DEVELOPER_USERNAME", ""),
                "first_name": "Developer"
            })
        for admin_id in getattr(config, "ADMIN_IDS", []):
            if admin_id == developer_id:
                continue
            config_admins.append({
                "user_id": admin_id,
                "added_by": None,
                "permissions": "all",
                "username": "",
                "first_name": "Admin"
            })

        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT a.*, u.username, u.first_name FROM admins a
                    LEFT JOIN users u ON a.user_id = u.user_id
                    ORDER BY a.added_at DESC
                ''')
                db_admins = [dict(row) for row in cursor.fetchall()]
                # avoid duplicates
                existing_ids = {str(a["user_id"]) for a in db_admins}
                for a in config_admins:
                    if str(a["user_id"]) not in existing_ids:
                        db_admins.insert(0, a)
                return db_admins
            finally:
                conn.close()
    
    # ============ عمليات البوتات ============
    
    def add_bot(self, bot_id: str, bot_name: str, bot_token: str, bot_type: str = None,
                creator_id: int = None) -> bool:
        """إضافة بوت جديد"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO bots (bot_id, bot_name, bot_token, bot_type, creator_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (bot_id, bot_name, bot_token, bot_type, creator_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error adding bot: {e}")
                return False
            finally:
                conn.close()
    
    def get_bot(self, bot_id: str) -> Optional[Dict]:
        """الحصول على بيانات البوت"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM bots WHERE bot_id = ?', (bot_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
            finally:
                conn.close()
    
    def get_all_bots(self) -> List[Dict]:
        """الحصول على جميع البوتات"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM bots WHERE is_active = 1 ORDER BY created_at DESC')
                return [dict(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    def get_bots_count(self) -> int:
        """عدد البوتات النشطة"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT COUNT(*) FROM bots WHERE is_active = 1')
                return cursor.fetchone()[0]
            finally:
                conn.close()

    def get_bots_by_creator(self, creator_id: int) -> List[Dict]:
        """الحصول على البوتات التي أضافها المستخدم"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM bots WHERE creator_id = ? AND is_active = 1 ORDER BY created_at DESC', (creator_id,))
                return [dict(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    # ============ عمليات الإذاعات ============
    
    def add_broadcast(self, admin_id: int, message_text: str, total_users: int) -> int:
        """إضافة إذاعة جديدة وإرجاع معرّفها"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO broadcasts (admin_id, message_text, total_users)
                    VALUES (?, ?, ?)
                ''', (admin_id, message_text, total_users))
                conn.commit()
                return cursor.lastrowid
            finally:
                conn.close()
    
    def update_broadcast_stats(self, broadcast_id: int, successful: int, failed: int) -> bool:
        """تحديث إحصائيات الإذاعة"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    UPDATE broadcasts SET successful_count = ?, failed_count = ?
                    WHERE broadcast_id = ?
                ''', (successful, failed, broadcast_id))
                conn.commit()
                return True
            finally:
                conn.close()
    
    def get_broadcast_stats(self) -> Dict:
        """الحصول على إحصائيات الإذاعات"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT COUNT(*) as total, SUM(successful_count) as successful,
                    SUM(failed_count) as failed FROM broadcasts
                ''')
                row = cursor.fetchone()
                return {
                    'total': row[0] or 0,
                    'successful': row[1] or 0,
                    'failed': row[2] or 0
                }
            finally:
                conn.close()
    
    # ============ عمليات الإعدادات ============
    
    def set_setting(self, bot_id: str, key: str, value: str) -> bool:
        """حفظ إعداد"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO bot_settings (bot_id, setting_key, setting_value)
                    VALUES (?, ?, ?)
                ''', (bot_id, key, value))
                conn.commit()
                return True
            finally:
                conn.close()
    
    def get_setting(self, bot_id: str, key: str, default: str = None) -> Optional[str]:
        """الحصول على إعداد"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT setting_value FROM bot_settings 
                    WHERE bot_id = ? AND setting_key = ?
                ''', (bot_id, key))
                row = cursor.fetchone()
                return row[0] if row else default
            finally:
                conn.close()
    
    def get_all_settings(self, bot_id: str) -> Dict:
        """الحصول على جميع إعدادات البوت"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT setting_key, setting_value FROM bot_settings WHERE bot_id = ?
                ''', (bot_id,))
                return {row[0]: row[1] for row in cursor.fetchall()}
            finally:
                conn.close()
    
    # ============ عمليات الرسائل ============
    
    def add_message(self, user_id: int, bot_id: str, message_text: str, 
                   message_type: str = 'text', is_forwarded: int = 0) -> int:
        """إضافة رسالة"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO messages (user_id, bot_id, message_text, message_type, is_forwarded)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, bot_id, message_text, message_type, is_forwarded))
                conn.commit()
                return cursor.lastrowid
            finally:
                conn.close()
    
    def get_user_messages(self, user_id: int, limit: int = 50) -> List[Dict]:
        """الحصول على رسائل المستخدم"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT * FROM messages WHERE user_id = ? 
                    ORDER BY sent_at DESC LIMIT ?
                ''', (user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    # ============ عمليات السجل (Logging) ============
    
    def log_action(self, bot_id: str, user_id: int, action: str, details: str = None) -> bool:
        """تسجيل إجراء"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO logs (bot_id, user_id, action, details)
                    VALUES (?, ?, ?, ?)
                ''', (bot_id, user_id, action, details))
                conn.commit()
                return True
            finally:
                conn.close()
    
    def get_logs(self, bot_id: str = None, limit: int = 100) -> List[Dict]:
        """الحصول على السجلات"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                if bot_id:
                    cursor.execute('''
                        SELECT * FROM logs WHERE bot_id = ?
                        ORDER BY timestamp DESC LIMIT ?
                    ''', (bot_id, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM logs
                        ORDER BY timestamp DESC LIMIT ?
                    ''', (limit,))
                return [dict(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    # ============ عمليات الإحصائيات ============
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات شاملة"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT COUNT(*) FROM users WHERE is_banned = 0')
                users_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM admins')
                admins_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM bots WHERE is_active = 1')
                bots_count = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT COUNT(*) FROM broadcasts
                ''')
                broadcasts_count = cursor.fetchone()[0]
                
                return {
                    'users': users_count,
                    'admins': admins_count,
                    'bots': bots_count,
                    'broadcasts': broadcasts_count
                }
            finally:
                conn.close()
    
    # ============ عمليات إعدادات النظام ============
    
    def set_system_config(self, key: str, value: str) -> bool:
        """حفظ إعداد نظام (التوكن، معرف المطور، إلخ)"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO system_config (config_key, config_value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value))
                conn.commit()
                return True
            finally:
                conn.close()
    
    def get_system_config(self, key: str) -> str:
        """الحصول على قيمة إعداد نظام"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    SELECT config_value FROM system_config WHERE config_key = ?
                ''', (key,))
                result = cursor.fetchone()
                return result[0] if result else None
            finally:
                conn.close()
    
    def get_all_system_config(self) -> Dict[str, str]:
        """الحصول على جميع إعدادات النظام"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT config_key, config_value FROM system_config')
                return {row[0]: row[1] for row in cursor.fetchall()}
            finally:
                conn.close()
    
    def delete_system_config(self, key: str) -> bool:
        """حذف إعداد نظام"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM system_config WHERE config_key = ?', (key,))
                conn.commit()
                return True
            finally:
                conn.close()
    
    def close(self):
        """إغلاق الاتصالات"""
        pass
