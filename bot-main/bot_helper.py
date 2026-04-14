import httpx
import asyncio
import json
import os
import threading
from datetime import datetime
from typing import Any, Optional, Dict, List

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

# ══════════════════════════════════════════════════════════════════════════════
# Client مشترك ومستمر - يُفتح مرة واحدة ويُعاد الاستخدام لجميع الطلبات
# هذا هو الإصلاح الرئيسي للبطء: بدلاً من فتح TCP+TLS لكل طلب
# ══════════════════════════════════════════════════════════════════════════════

_shared_client: Optional[httpx.AsyncClient] = None
_client_lock = asyncio.Lock() if False else threading.Lock()


def _get_client() -> httpx.AsyncClient:
    """جلب الـ client المشترك أو إنشاءه إذا لم يكن موجوداً"""
    global _shared_client
    if _shared_client is None or _shared_client.is_closed:
        _shared_client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,   # وقت انتظار الاتصال
                read=40.0,      # وقت انتظار القراءة (أطول من poll timeout)
                write=15.0,     # وقت انتظار الكتابة
                pool=5.0,       # وقت انتظار الـ connection pool
            ),
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=30,
                keepalive_expiry=60.0,
            ),
            http2=False,
        )
    return _shared_client


async def _ensure_client() -> httpx.AsyncClient:
    """التأكد من أن الـ client جاهز (async-safe)"""
    global _shared_client
    if _shared_client is None or _shared_client.is_closed:
        _shared_client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,
                read=40.0,
                write=15.0,
                pool=5.0,
            ),
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=30,
                keepalive_expiry=60.0,
            ),
            http2=False,
        )
    return _shared_client


async def close_shared_client():
    """إغلاق الـ client المشترك عند الإيقاف"""
    global _shared_client
    if _shared_client and not _shared_client.is_closed:
        await _shared_client.aclose()
        _shared_client = None


async def bot_call(token: str, method: str, data: dict = None, timeout: float = 30.0) -> dict:
    """إرسال طلب POST لـ Telegram API باستخدام الـ client المشترك"""
    url = TELEGRAM_API.format(token=token, method=method)
    try:
        client = await _ensure_client()
        if data:
            resp = await client.post(url, data=data, timeout=timeout)
        else:
            resp = await client.get(url, timeout=timeout)
        return resp.json()
    except httpx.TimeoutException:
        return {"ok": False, "description": "timeout"}
    except (httpx.RemoteProtocolError, httpx.LocalProtocolError):
        global _shared_client
        _shared_client = None
        return {"ok": False, "description": "connection_error"}
    except Exception as e:
        _shared_client = None
        return {"ok": False, "description": str(e)}


async def bot_get(token: str, method: str, params: dict = None, timeout: float = 30.0) -> dict:
    """إرسال طلب GET لـ Telegram API باستخدام الـ client المشترك"""
    url = TELEGRAM_API.format(token=token, method=method)
    try:
        client = await _ensure_client()
        resp = await client.get(url, params=params, timeout=timeout)
        return resp.json()
    except httpx.TimeoutException:
        return {"ok": False, "description": "timeout"}
    except (httpx.RemoteProtocolError, httpx.LocalProtocolError):
        global _shared_client
        _shared_client = None
        return {"ok": False, "description": "connection_error"}
    except Exception as e:
        _shared_client = None
        return {"ok": False, "description": str(e)}


# ============================================================================
# نظام قاعدة البيانات - جميع العمليات مباشرة إلى SQLite بدون ملفات
# ============================================================================

_FS_LOCK = threading.RLock()


def ensure_dir(path: str) -> None:
    """no-op: قاعدة البيانات لا تحتاج مجلدات"""
    pass


def read_file(path: str, default: str = "") -> str:
    """قراءة نص مباشرة من قاعدة البيانات"""
    from db_config import db_read
    try:
        return db_read(path, default)
    except Exception as e:
        print(f"[DB] خطأ في قراءة '{path}': {e}")
        return default


def write_file(path: str, content: str) -> None:
    """كتابة نص مباشرة في قاعدة البيانات"""
    from db_config import db_write
    try:
        db_write(path, content)
    except Exception as e:
        print(f"[DB] خطأ في كتابة '{path}': {e}")


def append_file(path: str, content: str) -> None:
    """إضافة نص مباشرة في قاعدة البيانات"""
    from db_config import db_append
    try:
        db_append(path, content)
    except Exception as e:
        print(f"[DB] خطأ في الإضافة إلى '{path}': {e}")


