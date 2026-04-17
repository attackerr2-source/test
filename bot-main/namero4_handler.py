###by @Voltees
### Volt Bot Factory - All rights reserved ⚡

import os
import re
import json
import asyncio
import signal
import sys
import config
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from bot_helper import (
    bot_call, bot_get, read_file, write_file, append_file,
    read_json, write_json, file_lines, ensure_dir, file_exists,
    delete_file, extract_update_fields,
)

# ═══════════════════════════════════════════════════════════════════════════
# Logging System
# ═══════════════════════════════════════════════════════════════════════════

def _setup_logger(bot_dir: str) -> logging.Logger:
    """Setup logger for the bot."""
    logger = logging.getLogger(f"namero4_{os.path.basename(bot_dir)}")
    logger.setLevel(logging.INFO)

    # Create logs directory if not exists
    logs_dir = os.path.join(bot_dir, "logs")
    ensure_dir(logs_dir)
    
    # تأكد من إنشاء المجلد بشكل صحيح
    try:
        os.makedirs(logs_dir, exist_ok=True)
    except Exception as e:
        print(f"⚠️ تحذير: لا يمكن إنشاء مجلد السجلات {logs_dir}: {e}")

    # File handler
    log_file = os.path.join(logs_dir, f"bot_{datetime.now().strftime('%Y%m%d')}.log")
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
    except Exception as e:
        print(f"⚠️ تحذير: لا يمكن إنشاء ملف السجل {log_file}: {e}")
        # استخدم console handler فقط كبديل
        file_handler = None

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    if file_handler:
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# ═══════════════════════════════════════════════════════════════════════════
# Constants and Configuration
# ═══════════════════════════════════════════════════════════════════════════

# Global Cache
_CACHE = {}

# Media restrictions
MEDIA_ALLOWED = "❌"
MEDIA_BLOCKED = "✅"

# Bot status
BOT_ON = "on"
BOT_OFF = "off"

# Cache TTL - تعريف المتغيرات ضروري في البداية
_CACHE_TTL = 30  # seconds - used globally
CACHE_TTL = _CACHE_TTL  # Alias for backward compatibility

# Pagination
ITEMS_PER_PAGE = 10

# API timeouts and retries
API_TIMEOUT = 10
MAX_RETRIES = 3

# Rate limiting
BROADCAST_BATCH_SIZE = 10
BROADCAST_BATCH_DELAY = 2  # seconds

# Exclude texts for message filtering
_EXCLUDE_TEXTS = {
    "/start", "جهة اتصال المدير☎️", "⚜️〽️┇قناه البوت",
    "ارفعني", "القوانين ⚠️", "معلومات المدير 📋",
    "المساعده 💡", "اطلب بوتك من المطور",
}

# Link markers for filtering
_LINK_MARKERS = ["t.me", "telegram.me", "https://", "://", "wWw.", "WwW.", "T.me/", "WWW."]

# Media toggle mapping
_MEDIA_TOGGLE_MAP = {
    "photo":    "modetext1",
    "music":    "modetext2",
    "file":     "modetext3",
    "stick":    "modetext4",
    "video":    "modetext5",
    "mov":      "modetext6",
    "contact":  "modetext7",   # typo preserved from PHP
    "i3ad":     "modetext8",
    "alllink":  "modetext9",
    "linktele": "modetext10",
}



def _get_cached(key: str, fetch_func, *args, **kwargs):
    """Get cached value or fetch and cache it."""
    current_time = time.time()
    if key in _CACHE:
        cached_value, timestamp = _CACHE[key]
        if current_time - timestamp < CACHE_TTL:
            return cached_value

    # Fetch new value
    value = fetch_func(*args, **kwargs)
    _CACHE[key] = (value, current_time)
    return value

def _invalidate_cache(key: str):
    """Invalidate specific cache entry."""
    if key in _CACHE:
        del _CACHE[key]

def _clear_cache():
    """Clear all cache."""
    global _CACHE
    _CACHE = {}

# ═══════════════════════════════════════════════════════════════════════════
# Sync file helpers (all paths are absolute; bot_dir is injected at call time)
# ═══════════════════════════════════════════════════════════════════════════

def _rf(path: str, default: str = "") -> str:
    return read_file(path, default).strip()


def _wf(path: str, content: str) -> None:
    write_file(path, content)


def _af(path: str, content: str) -> None:
    append_file(path, content)


def _rj(path: str, default=None):
    if default is None:
        default = {}
    return read_json(path, default)


def _wj(path: str, data) -> None:
    write_json(path, data)


def _save_message(bot_dir: str, from_id: str, from_name: str, from_user: str,
                  to_id: str, to_user: str, text: str, message_id: int, direction: str = "user->admin") -> None:
    """حفظ الرسالة مباشرة في قاعدة البيانات SQLite"""
    from db_config import db_save_message
    bot_id = os.path.basename(bot_dir)
    try:
        db_save_message(bot_id, from_id, from_name, from_user,
                        to_id, to_user, text, message_id, direction)
    except Exception as e:
        print(f"[DB] خطأ في حفظ الرسالة: {e}")

def _ri(path: str, default: int = 0) -> int:
    """Safely read integer from file with validation."""
    try:
        content = _rf(path, str(default)).strip()
        if not content:
            return default
        result = int(content)
        return result if result >= 0 else default
    except (ValueError, TypeError, OSError) as e:
        logger = logging.getLogger("namero4")
        logger.warning(f"Error reading integer from {path}: {e}")
        return default


def _unlink(path: str) -> None:
    delete_file(path)


def _mkdir(path: str) -> None:
    # no-op: database backend does not require directories
    pass


def _get_ban_list(bot_dir: str) -> list:
    """Get cached ban list."""
    def fetch_ban():
        ban_content = _rf(os.path.join(bot_dir, "data", "ban"))
        return [x for x in ban_content.splitlines() if x.strip()]
    return _get_cached(f"ban_{bot_dir}", fetch_ban)

def _get_admin_list(bot_dir: str) -> list:
    """Get cached admin list from files."""
    def fetch_admins():
        # جرب قراءة من مسارات مختلفة - المسارات الصحيحة للبوتات
        admin_sources = [
            "admin",                   # مالك البوت الأساسي
            os.path.join("NaMero", "member"),  # أعضاء NaMero
            os.path.join("data", "admins_list"),  # قائمة الإداريين
        ]
        
        all_admins = set()
        for source in admin_sources:
            source_path = os.path.join(bot_dir, source) if not os.path.isabs(source) else source
            try:
                admin_content = read_file(source_path, "").strip()
                if admin_content:
                    for line in admin_content.splitlines():
                        line = line.strip()
                        if line and line.isdigit():
                            all_admins.add(line)
            except:
                pass
        
        return list(all_admins)
    
    return _get_cached(f"admins_{bot_dir}", fetch_admins)

def _fetch_setting_raw(bot_dir: str) -> dict:
    """تحميل الإعدادات الخام من DB/القرص وتطبيق القيم الافتراضية."""
    setting_path = os.path.join(bot_dir, "setting")
    setting = _rj(setting_path)

    if not setting:
        setting = {"twasl": {}}
    if "twasl" not in setting:
        setting["twasl"] = {}

    defaults = {
        "type":            "✅",
        "replymod":        "✅",
        "modetext1":       "✅",
        "modetext2":       "✅",
        "modetext3":       "✅",
        "modetext4":       "✅",
        "modetext5":       "✅",
        "modetext6":       "✅",
        "modetext7":       "✅",
        "modetext8":       "✅",
        "modetext9":       "✅",
        "modetext10":      "✅",
        "notif_new_users": "✅",
        "notif_blocked":   "✅",
    }
    for k, v in defaults.items():
        if k not in setting["twasl"]:
            setting["twasl"][k] = v
    return setting


def _get_setting(bot_dir: str) -> dict:
    """إعدادات البوت — مع كاش TTL لتقليل قراءات DB."""
    return _get_cached(f"setting_{bot_dir}", _fetch_setting_raw, bot_dir)


def _save_setting(bot_dir: str, setting_path: str, data: dict) -> None:
    """حفظ الإعدادات وتحديث الكاش فوراً."""
    _wj(setting_path, data)
    _invalidate_cache(f"setting_{bot_dir}")

def _track_user(user_id, user_name, bot_dir: str) -> bool:
    """Track new users and notify admins. Returns True if new user."""
    key = f"{bot_dir}/data/users_list"
    users_data = _rj(key, {})
    user_key = str(user_id)
    is_new = user_key not in users_data
    
    if is_new:
        users_data[user_key] = {
            "name": user_name,
            "user_id": user_id,
            "joined": str(__import__('datetime').datetime.now()),
            "message_count": 0
        }
        _wj(key, users_data)
    else:
        users_data[user_key]["message_count"] = users_data[user_key].get("message_count", 0) + 1
        _wj(key, users_data)
    
    return is_new


def _get_users_count(bot_dir: str) -> int:
    """Get total unique users count."""
    users_file = os.path.join(bot_dir, "data", "users_list")
    users_data = _rj(users_file, {})
    return len(users_data)


def _get_stats(bot_dir: str) -> dict:
    """Get comprehensive bot statistics."""
    users_file = os.path.join(bot_dir, "data", "users_list")
    admins_file = os.path.join(bot_dir, "data", "admins_list")
    broadcast_file = os.path.join(bot_dir, "data", "broadcast_count")
    
    users_data = _rj(users_file, {})
    admins_data = _rj(admins_file, {})
    broadcast_data = _rj(broadcast_file, {"total_sent": 0, "total_received": 0})
    
    return {
        "total_users": len(users_data),
        "total_admins": len(admins_data),
        "broadcast_sent": broadcast_data.get("total_sent", 0),
        "broadcast_received": broadcast_data.get("total_received", 0),
    }


async def _send_broadcast(token: str, message_text: str, bot_dir: str, admin_id: str) -> tuple:
    """Send broadcast message to all users with batch processing and rate limiting."""
    users_file = os.path.join(bot_dir, "data", "users_list")
    users_data = _rj(users_file, {})

    sent_count = 0
    failed_count = 0
    broadcast_file = os.path.join(bot_dir, "data", "broadcast_count")
    broadcast_data = _rj(broadcast_file, {"total_sent": 0, "total_received": 0})

    # Process users in batches of 10 to avoid rate limits
    user_ids = list(users_data.keys())
    batch_size = 10

    for i in range(0, len(user_ids), batch_size):
        batch = user_ids[i:i + batch_size]

        # Send batch
        for user_id in batch:
            try:
                result = await bot_call(token, "sendMessage", {
                    "chat_id": user_id,
                    "text": message_text,
                    "parse_mode": "Markdown"
                })
                if result.get("ok"):
                    sent_count += 1
                    broadcast_data["total_received"] += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"Broadcast error for user {user_id}: {e}")
                failed_count += 1

        # Wait 2 seconds between batches to respect rate limits
        if i + batch_size < len(user_ids):
            await asyncio.sleep(2)

    broadcast_data["total_sent"] += 1
    _wj(broadcast_file, broadcast_data)

    return sent_count, failed_count


def _add_admin(user_id, bot_dir: str) -> bool:
    """Add new admin user. Returns True if added, False if already admin."""
    key = f"{bot_dir}/data/admins_list"
    admins_data = _rj(key, {})
    user_key = str(user_id)
    
    if user_key in admins_data:
        return False
    
    admins_data[user_key] = {
        "user_id": user_id,
        "added_at": str(__import__('datetime').datetime.now())
    }
    _wj(key, admins_data)
    return True


def _remove_admin(user_id, bot_dir: str) -> bool:
    """Remove admin user. Returns True if removed, False if not found."""
    key = f"{bot_dir}/data/admins_list"
    admins_data = _rj(key, {})
    user_key = str(user_id)
    
    if user_key not in admins_data:
        return False
    
    del admins_data[user_key]
    _wj(key, admins_data)
    return True


