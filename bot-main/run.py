#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت مصنع ناميرو - Polling Mode فقط
بدون أي Webhook
"""

import os
import sys
import asyncio
import signal
import re

# تأكد من المسار الصحيح - انتقل إلى مجلد bot-main
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import config
from bot_helper import bot_get, file_lines, file_exists, read_file, write_file
from db_config import get_config, set_config
from maker_handler import _run_polling as run_maker_polling
from saleh_handler import _run_polling as run_saleh_polling
from namero4_handler import _run_polling as run_namero4_polling

TOKEN = config.TOKEN.strip()

# قائمة مهام البوتات النشطة
_active_bot_tasks: dict = {}


def get_active_tasks() -> dict:
    return _active_bot_tasks


async def start_bot_polling(idbot: str) -> bool:
    """
    بدء polling لبوت مصنوع واحد.
    تُستدعى عند إنشاء بوت جديد أو عند الإقلاع.
    """
    global _active_bot_tasks

    bot_dir = f"botmak/{idbot}"
    token_path = f"{bot_dir}/token"
    admin_path = f"{bot_dir}/admin"

    # محاولة استعادة التوكن من NAMERO/{idbot}.py إذا غاب botmak/{idbot}/token
    if not file_exists(token_path):
        py_path = f"NAMERO/{idbot}.py"
        if file_exists(py_path):
            content = read_file(py_path)
            m = re.search(r'tokenbot\s*=\s*["\'](.+?)["\']', content)
            if m:
                write_file(token_path, m.group(1).strip())
                print(f"[Boot] ✅ استُعيد token لبوت {idbot}")
            else:
                print(f"[Boot] ⚠️  لا يمكن قراءة token من {py_path}")
                return False
        else:
            print(f"[Boot] ⚠️  لا يوجد token لبوت {idbot}")
            return False

    # محاولة استعادة admin من info إذا غاب
    if not file_exists(admin_path):
        info_path = f"{bot_dir}/info"
        if file_exists(info_path):
            lines = read_file(info_path).split("\n")
            if len(lines) > 4 and lines[4].strip():
                write_file(admin_path, lines[4].strip())
                print(f"[Boot] ✅ استُعيد admin لبوت {idbot}")
            else:
                print(f"[Boot] ⚠️  لا يوجد admin في info لبوت {idbot}")
                return False
        else:
            print(f"[Boot] ⚠️  لا يوجد admin لبوت {idbot}")
            return False

    # لا تكرر إذا كانت المهمة تعمل بالفعل
    if idbot in _active_bot_tasks and not _active_bot_tasks[idbot].done():
        return True

    # قراءة نوع البوت من ملف info
    info_path = f"{bot_dir}/info"
    bot_type = "SALEH"  # النوع الافتراضي
    if file_exists(info_path):
        try:
            content = read_file(info_path).strip()
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            # ابحث عن الخط الذي يحتوي على NAMERO4 أو SALEH
            for line in reversed(lines):
                if line == "NAMERO4":
                    bot_type = "NAMERO4"
                    break
                elif line == "SALEH":
                    bot_type = "SALEH"
                    break
        except Exception as e:
            print(f"[Boot] ⚠️  خطأ في قراءة نوع البوت: {e}")
    
    # استدعاء المعالج المناسب حسب نوع البوت
    if bot_type == "NAMERO4":
        task = asyncio.create_task(run_namero4_polling(bot_dir))
        print(f"[Boot] 🤖 بدء polling للبوت {idbot} (نوع: NAMERO4)")
    else:
        task = asyncio.create_task(run_saleh_polling(bot_dir))
        print(f"[Boot] 🤖 بدء polling للبوت {idbot} (نوع: SALEH)")
    
    _active_bot_tasks[idbot] = task
    return True


async def start_all_created_bots():
    """تشغيل polling لجميع البوتات المصنوعة الموجودة"""
    if not file_exists("infoidbots"):
        print("[Boot] ℹ️  لا توجد بوتات مصنوعة")
        return

    bots = [x for x in read_file("infoidbots").split("\n") if x.strip()]
    if not bots:
        print("[Boot] ℹ️  قائمة البوتات فارغة")
        return

    print(f"[Boot] 📋 تشغيل {len(bots)} بوت مصنوع...")
    started = 0
    for idbot in bots:
        ok = await start_bot_polling(idbot)
        if ok:
            started += 1

    print(f"[Boot] ✅ بدأ {started}/{len(bots)} بوت")


def _migrate_physical_files_to_db():
    """
    ترحيل تلقائي لمرة واحدة: قراءة الملفات الفيزيائية الموجودة وحفظها في قاعدة البيانات.
    بعد الترحيل لا يُلمس أي ملف فيزيائي أبداً.
    """
    from db_config import db_write, db_write_json, db_lines, db_exists
    import os as _os

    if get_config("files_migrated_v1") == "true":
        return

    migrated = 0

    def _migrate_text(path: str):
        nonlocal migrated
        if _os.path.isfile(path) and not db_exists(path):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    db_write(path, f.read())
                migrated += 1
            except Exception as e:
                print(f"[Migrate] خطأ في ترحيل '{path}': {e}")

    def _migrate_json(path: str):
        nonlocal migrated
        if _os.path.isfile(path) and not db_exists(path):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    import json as _json
                    data = _json.load(f)
                    db_write_json(path, data)
                migrated += 1
            except Exception as e:
                print(f"[Migrate] خطأ في ترحيل JSON '{path}': {e}")

    # ─── ملفات الجذر ──────────────────────────────────────────────────
    for txt_path in ("NaMero/member", "NaMero/ban", "infoidbots", "botfreeid",
                     "namero_admins", "base_url"):
        _migrate_text(txt_path)

    for json_path in ("NaMeroData", "botmak/NAMERO", "code", "datatime"):
        _migrate_json(json_path)

    # ─── ملفات كل بوت مصنوع ──────────────────────────────────────────
    botmak_root = "botmak"
    if _os.path.isdir(botmak_root):
        for bot_id in _os.listdir(botmak_root):
            bot_dir = _os.path.join(botmak_root, bot_id)
            if not _os.path.isdir(bot_dir):
                continue

            # zune (الإعدادات الرئيسية للبوت)
            _migrate_json(_os.path.join(bot_dir, "zune"))

            # ملفات نصية داخل مجلد البوت
            for txt_file in ("token", "admin", "allUser", "sudo", "setting",
                             "message", "countinfo", "datalogs"):
                _migrate_text(_os.path.join(bot_dir, txt_file))

            # NaMero/member و NaMero/ban الخاصة بالبوت
            namero_dir = _os.path.join(bot_dir, "NaMero")
            if _os.path.isdir(namero_dir):
                _migrate_text(_os.path.join(namero_dir, "member"))
                _migrate_text(_os.path.join(namero_dir, "ban"))

            # count/
            count_dir = _os.path.join(bot_dir, "count")
            if _os.path.isdir(count_dir):
                for root, dirs, files in _os.walk(count_dir):
                    for fname in files:
                        _migrate_text(_os.path.join(root, fname))

    set_config("files_migrated_v1", "true")
    print(f"[Migrate] ✅ تم ترحيل {migrated} ملف إلى قاعدة البيانات")


def _init_db():
    """تهيئة قاعدة البيانات بالقيم الافتراضية — بدون أي ملفات فيزيائية"""
    # فقط نتأكد أن مجلد db موجود للـ SQLite نفسه
    import os as _os
    _os.makedirs("db", exist_ok=True)

    # القيم الافتراضية في system_config
    defaults = {
        "saleh_admin": str(config.DEVELOPER_ID),
        "userbot":     getattr(config, "USER_BOT_NAMERO", ""),
        "xx":          getattr(config, "XX", config.DEVELOPER_USERNAME),
        "xxx":         getattr(config, "XXX", ""),
        "base_url":    getattr(config, "BASE_URL", ""),
    }
    for key, val in defaults.items():
        if not get_config(key):
            set_config(key, val)
            print(f"[DB] ✅ تم تعيين {key}: {val[:20] if val else ''}")

    # القيم الافتراضية في content_storage (بديل الملفات النصية)
    from db_config import db_exists, db_write, db_write_json
    text_defaults = {
        "NaMero/member": "",
        "NaMero/ban":    "",
        "infoidbots":    "",
        "botfreeid":     "",
    }
    for path, val in text_defaults.items():
        if not db_exists(path):
            db_write(path, val)

    json_defaults = {
        "NaMeroData": {
            "info": {
                "update": "✅",
                "propots": "مجانية",
                "fwrmember": "❌",
                "tnbih": "✅",
                "silk": "✅",
                "allch": "error",
                "updatechannel": "Voltees",
                "klish_sil": "• عذراً عزيزي عليك الاشتراك في قناة المصنع أولاً 🪢\n\n🌴 اشترك ثم أرسل /start"
            }
        },
        "botmak/NAMERO": {"info": {"st_ch_bots": "❌", "user_bot": "Voltees"}},
        "code":          {},
        "datatime":      {},
    }
    for path, val in json_defaults.items():
        if not db_exists(path):
            db_write_json(path, val)


async def main():
    # 1. إنشاء مجلد DB وتهيئة قاعدة البيانات بالقيم الافتراضية
    _init_db()
    # 2. ترحيل الملفات الفيزيائية القديمة لمرة واحدة فقط
    _migrate_physical_files_to_db()

    print("=" * 55)
    print("  NaMero Bot Factory — Polling Mode")
    print("  by @Voltees")
    print("=" * 55)
    print(f"✅ التوكن: {TOKEN[:10]}...{TOKEN[-8:]}")

    # اختبار الاتصال
    result = await bot_get(TOKEN, "getMe")
    if not result.get("ok"):
        print(f"❌ فشل الاتصال: {result.get('description')}")
        sys.exit(1)

    bot_info = result["result"]
    bot_username = bot_info.get("username", "")
    print(f"✅ البوت: @{bot_username} | {bot_info.get('first_name')}")
    print(f"🔄 وضع Polling فقط - بدون Webhook")
    print("=" * 55)

    # حفظ اسم البوت في قاعدة البيانات (يُستخدم بدلاً من ملف userbot)
    if bot_username:
        set_config("userbot", bot_username)
        print(f"[DB] ✅ تم تحديث userbot: {bot_username}")

    # حذف أي webhook موجود على البوت الرئيسي
    dw = await bot_get(TOKEN, "deleteWebhook", {"drop_pending_updates": "false"})
    if dw.get("ok"):
        print("✅ تم حذف Webhook من البوت الرئيسي")

    # تشغيل البوتات المصنوعة في الخلفية
    asyncio.create_task(start_all_created_bots())

    # تشغيل البوت الرئيسي (Maker) - هذا يبقى يعمل
    await run_maker_polling()


if __name__ == "__main__":
    def _stop(sig, frame):
        print(f"\n🛑 إيقاف البوت...")
        sys.exit(0)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    asyncio.run(main())