def read_json(path: str, default: dict = None) -> dict:
    """قراءة JSON مباشرة من قاعدة البيانات"""
    from db_config import db_read_json
    if default is None:
        default = {}
    try:
        return db_read_json(path, default)
    except Exception as e:
        print(f"[DB] خطأ في قراءة JSON '{path}': {e}")
        return default


def write_json(path: str, data: dict) -> None:
    """كتابة JSON مباشرة في قاعدة البيانات"""
    from db_config import db_write_json
    try:
        db_write_json(path, data)
    except Exception as e:
        print(f"[DB] خطأ في كتابة JSON '{path}': {e}")


def file_lines(path: str) -> list:
    """قراءة أسطر مباشرة من قاعدة البيانات"""
    from db_config import db_lines
    try:
        return db_lines(path)
    except Exception as e:
        print(f"[DB] خطأ في قراءة أسطر '{path}': {e}")
        return []


def file_exists(path: str) -> bool:
    """التحقق من وجود البيانات في قاعدة البيانات فقط"""
    from db_config import db_exists
    try:
        return db_exists(path)
    except Exception:
        return False


def delete_file(path: str) -> None:
    """حذف المحتوى من قاعدة البيانات"""
    from db_config import db_delete
    try:
        db_delete(path)
    except Exception as e:
        print(f"[DB] خطأ في حذف '{path}': {e}")


def get_chat_member_status(response_text: str) -> str:
    if ('"status":"left"' in response_text
            or '"Bad Request:' in response_text
            or '"status":"kicked"' in response_text):
        return "no"
    return "yes"


async def check_member(token: str, channel_id: str, user_id) -> str:
    """التحقق من اشتراك المستخدم في قناة"""
    result = await bot_get(token, "getChatMember", {"chat_id": channel_id, "user_id": user_id})
    if not result.get("ok"):
        return "left"
    status = result.get("result", {}).get("status", "left")
    if status in ("left", "kicked"):
        return "no"
    return "yes"


async def get_chat_admins_ok(token: str, chat_id: str) -> bool:
    result = await bot_get(token, "getChatAdministrators", {"chat_id": chat_id})
    return result.get("ok", False)


def parse_update(body: bytes) -> dict:
    try:
        return json.loads(body)
    except Exception:
        return {}


def extract_update_fields(update: dict) -> dict:
    fields = {
        "message": None, "callback": None,
        "chat_id": None, "from_id": None, "message_id": None,
        "text": None, "data": None, "name": None, "user": None,
        "caption": None, "photo": None, "video": None,
        "document": None, "sticker": None, "voice": None, "audio": None,
        "forward_from_chat": None, "forward_from": None,
        "reply_to_message": None, "new_chat_members": None,
        "chat_type": None, "channel_post": None,
    }
    msg = update.get("message")
    cb  = update.get("callback_query")
    ch_post = update.get("channel_post")

    if msg:
        fields["message"]       = msg
        fields["chat_id"]       = msg.get("chat", {}).get("id")
        fields["from_id"]       = msg.get("from", {}).get("id")
        fields["message_id"]    = msg.get("message_id")
        fields["text"]          = msg.get("text", "")
        fields["caption"]       = msg.get("caption", "")
        fields["name"]          = msg.get("from", {}).get("first_name", "")
        fields["user"]          = msg.get("from", {}).get("username", "")
        fields["photo"]         = msg.get("photo")
        fields["video"]         = msg.get("video")
        fields["document"]      = msg.get("document")
        fields["sticker"]       = msg.get("sticker")
        fields["voice"]         = msg.get("voice")
        fields["audio"]         = msg.get("audio")
        fields["forward_from_chat"] = msg.get("forward_from_chat")
        fields["forward_from"]  = msg.get("forward_from")
        fields["reply_to_message"]  = msg.get("reply_to_message")
        fields["new_chat_members"]  = msg.get("new_chat_members")
        fields["chat_type"]     = msg.get("chat", {}).get("type")

    if cb:
        fields["callback"]   = cb
        fields["data"]       = cb.get("data", "")
        if not fields["chat_id"]:
            fields["chat_id"] = cb.get("message", {}).get("chat", {}).get("id")
        fields["from_id"]    = cb.get("from", {}).get("id")
        if not fields["message_id"]:
            fields["message_id"] = cb.get("message", {}).get("message_id")
        fields["name"]       = cb.get("from", {}).get("first_name", "")
        fields["user"]       = cb.get("from", {}).get("username", "")
        if not fields["text"]:
            fields["text"]   = ""

    if ch_post:
        fields["channel_post"] = ch_post

    return fields