async def _safe_get_chat_member(token: str, chat_id: str, user_id: str, max_retries: int = 3) -> dict:
    """Safely get chat member with timeout and retry logic."""
    logger = logging.getLogger("namero4")
    
    for attempt in range(max_retries):
        try:
            result = await bot_get(token, "getChatMember", {
                "chat_id": chat_id,
                "user_id": user_id
            }, timeout=10)  # 10 second timeout

            if result.get("ok"):
                return result
            elif result.get("error_code") in (400, 403):  # User not found or bot not admin
                return {"ok": False, "error": "not_member"}
            else:
                logger.warning(f"getChatMember attempt {attempt + 1} failed: {result}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # Wait 1 second before retry

        except asyncio.TimeoutError:
            logger.warning(f"getChatMember timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)  # Wait 2 seconds before retry
        except Exception as e:
            logger.error(f"getChatMember error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)

    logger.error(f"getChatMember failed after {max_retries} retries for user {user_id}")
    return {"ok": False, "error": "max_retries_exceeded"}


def _get_bot_status(bot_dir: str) -> str:
    """Get bot status: 'on' or 'off'."""
    key = f"{bot_dir}/data/bot_status"
    status = _rf(key, "on")
    return status.strip() or "on"


def _set_bot_status(bot_dir: str, status: str) -> None:
    """Set bot status: 'on' or 'off'."""
    key = f"{bot_dir}/data/bot_status"
    _wf(key, status.strip())


def _validate_user_id(user_id: str) -> tuple:
    """Validate user ID. Returns (is_valid, error_message)."""
    if not user_id or not user_id.strip():
        return False, "يجب إدخال معرّف صحيح"

    user_id = user_id.strip()

    if not user_id.isdigit():
        return False, "المعرّف يجب أن يكون أرقام فقط"

    user_id_int = int(user_id)
    if user_id_int <= 0:
        return False, "المعرّف يجب أن يكون رقم موجب"

    if len(user_id) < 5 or len(user_id) > 20:
        return False, "طول المعرّف غير صحيح (5-20 رقم)"

    return True, ""

def _paginate_list(items: list, page: int, per_page: int = 10) -> tuple:
    """Paginate a list. Returns (page_items, total_pages, has_next, has_prev)."""
    if not items:
        return [], 0, False, False

    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page  # Ceiling division

    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    page_items = items[start_idx:end_idx]
    has_next = page < total_pages
    has_prev = page > 1

    return page_items, total_pages, has_next, has_prev

def _validate_text(text: str, max_length: int = 4096) -> tuple:
    """Validate text. Returns (is_valid, error_message)."""
    if not text:
        return False, "النص لا يمكن أن يكون فارغاً"

    if len(text) > max_length:
        return False, f"النص طويل جداً (الحد الأقصى {max_length} حرف)"

    return True, ""

def _safe_int_convert(value: str, default: int = 0) -> int:
    """Safely convert string to int with validation."""
    try:
        result = int(value.strip())
        return result if result >= 0 else default
    except (ValueError, AttributeError):
        return default


# ═══════════════════════════════════════════════════════════════════════════
# Keyboard builders (used multiple times in the file)
# ═══════════════════════════════════════════════════════════════════════════

def _media_kbd(setting: dict) -> str:
    t   = setting.get("twasl", {})
    m1  = t.get("modetext1",  "✅")
    m2  = t.get("modetext2",  "✅")
    m3  = t.get("modetext3",  "✅")
    m4  = t.get("modetext4",  "✅")
    m5  = t.get("modetext5",  "✅")
    m6  = t.get("modetext6",  "✅")
    m7  = t.get("modetext7",   "✅")   # fixed typo from PHP (was modetex7)
    m8  = t.get("modetext8",  "✅")
    m9  = t.get("modetext9",  "✅")
    m10 = t.get("modetext10", "✅")
    return json.dumps({"inline_keyboard": [
        [{"text": "الصور ",         "callback_data": "#"}, {"text": m1,  "callback_data": "photo"}],
        [{"text": "الموسيقي ",      "callback_data": "#"}, {"text": m2,  "callback_data": "music"}],
        [{"text": "الملفات ",       "callback_data": "#"}, {"text": m3,  "callback_data": "file"}],
        [{"text": "الملصقات  ",     "callback_data": "#"}, {"text": m4,  "callback_data": "stick"}],
        [{"text": "االفيديو ",      "callback_data": "#"}, {"text": m5,  "callback_data": "video"}],
        [{"text": "الصوتيات ",      "callback_data": "#"}, {"text": m6,  "callback_data": "mov"}],
        [{"text": "جهه الاتصال ",   "callback_data": "#"}, {"text": m7,  "callback_data": "contact"}],
        [{"text": "اعاده توجيه ",   "callback_data": "#"}, {"text": m8,  "callback_data": "i3ad"}],
        [{"text": "جميع الروابط ",  "callback_data": "#"}, {"text": m9,  "callback_data": "alllink"}],
        [{"text": "روابط تيلجرام ", "callback_data": "#"}, {"text": m10, "callback_data": "linktele"}],
        [{"text": "رجوع",           "callback_data": "bot9"}],
    ]})


def _bot9_kbd(setting: dict) -> str:
    t                = setting.get("twasl", {})
    typeing          = t.get("type",    "✅")
    replymod         = t.get("replymod","✅")
    return json.dumps({"inline_keyboard": [
        [{"text": f"جاري الكتابه : {typeing}", "callback_data": "onbott"}],
        [{"text": "تعين رساله الاستلام",       "callback_data": "msrd"},
         {"text": "تعين رساله الترحيب",        "callback_data": "setstart"}],
        [{"text": "مكان الاستلام للرسائل  ",    "callback_data": "bbuio"}],
        [{"text": "🎛️ الإعدادات المتقدمة",      "callback_data": "man3er"}],
        [{"text": "📢 الإذاعة",                 "callback_data": "broadcast_menu"},
         {"text": "📊 الإحصائيات",              "callback_data": "show_stats"}],
        [{"text": "👥 إدارة الأدمنية",        "callback_data": "manage_admins"},
         {"text": "🔌 حالة البوت",              "callback_data": "bot_status_menu"}],
        [{"text": "🔔 الإخطارات",              "callback_data": "notifications_menu"}],
        [{"text": "رجوع",                       "callback_data": "bot9"}],
    ]})


# ═══════════════════════════════════════════════════════════════════════════
# مجموعة لتتبع الـ update_ids التي تمت معالجتها — تمنع التكرار
# ═══════════════════════════════════════════════════════════════════════════
_processed_update_ids: set = set()

# ═══════════════════════════════════════════════════════════════════════════
# Main async handler
# ═══════════════════════════════════════════════════════════════════════════

async def handle_namero4(
    update:    dict,
    bot_dir:   str,
    token:     str,
    NaMerOset: dict,
    makerinve: dict,
) -> None:

    # ── deduplication: منع معالجة نفس الـ update مرتين ──────────────────
    _upd_id = update.get("update_id", 0)
    if _upd_id:
        if _upd_id in _processed_update_ids:
            return
        _processed_update_ids.add(_upd_id)
        if len(_processed_update_ids) > 1000:
            _processed_update_ids.clear()

    # ── local path helper ──────────────────────────────────────────────────
    def p(*parts) -> str:
        return os.path.join(bot_dir, *parts)

    # ── extract update fields ──────────────────────────────────────────────
    message  = update.get("message") or {}
    callback = update.get("callback_query") or {}
    my_chat_member = update.get("my_chat_member") or {}

    chat_id    = 0
    from_id    = 0
    text       = ""
    data       = ""
    message_id = 0
    name       = ""
    user       = ""
    admin      = _rf(p("admin")).strip() if _rf(p("admin")) else ""

    # Handle my_chat_member events (bot blocked/unblocked)
    if my_chat_member:
        new_member_status = my_chat_member.get("new_chat_member", {}).get("status", "")
        from_user_id = my_chat_member.get("from", {}).get("id", 0)
        from_user_name = my_chat_member.get("from", {}).get("first_name", "") or ""
        from_user_username = (my_chat_member.get("from", {}).get("username") or "").lower()
        from_user_lang = my_chat_member.get("from", {}).get("language_code", "ar")
        
        # If bot status is "blocked" or "kicked"
        if new_member_status in ("blocked", "kicked"):
            setting = _get_setting(bot_dir)
            notif_enabled = setting.get("twasl", {}).get("notif_blocked", "✅") == "✅"
            if notif_enabled:
                ban_count = len(_get_ban_list(bot_dir))
                msg = (
                    f"🚫 قام أحد الأعضاء بحظر البوت الخاص بك\n\n"
                    f"👤 معلومات العضو:\n"
                    f"• الاسم: {from_user_name}\n"
                    f"• المعرّف: @{from_user_username}\n"
                    f"• الآيدي: {from_user_id}\n"
                    f"• 🌐 اللغة: {from_user_lang}\n\n"
                    f"📊 إجمالي الحظر: {ban_count}"
                )
                await bot_call(token, "sendMessage", {
                    "chat_id": admin,
                    "text": msg,
                })
        return

    if message:
        chat_id    = message.get("chat", {}).get("id", 0)
        from_id    = message.get("from", {}).get("id", 0)
        text       = message.get("text", "") or ""
        message_id = message.get("message_id", 0)
        name       = message.get("from", {}).get("first_name", "") or ""
        user       = (message.get("from", {}).get("username") or "").lower()

    if callback:
        data       = callback.get("data", "") or ""
        chat_id    = callback.get("message", {}).get("chat", {}).get("id", 0)
        message_id = callback.get("message", {}).get("message_id", 0)
        from_id    = callback.get("from", {}).get("id", 0)
        name       = callback.get("from", {}).get("first_name", "") or ""
        user       = (callback.get("from", {}).get("username") or "").lower()

    S_P_P1    = data or text
    chat_type = message.get("chat", {}).get("type", "private")
    caption   = message.get("caption") or ""

    reply_msg = message.get("reply_to_message") or {}
    reply_id  = reply_msg.get("message_id", 0)

    photo    = message.get("photo")
    video    = message.get("video")
    document = message.get("document")
    sticker  = message.get("sticker")
    voice    = message.get("voice")
    audio    = message.get("audio")
    forward  = message.get("forward_from_chat")

    # ── admin & sudo ───────────────────────────────────────────────────────
    admin    = _rf(p("admin")).strip() if _rf(p("admin")) else ""
    
    # تحذير إذا كان admin فارغاً
    if not admin or not str(admin).isdigit():
        print(f"⚠️ تحذير: admin غير محدد بشكل صحيح في {bot_dir}")
    
    # Debug: طباعة المعلومات الأساسية
    if text:
        print(f"[DEBUG] رسالة من {from_id} ({name}): {text[:50]}")
        print(f"[DEBUG] text.strip().lower() = '{text.strip().lower()}'")

    # sudo_ids: فقط أدمن البوت الخاص بهذا البوت المصنوع
    # المطور العام لا يملك صلاحيات تلقائية على بوتات المستخدمين الآخرين
    sudo_ids = set()
    if admin and str(admin).lstrip("-").isdigit():
        sudo_ids.add(str(admin))

    # ── cached data ──────────────────────────────────────────────────────
    try:
        ban         = _get_ban_list(bot_dir)
        adminall    = _get_admin_list(bot_dir)
        setting     = _get_setting(bot_dir)
        setting_path = os.path.join(bot_dir, "setting")
    except Exception as e:
        print(f"[ERROR] Error loading cached data: {e}")
        return

    # ── info lines ─────────────────────────────────────────────────────
    try:
        info_lines  = _rf(p("info")).split("\n")
        usernamebot = info_lines[1] if len(info_lines) > 1 else ""
        no3mak      = info_lines[6] if len(info_lines) > 6 else ""
    except Exception as e:
        print(f"[ERROR] Error parsing info: {e}")
        return

    def is_admin(uid) -> bool:
        """Check if user is admin (from adminall list or sudo_ids)."""
        return str(uid) in sudo_ids or str(uid) in adminall

    # ── welcome message ────────────────────────────────────────────────────
    if NaMerOset.get("wellcom"):
        start = f"مرحباً بك {name}\n\n" + NaMerOset["wellcom"]
    else:
        start = f"مرحباً بك [{name}](tg://user?id={from_id}) ❤️"

    # ── keyboards ─────────────────────────────────────────────────────────
    def build_keyboard() -> str:
        kb = {"inline_keyboard": []}
        azrari = NaMerOset.get("azrari", [])
        if azrari:
            row = []
            for btn in azrari:
                row.append({"text": btn, "callback_data": btn})
                if len(row) == 2:
                    kb["inline_keyboard"].append(row)
                    row = []
            if row:
                kb["inline_keyboard"].append(row)
        return json.dumps(kb)

    def back_keyboard() -> str:
        return json.dumps({"inline_keyboard": [[{"text": "• رجوع •", "callback_data": "bot9"}]]})

    # ══════════════════════════════════════════════════════════════════════
    # /start command (including typos like /srart, /staert, etc.)
    # ══════════════════════════════════════════════════════════════════════
    start_commands = {"/start", "/srart", "/staert", "/strart", "/satrt", "/sart"}
    if text and text.strip().lower() in start_commands:
        print(f"[DEBUG /START] تطابق أمر البداية!")
        print(f"[DEBUG /START] من: {from_id}, chat_id: {chat_id}, is_admin: {is_admin(from_id)}, الأمر: {text}")
        
        # Check if user is new and notify admins
        is_new_user = _track_user(from_id, name, bot_dir)
        
        # تحقق من أن المستخدم ليس هو الصانع/الأدمن قبل إرسال الإخطار
        if is_new_user and str(from_id) != str(admin):
            # Check if new user notifications are enabled
            notif_enabled = setting.get("twasl", {}).get("notif_new_users", "✅") == "✅"
            if notif_enabled:
                users_data = _rj(p("data", "users_list"), {})
                total_users = len(users_data)
                from_username = f"@{user}" if user else "بدون معرّف"
                
                new_user_msg = (
                    f"٭ تم دخول شخص جديد الى البوت الخاص بك 👾\n"
                    f"-----------------------\n"
                    f"\n• معلومات العضو الجديد .\n"
                    f"• الاسم : {name} \n"
                    f"• المعرف : {from_username}\n"
                    f"• الايدي : {from_id}\n"
                    f"-----------------------\n"
                    f"• عدد الاعضاء الكلي : {{  {total_users} }}"
                )
                try:
                    await bot_call(token, "sendMessage", {
                        "chat_id": admin,
                        "text": new_user_msg,
                    })
                except:
                    pass
        
        # إذا كان Admin، عرض لحة التحكم الكاملة
        if is_admin(from_id):
            print(f"[DEBUG /START] إرسال لوحة التحكم للمسؤول {from_id}")
            result = await bot_call(token, "sendMessage", {
                "chat_id":    chat_id,
                "text": (
                    "◾️ إعدادات بوت التواصل ⚙️ .\n\n"
                    "▫️ ↴ أهلا بك في لحة التحكم! يمكنك تغيير إعدادات البوت و تخصيص الإعدادات كم تريد .\n"
                ),
                "parse_mode":   "MarkDown",
                "reply_markup": _bot9_kbd(setting),
            })
            print(f"[DEBUG /START] نتيجة إرسال اللوحة: {result.get('ok')}")
        else:
            # رسالة ترحيب عادية للمستخدمين العاديين
            print(f"[DEBUG /START] إرسال رسالة ترحيب للمستخدم {from_id}")
            result = await bot_call(token, "sendMessage", {
                "chat_id":                  chat_id,
                "text":                     start,
                "parse_mode":               "MarkDown",
                "disable_web_page_preview": True,
                "reply_markup":             build_keyboard(),
            })
            print(f"[DEBUG /START] نتيجة إرسال الترحيب: {result.get('ok')}")
        return  # لا تستمر معالجة أوامر إضافية

    # ══════════════════════════════════════════════════════════════════════
    # home callback — return to main menu
    # ══════════════════════════════════════════════════════════════════════
    if data == "home":
        # إذا كان Admin، عرض لحة التحكم
        if is_admin(from_id):
            await bot_call(token, "editMessageText", {
                "chat_id":    chat_id,
                "message_id": message_id,
                "text": (
                    "◾️ إعدادات بوت التواصل ⚙️ .\n\n"
                    "▫️ ↴ يمكنك تغيير إعدادات البوت و تخصيص الإعدادات كم تريد .\n"
                ),
                "parse_mode":   "MarkDown",
                "reply_markup": _bot9_kbd(setting),
            })
        else:
            # رسالة عادية للمستخدمين العاديين
            await bot_call(token, "editMessageText", {
                "chat_id":                  chat_id,
                "message_id":               message_id,
                "text":                     start,
                "parse_mode":               "MarkDown",
                "disable_web_page_preview": True,
                "reply_markup":             build_keyboard(),
            })
        return  # توقف المعالجة

    # ══════════════════════════════════════════════════════════════════════
    # azrari button press — handle custom button interaction
    # ══════════════════════════════════════════════════════════════════════
    if S_P_P1 and not S_P_P1.startswith("/"):
        # Check if it's a custom button (azrari) or custom content (azrari_content)
        if NaMerOset.get("azrari_content", {}).get(S_P_P1, {}).get("text"):
            # Has custom content for this button
            army = NaMerOset["azrari_content"][S_P_P1]["text"]
            await bot_call(token, "editMessageText", {
                "chat_id":                  chat_id,
                "message_id":               message_id,
                "text":                     army,
                "disable_web_page_preview": True,
                "reply_markup":             back_keyboard(),
            })
        elif S_P_P1 in NaMerOset.get("azrari", []):
            # It's a custom button but no special content - show confirmation
            await bot_call(token, "answerCallbackQuery", {
                "callback_query_id": callback.get("id", ""),
                "text": f"✅ {S_P_P1}",
                "show_alert": False,
            })

    # ── sendmessage helper: refresh the bot9 settings panel ───────────────
    async def _sendmessage() -> None:
        s2 = _rj(setting_path)
        await bot_call(token, "editMessageText", {
            "chat_id":                  chat_id,
            "message_id":               message_id,
            "text": (
                "◾️ إعدادات بوت التواصل ⚙️ .\n\n"
                "▫️ ↴ يمكنك تغيير إعدادات البوت و تخصيص الإعدادات كم تريد .\n"
            ),
            "disable_web_page_preview": True,
            "reply_markup":             _bot9_kbd(s2),
        })

    async def _maybe_typing(chat_id: int) -> None:
        if not chat_id or not str(chat_id).isdigit():
            return
        if setting.get("twasl", {}).get("type", "✅") == "✅":
            try:
                await bot_call(token, "sendChatAction", {
                    "chat_id": chat_id,
                    "action":  "typing",
                })
            except Exception:
                pass

    # ══════════════════════════════════════════════════════════════════════
    # bot9 / toch — communication settings panel
    # ══════════════════════════════════════════════════════════════════════
    if data in ("bot9", "toch"):
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text": (
                "◾️ إعدادات بوت التواصل ⚙️ .\n\n"
                "▫️ ↴ يمكنك تغيير إعدادات البوت و تخصيص الإعدادات كم تريد .\n"
            ),
            "parse_mode":   "MarkDown",
            "reply_markup": _bot9_kbd(setting),
        })
        setting["twasl"]["moder"] = "s"
        _save_setting(bot_dir, setting_path, setting)

    # ══════════════════════════════════════════════════════════════════════
    # bromk — toggle message receive on/off
    # ══════════════════════════════════════════════════════════════════════
    if data == "bromk":
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text": (
                "◾️ إعدادات بوت التواصل ⚙️ .\n\n"
                "▫️ ↴ يمكنك تغيير إعدادات البوت و تخصيص الإعدادات كم تريد .\n"
            ),
            "reply_to_message_id": message.get("message_id"),
            "parse_mode":   "MarkDown",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "رجوع", "callback_data": "bot9"}],
            ]}),
        })
        setting["twasl"]["moder"] = "s"
        _save_setting(bot_dir, setting_path, setting)

    # ══════════════════════════════════════════════════════════════════════
    # bbuio — choose message receive location
    # ══════════════════════════════════════════════════════════════════════
    if data == "bbuio":
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text": (
                "◾️ إعدادات مكان استلام الرسائل  .\n\n"
                "▫️ ↴ اختر المكان الاتي تريد استقبال الرسائل فيها .\n"
            ),
            "parse_mode":   "MarkDown",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "في الخاص ",    "callback_data": "typee"},
                 {"text": "في المجموعة  ", "callback_data": "supergruope"}],
                [{"text": "رجوع", "callback_data": "bot9"}],
            ]}),
        })
        setting["twasl"]["moder"] = "s"
        _save_setting(bot_dir, setting_path, setting)

    # ══════════════════════════════════════════════════════════════════════
    # man3er — media restrictions panel + commands (admin only)
    # ══════════════════════════════════════════════════════════════════════
    if data == "man3er" and is_admin(from_id):
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text": (
                "🎛️ *الإعدادات المتقدمة*\n\n"
                "━━━━━━━━━━━━━━━━\n"
                "📌 *الوسائط الممنوعة:*\n"
                "✅ = مسموح | ❌ = ممنوع\n"
                "━━━━━━━━━━━━━━━━\n"
            ),
            "disable_web_page_preview": True,
            "parse_mode": "Markdown",
            "reply_markup": _media_kbd(setting),
        })
        setting["twasl"]["moder"] = "links"
        _save_setting(bot_dir, setting_path, setting)

    # ══════════════════════════════════════════════════════════════════════
    # Media toggle buttons (photo/music/file/stick/video/mov/contact/i3ad/alllink/linktele)
    # Each shows the media panel and, if admin, toggles that setting key
    # ══════════════════════════════════════════════════════════════════════
    _MEDIA_TOGGLE_MAP = {
        "photo":    "modetext1",
        "music":    "modetext2",
        "file":     "modetext3",
        "stick":    "modetext4",
        "video":    "modetext5",
        "mov":      "modetext6",
        "contact":  "modetext7",   # typo fixed from PHP (was modetex7)
        "i3ad":     "modetext8",
        "alllink":  "modetext9",
        "linktele": "modetext10",
    }

    if data in _MEDIA_TOGGLE_MAP:
        s2 = _rj(setting_path)
        if is_admin(from_id):
            key     = _MEDIA_TOGGLE_MAP[data]
            current = s2.get("twasl", {}).get(key, "✅")
            s2.setdefault("twasl", {})[key] = "❌" if current == "✅" else "✅"
            _save_setting(bot_dir, setting_path, s2)
            s2 = _rj(setting_path)  # reload updated
        
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text": (
                "🎛️ *الإعدادات المتقدمة*\n\n"
                "━━━━━━━━━━━━━━━━\n"
                "📌 اضغط على الزر لتبديل (toggle) الحالة:\n"
                "✅ = مسموح | ❌ = ممنوع\n"
                "━━━━━━━━━━━━━━━━\n"
            ),
            "disable_web_page_preview": True,
            "parse_mode": "Markdown",
            "reply_markup": _media_kbd(s2),
        })

    # ══════════════════════════════════════════════════════════════════════
    # setsta / setstart — prompt admin to enter welcome message
    # ══════════════════════════════════════════════════════════════════════
    if data in ("setsta", "setstart") and is_admin(from_id):
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text": (
                "▫️ إرسل رسالة الترحيب التي تريد:\n"
                "▪️ يمكنك إستخدام الـMarkdown .\n"
                "-\n"
                "-\n"
            ),
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "• رجوع •", "callback_data": "bot9"}],
            ]}),
        })
        setting["twasl"]["mode"] = "set2"
        _save_setting(bot_dir, setting_path, setting)

    # ══════════════════════════════════════════════════════════════════════
    # Receive welcome message text when mode == "set2"
    # ══════════════════════════════════════════════════════════════════════
    if text and setting.get("twasl", {}).get("mode") == "set2" and is_admin(from_id):
        await bot_call(token, "sendMessage", {
            "chat_id":                  chat_id,
            "message_id":               message_id,
            "text":                     f"\n{text}\n",
            "disable_web_page_preview": True,
            "parse_mode":               "markdown",
        })
        await bot_call(token, "sendMessage", {
            "chat_id":                  chat_id,
            "message_id":               message_id,
            "text":                     "\n",
            "disable_web_page_preview": True,
            "parse_mode":               "markdown",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "• رجوع •", "callback_data": "bot9"}],
            ]}),
        })
        setting["twasl"]["start"] = text
        setting["twasl"]["mode"]  = None
        _save_setting(bot_dir, setting_path, setting)

    # ══════════════════════════════════════════════════════════════════════
    # onbott — toggle typing indicator
    # ══════════════════════════════════════════════════════════════════════
    if data == "onbott" and is_admin(from_id):
        s2 = _rj(setting_path)
        cur = s2.get("twasl", {}).get("type", "✅")
        s2.setdefault("twasl", {})["type"] = "❌" if cur == "✅" else "✅"
        _save_setting(bot_dir, setting_path, s2)
        await _sendmessage()

    # ══════════════════════════════════════════════════════════════════════
    # replymod — toggle reply mode
    # ══════════════════════════════════════════════════════════════════════
    if data == "replymod" and is_admin(from_id):
        s2 = _rj(setting_path)
        cur = s2.get("twasl", {}).get("replymod", "✅")
        s2.setdefault("twasl", {})["replymod"] = "❌" if cur == "✅" else "✅"
        _save_setting(bot_dir, setting_path, s2)
        await _sendmessage()

    # ══════════════════════════════════════════════════════════════════════
    # Factory / maker settings from makerinve (equivalent of KhAlEdJ)
    # ══════════════════════════════════════════════════════════════════════
    st_ch_bots    = makerinve.get("st_ch_bots",    "")
    id_ch_sudo1   = makerinve.get("id_channel",    "")
    link_ch_sudo1 = makerinve.get("link_channel",  "")
    id_ch_sudo2   = makerinve.get("id_channel2",   "")
    link_ch_sudo2 = makerinve.get("link_channel2", "")
    user_bot_sudo = makerinve.get("user_bot",      "")

    # ══════════════════════════════════════════════════════════════════════
    # pro
    # ══════════════════════════════════════════════════════════════════════
    projson = _rj(p("pro"))
    pro     = projson.get("info", {}).get("pro")
    dateon  = projson.get("info", {}).get("dateon")
    dateoff = projson.get("info", {}).get("dateoff")

    txtfree = ""
    if pro != "yes" or pro is None:
        txtfree = (
            f'<a href="https://t.me/{user_bot_sudo}">'
            f'• اضغط هنا لنصع {no3mak} خاص بك </a>'
        )

    # ══════════════════════════════════════════════════════════════════════
    # Member and ban lists
    # ══════════════════════════════════════════════════════════════════════
    member_lines = [x for x in _rf(p("sudo", "member")).splitlines() if x.strip()]
    cunte        = len(member_lines)

    # Convert ban to set for O(1) lookups
    ban_set      = {str(b).strip() for b in ban if b}
    countban     = len(ban)

    ban2_content = _rf(p("sudo", "ban"))
    ban2_set     = {x.strip() for x in ban2_content.splitlines() if x.strip()}
    countban2    = len(ban2_set)

    # ══════════════════════════════════════════════════════════════════════
    # sudo/ state files
    # ══════════════════════════════════════════════════════════════════════
    amr     = _rf(p("sudo", "amr"))
    ch1     = _rf(p("sudo", "ch1"))
    ch2     = _rf(p("sudo", "ch2"))
    taf3il  = _rf(p("sudo", "tanbih"))

    # ══════════════════════════════════════════════════════════════════════
    # Subscription check for ch1 / ch2 (block user if not subscribed)
    # ══════════════════════════════════════════════════════════════════════
    if message:
        not_joined = False
        if ch1 or ch2:
            try:
                # Run checks in parallel with overall timeout
                tasks = []
                if ch1:
                    tasks.append(_safe_get_chat_member(token, ch1, from_id))
                if ch2:
                    tasks.append(_safe_get_chat_member(token, ch2, from_id))
                
                # Overall 8-second timeout for all checks
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=8.0
                )
                
                result_idx = 0
                if ch1 and result_idx < len(results):
                    j1 = results[result_idx]
                    result_idx += 1
                    if isinstance(j1, Exception) or not j1.get("ok"):
                        not_joined = True
                    else:
                        status1 = j1.get("result", {}).get("status", "left")
                        if status1 in ("left", "kicked"):
                            not_joined = True
                
                if ch2 and result_idx < len(results) and not not_joined:
                    j2 = results[result_idx]
                    if isinstance(j2, Exception) or not j2.get("ok"):
                        not_joined = True
                    else:
                        status2 = j2.get("result", {}).get("status", "left")
                        if status2 in ("left", "kicked"):
                            not_joined = True
            except asyncio.TimeoutError:
                logger.warning(f"Subscription check timeout for user {from_id}")
                not_joined = True
            except Exception as e:
                logger.error(f"Subscription check error for user {from_id}: {e}")
                not_joined = True

        if not_joined:
            ch1c = ch1.replace("@", "") if ch1 else ""
            ch2c = ch2.replace("@", "") if ch2 else ""
            try:
                await bot_call(token, "sendMessage", {
                    "chat_id":                  chat_id,
                    "reply_to_message_id":      message_id,
                    "text":                     f"\n\n",
                    "disable_web_page_preview": True,
                    "parse_mode":               "markdown",
                    "reply_markup":             json.dumps({"inline_keyboard": []}),
                })
                return
            except Exception as e:
                logger.error(f"Failed to send subscription message: {e}")
                return

    # ══════════════════════════════════════════════════════════════════════
    # typee — set receive destination to admin's private
    # ══════════════════════════════════════════════════════════════════════
    if data == "typee":
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text":       "• تم التفعيل مسبقا !",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "رجوع ", "callback_data": "bot9"}],
            ]}),
        })
        _wf(p("sudo", "typee"), str(from_id))

    # ══════════════════════════════════════════════════════════════════════
    # supergruope — set receive destination to a group
    # ══════════════════════════════════════════════════════════════════════
    if data == "supergruope":
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text": (
                "◾️ يمكنك استقبال الرسائل في مجموعتك انت وفريقك او اصدقائك  .\n\n"
                "▫️ ↴ اضغط على الزر و اختر المجموعة التي تريد، ثم أرسل تفعيل من داخل المجموعة\n"
            ),
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "• اضفني الى مجموعتك • ", "switch_inline_query": ""}],
                [{"text": "رجوع ", "callback_data": "bot9"}],
            ]}),
        })
        _wf(p("sudo", "amr"), "set")

    # ── activate group receive with "تفعيل" ───────────────────────────────
    if text == "تفعيل" and amr == "set" and str(from_id) in sudo_ids:
        _wf(p("sudo", "amr"), "")
        await bot_call(token, "sendMessage", {
            "chat_id": chat_id,
            "text":    "- حسناا عزيزي تم تحديد الكروب بنجاح سيتم نشر الرسائل في الكروب✅",
        })
        _wf(p("sudo", "typee"), str(chat_id))

    # ══════════════════════════════════════════════════════════════════════
    # estgbalon — enable message forwarding
    # ══════════════════════════════════════════════════════════════════════
    if data == "estgbalon":
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text":       " - تم تفعيل الرد بنجاح ✅،",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "رجوع ", "callback_data": "bot9"}],
            ]}),
        })
        _wf(p("sudo", "estgbal"), "on")

    # ══════════════════════════════════════════════════════════════════════
    # estgbaloff — disable message forwarding
    # ══════════════════════════════════════════════════════════════════════
    if data == "estgbaloff":
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text":       ' تم تعطيل توجيه الرسائل ✅".',
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": 'رجوع ".', "callback_data": "bot9"}],
            ]}),
        })
        _unlink(p("sudo", "amr"))
        _unlink(p("sudo", "estgbal"))

    # ══════════════════════════════════════════════════════════════════════
    # msrd — prompt admin to set delivery message
    # ══════════════════════════════════════════════════════════════════════
    if data == "msrd":
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text": (
                "▫️ إرسل رسالة التسليم التي تريد:\n"
                "▪️ يمكنك إستخدام الـMarkdown .\n"
                "-\n"
            ),
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "رجوع", "callback_data": "bot9"}],
            ]}),
        })
        _wf(p("sudo", "amr"), "msrd")

    # ── receive delivery message text when amr == "msrd" ──────────────────
    if text and amr == "msrd" and str(from_id) in sudo_ids:
        _unlink(p("sudo", "amr"))
        await bot_call(token, "sendMessage", {
            "chat_id": chat_id,
            "text": (
                f"-  تم إضافة ( رسالة تسليم ) إلى بوت التواصل الخاص بك .\n"
                f"▫️ مثل على رسالة التسليم ( {text} ) 🥏\n"
            ),
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "رجوع", "callback_data": "bot9"}],
            ]}),
        })
        _wf(p("data", "msrd"), text)

    # ══════════════════════════════════════════════════════════════════════
    # Resolve receive destination (yppee) and message counters
    # ══════════════════════════════════════════════════════════════════════
    yppee = _rf(p("sudo", "typee")).strip() if _rf(p("sudo", "typee")) else ""
    if not yppee or not str(yppee).lstrip("-").isdigit():
        yppee = admin
    
    # تحذير إذا كان yppee فارغاً - لن تصل رسائل المستخدمين للأدمن
    if not yppee or not str(yppee).lstrip("-").isdigit():
        print(f"⚠️ تحذير: وجهة الرسائل (yppee/admin) = {yppee}, admin = {admin}")
        yppee = admin if admin and str(admin).isdigit() else ""

    co_m_all = _ri(p("count", "user", "all"))
    co1      = co_m_all + 1

    # ── تهيئة مجلد message إذا كان مفقوداً ──────────────────────────────────
    ensure_dir(p("message"))

    # ── resolve replied-to message metadata ───────────────────────────────
    # عند الرد، reply_id هو رقم الرسالة التي نرد عليها (الرسالة من البوت)
    # وقد حفظنا معرف المستخدم في message/{reply_id}
    repp_id       = reply_id if reply_id else 0  # ← تم التصحيح
    msg_file_raw  = _rf(p("message", f"{repp_id}")) if reply_id else ""
    msg_parts     = msg_file_raw.split("=") if msg_file_raw else []
    n_id          = msg_parts[1] if len(msg_parts) > 1 else None

    msrd      = _rf(p("data", "msrd"))

    # ── اقرأ حالة قيود الوسائط من إعدادات البوت (setting JSON) ──────────
    # ✅ = مسموح (allowed)  |  ❌ = مرفوض (blocked)
    _twasl = setting.get("twasl", {})
    c_photo    = _twasl.get("modetext1", "")
    c_audio    = _twasl.get("modetext2", "")
    c_document = _twasl.get("modetext3", "")
    c_sticker  = _twasl.get("modetext4", "")
    c_video    = _twasl.get("modetext5", "")
    c_voice    = _twasl.get("modetext6", "")
    c_forward  = _twasl.get("modetext8", "")

    # ══════════════════════════════════════════════════════════════════════
    # Ban/Unban user from message button
    # ══════════════════════════════════════════════════════════════════════
    if data.startswith("ban_user_"):
        if is_admin(from_id):
            parts = data.split("_")
            if len(parts) >= 3:
                user_id_to_ban = parts[2]
                
                # قراءة قائمة الحظر الحالية
                ban_list = _get_ban_list(bot_dir)
                
                if str(user_id_to_ban) in ban_list:
                    # إلغاء الحظر
                    ban_list.remove(str(user_id_to_ban))
                    action_text = "✅ تم إلغاء حظر المستخدم"
                    button_text = "🚫 حظر المستخدم"
                else:
                    # حظر المستخدم
                    ban_list.append(str(user_id_to_ban))
                    action_text = "🚫 تم حظر المستخدم"
                    button_text = "✅ إلغاء الحظر"
                    
                    # إرسال رسالة للمستخدم المحظور
                    try:
                        await bot_call(token, "sendMessage", {
                            "chat_id": user_id_to_ban,
                            "text": "🚫 تم حظرك من هذا البوت\n\nلا يمكنك الآن إرسال رسائل إلى المسؤول ❌",
                        })
                    except:
                        pass  # قد لا يكون المستخدم متاحاً
                
                # حفظ قائمة الحظر
                ban_file_content = "\n".join(ban_list)
                _wf(p("NaMero", "ban"), ban_file_content)
                
                # تحديث الزر
                new_button_data = f"ban_user_{user_id_to_ban}_{message_id}"
                keyboards = {
                    "inline_keyboard": [
                        [
                            {"text": button_text, "callback_data": new_button_data}
                        ]
                    ]
                }
                
                await bot_call(token, "editMessageReplyMarkup", {
                    "chat_id":    chat_id,
                    "message_id": message_id,
                    "reply_markup": json.dumps(keyboards),
                })
                
                await bot_call(token, "answerCallbackQuery", {
                    "callback_query_id": callback.get("id", ""),
                    "text": action_text,
                    "show_alert": False,
                })

    # ══════════════════════════════════════════════════════════════════════
    # Forward text message from user to admin
    # ══════════════════════════════════════════════════════════════════════
    _EXCLUDE_TEXTS = {
        "/start", "جهة اتصال المدير☎️", "⚜️〽️┇قناه البوت",
        "ارفعني", "القوانين ⚠️", "معلومات المدير 📋",
        "المساعده 💡", "اطلب بوتك من المطور",
    }

    if (
        text
        and text not in _EXCLUDE_TEXTS
        and chat_type == "private"
        and str(from_id) != str(admin)
    ):
        print(f"[DEBUG] معالجة رسالة من المستخدم: text='{text}'")
        # تحقق من أن yppee محدد
        if not yppee or not str(yppee).lstrip("-").isdigit():
            print(f"⚠️ تحذير: لا يمكن إرسال رسائل - yppee غير محدد بشكل صحيح")
            return
        
        if str(from_id) not in ban:
            co_m_us = _ri(p("count", "user", f"{from_id}"))
            co_m_us += 1
            _wf(p("count", "user", f"{from_id}"), str(co_m_us))
            _wf(p("count", "user", "all"), str(co1))

            # إنشاء رسالة المعلومات (الرسالة الأولى)
            from_username = f"@{user}" if user else "بدون معرّف"
            separator = "-" * 35
            msg_info = (
                f"📨 رسالة جديدة من مستخدم\n"
                f"{separator}\n"
                f"👤 المرسل: {name}\n"
                f"🆔 المعرف: {from_username}\n"
                f"💬 الأيدي: {from_id}\n"
                f"📊 عدد الرسائل: {co_m_us}\n"
                f"{separator}"
            )
            
            # إرسال رسالة المعلومات الأولى (بدون أزرار)
            response_info = await bot_call(token, "sendMessage", {
                "chat_id": yppee,
                "text": msg_info,
            })
            
            # إرسال الرسالة الثانية (محتوى الرسالة)
            response = await bot_call(token, "sendMessage", {
                "chat_id": yppee,
                "text":    text,
            })
            
            if response.get("ok"):
                print(f"✅ تم إرسال الرسالة من {from_id} إلى المسؤول {yppee}")
                # احفظ معرف الرسالة المُرسلة مع معرف المستخدم الأصلي
                msg_id = response.get("result", {}).get("message_id", 0)
                ban_button_text = "🚫 حظر"
                ban_button_data = f"ban_user_{from_id}_{message_id}"
                reply_button_text = "↩️ رد"
                reply_button_data = f"reply_{msg_id}"

                keyboards = {
                    "inline_keyboard": [
                        [
                            {"text": ban_button_text, "callback_data": ban_button_data},
                            {"text": reply_button_text, "callback_data": reply_button_data},
                        ]
                    ]
                }

                await bot_call(token, "sendMessage", {
                    "chat_id":             yppee,
                    "text":                "⚙️ الخيارات:",
                    "reply_to_message_id": msg_id,
                    "reply_markup":        json.dumps(keyboards),
                })

                _wf(p("message", f"{msg_id}"), f"{chat_id}={name}={message_id}")
                print(f"[DEBUG] تم حفظ معرف المستخدم في: message/{msg_id} = {chat_id}={name}={message_id}")
                # حفظ الرسالة في نظام التخزين المنظم
                admin_name = _rf(p("info")).split("\n")[0] if _rf(p("info")) else "Admin"
                admin_user = _rf(p("info")).split("\n")[1] if len(_rf(p("info")).split("\n")) > 1 else ""
                _save_message(bot_dir, str(from_id), name, user, str(yppee), admin_user, text, message_id, "user→admin")
            else:
                print(f"❌ خطأ في إرسال الرسالة: {response.get('description')}")

            # إرسال رسالة الرد فقط إذا عيّن المستخدم رسالة مخصصة
            if msrd:
                print(f"[DEBUG] إرسال تأكيد: msrd='{msrd[:50]}'...")
                ack_response = await bot_call(token, "sendMessage", {
                    "chat_id":           chat_id,
                    "text":              f"{msrd}",
                    "reply_to_message_id": message_id,
                })
                if ack_response.get("ok"):
                    print(f"✅ تم إرسال رسالة التأكيد للمستخدم {chat_id}")
                    print(f"[DEBUG] العودة من معالجة الرسالة - لا تستمر المعالجة")
                    return  # ← أضفت return هنا
                else:
                    print(f"❌ خطأ في رسالة التأكيد: {ack_response.get('description')}")
            else:
                print(f"[DEBUG] msrd فارغ، عدم إرسال تأكيد")
                return  # ← أضفت return هنا أيضاً
        else:
            await bot_call(token, "sendMessage", {
                "chat_id":           chat_id,
                "text":              "🚫 أنت محظور من هذا البوت\n\nلا يمكنك إرسال رسائل إلى المسؤول ❌",
                "reply_to_message_id": message_id,
            })
            return  # ← توقف المعالجة

    # ══════════════════════════════════════════════════════════════════════
    # Admin replies to user via reply-to-message
    # ══════════════════════════════════════════════════════════════════════
    if (
        reply_id
        and text not in ("الغاء الحظر", "حظر", "معلومات")
        and str(chat_id) == str(yppee)
        and n_id is not None
    ):
        print(f"[DEBUG] محاولة الرد: reply_id={reply_id}, chat_id={chat_id}, yppee={yppee}, n_id={n_id}")
        if is_admin(from_id):
            print(f"[DEBUG] المستخدم {from_id} هو صاحب البوت - محاولة الرد")
            user_chat_id = msg_parts[0] if msg_parts else ""
            user_name    = msg_parts[1] if len(msg_parts) > 1 else ""
            orig_msg_id  = msg_parts[2] if len(msg_parts) > 2 else ""
            print(f"[DEBUG] تفاصيل الرد: user_chat_id={user_chat_id}, user_name={user_name}, orig_msg_id={orig_msg_id}")
            sent_msg_id  = 0

            if text:
                print(f"[DEBUG] إرسال رسالة نصية للمستخدم {user_chat_id}: '{text[:50]}'")
                await _maybe_typing(user_chat_id)
                get_r = await bot_call(token, "sendMessage", {
                    "chat_id":           user_chat_id,
                    "text":              text,
                    "reply_to_message_id": orig_msg_id,
                })
                sent_msg_id = get_r.get("result", {}).get("message_id", 0)
                print(f"[DEBUG] النتيجة: ok={get_r.get('ok')}, message_id={sent_msg_id}")
                
                # حفظ رد المسؤول
                if get_r.get("ok"):
                    print(f"✅ تم إرسال الرد للمستخدم {user_chat_id}")
                    admin_user_name = (message.get("from", {}).get("username") or "").lower()
                    _save_message(bot_dir, str(from_id), name, admin_user_name, str(user_chat_id), user_name, text, sent_msg_id, "admin→user")
                else:
                    print(f"❌ خطأ في إرسال الرد: {get_r.get('description')}")
            else:
                sens    = None
                file_id = None
                ss      = None
                if photo:
                    photos = update.get("message", {}).get("photo") or []
                    file_id = photos[-1].get("file_id", "") if photos else ""
                    sens = "sendPhoto"; ss = "photo"
                elif document:
                    file_id = document.get("file_id", "")
                    sens = "sendDocument"; ss = "document"
                elif video:
                    file_id = video.get("file_id", "")
                    sens = "sendVideo"; ss = "video"
                elif audio:
                    file_id = audio.get("file_id", "")
                    sens = "sendAudio"; ss = "audio"
                elif voice:
                    file_id = voice.get("file_id", "")
                    sens = "sendVoice"; ss = "voice"
                elif sticker:
                    file_id = sticker.get("file_id", "")
                    sens = "sendSticker"; ss = "sticker"

                if sens and file_id:
                    await _maybe_typing(user_chat_id)
                    get_r = await bot_call(token, sens, {
                        "chat_id":           user_chat_id,
                        ss:                  file_id,
                        "reply_to_message_id": orig_msg_id,
                    })
                    sent_msg_id = get_r.get("result", {}).get("message_id", 0)

            wathqid = f"{user_chat_id}={sent_msg_id}={user_name}"
            _wf(p("message", f"{sent_msg_id}"), wathqid)

            co_m_ad = _ri(p("count", "admin", f"{user_chat_id}"))
            _wf(p("count", "admin", f"{user_chat_id}"), str(co_m_ad + 1))
            co_m_all2 = _ri(p("count", "admin", "all"))
            _wf(p("count", "admin", "all"), str(co_m_all2 + 1))

            await bot_call(token, "sendMessage", {
                "chat_id":                  yppee,
                "text":                     f"-  تم الارسال بنجاح  [{user_name}](tg://user?id={user_chat_id}) ✉️\n",
                "reply_to_message_id":      message_id,
                "parse_mode":               "MarkDown",
                "disable_web_page_preview": True,
                "reply_markup": json.dumps({"inline_keyboard": [
                    [{"text": " تعديل الرسالة ", "callback_data": f"edit_msg {sent_msg_id}"}],
                    [{"text": " حذف الرسالة ",   "callback_data": f"del_msg {sent_msg_id}"}],
                ]}),
            })

    # ══════════════════════════════════════════════════════════════════════
    # del_msg — delete a sent message
    # ══════════════════════════════════════════════════════════════════════
    del_match = re.match(r'^del_msg (.+)$', data or "", re.S)
    if del_match and is_admin(from_id):
        wathqid = del_match.group(1)
        info    = _rf(p("message", f"{wathqid}")).split("=")
        ch_id_d = info[0] if info else ""
        msg_id_d= info[1] if len(info) > 1 else ""
        nm_id_d = info[2] if len(info) > 2 else ""
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text":       "-  تم حذف رسالة بنجاح 🗑\n\n",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "رجوع ", "callback_data": "bot9"}],
            ]}),
        })
        await bot_call(token, "deleteMessage", {
            "chat_id":    ch_id_d,
            "message_id": msg_id_d,
        })

    # ══════════════════════════════════════════════════════════════════════
    # edit_msg — start editing a sent message
    # ══════════════════════════════════════════════════════════════════════
    edit_match = re.match(r'^edit_msg (.+)$', data or "", re.S)
    if edit_match and is_admin(from_id):
        wathqid  = edit_match.group(1)
        info     = _rf(p("message", f"{wathqid}")).split("=")
        ch_id_e  = info[0] if info else ""
        msg_id_e = info[1] if len(info) > 1 else ""
        nm_id_e  = info[2] if len(info) > 2 else ""
        _wf(p("data", "t3dil"), f"{ch_id_e}={msg_id_e}={nm_id_e}")
        await bot_call(token, "sendMessage", {
            "chat_id":                  chat_id,
            "text":                     "- قم بارسال رسالتك الجديده ليتم تعديل رسالتك ✉️\n",
            "reply_to_message_id":      message_id,
            "parse_mode":               "MarkDown",
            "disable_web_page_preview": True,
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "رجوع ", "callback_data": "bot9"}],
            ]}),
        })
        _wf(p("sudo", "amr"), "edit")

    # ══════════════════════════════════════════════════════════════════════
    # trag3 — cancel editing
    # ══════════════════════════════════════════════════════════════════════
    if data == "trag3":
        await bot_call(token, "editMessageText", {
            "chat_id":    chat_id,
            "message_id": message_id,
            "text":       "تم الغاء التعديل بنجاح",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "رجوع ", "callback_data": "bot9"}],
            ]}),
        })
        _wf(p("sudo", "amr"), "")
        _wf(p("data", "t3dil"), "")

    # ══════════════════════════════════════════════════════════════════════
    # edit mode: admin sends new message text
    # ══════════════════════════════════════════════════════════════════════
    if text and amr == "edit" and str(chat_id) == str(yppee) and is_admin(from_id):
        _wf(p("sudo", "amr"), "")
        wathqget  = _rf(p("data", "t3dil"))
        wathqidd  = wathqget.split("=")
        ch_id_ed  = wathqidd[0] if wathqidd else ""
        msg_id_ed = wathqidd[1] if len(wathqidd) > 1 else ""
        nm_id_ed  = wathqidd[2] if len(wathqidd) > 2 else ""

        await bot_call(token, "deleteMessage", {"chat_id": chat_id, "message_id": message_id - 2})
        await bot_call(token, "deleteMessage", {"chat_id": chat_id, "message_id": message_id - 1})

        await bot_call(token, "sendMessage", {
            "chat_id":                  chat_id,
            "text":                     f"- تم التعديل رساله سابقة للمستخدم  [{nm_id_ed}](tg://user?id={ch_id_ed}) ✉️",
            "reply_to_message_id":      message_id,
            "parse_mode":               "MarkDown",
            "disable_web_page_preview": True,
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": " تعديل الرسالة ", "callback_data": f"edit_msg {msg_id_ed}"},
                 {"text": " حذف الرسالة ",   "callback_data": f"del_msg {msg_id_ed}"}],
            ]}),
        })
        _wf(p("data", "t3dil"), "")
        await bot_call(token, "editMessageText", {
            "chat_id":    ch_id_ed,
            "message_id": msg_id_ed,
            "text":       text,
        })

    # ══════════════════════════════════════════════════════════════════════
    # حظر via text command: "حظر <ID>"
    # ══════════════════════════════════════════════════════════════════════
    ban_cmd = re.match(r'^حظر (.+)$', text or "", re.S)
    if ban_cmd and str(chat_id) == str(yppee) and is_admin(from_id):
        textt = ban_cmd.group(1).replace(" ", "").strip()
        is_valid, error_msg = _validate_user_id(textt)

        if not is_valid:
            await bot_call(token, "sendMessage", {
                "chat_id":           chat_id,
                "text":              f"❌ خطأ: {error_msg}",
                "reply_to_message_id": message_id,
            })
        elif textt in ban:
            await bot_call(token, "sendMessage", {
                "chat_id":           chat_id,
                "text":              "• العضو محظور مسبقاً.!",
                "reply_to_message_id": message_id,
            })
        else:
            try:
                await bot_call(token, "sendMessage", {"chat_id": textt, "text": "🔴 تم حظرك من البوت"})
            except Exception as e:
                logger.warning(f"Could not notify banned user {textt}: {e}")

            await bot_call(token, "sendMessage", {
                "chat_id":           chat_id,
                "text":              f"✅ تم حظر المستخدم {textt} من البوت",
                "reply_to_message_id": message_id,
            })
            _af(p("data", "ban"), f"{textt}\n")
            _invalidate_cache(f"ban_{bot_dir}")  # Invalidate cache

    # ══════════════════════════════════════════════════════════════════════
    # الغاء حظر via text command: "الغاء حظر <ID>"
    # ══════════════════════════════════════════════════════════════════════
    unban_cmd = re.match(r'^الغاء حظر (.+)$', text or "", re.S)
    if unban_cmd and str(chat_id) == str(yppee) and is_admin(from_id):
        textt = unban_cmd.group(1).replace(" ", "").strip()
        is_valid, error_msg = _validate_user_id(textt)

        if not is_valid:
            await bot_call(token, "sendMessage", {
                "chat_id":           chat_id,
                "text":              f"❌ خطأ: {error_msg}",
                "reply_to_message_id": message_id,
            })
        elif textt not in ban:
            await bot_call(token, "sendMessage", {
                "chat_id":           chat_id,
                "text":              "• العضو ليس محظور ❕❕",
                "reply_to_message_id": message_id,
            })
        else:
            try:
                await bot_call(token, "sendMessage", {"chat_id": textt, "text": "🟢 تم إلغاء حظرك من البوت"})
            except Exception as e:
                logger.warning(f"Could not notify unbanned user {textt}: {e}")

            await bot_call(token, "sendMessage", {
                "chat_id":           chat_id,
                "text":              f"✅ تم إلغاء حظر المستخدم {textt} 🚫",
                "reply_to_message_id": message_id,
            })
            # Remove from ban list
            ban_list_updated = "\n".join([b for b in ban if b != textt])
            _wf(p("data", "ban"), ban_list_updated)
            _invalidate_cache(f"ban_{bot_dir}")  # Invalidate cache

    # ══════════════════════════════════════════════════════════════════════
    # حظر via reply-to-message
    # ══════════════════════════════════════════════════════════════════════
    if reply_id and text == "حظر" and str(chat_id) == str(yppee) and n_id is not None:
        if is_admin(from_id):
            from_user = msg_parts[0] if msg_parts else ""
            if from_user not in ban:
                await bot_call(token, "sendMessage", {
                    "chat_id":           chat_id,
                    "text":              "تم حظر الشخص من البوت",
                    "reply_to_message_id": message_id,
                })
                await bot_call(token, "sendMessage", {"chat_id": from_user, "text": ""})
                _af(p("data", "ban"), f"{from_user}\n")
            else:
                await bot_call(token, "sendMessage", {
                    "chat_id":           chat_id,
                    "text":              "• العضو محظور مسبقآ.!",
                    "reply_to_message_id": message_id,
                })

    # ══════════════════════════════════════════════════════════════════════
    # الغاء الحظر via reply-to-message
    # ══════════════════════════════════════════════════════════════════════
    if reply_id and text == "الغاء الحظر" and str(chat_id) == str(yppee) and n_id is not None:
        if is_admin(from_id):
            from_user = msg_parts[0] if msg_parts else ""
            if from_user in ban:
                await bot_call(token, "sendMessage", {
                    "chat_id":           chat_id,
                    "text":              "تم الغاء حظر الشخص من البوت 🚫",
                    "reply_to_message_id": message_id,
                })
                await bot_call(token, "sendMessage", {"chat_id": from_user, "text": ""})
                ban_content = _rf(p("data", "ban"))
                new_ban = ban_content.replace(f"{from_user}\n", "")
                _wf(p("data", "ban"), new_ban)
                _invalidate_cache("ban_list")
            else:
                await bot_call(token, "sendMessage", {
                    "chat_id":           chat_id,
                    "text":              "  • العضو ليس محظور ❕❕",
                    "reply_to_message_id": message_id,
                })

    # ══════════════════════════════════════════════════════════════════════
    # معلومات via reply — show user info to admin
    # ══════════════════════════════════════════════════════════════════════
    if reply_id and text == "معلومات" and str(chat_id) == str(yppee):
        if is_admin(from_id):
            from_user   = msg_parts[0] if msg_parts else ""
            chat_info   = await bot_get(token, "getChat", {"chat_id": from_user})
            r           = chat_info.get("result", {})
            u_name      = r.get("first_name", "")
            u_user      = r.get("username", "")
            bio_res     = await bot_get(token, "getChat", {"chat_id": from_id})
            bio         = bio_res.get("result", {}).get("bio", "")
            info_status = "محظور" if str(from_user) in ban_set else "غير محظور"
            co_m_us2    = _ri(p("count", "user",  f"{from_user}"))
            co_m_ad2    = _ri(p("count", "admin", f"{from_user}"))
            photo_url   = f"http://telegram.me/{u_user}"
            await bot_call(token, "sendPhoto", {
                "chat_id": chat_id,
                "photo":   photo_url,
                "caption": (
                    f"👤| اسم المستخدم : [ {u_name}](tg://user?id={from_user})  .\n"
                    f"ℹ️| ايدي المستخدم : {from_user}\n"
                    f"📍| معرف المستخدم : *@{u_user}*\n"
                    f"🔎| حالة المستخدم : {info_status}\n"
                    f"✉️| عدد الرسائل المستلمة منة : {co_m_us2} \n"
                    f" 📬| عدد الرسائل المرسلة لة : {co_m_ad2} \n"
                ),
                "reply_to_message_id":      message_id,
                "parse_mode":               "MarkDown",
                "disable_web_page_preview": True,
            })

    # ══════════════════════════════════════════════════════════════════════
    # معلومات without reply — show full bot stats with pagination
    # ══════════════════════════════════════════════════════════════════════
    if text == "معلومات" and not reply_id and str(chat_id) == str(yppee):
        if is_admin(from_id):
            _unlink(p("sudo", "admins"))
            admins_text = ""
            page = 1  # Default page

            # Get paginated admins
            page_admins, total_pages, has_next, has_prev = _paginate_list(adminall, page, ITEMS_PER_PAGE)

            for h, aid in enumerate(page_admins, 1):
                if aid:
                    try:
                        ai_res = await _safe_get_chat_member(token, yppee, aid)
                        ai = ai_res.get("result", {}) if ai_res.get("ok") else {}
                        ai_name = ai.get("first_name", f"ID: {aid}")
                        line = f"{(page-1)*ITEMS_PER_PAGE + h} - [{ai_name}](tg://user?id={aid}) `{aid}`"
                        admins_text += line + "\n"
                    except Exception as e:
                        logger.error(f"Error getting admin info for {aid}: {e}")
                        line = f"{(page-1)*ITEMS_PER_PAGE + h} - ID: `{aid}`"
                        admins_text += line + "\n"

            # Navigation buttons
            nav_buttons = []
            if has_prev:
                nav_buttons.append({"text": "⬅️ السابق", "callback_data": f"admins_page_{page-1}"})
            nav_buttons.append({"text": f"{page}/{total_pages}", "callback_data": "current_page"})
            if has_next:
                nav_buttons.append({"text": "التالي ➡️", "callback_data": f"admins_page_{page+1}"})

            co_m_us3 = _ri(p("count", "user",  "all"))
            co_m_ad3 = _ri(p("count", "admin", "all"))

            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": (
                    "ℹ معلومات شاملة عن البوت  \n"
                    "~~~~~~~~~~~~~~~~~~~~~~~\n"
                    f"👮 - الادمنية (صفحة {page}/{total_pages}): \n{admins_text}"
                    "--------------------\n"
                    f"👪 - عدد الاعضاء : {cunte}\n"
                    f"🚫 - المحضورين : {countban}\n"
                    "--------------------\n"
                    "📮 - الرسائل \n"
                    f"📩 - المستلمة :{co_m_us3}\n"
                    f"📬 - الصادرة :{co_m_ad3}\n\n\n"
                ),
                "reply_to_message_id":      message_id,
                "parse_mode":               "MarkDown",
                "disable_web_page_preview": True,
                "reply_markup": json.dumps({"inline_keyboard": [nav_buttons] if nav_buttons else []}),
            })

    # ══════════════════════════════════════════════════════════════════════
    # Media forwarding helper
    # Forwards a media message from user to admin if the media type is allowed.
    # In the data files: ✅ = allowed/open, ❌ = locked/blocked, "" = allowed (default)
    # ══════════════════════════════════════════════════════════════════════
    async def _fwd_media(content_flag: str) -> None:
        if content_flag in ("✅", "") or not content_flag:
            co_us = _ri(p("count", "user", f"{from_id}"))
            co_us += 1
            _wf(p("count", "user", f"{from_id}"), str(co_us))
            _wf(p("count", "user", "all"), str(co1))

            # إنشاء رسالة المعلومات (الرسالة الأولى)
            from_username = f"@{user}" if user else "بدون معرّف"
            separator = "-" * 35
            msg_info = (
                f"📨 رسالة جديدة من مستخدم\n"
                f"{separator}\n"
                f"👤 المرسل: {name}\n"
                f"🆔 المعرف: {from_username}\n"
                f"💬 الأيدي: {from_id}\n"
                f"📊 عدد الرسائل: {co_us}\n"
                f"{separator}"
            )
            
            # إرسال رسالة المعلومات الأولى (بدون أزرار)
            await _maybe_typing(yppee)
            response_info = await bot_call(token, "sendMessage", {
                "chat_id": yppee,
                "text": msg_info,
            })
            
            # الرسالة الثانية: forward الوسيط/الرسالة الأصلية
            get_r = await bot_call(token, "forwardMessage", {
                "chat_id":      yppee,
                "from_chat_id": chat_id,
                "message_id":   message_id,
            })
            
            # إذا نجح forward، أرسل رسالة تعليق بالأزرار (وليس تعديل)
            if get_r.get("ok"):
                msg_id = get_r.get("result", {}).get("message_id", 0)
                
                # إنشاء أزرار الحظر/إلغاء الحظر
                ban_button_text = "🚫 حظر"
                ban_button_data = f"ban_user_{from_id}_{message_id}"
                
                reply_button_text = "↩️ رد"
                reply_button_data = f"reply_{msg_id}"
                
                keyboards = {
                    "inline_keyboard": [
                        [
                            {"text": ban_button_text, "callback_data": ban_button_data},
                            {"text": reply_button_text, "callback_data": reply_button_data}
                        ]
                    ]
                }
                
                # أرسل رسالة تعليق (reply) مع الأزرار بدلاً من محاولة التعديل
                reply_response = await bot_call(token, "sendMessage", {
                    "chat_id":              yppee,
                    "text":                 "⚙️ الخيارات:",
                    "reply_to_message_id":  msg_id,
                    "reply_markup":         json.dumps(keyboards),
                })
                
                if reply_response.get("ok"):
                    _wf(p("message", f"{msg_id}"), f"{chat_id}={name}={message_id}")
            else:
                msg_id = 0
            
            # إرسال رسالة الرد فقط إذا عيّن المستخدم رسالة مخصصة
            if msrd:
                await bot_call(token, "sendMessage", {
                    "chat_id":           chat_id,
                    "text":              f"{msrd}",
                    "reply_to_message_id": message_id,
                })
        else:
            await bot_call(token, "sendMessage", {
                "chat_id":           chat_id,
                "text":              "🚫 هذا النوع من الوسائط غير مسموح.",
                "reply_to_message_id": message_id,
            })

    is_user_private = (str(from_id) != str(admin) and chat_type == "private")

    # ── الصور — photos ────────────────────────────────────────────────────
    if photo and not forward and is_user_private:
        await _fwd_media(c_photo)
        return

    # ── الفيديو — videos ──────────────────────────────────────────────────
    if video and not forward and is_user_private:
        await _fwd_media(c_video)
        return

    # ── الملفات — documents ───────────────────────────────────────────────
    if document and not forward and is_user_private:
        await _fwd_media(c_document)
        return

    # ── الملصقات — stickers ───────────────────────────────────────────────
    if sticker and not forward and is_user_private:
        await _fwd_media(c_sticker)
        return

    # ── الصوتيات — voice messages ─────────────────────────────────────────
    if voice and not forward and is_user_private:
        await _fwd_media(c_voice)
        return

    # ── الصوتيات — audio files ────────────────────────────────────────────
    if audio and not forward and is_user_private:
        await _fwd_media(c_audio)
        return

    # ── التوجية — forwarded messages ──────────────────────────────────────
    if forward and is_user_private:
        await _fwd_media(c_forward)
        return

    # ══════════════════════════════════════════════════════════════════════
    # Link detection — block links if users == "مقفول"
    # ══════════════════════════════════════════════════════════════════════
    _LINK_MARKERS = ["t.me", "telegram.me", "https://", "://", "wWw.", "WwW.", "T.me/", "WWW."]
    text_or_cap   = (text or "") + (caption or "")
    if any(m in text_or_cap for m in _LINK_MARKERS):
        users_lock = _rf(p("data", "users"))
        if users_lock == "مقفول":
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text":    " يمنع ارسال الروابط .",
            })

    # ══════════════════════════════════════════════════════════════════════
    # New Features: Broadcast, Stats, Admin Management, Bot Status
    # ══════════════════════════════════════════════════════════════════════

    # Track new users when they first interact
    if message and str(from_id) != str(admin) and from_id:
        _track_user(from_id, name, bot_dir)

    # ══════════════════════════════════════════════════════════════════════
    # Ban/Unban text commands (must reply to a message)
    # ══════════════════════════════════════════════════════════════════════
    if text and str(from_id) in sudo_ids and reply_id:
        try:
            target_msg = await bot_get(token, "getMessage", {"chat_id": chat_id, "message_id": reply_id})
            target_user = target_msg.get("result", {}).get("from", {}).get("id") if target_msg.get("ok") else None
            
            ban_file = p(bot_dir, "data", "ban")
            
            if text == "حظر" and target_user:
                ban_list = _get_ban_list(bot_dir)
                if str(target_user) not in ban_list:
                    ban_list.append(str(target_user))
                    _wf(ban_file, "\n".join(ban_list))
                    _invalidate_cache(f"ban_{bot_dir}")
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": f"✅ تم حظر المستخدم {target_user}",
                })
            
            elif text == "الغاء حظر" and target_user:
                ban_list = _get_ban_list(bot_dir)
                if str(target_user) in ban_list:
                    ban_list.remove(str(target_user))
                    _wf(ban_file, "\n".join(ban_list))
                    _invalidate_cache(f"ban_{bot_dir}")
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": f"✅ تم إلغاء حظر المستخدم {target_user}",
                })
        except Exception as e:
            logger.error(f"Error in ban/unban command: {e}")

    # broadcast_menu — show broadcast options
    if data == "broadcast_menu" and is_admin(from_id):
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": "📢 *قائمة الإذاعة*\n\nاختر نوع الإذاعة:",
            "parse_mode": "Markdown",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "📝 إذاعة نصية", "callback_data": "broadcast_text"}],
                [{"text": "🔙 رجوع", "callback_data": "bot9"}],
            ]}),
        })

    # broadcast_text — prompt for broadcast message
    if data == "broadcast_text" and is_admin(from_id):
        _wf(p("data", "broadcast_mode"), "waiting_for_message")
        await bot_call(token, "sendMessage", {
            "chat_id": chat_id,
            "text": "📝 أرسل الآن النص الذي تريد إذاعته لجميع المستخدمين:",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "❌ إلغاء", "callback_data": "bot9"}],
            ]}),
        })

    # Receive broadcast message and send it
    if text and _rf(p("data", "broadcast_mode")) == "waiting_for_message" and is_admin(from_id):
        _unlink(p("data", "broadcast_mode"))
        await bot_call(token, "sendMessage", {
            "chat_id": chat_id,
            "text": "⏳ جاري إرسال الإذاعة...",
        })
        sent, failed = await _send_broadcast(token, text, bot_dir, str(from_id))
        await bot_call(token, "sendMessage", {
            "chat_id": chat_id,
            "text": f"✅ تمّت الإذاعة!\n\n📤 تم الإرسال إلى: {sent}\n❌ فشل: {failed}",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "🔙 رجوع", "callback_data": "bot9"}],
            ]}),
        })

    # show_stats — display statistics
    if data == "show_stats" and is_admin(from_id):
        stats = _get_stats(bot_dir)
        bot_status = _get_bot_status(bot_dir)
        stats_text = (
            "📊 *إحصائيات البوت*\n\n"
            f"👥 المستخدمون: {stats['total_users']}\n"
            f"👮 الأدمنية: {stats['total_admins']}\n"
            f"📢 الإذاعات المُرسلة: {stats['broadcast_sent']}\n"
            f"📥 الإذاعات المُستقبلة: {stats['broadcast_received']}\n"
            f"🔌 حالة البوت: {'✅ مُشغّل' if bot_status == 'on' else '❌ موقوف'}\n"
        )
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": stats_text,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "🔙 رجوع", "callback_data": "bot9"}],
            ]}),
        })

    # manage_admins — admin management menu
    if data == "manage_admins" and is_admin(from_id):
        admins = _get_admin_list(bot_dir)
        admins_count = len(admins)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": f"👥 *إدارة الأدمنية*\n\nعدد الأدمنية الحالية: {admins_count}",
            "parse_mode": "Markdown",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "➕ إضافة أدمن", "callback_data": "add_admin_prompt"}],
                [{"text": "➖ حذف أدمن", "callback_data": "remove_admin_prompt"}],
                [{"text": "📋 قائمة الأدمنية", "callback_data": "list_admins"}],
                [{"text": "🔙 رجوع", "callback_data": "bot9"}],
            ]}),
        })

    # add_admin_prompt — ask for user ID to add as admin
    if data == "add_admin_prompt" and is_admin(from_id):
        _wf(p("data", "admin_mode"), "waiting_to_add")
        await bot_call(token, "sendMessage", {
            "chat_id": chat_id,
            "text": "👑 أرسل معرّف المستخدم (ID) الذي تريد إضافته كأدمن:",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "❌ إلغاء", "callback_data": "manage_admins"}],
            ]}),
        })

    # Receive user ID and add as admin
    if text and _rf(p("data", "admin_mode")) == "waiting_to_add" and is_admin(from_id):
        _unlink(p("data", "admin_mode"))
        text_clean = text.strip()
        is_valid, error_msg = _validate_user_id(text_clean)

        if not is_valid:
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": f"❌ خطأ: {error_msg}",
            })
        else:
            new_admin_id = int(text_clean)
            if _add_admin(new_admin_id, bot_dir):
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": f"✅ تمّ إضافة المستخدم {new_admin_id} كأدمن!",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "🔙 رجوع", "callback_data": "manage_admins"}],
                    ]}),
                })
                _invalidate_cache(f"admins_{bot_dir}")  # Invalidate cache
            else:
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": f"⚠️ المستخدم {new_admin_id} أدمن بالفعل!",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "🔙 رجوع", "callback_data": "manage_admins"}],
                    ]}),
                })

    # remove_admin_prompt — ask for user ID to remove from admins
    if data == "remove_admin_prompt" and is_admin(from_id):
        _wf(p("data", "admin_mode"), "waiting_to_remove")
        await bot_call(token, "sendMessage", {
            "chat_id": chat_id,
            "text": "🗑️ أرسل معرّف المستخدم (ID) الذي تريد حذفه من الأدمنية:",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "❌ إلغاء", "callback_data": "manage_admins"}],
            ]}),
        })

    # Receive user ID and remove from admins
    if text and _rf(p("data", "admin_mode")) == "waiting_to_remove" and is_admin(from_id):
        _unlink(p("data", "admin_mode"))
        text_clean = text.strip()
        is_valid, error_msg = _validate_user_id(text_clean)

        if not is_valid:
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": f"❌ خطأ: {error_msg}",
            })
        else:
            remove_admin_id = int(text_clean)
            if _remove_admin(remove_admin_id, bot_dir):
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": f"✅ تمّ حذف المستخدم {remove_admin_id} من الأدمنية!",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "🔙 رجوع", "callback_data": "manage_admins"}],
                    ]}),
                })
                _invalidate_cache(f"admins_{bot_dir}")  # Invalidate cache
            else:
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": f"⚠️ المستخدم {remove_admin_id} ليس أدمن!",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "🔙 رجوع", "callback_data": "manage_admins"}],
                    ]}),
                })

    # list_admins — show list of all admins
    if data == "list_admins" and is_admin(from_id):
        admins = _get_admin_list(bot_dir)
        if admins:
            admins_text = "👮 *قائمة الأدمنية:*\n\n"
            for idx, admin_id in enumerate(admins, 1):
                admins_text += f"{idx}. ID: {admin_id}\n"
        else:
            admins_text = "لا توجد أدمنية مضافة حتى الآن"
        
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": admins_text,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "🔙 رجوع", "callback_data": "manage_admins"}],
            ]}),
        })

    # bot_status_menu — show bot status menu
    if data == "bot_status_menu" and is_admin(from_id):
        current_status = _get_bot_status(bot_dir)
        status_text = f"🔌 حالة البوت الحالية: {'✅ مُشغّل' if current_status == 'on' else '❌ موقوف'}"
        
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": status_text,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "✅ تشغيل البوت", "callback_data": "bot_on"}],
                [{"text": "❌ إيقاف البوت", "callback_data": "bot_off"}],
                [{"text": "🔙 رجوع", "callback_data": "bot9"}],
            ]}),
        })

    # bot_on — enable bot
    if data == "bot_on" and is_admin(from_id):
        _set_bot_status(bot_dir, "on")
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": "✅ تمّ تشغيل البوت بنجاح!",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "🔙 رجوع", "callback_data": "bot_status_menu"}],
            ]}),
        })

    # bot_off — disable bot
    if data == "bot_off" and is_admin(from_id):
        _set_bot_status(bot_dir, "off")
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": "❌ تمّ إيقاف البوت بنجاح!\nالمستخدمون العاديون لن يتمكّنوا من استخدام البوت.",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "🔙 رجوع", "callback_data": "bot_status_menu"}],
            ]}),
        })

    # ══════════════════════════════════════════════════════════════════════
    # ══════════════════════════════════════════════════════════════════════
    # notifications_menu — show notification options
    # ══════════════════════════════════════════════════════════════════════
    if data == "notifications_menu" and is_admin(from_id):
        new_user_status = setting.get("twasl", {}).get("notif_new_users", "✅")
        blocked_status = setting.get("twasl", {}).get("notif_blocked", "✅")
        
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": (
                "🔔 *إدارة الإخطارات*\n\n"
                "━━━━━━━━━━━━━━━━\n"
                "اختر الإخطارات التي تريد تفعيلها:"
            ),
            "parse_mode": "Markdown",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": f"👾 دخول جديد: {new_user_status}", "callback_data": "notif_new_users"}],
                [{"text": f"🚫 حظر البوت: {blocked_status}", "callback_data": "notif_blocked"}],
                [{"text": "🔙 رجوع", "callback_data": "bot9"}],
            ]}),
        })

    # notifications_new_users — toggle new user notifications
    if data == "notif_new_users" and is_admin(from_id):
        current = setting.get("twasl", {}).get("notif_new_users", "✅")
        new_status = "❌" if current == "✅" else "✅"
        setting.setdefault("twasl", {})["notif_new_users"] = new_status
        _save_setting(bot_dir, setting_path, setting)
        
        new_user_status = new_status
        blocked_status = setting.get("twasl", {}).get("notif_blocked", "✅")
        
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": (
                "🔔 *إدارة الإخطارات*\n\n"
                "━━━━━━━━━━━━━━━━\n"
                "اختر الإخطارات التي تريد تفعيلها:"
            ),
            "parse_mode": "Markdown",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": f"👾 دخول جديد: {new_user_status}", "callback_data": "notif_new_users"}],
                [{"text": f"🚫 حظر البوت: {blocked_status}", "callback_data": "notif_blocked"}],
                [{"text": "🔙 رجوع", "callback_data": "bot9"}],
            ]}),
        })

    # notifications_blocked — toggle blocked bot notifications
    if data == "notif_blocked" and is_admin(from_id):
        current = setting.get("twasl", {}).get("notif_blocked", "✅")
        new_status = "❌" if current == "✅" else "✅"
        setting.setdefault("twasl", {})["notif_blocked"] = new_status
        _save_setting(bot_dir, setting_path, setting)
        
        new_user_status = setting.get("twasl", {}).get("notif_new_users", "✅")
        blocked_status = new_status
        
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": (
                "🔔 *إدارة الإخطارات*\n\n"
                "━━━━━━━━━━━━━━━━\n"
                "اختر الإخطارات التي تريد تفعيلها:"
            ),
            "parse_mode": "Markdown",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": f"👾 دخول جديد: {new_user_status}", "callback_data": "notif_new_users"}],
                [{"text": f"🚫 حظر البوت: {blocked_status}", "callback_data": "notif_blocked"}],
                [{"text": "🔙 رجوع", "callback_data": "bot9"}],
            ]}),
        })

    # admins_page_X — show specific page of admins
    page_match = re.match(r'^admins_page_(\d+)$', data or "", re.S)
    if page_match and is_admin(from_id):
        page = int(page_match.group(1))

        admins_text = ""
        # Get paginated admins
        page_admins, total_pages, has_next, has_prev = _paginate_list(adminall, page, ITEMS_PER_PAGE)

        for h, aid in enumerate(page_admins, 1):
            if aid:
                try:
                    ai_res = await _safe_get_chat_member(token, yppee, aid)
                    ai = ai_res.get("result", {}) if ai_res.get("ok") else {}
                    ai_name = ai.get("first_name", f"ID: {aid}")
                    line = f"{(page-1)*ITEMS_PER_PAGE + h} - [{ai_name}](tg://user?id={aid}) `{aid}`"
                    admins_text += line + "\n"
                except Exception as e:
                    logger.error(f"Error getting admin info for {aid}: {e}")
                    line = f"{(page-1)*ITEMS_PER_PAGE + h} - ID: `{aid}`"
                    admins_text += line + "\n"

        # Navigation buttons
        nav_buttons = []
        if has_prev:
            nav_buttons.append({"text": "⬅️ السابق", "callback_data": f"admins_page_{page-1}"})
        nav_buttons.append({"text": f"{page}/{total_pages}", "callback_data": "current_page"})
        if has_next:
            nav_buttons.append({"text": "التالي ➡️", "callback_data": f"admins_page_{page+1}"})

        co_m_us3 = _ri(p("count", "user",  "all"))
        co_m_ad3 = _ri(p("count", "admin", "all"))

        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": (
                "ℹ معلومات شاملة عن البوت  \n"
                "~~~~~~~~~~~~~~~~~~~~~~~\n"
                f"👮 - الادمنية (صفحة {page}/{total_pages}): \n{admins_text}"
                "--------------------\n"
                f"👪 - عدد الاعضاء : {cunte}\n"
                f"🚫 - المحضورين : {countban}\n"
                "--------------------\n"
                "📮 - الرسائل \n"
                f"📩 - المستلمة :{co_m_us3}\n"
                f"📬 - الصادرة :{co_m_ad3}\n\n\n"
            ),
            "reply_to_message_id":      message_id,
            "parse_mode":               "MarkDown",
            "disable_web_page_preview": True,
            "reply_markup": json.dumps({"inline_keyboard": [nav_buttons] if nav_buttons else []}),
        })