# ══════════════════════════════════════════════════════════════════════════════
# دوال مساعدة للويب هوك والـ Polling
# ══════════════════════════════════════════════════════════════════════════════

async def delete_webhook(token: str) -> dict:
    """حذف الويب هوك - يجب استدعاؤها قبل بدء الـ Polling"""
    return await bot_get(token, "deleteWebhook", {"drop_pending_updates": False})


async def get_me(token: str) -> dict:
    """الحصول على معلومات البوت"""
    return await bot_get(token, "getMe")


# set_webhook محذوفة - المشروع يعمل على Polling فقط
# async def set_webhook(...) - تم حذفها عمداً


# ══════════════════════════════════════════════════════════════════════════════
# TelegramAPI - واجهة موحدة (تستخدم نفس الـ client المشترك)
# ══════════════════════════════════════════════════════════════════════════════

from dataclasses import dataclass, field


class TelegramAPI:
    """
    واجهة برمجة تطبيقات Telegram
    تستخدم الـ client المشترك في bot_helper للأداء المثالي
    """

    BASE_URL = "https://api.telegram.org"

    async def call(self, token: str, method: str, data: Dict = None,
                   timeout: float = 30.0) -> Dict:
        return await bot_call(token, method, data, timeout)

    async def get(self, token: str, method: str, params: Dict = None,
                  timeout: float = 30.0) -> Dict:
        return await bot_get(token, method, params, timeout)

    async def send_message(self, token: str, chat_id: int, text: str, **kwargs) -> Dict:
        data = {"chat_id": chat_id, "text": text, **kwargs}
        if "reply_markup" in data and isinstance(data["reply_markup"], (dict, list)):
            data["reply_markup"] = json.dumps(data["reply_markup"], ensure_ascii=False)
        return await self.call(token, "sendMessage", data)

    async def send_photo(self, token: str, chat_id: int, photo: str, **kwargs) -> Dict:
        return await self.call(token, "sendPhoto", {"chat_id": chat_id, "photo": photo, **kwargs})

    async def send_document(self, token: str, chat_id: int, document: str, **kwargs) -> Dict:
        return await self.call(token, "sendDocument", {"chat_id": chat_id, "document": document, **kwargs})

    async def edit_message(self, token: str, chat_id: int, message_id: int,
                           text: str, **kwargs) -> Dict:
        return await self.call(token, "editMessageText",
                               {"chat_id": chat_id, "message_id": message_id, "text": text, **kwargs})

    async def delete_message(self, token: str, chat_id: int, message_id: int) -> Dict:
        return await self.call(token, "deleteMessage",
                               {"chat_id": chat_id, "message_id": message_id})

    async def get_updates(self, token: str, offset: int = 0, timeout: int = 30) -> Dict:
        params = {"offset": offset, "timeout": timeout, "allowed_updates": []}
        return await self.get(token, "getUpdates", params, timeout=timeout + 10)

    async def get_chat_member(self, token: str, chat_id: str, user_id: int) -> Dict:
        return await self.get(token, "getChatMember", {"chat_id": chat_id, "user_id": user_id})

    async def forward_message(self, token: str, chat_id: int, from_chat_id: int,
                              message_id: int) -> Dict:
        return await self.call(token, "forwardMessage",
                               {"chat_id": chat_id, "from_chat_id": from_chat_id,
                                "message_id": message_id})

    async def get_me(self, token: str) -> Dict:
        return await self.get(token, "getMe", {})

    async def batch_send_messages(self, token: str, user_ids: list, text: str,
                                  batch_size: int = 50, delay: float = 0.1) -> Dict:
        results = {"success": 0, "failed": 0, "errors": []}
        for i in range(0, len(user_ids), batch_size):
            batch = user_ids[i:i + batch_size]
            for user_id in batch:
                try:
                    resp = await self.send_message(token, user_id, text, parse_mode="Markdown")
                    if resp.get("ok"):
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append({"user_id": user_id, "error": resp.get("description")})
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({"user_id": user_id, "error": str(e)})
                await asyncio.sleep(delay)
        return results


_telegram_api: Optional[TelegramAPI] = None


async def get_telegram_api() -> TelegramAPI:
    global _telegram_api
    if _telegram_api is None:
        _telegram_api = TelegramAPI()
    return _telegram_api


async def close_telegram_api():
    global _telegram_api
    _telegram_api = None
    await close_shared_client()