# ═══════════════════════════════════════════════════════════════════════════
# Polling runner — run when executed directly:
#   python namero4_handler.py <bot_dir>
#   Example: python namero4_handler.py botmak/mybotfolder
# ═══════════════════════════════════════════════════════════════════════════

_POLL_TIMEOUT = 30
_RETRY_DELAY  = 0.5  # تقليل من 5 إلى 0.5 ثانية
_MAX_ERRORS   = 10


async def _delete_webhook(token: str, name: str = "NAMERO4") -> None:
    result = await bot_get(token, "deleteWebhook", {"drop_pending_updates": False})
    if result.get("ok"):
        print(f"[{name}] ✅ تم حذف الويب هوك - جاهز للـ Polling")
    else:
        print(f"[{name}] ⚠️ deleteWebhook: {result.get('description')}")


async def _get_updates(token: str, offset: int) -> list:
    try:
        result = await bot_get(
            token,
            "getUpdates",
            {"offset": offset, "timeout": _POLL_TIMEOUT, "allowed_updates": []},
            timeout=_POLL_TIMEOUT + 10,
        )
        if result.get("ok"):
            return result.get("result", [])
    except Exception as e:
        print(f"[NAMERO4] getUpdates error: {e}")
    return []


async def _run_polling(bot_dir: str) -> None:
    token_path = os.path.join(bot_dir, "token")
    admin_path = os.path.join(bot_dir, "admin")

    if not file_exists(token_path):
        print(f"[NAMERO4] ❌ لم يتم العثور على {token_path}")
        return
    if not file_exists(admin_path):
        print(f"[NAMERO4] ❌ لم يتم العثور على {admin_path}")
        return

    token = read_file(token_path).strip()
    bot_name = os.path.basename(os.path.abspath(bot_dir))

    # load NaMerOset (zune) and makerinve (NameroF or ../KhAlEdJ)
    zune_path    = os.path.join(bot_dir, "zune")
    namero_path  = os.path.join(bot_dir, "NameroF")
    khaled_path  = os.path.join(bot_dir, "..", "KhAlEdJ")

    NaMerOset = read_json(zune_path, {})
    makerinve = read_json(namero_path, {})
    if not makerinve:
        makerinve = read_json(khaled_path, {}).get("info", {})

    if not token:
        print("[NAMERO4] ❌ token فارغ")
        return

    # Setup logger
    logger = _setup_logger(bot_dir)

    print("=" * 55)
    print("  NaMero Robots — NAMERO4 Bot Polling")
    print("  by @Voltees")
    print(f"  المجلد : {bot_dir}")
    print("=" * 55)

    await _delete_webhook(token, bot_name)

    offset      = 0
    offset_file = os.path.join(bot_dir, "offset")
    
    # استرجاع آخر offset محفوظ
    if file_exists(offset_file):
        try:
            offset = int(read_file(offset_file).strip())
        except:
            offset = 0
    
    error_count = 0

    while True:
        try:
            updates = await _get_updates(token, offset)
            error_count = 0

            for update in updates:
                update_id = update.get("update_id", 0)
                try:
                    await handle_namero4(
                        update    = update,
                        bot_dir   = bot_dir,
                        token     = token,
                        NaMerOset = NaMerOset,
                        makerinve = makerinve,
                    )
                except Exception as e:
                    print(f"[{bot_name}] ❌ خطأ في التحديث {update_id}: {e}")
                    logger.error(f"Error processing update {update_id}: {e}", exc_info=True)
                finally:
                    # احفظ الـ offset دائماً بعد معالجة التحديث (نجح أم فشل)
                    offset = update_id + 1
                    write_file(offset_file, str(offset))
                    print(f"[{bot_name}] 💾 تم حفظ offset: {offset}")

            # sleep بسيط بين الطلبات لتجنب إرهاق الـ API
            if not updates:
                await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            print(f"[{bot_name}] ⛔ تم إيقاف الـ Polling")
            break
        except Exception as e:
            error_count += 1
            print(f"[{bot_name}] ❌ خطأ ({error_count}/{_MAX_ERRORS}): {e}")
            logger.error(f"Polling error: {e}", exc_info=True)
            
            if error_count >= _MAX_ERRORS:
                print(f"[{bot_name}] ⚠️ وصلنا لـ {_MAX_ERRORS} أخطاء متتالية، سيتم إعادة المحاولة...")
                await asyncio.sleep(2)
                error_count = 0
            else:
                await asyncio.sleep(1)


async def _main() -> None:
    bot_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.isdir(bot_dir):
        print(f"[NAMERO4] ❌ المجلد غير موجود: {bot_dir}")
        sys.exit(1)

    loop = asyncio.get_running_loop()
    task = asyncio.create_task(_run_polling(bot_dir))

    def _stop(sig):
        print(f"\n[NAMERO4] إشارة إيقاف ({sig.name})")
        task.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop, sig)
        except (NotImplementedError, RuntimeError):
            pass

    await asyncio.gather(task, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(_main())