# ══════════════════════════════════════════════════════════════════════════════
# UpdateContext - سياق التحديث
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class UpdateContext:
    update_id: int
    timestamp: datetime
    user_id: int
    chat_id: int
    message_id: Optional[int] = None
    text: Optional[str] = None
    command: Optional[str] = None
    callback_data: Optional[str] = None
    message_type: str = "text"
    is_private: bool = True
    is_admin: bool = False
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    reply_to_id: Optional[int] = None
    forwarded: bool = False
    raw_update: Dict = field(default_factory=dict)


class EventProcessor:
    @staticmethod
    def extract_update_context(update: Dict, admin_ids: list = None) -> Optional[UpdateContext]:
        if admin_ids is None:
            admin_ids = []

        message  = update.get("message") or {}
        callback = update.get("callback_query") or {}

        if not message and not callback:
            return None

        if message:
            chat_id    = message.get("chat", {}).get("id")
            user_id    = message.get("from", {}).get("id")
            message_id = message.get("message_id")
            text       = message.get("text") or ""
            timestamp  = datetime.fromtimestamp(message.get("date", 0))
            is_private = message.get("chat", {}).get("type") == "private"
        else:
            chat_id    = callback.get("message", {}).get("chat", {}).get("id")
            user_id    = callback.get("from", {}).get("id")
            message_id = callback.get("message", {}).get("message_id")
            text       = ""
            timestamp  = datetime.now()
            is_private = True

        username   = (message.get("from", {}).get("username") or
                      callback.get("from", {}).get("username") or "").lower()
        first_name = (message.get("from", {}).get("first_name") or
                      callback.get("from", {}).get("first_name") or "")
        last_name  = (message.get("from", {}).get("last_name") or
                      callback.get("from", {}).get("last_name") or "")

        message_type = "text"
        if   message.get("photo"):    message_type = "photo"
        elif message.get("video"):    message_type = "video"
        elif message.get("document"): message_type = "document"
        elif message.get("voice"):    message_type = "voice"
        elif message.get("audio"):    message_type = "audio"
        elif message.get("sticker"):  message_type = "sticker"
        elif callback:                message_type = "callback"

        command      = None
        if text.startswith("/"):
            command  = text.split()[0][1:]

        callback_data = callback.get("data") if callback else None
        reply_to_id   = message.get("reply_to_message", {}).get("message_id") if message else None
        forwarded     = bool(message.get("forward_from")) if message else False

        return UpdateContext(
            update_id=update.get("update_id", 0),
            timestamp=timestamp,
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            command=command,
            callback_data=callback_data,
            message_type=message_type,
            is_private=is_private,
            is_admin=user_id in admin_ids,
            username=username,
            first_name=first_name,
            last_name=last_name,
            reply_to_id=reply_to_id,
            forwarded=forwarded,
            raw_update=update,
        )

    @staticmethod
    def should_process_update(context: UpdateContext, bot_status: str = "on") -> bool:
        if bot_status == "off" and not context.is_admin:
            return False
        if not context.text and not context.callback_data and context.message_type == "text":
            return False
        return True

    @staticmethod
    def format_log_entry(context: UpdateContext, action: str, details: str = None) -> Dict:
        return {
            "timestamp":    context.timestamp.isoformat(),
            "user_id":      context.user_id,
            "chat_id":      context.chat_id,
            "action":       action,
            "details":      details or "",
            "message_type": context.message_type,
            "is_admin":     context.is_admin,
        }


class CommandRouter:
    def __init__(self):
        self.commands         = {}
        self.callback_handlers = {}

    def register_command(self, cmd: str, handler):
        self.commands[cmd] = handler

    def register_callback(self, callback_prefix: str, handler):
        self.callback_handlers[callback_prefix] = handler

    async def route_command(self, context: UpdateContext) -> bool:
        if not context.command:
            return False
        handler = self.commands.get(context.command)
        if handler:
            return await handler(context)
        return False

    async def route_callback(self, context: UpdateContext) -> bool:
        if not context.callback_data:
            return False
        for prefix, handler in self.callback_handlers.items():
            if context.callback_data.startswith(prefix):
                return await handler(context)
        return False


class MessageProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        return text.strip() if text else ""

    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        import re
        return re.findall(r"#\w+", text)

    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        import re
        return re.findall(r"@[\w_]+", text)

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        import re
        pattern = (r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}'
                   r'\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)')
        return re.findall(pattern, text)

    @staticmethod
    def truncate_text(text: str, max_length: int = 4096) -> str:
        if len(text) > max_length:
            return text[:max_length - 3] + "..."
        return text
