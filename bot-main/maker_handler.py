import os
import json
import re
import secrets
import string
import shutil
import asyncio
import signal
from datetime import datetime, timezone, timedelta
import config
from bot_helper import (
    bot_call, bot_get, read_file, write_file, append_file,
    read_json, write_json, file_lines, ensure_dir, file_exists,
    delete_file, check_member, get_chat_admins_ok, extract_update_fields
)
from saleh_handler import _run_polling as _run_saleh_polling
from db_config import get_config, set_config

TOKEN = config.TOKEN

# تتبع tasks البوتات التي أنشأها الصانع — يمنع إنشاء task مكررة لنفس البوت
_maker_active_tasks: dict = {}

def _load_namero_admins() -> list:
    """تحميل قائمة الأدمنية من config.py + ملف namero_admins إن وُجد"""
    admins = set(str(x) for x in config.ADMIN_IDS if x)
    # دعم ملف namero_admins القديم للتوافق مع البيانات الموجودة
    raw = read_file("namero_admins", "").strip()
    if raw:
        for line in raw.split("\n"):
            line = line.strip()
            if line and line.isdigit():
                admins.add(line)
    return list(admins)


USER_BOT_NAMERO = get_config("userbot", getattr(config, "USER_BOT_NAMERO", ""))
XX              = get_config("xx",      getattr(config, "XX",              config.DEVELOPER_USERNAME))
XXX             = get_config("xxx",     getattr(config, "XXX",             ""))
SALEH_ADMIN     = get_config("saleh_admin", str(config.DEVELOPER_ID))
BASE_URL        = get_config("base_url",    getattr(config, "BASE_URL",    ""))
NAMERO_ADMINS   = _load_namero_admins()
UPDATE_CHANNEL  = ""

BOTS_LIST = {
    1: "بوت تواصل ",
}

def reload_config():
    """إعادة تحميل الإعدادات من قاعدة البيانات وconfig.py"""
    global TOKEN, USER_BOT_NAMERO, XX, XXX, SALEH_ADMIN, NAMERO_ADMINS, BASE_URL, UPDATE_CHANNEL
    TOKEN           = config.TOKEN
    USER_BOT_NAMERO = get_config("userbot",     getattr(config, "USER_BOT_NAMERO", ""))
    XX              = get_config("xx",          getattr(config, "XX",              config.DEVELOPER_USERNAME))
    XXX             = get_config("xxx",         getattr(config, "XXX",             ""))
    SALEH_ADMIN     = get_config("saleh_admin", str(config.DEVELOPER_ID))
    BASE_URL        = get_config("base_url",    getattr(config, "BASE_URL",        ""))
    NAMERO_ADMINS   = _load_namero_admins()

def get_token():
    return TOKEN

def get_namero_admins():
    return NAMERO_ADMINS

def get_base_url():
    return BASE_URL

def get_saleh_admin():
    return SALEH_ADMIN

def get_update_channel():
    return UPDATE_CHANNEL

def remove_dir(path: str):
    try:
        for entry in os.scandir(path):
            if entry.name in ('.', '..', 'NaMero', 'pro'):
                continue
            if entry.is_file():
                os.unlink(entry.path)
            elif entry.is_dir():
                remove_dir(entry.path)
        os.rmdir(path)
    except:
        pass


async def send_namero_async(token, chat_id, message_id):
    """لوحة تحكم المصنع الرئيسية - sendNAMERO من PHP"""
    info = read_json("NaMeroData", {})
    updatenew = info.get("info", {}).get("update", "✅")
    fwrmember = info.get("info", {}).get("fwrmember", "❌")
    tnbih = info.get("info", {}).get("tnbih", "✅")

    member = file_lines("NaMero/member")
    cunte = len(member)
    ban = [x for x in read_file("NaMero/ban").split("\n") if x]
    countban = len(ban)
    countban_str = "لايوجد محظورين" if countban <= 0 else str(countban)

    infoidbots = file_lines("infoidbots") if file_exists("infoidbots") else []
    countbots = len(infoidbots)
    countbots_str = "لايوجد بوتات مصنوعة" if countbots <= 0 else str(countbots)

    await bot_call(token, "editMessageText", {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": f"اهلا بك في لوحه تحكم المصنع  VOLT  ↕️\n----------------------------\n• عدد الاعضاء : {cunte}\n• المحظورين: {countban_str}\n• البوتات المصنوعة : {countbots_str}\n",
        "disable_web_page_preview": "true",
        "reply_markup": json.dumps({"inline_keyboard": [
            [{"text": f"توجيه الرسائل :{fwrmember}", "callback_data": "fwrmember"}],
            [{"text": f" عمل البوت : {updatenew}", "callback_data": "updatenew"}, {"text": f"اشعارات الدخول: {tnbih}", "callback_data": "tnbih"}],
            [{"text": "رساله الترحيب (start) ", "callback_data": "start"}],
            [{"text": " قسم الادمنية ", "callback_data": "admins"}, {"text": " قسم الاذاعة ", "callback_data": "sendmessage"}],
            [{"text": "قسم الاشتراك الاجباري ", "callback_data": "الاجباري"}, {"text": "قسم الاحصائيات ", "callback_data": "ahsre"}],
            [{"text": " • لوحه تحكم الصانع • ", "callback_data": "Mak3"}],
        ]})
    })


async def send_NAMERO_maker_async(token, chat_id, message_id):
    """لوحة تحكم الصانع - send_NAMERO من PHP"""
    namero_x = read_json("botmak/NAMERO", {})
    st_ch_bots = namero_x.get("info", {}).get("st_ch_bots", "❌")
    info = read_json("NaMeroData", {})
    propots = info.get("info", {}).get("propots", "مجانية")

    await bot_call(token, "editMessageText", {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": "- اهلا بك في لوحه الأدمن الخاصه بالبوت 🌀\n----------------------------\n• تحكم في اعدادت الصانع من الاسفل ➕\n",
        "parse_mode": "MarkDown",
        "reply_markup": json.dumps({"inline_keyboard": [
            [{"text": " معلومات اكثر عن بوت", "callback_data": "info_kl"}, {"text": " تعين المطور ", "callback_data": "NaMero"}],
            [{"text": f"الإشتراك الاجباري لكل البوتات : {st_ch_bots} ", "callback_data": "st_ch_bots"}],
            [{"text": "الاشتراك للبوتات 1", "callback_data": "channelbots"}, {"text": "الاشتراك للبوتات 2", "callback_data": "channelbots2"}],
            [{"text": "ضبط قناةتحديثات ", "callback_data": "updatechannel"}],
            [{"text": "اشتراك مدفوع", "callback_data": "delprobot"}, {"text": "اضافة اشتراك مدفوع", "callback_data": "addprobot"}],
            [{"text": f"البوتات المصنوعة : {propots}", "callback_data": "propots"}],
            [{"text": "تعيين كليشة ارسال التوكن", "callback_data": "token_kl"}],
            [{"text": "رجوع ", "callback_data": "home"}],
        ]})
    })


async def send_NNNAMERO_async(token, chat_id, message_id):
    """لوحة تحكم الاشتراك الاجباري - sendNNAMERO من PHP"""
    info = read_json("NaMeroData", {})
    silk = info.get("info", {}).get("silk", "✅")
    await bot_call(token, "editMessageText", {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": "• *لوحه تحكم الاشتراك الاجباري 📬*",
        "parse_mode": "markdown",
        "disable_web_page_preview": "true",
        "reply_markup": json.dumps({"inline_keyboard": [
            [{"text": " جميع القنوات ", "callback_data": "viwechannel"}],
            [{"text": "مسح قناة", "callback_data": "delchannel"}, {"text": "إضافة قناة", "callback_data": "addchannel"}],
            [{"text": "كليشه الاشتراك الاجباري ", "callback_data": "klish_sil"}],
            [{"text": f"عرض الاشتراك الاجباري ازرار : {silk} ", "callback_data": "silk"}],
            [{"text": "رجوع .", "callback_data": "home"}],
        ]})
    })


async def handle_maker(body: bytes, request_host: str = None) -> dict:
    update = json.loads(body)
    token = get_token()
    namero_admins = get_namero_admins()
    saleh_admin = get_saleh_admin()
    base_url = get_base_url()
    update_channel = get_update_channel()

    f = extract_update_fields(update)
    msg = f["message"]
    cb = update.get("callback_query")

    chat_id = f["chat_id"]
    from_id = f["from_id"]
    message_id = f["message_id"]
    text = f["text"] or ""
    data = f["data"] or ""
    name = f["name"] or ""
    user = f["user"] or ""
    caption = f["caption"] or ""
    photo = f["photo"]
    video = f["video"]
    document = f["document"]
    sticker = f["sticker"]
    voice = f["voice"]
    audio = f["audio"]
    forward_from_chat = f["forward_from_chat"]

    if not chat_id:
        return {"ok": True}

    ensure_dir("NaMero")
    ensure_dir("data")
    ensure_dir("botmak")
    ensure_dir("user")

    if not file_exists("NaMero/member"):
        write_file("NaMero/member", "")
    if not file_exists("NaMero/ban"):
        write_file("NaMero/ban", "")

    get_ban = read_file("NaMero/ban")
    ban = [x for x in get_ban.split("\n") if x]
    member = file_lines("NaMero/member")
    cunte = len(member)

    namero_x = read_json("botmak/NAMERO", {})
    if not namero_x.get("info"):
        namero_x["info"] = {"st_ch_bots": "❌", "user_bot": USER_BOT_NAMERO}
        write_json("botmak/NAMERO", namero_x)

    st_ch_bots = namero_x.get("info", {}).get("st_ch_bots", "❌")
    id_ch_namero = namero_x.get("info", {}).get("id_channel", "")
    link_ch_namero = namero_x.get("info", {}).get("link_channel", "")
    user_bot_namero = namero_x.get("info", {}).get("user_bot", USER_BOT_NAMERO)

    info_namero = read_json("NaMeroData", {})
    if not info_namero.get("info"):
        info_namero["info"] = {
            "update": "✅", "propots": "مجانية", "fwrmember": "❌",
            "tnbih": "✅", "silk": "✅", "allch": "error",
            "klish_sil": "• عزرا عزيزي عليك الاشتراك في قناه مصنع المبرمج ناميرو لتتمكن من فتح البوت 🪢\n\n🌴- اشترك ثم ارسل /start"
        }
        write_json("NaMeroData", info_namero)

    updatenew = info_namero.get("info", {}).get("update", "✅")
    propots = info_namero.get("info", {}).get("propots", "مجانية")
    fwrmember = info_namero.get("info", {}).get("fwrmember", "❌")
    tnbih = info_namero.get("info", {}).get("tnbih", "✅")
    silk = info_namero.get("info", {}).get("silk", "✅")
    allch = info_namero.get("info", {}).get("allch", "error")
    start_msg = info_namero.get("info", {}).get("start", "")
    klish_sil = info_namero.get("info", {}).get("klish_sil", "")
    update_channel = info_namero.get("info", {}).get("updatechannel", "Voltees")
    admins_list = info_namero.get("info", {}).get("admins", [])
    info_kl = info_namero.get("info", {}).get("info_kl", "")
    token_kl = info_namero.get("info", {}).get("token_kl", "")

    if not file_exists("infoidbots"):
        write_file("infoidbots", "")
    if not file_exists("botfreeid"):
        write_file("botfreeid", "")
    if not file_exists("code"):
        write_json("code", {})
    if not file_exists("datatime"):
        write_json("datatime", {})

    infoidbots = file_lines("infoidbots")
    countbots = len(infoidbots)
    countbots_str = "لايوجد بوتات مصنوعة" if countbots <= 0 else str(countbots)
    countban = len(ban)
    countban_str = "لايوجد محظورين" if countban <= 0 else str(countban)

    is_namero_admin = str(from_id) in namero_admins
    is_admin_or_sudo = is_namero_admin or str(from_id) in [str(x) for x in admins_list]

    # --- تحديث البوت ---
    if text == "تحديث":
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "\nتم تحديث البوت بنجاح \n", "reply_to_message_id": message_id})
        return {"ok": True}

    # --- وضع التحديث ---
    if msg and updatenew == "❌" and not is_namero_admin:
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "البوت قيد التحديث الرجاء الانتظار حتى يتم الانتهاء من التحديث 🥺", "reply_to_message_id": message_id})
        return {"ok": True}

    # --- فحص الاشتراك الاجباري ---
    if msg:
        if allch != "مفردة":
            channels = info_namero.get("info", {}).get("channel", {})
            keyboard = {"inline_keyboard": []}
            show_sub_msg = False
            sub_text = ""
            for ch_id, ch_data in channels.items():
                ch_name = ch_data.get("name")
                ch_st = ch_data.get("st")
                ch_user = ch_data.get("user", "").replace("@", "")
                if ch_name:
                    status = await check_member(token, ch_id, from_id)
                    if status == "no":
                        if ch_st == "عامة":
                            url = f"t.me/{ch_user}"
                        else:
                            url = ch_data.get("user", "")
                        if silk == "✅":
                            keyboard["inline_keyboard"].append([{"text": ch_name, "url": url}])
                        else:
                            sub_text += "\n" + ch_data.get("user", "")
                        show_sub_msg = True
            if show_sub_msg:
                await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"{klish_sil}\n{sub_text}", "disable_web_page_preview": "true", "reply_markup": json.dumps(keyboard)})
                return {"ok": True}
        else:
            channels = info_namero.get("info", {}).get("channel", {})
            for ch_id, ch_data in channels.items():
                ch_name = ch_data.get("name")
                ch_st = ch_data.get("st")
                ch_user = ch_data.get("user", "").replace("@", "")
                if ch_name:
                    status = await check_member(token, ch_id, from_id)
                    if status == "no":
                        keyboard = {"inline_keyboard": []}
                        if ch_st == "عامة":
                            url = f"t.me/{ch_user}"
                            tt = ch_data.get("user", "")
                        else:
                            url = ch_data.get("user", "")
                            tt = ch_data.get("user", "")
                        if silk == "✅":
                            keyboard["inline_keyboard"].append([{"text": ch_name, "url": url}])
                        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"{klish_sil}\n{tt}\n", "disable_web_page_preview": "true", "reply_markup": json.dumps(keyboard)})
                        return {"ok": True}

    # --- تسجيل الأعضاء الجدد ---
    if (msg or cb) and str(from_id) not in member:
        append_file("NaMero/member", f"{from_id}\n")
        member.append(str(from_id))
        cunte = len(member)
        if tnbih == "✅" and is_namero_admin is False:
            await bot_call(token, "sendMessage", {
                "chat_id": saleh_admin,
                "text": f"- دخل شخص إلى البوت 👥\n----------------------------\n• الاسم: [{name}](tg://user?id={from_id}) \n• ايديه {from_id} \n• معرفة : {user}\n\n- عدد اعضاء بوتك هو : {cunte}\n",
                "disable_web_page_preview": "true",
                "parse_mode": "markdown"
            })

    # --- فحص الحظر ---
    if str(from_id) in ban:
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "❌ لا تستطيع استخدام البوت انت محظور ❌"})
        return {"ok": True}

    # --- إنشاء مجلدات المستخدم ---
    ensure_dir(f"from_id/{from_id}")
    if not file_exists(f"from_id/{from_id}/amr"):
        write_file(f"from_id/{from_id}/amr", "")
    if not file_exists(f"from_id/{from_id}/countbot"):
        write_file(f"from_id/{from_id}/countbot", "")
    if not file_exists(f"from_id/{from_id}/countuserbot"):
        write_file(f"from_id/{from_id}/countuserbot", "")
    if not file_exists(f"from_id/{from_id}/idbot"):
        write_file(f"from_id/{from_id}/idbot", "")

    amr_mem = read_file(f"from_id/{from_id}/amr").strip()

    if not start_msg:
        start_msg = "• مرحبا بك عزيزي في مصنع بوتات فولت (Volt) ⚡️\n\n- اصنع العديد من البوتات بكل سهوله من الاسفل 🔥"
    if not info_kl:
        info_kl = "• مرحبا بك عزيزي في مصنع بوتات فولت (Volt) ⚡️\n\n- اصنع العديد من البوتات بكل سهوله من الاسفل 🔥\n\n- البوتات بدون حقوق اعلانات مزعجه 👍\n\n- تابع قناتنا من هنا: @Voltees 🎉"
    if not token_kl:
        token_kl = "• أرسل التوكن الخاص بك الآن لصنع بوت \n خاص بك :\n- إذا كنت لا تعلم كيف يمكنك الحصول على توكن اضغط على زر شرح صنع توكن خاص بك\n"

    # =============================================================
    # أوامر لوحة تحكم المصنع (للأدمن الرئيسي فقط)
    # =============================================================

    # --- /start للأدمن الرئيسي ---
    if text == "/start" and is_namero_admin:
        await bot_call(token, "sendMessage", {
            "chat_id": chat_id,
            "text": f"اهلا بك في لوحه تحكم المصنع للمبرمج ناميرو ↕️\n----------------------------\n• عدد الاعضاء : {cunte}\n• المحظورين: {countban_str}\n• البوتات المصنوعة : {countbots_str}\n",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": f"توجيه الرسائل :{fwrmember}", "callback_data": "fwrmember"}],
                [{"text": f" عمل البوت : {updatenew}", "callback_data": "updatenew"}, {"text": f"اشعارات الدخول: {tnbih}", "callback_data": "tnbih"}],
                [{"text": "رساله الترحيب (start) ", "callback_data": "start"}],
                [{"text": " قسم الادمنية ", "callback_data": "admins"}, {"text": " قسم الاذاعة ", "callback_data": "sendmessage"}],
                [{"text": "قسم الاشتراك الاجباري ", "callback_data": "الاجباري"}, {"text": "قسم الاحصائيات ", "callback_data": "ahsre"}],
                [{"text": " • لوحه تحكم الصانع • ", "callback_data": "Mak3"}],
            ]})
        })
        return {"ok": True}

    # --- home ---
    if data == "home" and is_admin_or_sudo:
        await bot_call(token, "answerCallbackQuery", {"callback_query_id": cb.get("id", "") if cb else "", "text": "✓"})
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "null"
        write_json("NaMeroData", info_namero)
        await send_namero_async(token, chat_id, message_id)
        return {"ok": True}

    # --- الاجباري ---
    if data == "الاجباري" and is_admin_or_sudo:
        await send_NNNAMERO_async(token, chat_id, message_id)
        return {"ok": True}

    # --- احصائيات ---
    if data == "ahsre" and is_admin_or_sudo:
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": f"*اليك احصائيات بوتك🔥:*\n\nعدد المشتركين الكلي : * {cunte}*\nالمحظورين منهم : *{countban_str}*\nالوهمين منهم : *لايوجد .*\nالمشتركين النشطين : *{max(cunte - countban, 0)}*\n• عدد الاعضاء : {cunte}\n• المحظورين: {countban_str}\n• البوتات المصنوعة :{countbots_str}\n",
            "parse_mode": "markdown",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "رجوع .", "callback_data": "home"}]]})
        })
        return {"ok": True}

    # --- تبديل عمل البوت (updatenew) ---
    if data == "updatenew" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        join = info_namero.get("info", {}).get("update", "✅")
        info_namero["info"]["update"] = "❌" if join == "✅" else "✅"
        write_json("NaMeroData", info_namero)
        await send_namero_async(token, chat_id, message_id)
        return {"ok": True}

    # --- تبديل اشعارات الدخول (tnbih) ---
    if data == "tnbih" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        join = info_namero.get("info", {}).get("tnbih", "✅")
        info_namero["info"]["tnbih"] = "❌" if join == "✅" else "✅"
        write_json("NaMeroData", info_namero)
        await send_namero_async(token, chat_id, message_id)
        return {"ok": True}

    # --- تبديل توجيه الرسائل (fwrmember) ---
    if data == "fwrmember" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        fw = info_namero.get("info", {}).get("fwrmember", "❌")
        info_namero["info"]["fwrmember"] = "✅" if fw == "❌" else "❌"
        write_json("NaMeroData", info_namero)
        await send_namero_async(token, chat_id, message_id)
        return {"ok": True}

    # --- تبديل ازرار الاشتراك الاجباري (silk) ---
    if data == "silk" and is_admin_or_sudo:
        info_namero = read_json("NaMeroData", {})
        skil = info_namero.get("info", {}).get("silk", "✅")
        info_namero["info"]["silk"] = "❌" if skil == "✅" else "✅"
        write_json("NaMeroData", info_namero)
        await send_NNNAMERO_async(token, chat_id, message_id)
        return {"ok": True}

    # --- تبديل نشر الكل (allch) ---
    if data == "allch" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        allch_val = info_namero.get("info", {}).get("allch", "مجموعة")
        info_namero["info"]["allch"] = "مجموعة" if allch_val == "مفردة" else "مفردة"
        write_json("NaMeroData", info_namero)
        await send_namero_async(token, chat_id, message_id)
        return {"ok": True}

    if data == "allchs" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        allch_val = info_namero.get("info", {}).get("allch", "مجموعة")
        info_namero["info"]["allch"] = "مجموعة" if allch_val == "مفردة" else "مفردة"
        write_json("NaMeroData", info_namero)
        await send_namero_async(token, chat_id, message_id)
        return {"ok": True}

    # =============================================================
    # لوحة تحكم الصانع (Mak3)
    # =============================================================

    if data == "Mak3" and is_namero_admin:
        await send_NAMERO_maker_async(token, chat_id, message_id)
        return {"ok": True}

    # --- تبديل الاشتراك الاجباري لكل البوتات (st_ch_bots) ---
    if data == "st_ch_bots" and is_namero_admin:
        namero_x = read_json("botmak/NAMERO", {})
        join = namero_x.get("info", {}).get("st_ch_bots", "❌")
        namero_x["info"]["st_ch_bots"] = "❌" if join == "✅" else "✅"
        write_json("botmak/NAMERO", namero_x)
        await send_NAMERO_maker_async(token, chat_id, message_id)
        return {"ok": True}

    # --- تبديل البوتات مجانية/مدفوعة (propots) ---
    if data == "propots" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        join = info_namero.get("info", {}).get("propots", "مجانية")
        info_namero["info"]["propots"] = "مدفوعة" if join == "مجانية" else "مجانية"
        write_json("NaMeroData", info_namero)
        await send_NAMERO_maker_async(token, chat_id, message_id)
        return {"ok": True}

    # --- ضبط قناة التحديثات ---
    if data == "updatechannel" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "updatechannel"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "- قم بارسال الرابط الخاص لقناة التحديثات \n",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if text and text != "/start" and not data and msg and is_namero_admin:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "updatechannel":
            tex = text.replace("https://t.me/joinchat/", "").replace("http://t.me/joinchat/", "")
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            info_namero["info"]["updatechannel"] = tex
            write_json("NaMeroData", info_namero)
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": f"- ✅ تم حفظ الرابط الخاص لقناة التحديثات 📬\n----------------------------\n-الرابط : \n{text} ",
                "disable_web_page_preview": "true",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "home"}]]})
            })
            return {"ok": True}

    # --- رسالة start ---
    if data == "start" and is_admin_or_sudo:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "start"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "- قم بارسال نص رسالة /start\n",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if text and text != "/start" and not data and msg:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "start" and is_namero_admin:
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            info_namero["info"]["start"] = text
            write_json("NaMeroData", info_namero)
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": f"- ✅ تم حفظ كليشة /start \n-الكليشة : \n----------------------------\n{text} ",
                "disable_web_page_preview": "true",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "home"}]]})
            })
            return {"ok": True}

    # --- كليشة معلومات عن البوت ---
    if data == "info_kl" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "info_kl"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "- قم بارسال نص كليشة معلومات عن البوت\n",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if text and text != "/start" and not data and msg:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "info_kl" and is_namero_admin:
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            info_namero["info"]["info_kl"] = text
            write_json("NaMeroData", info_namero)
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": f"- ✅ تم حفظ كليشة معلومات عن البوت \n-الكليشة : \n{text} ",
                "disable_web_page_preview": "true",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "Mak3"}]]})
            })
            return {"ok": True}

    # --- كليشة ارسال التوكن ---
    if data == "token_kl" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "token_kl"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "- قم بارسال نص كليشة إرسال التوكن",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if text and text != "/start" and not data and msg:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "token_kl" and is_namero_admin:
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            info_namero["info"]["token_kl"] = text
            write_json("NaMeroData", info_namero)
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": f"- ✅ تم حفظ كليشة إرسال التوكن\n-الكليشة : \n{text} ",
                "disable_web_page_preview": "true",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "home"}]]})
            })
            return {"ok": True}

    # --- كليشة الاشتراك الاجباري ---
    if data == "klish_sil" and is_admin_or_sudo:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "klish_sil"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "- قم بارسال كليشة الاشتراك الاجباريي \n",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if text and text != "/start" and not data and msg:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "klish_sil" and is_namero_admin:
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            info_namero["info"]["klish_sil"] = text
            write_json("NaMeroData", info_namero)
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": f"- ✅ تم حفظ كليشة الاشتراك الاجباري \n-الكليشة : \n{text} ",
                "disable_web_page_preview": "true",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "home"}]]})
            })
            return {"ok": True}

    # --- تعيين المطور ---
    if data == "NaMero" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "NaMero"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "- قم بارسالايدي حساب المطور ",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if text and text != "/start" and not data and msg:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "NaMero" and is_namero_admin:
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            info_namero["info"]["NaMero"] = text
            write_json("NaMeroData", info_namero)
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": f"- ✅ تم حفظ حساب المطور\n-الحساب : \n{text} ",
                "disable_web_page_preview": "true",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "home"}]]})
            })
            return {"ok": True}

    # =============================================================
    # قسم الحظر
    # =============================================================

    if data == "ban" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "ban"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "- قم بارسال أيدي العضو لحظره",
            "parse_mode": "Markdown",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if text and text != "/start" and not data and msg and text.isdigit() and is_namero_admin:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "ban":
            ban_list = [x for x in read_file("NaMero/ban").split("\n") if x]
            if text not in ban_list:
                append_file("NaMero/ban", f"{text}\n")
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": f"- ✅ تم حظر العضو بنجاح \n{text}",
                    "disable_web_page_preview": "true",
                    "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "home"}]]})
                })
                await bot_call(token, "sendMessage", {"chat_id": text, "text": "❌ لقد قام الادمن بحظرك من استخدام البوت"})
            else:
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": "🚫 العضو محظور مسبقاً",
                    "disable_web_page_preview": "true",
                    "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "home"}]]})
                })
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            write_json("NaMeroData", info_namero)
            return {"ok": True}

    if data == "unban" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "unban"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "- قم بارسال أيدي العضو للإلغاء الحظر عنه",
            "parse_mode": "Markdown",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if text and text != "/start" and not data and msg and text.isdigit() and is_namero_admin:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "unban":
            ban_list = [x for x in read_file("NaMero/ban").split("\n") if x]
            if text in ban_list:
                ban_content = read_file("NaMero/ban").replace(f"{text}\n", "")
                write_file("NaMero/ban", ban_content)
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": f"- ✅ تم الغاء حظر العضو بنجاح \n{text}",
                    "disable_web_page_preview": "true",
                    "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "home"}]]})
                })
                await bot_call(token, "sendMessage", {"chat_id": text, "text": "✅ لقد قام الادمن بالغاء الحظر عنك."})
            else:
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": "🚫 العضو ليسِ محظور مسبقاً",
                    "disable_web_page_preview": "true",
                    "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "home"}]]})
                })
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            write_json("NaMeroData", info_namero)
            return {"ok": True}

    if data == "unbanall" and is_namero_admin:
        if countban > 0:
            write_file("NaMero/ban", "")
            await bot_call(token, "editMessageText", {
                "chat_id": chat_id, "message_id": message_id,
                "text": "- ✅ تم مسح قائمة المحظورين بنجاح ",
                "disable_web_page_preview": "true",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
            })
        else:
            await bot_call(token, "answerCallbackQuery", {
                "callback_query_id": cb.get("id", "") if cb else "",
                "text": "0 ",
                "show_alert": "true"
            })
        return {"ok": True}

    # =============================================================
    # قسم الاشتراك المدفوع
    # =============================================================

    if data == "delprobot" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "delprobot"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "ℹ حذف اشتراك مدفوع : \nقم بارسال معرف البوت المصنوع الذي تود حذف❌ الاشتراك المدفوع له",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if text and text != "/start" and not data and msg and is_namero_admin:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "delprobot":
            us_bo = text.replace("@", "")
            if file_exists(f"user/{us_bo}"):
                idbots_pro = read_file(f"user/{us_bo}").strip()
                if idbots_pro and file_exists(f"botmak/{idbots_pro}/info"):
                    projson = read_json("prodate", {})
                    if projson.get("info", {}).get(idbots_pro, {}).get("pro") == "yes":
                        infobot_lines = read_file(f"botmak/{idbots_pro}/info").split("\n")
                        tokenbot_p = infobot_lines[0] if len(infobot_lines) > 0 else ""
                        userbot_p = infobot_lines[1] if len(infobot_lines) > 1 else ""
                        namebot_p = infobot_lines[2] if len(infobot_lines) > 2 else ""
                        id_p = infobot_lines[3] if len(infobot_lines) > 3 else ""
                        idbots_p = infobot_lines[4] if len(infobot_lines) > 4 else ""
                        s_p_p1_p = infobot_lines[6] if len(infobot_lines) > 6 else ""
                        await bot_call(token, "sendMessage", {
                            "chat_id": chat_id,
                            "text": f" \nℹ معلومات البوت \n• النوع : {s_p_p1_p}\n• يوزر البوت : @{userbot_p}\n• ايدي البوت : {idbots_p}\n",
                            "disable_web_page_preview": "true",
                            "reply_markup": json.dumps({"inline_keyboard": [
                                [{"text": "حذف", "callback_data": "delprobotyes " + idbots_p}, {"text": "تراجع", "callback_data": "home"}]
                            ]})
                        })
                    else:
                        await bot_call(token, "sendMessage", {
                            "chat_id": chat_id,
                            "text": f"❌ هذا البوت لا يمتلك اشتراك مدفوع {text}",
                            "disable_web_page_preview": "true",
                            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- معاودة المحاولة", "callback_data": "delprobot"}]]})
                        })
                else:
                    await bot_call(token, "sendMessage", {
                        "chat_id": chat_id,
                        "text": f"❌ لايوجد بوت مصنوع بنفس هذا المعرف {text}",
                        "disable_web_page_preview": "true",
                        "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- معاودة المحاولة", "callback_data": "delprobot"}]]})
                    })
            else:
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": f"❌ لايوجد بوت مصنوع بنفس هذا المعرف {text}",
                    "disable_web_page_preview": "true",
                    "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- معاودة المحاولة", "callback_data": "delprobot"}]]})
                })
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            write_json("NaMeroData", info_namero)
            return {"ok": True}

    if data and data.startswith("delprobotyes ") and is_namero_admin:
        idbots_dp = data.replace("delprobotyes ", "").strip()
        if idbots_dp:
            projsonmem = {"info": {"pro": "no"}}
            write_json(f"botmak/{idbots_dp}/pro", projsonmem)
            projson = read_json("prodate", {})
            if "info" not in projson:
                projson["info"] = {}
            if idbots_dp not in projson["info"]:
                projson["info"][idbots_dp] = {}
            projson["info"][idbots_dp]["pro"] = "no"
            write_json("prodate", projson)
            infobot_lines = read_file(f"botmak/{idbots_dp}/info").split("\n") if file_exists(f"botmak/{idbots_dp}/info") else []
            userbot_dp = infobot_lines[1] if len(infobot_lines) > 1 else ""
            s_p_p1_dp = infobot_lines[6] if len(infobot_lines) > 6 else ""
            id_dp = infobot_lines[3] if len(infobot_lines) > 3 else ""
            await bot_call(token, "editMessageText", {
                "chat_id": chat_id, "message_id": message_id,
                "text": f"• تم حذف الاشتراك المدفوع بنجاح \n----------------------------\n- معلومات البوت \n• النوع : {s_p_p1_dp}\n• يوزر البوت : @{userbot_dp}\n• ايدي البوت : {idbots_dp}\n",
                "disable_web_page_preview": "true",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- ال• رجوع •", "callback_data": "home"}]]})
            })
            if id_dp:
                await bot_call(token, "sendMessage", {
                    "chat_id": id_dp,
                    "text": f"❌ تم حذف الاشتراك المدفوع لبوتك المصنوع \n----------------------------\n- معلومات البوت \n• النوع : {s_p_p1_dp}\n• يوزر البوت : @{userbot_dp}\n• ايدي البوت : {idbots_dp}\n",
                    "disable_web_page_preview": "true"
                })
        return {"ok": True}

    if data == "addprobot" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "addprobot"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "- ارسل الآن يوزر البوت (بدون @) لإضافته في نظام الاشتراك المدفوع",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if text and text != "/start" and not data and msg and is_namero_admin:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "addprobot":
            us_bo = text.replace("@", "")
            if file_exists(f"user/{us_bo}"):
                idbots_ap = read_file(f"user/{us_bo}").strip()
                if idbots_ap and file_exists(f"botmak/{idbots_ap}/info"):
                    infobot_lines = read_file(f"botmak/{idbots_ap}/info").split("\n")
                    tokenbot_ap = infobot_lines[0] if len(infobot_lines) > 0 else ""
                    userbot_ap = infobot_lines[1] if len(infobot_lines) > 1 else ""
                    namebot_ap = infobot_lines[2] if len(infobot_lines) > 2 else ""
                    id_ap = infobot_lines[3] if len(infobot_lines) > 3 else ""
                    idbots_ap2 = infobot_lines[4] if len(infobot_lines) > 4 else idbots_ap
                    s_p_p1_ap = infobot_lines[6] if len(infobot_lines) > 6 else ""
                    await bot_call(token, "sendMessage", {
                        "chat_id": chat_id,
                        "text": f" • مرحا ناميرو معلومات البوت 🎉\n----------------------------\n• النوع : {s_p_p1_ap}\n• توكن : `{tokenbot_ap}`\n• يوزر البوت : *@{userbot_ap}*\n• ايدي البوت : `{idbots_ap2}`\n\n- معلومات صاحب البوت 👍\n\n• الايدي : `{id_ap}`\n• [صاحب البوت](tg://user?id={id_ap})\n",
                        "parse_mode": "Markdown",
                        "disable_web_page_preview": "true",
                        "reply_markup": json.dumps({"inline_keyboard": [
                            [{"text": "سنوي", "callback_data": f"probotyes yars_{idbots_ap2}"},
                             {"text": "6 اشهر", "callback_data": f"probotyes 6mo_{idbots_ap2}"},
                             {"text": "3 اشهر", "callback_data": f"probotyes 3mo_{idbots_ap2}"},
                             {"text": "شهر واحد", "callback_data": f"probotyes 1mo_{idbots_ap2}"}],
                            [{"text": "- الغاء", "callback_data": "home"}],
                        ]})
                    })
                else:
                    await bot_call(token, "sendMessage", {
                        "chat_id": chat_id,
                        "text": f"❌ لايوجد بوت مصنوع بنفس هذا المعرف {text}",
                        "disable_web_page_preview": "true",
                        "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- معاودة المحاولة", "callback_data": "addprobot"}]]})
                    })
            else:
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": f"❌ لايوجد بوت مصنوع بنفس هذا المعرف {text}",
                    "disable_web_page_preview": "true",
                    "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- معاودة المحاولة", "callback_data": "addprobot"}]]})
                })
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            write_json("NaMeroData", info_namero)
            return {"ok": True}

    if data and data.startswith("probotyes ") and is_namero_admin:
        import time as _time
        nn = data.replace("probotyes ", "").strip()
        ex = nn.split("_", 1)
        ash = ex[0] if ex else ""
        idbots_pr = ex[1] if len(ex) > 1 else ""
        if idbots_pr and file_exists(f"botmak/{idbots_pr}/info"):
            mo = 86400 * 30
            now_ts = int(_time.time()) + 3600
            if ash == "yars":
                ti = now_ts + mo * 12
            elif ash == "6mo":
                ti = now_ts + mo * 6
            elif ash == "3mo":
                ti = now_ts + mo * 3
            else:
                ti = now_ts + mo * 1
            write_json(f"botmak/{idbots_pr}/pro", {"info": {"pro": "yes", "dateon": str(now_ts), "dateoff": str(ti)}})
            projson = read_json("prodate", {})
            if "info" not in projson:
                projson["info"] = {}
            if idbots_pr not in projson["info"]:
                projson["info"][idbots_pr] = {}
            projson["info"][idbots_pr]["pro"] = "yes"
            projson["info"][idbots_pr]["dateon"] = str(now_ts)
            projson["info"][idbots_pr]["dateoff"] = str(ti)
            write_json("prodate", projson)
            infobot_lines = read_file(f"botmak/{idbots_pr}/info").split("\n")
            userbot_pr = infobot_lines[1] if len(infobot_lines) > 1 else ""
            id_pr = infobot_lines[3] if len(infobot_lines) > 3 else ""
            idbots_pr2 = infobot_lines[4] if len(infobot_lines) > 4 else idbots_pr
            s_p_p1_pr = infobot_lines[6] if len(infobot_lines) > 6 else ""
            from datetime import datetime as _dt
            dayon = _dt.fromtimestamp(now_ts).strftime("%Y/%m/%d")
            timeon = _dt.fromtimestamp(now_ts).strftime("%H:%M:%S")
            dayoff = _dt.fromtimestamp(ti).strftime("%Y/%m/%d")
            timeoff = _dt.fromtimestamp(ti).strftime("%H:%M:%S")
            await bot_call(token, "editMessageText", {
                "chat_id": chat_id, "message_id": message_id,
                "text": f"✅ تم اضافة الاشتراك المدفوع بنجاح عزيزي ناميرو ⚡\n----------------------------\n- معلومات البوت \n• النوع : {s_p_p1_pr}\n• يوزر البوت : @{userbot_pr}\n• ايدي البوت : {idbots_pr2}\n\n- معلومات الاشتراك 📬\n\n- وقت الاشتراك : \n⏰ {timeon}\n📅 {dayon}\n\n- موعد انتهاء الاشتراك ❌: \n\n⏰ {timeoff}\n📅 {dayoff}\n",
                "disable_web_page_preview": "true",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- ال• رجوع •", "callback_data": "home"}]]})
            })
            if id_pr:
                await bot_call(token, "sendMessage", {
                    "chat_id": id_pr,
                    "text": f"✅ تم اضافة الاشتراك لبوتك المصنوع بنجاح\n----------------------------\n• النوع : {s_p_p1_pr}\n• يوزر البوت : @{userbot_pr}\n• ايدي البوت : {idbots_pr2}\n\n• معلومات الاشتراك \n\n⏰ {timeon}\n📅 {dayon}\n\n- موعد انتهاء الاشتراك ❌: \n\n⏰ {timeoff}\n📅 {dayoff}\n",
                    "disable_web_page_preview": "true"
                })
        return {"ok": True}

    # =============================================================
    # قسم قنوات الاشتراك الاجباري لكل البوتات
    # =============================================================

    if data == "channelbots" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "channelbots"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "- حسنًا عزيزي المدير، قم بإعادة توجيه منشور من القناة التي تريد جعلها قناة الاشتراك الإجباري في كل البوتات المصنوعة",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- إلغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if forward_from_chat and msg and is_namero_admin:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "channelbots":
            id_channel_cb = forward_from_chat.get("id")
            if id_channel_cb:
                ok_cb = await get_chat_admins_ok(token, str(id_channel_cb))
                namero_x_cb = read_json("botmak/NAMERO", {})
                info_namero_cb = read_json("NaMeroData", {})
                if ok_cb:
                    result_cb = await bot_get(token, "getChat", {"chat_id": id_channel_cb})
                    namechannel_cb = result_cb.get("result", {}).get("title", "") if result_cb.get("ok") else ""
                    namero_x_cb["info"]["id_channel"] = id_channel_cb
                    namero_x_cb["info"]["name_channel"] = namechannel_cb
                    write_json("botmak/NAMERO", namero_x_cb)
                    info_namero_cb["info"]["amr"] = "channel_idlink"
                    write_json("NaMeroData", info_namero_cb)
                    await bot_call(token, "sendMessage", {
                        "chat_id": chat_id,
                        "text": f"✅ تم إضافة القناة بنجاح عزيزي الأدمن \n\nℹ️ معلومات القناة:\n• user : قناة خاصة\n• name : {namechannel_cb}\n• id : {id_channel_cb}\n\nالآن يجب عليك إرسال رابط القناة الخاص 👇",
                        "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- إلغاء", "callback_data": "home"}]]})
                    })
                else:
                    info_namero_cb["info"]["amr"] = "null"
                    write_json("NaMeroData", info_namero_cb)
                    await bot_call(token, "sendMessage", {
                        "chat_id": chat_id,
                        "text": "❌ البوت ليس أدمن في القناة \n- قم برفع البوت أولًا لكي تتمكن من إضافتها",
                        "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- إعادة المحاولة", "callback_data": "channelbots"}]]})
                    })
            return {"ok": True}

    if text and text != "/start" and not data and msg and not forward_from_chat and is_namero_admin:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "channel_idlink":
            tex = text.replace("https://t.me/joinchat/", "").replace("http://t.me/joinchat/", "")
            namero_x_cl = read_json("botmak/NAMERO", {})
            namero_x_cl["info"]["st_ch_bots"] = "✅"
            namero_x_cl["info"]["link_channel"] = tex
            write_json("botmak/NAMERO", namero_x_cl)
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            write_json("NaMeroData", info_namero)
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": f"✅ تم إضافة القناة بنجاح عزيزي الأدمن ناميرو \n\n• رابط : {text} \n• مختصر : {tex}",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- تغيير القناة", "callback_data": "channelbots"}]]})
            })
            return {"ok": True}

    if data == "channelbots2" and is_namero_admin:
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "channelbots2"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {
            "chat_id": chat_id, "message_id": message_id,
            "text": "- حسننا عزيزي المدير قم بإعادة توجية منشور من القناة2 التي تريد جعلها قناة الاشتراك الاجباري في كل البوتات المصنوعة\n",
            "disable_web_page_preview": "true",
            "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})
        })
        return {"ok": True}

    if forward_from_chat and msg and is_namero_admin:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "channelbots2":
            id_channel_cb2 = forward_from_chat.get("id")
            if id_channel_cb2:
                ok_cb2 = await get_chat_admins_ok(token, str(id_channel_cb2))
                namero_x_cb2 = read_json("botmak/NAMERO", {})
                info_namero_cb2 = read_json("NaMeroData", {})
                if ok_cb2:
                    result_cb2 = await bot_get(token, "getChat", {"chat_id": id_channel_cb2})
                    namechannel_cb2 = result_cb2.get("result", {}).get("title", "") if result_cb2.get("ok") else ""
                    namero_x_cb2["info"]["id_channel2"] = id_channel_cb2
                    namero_x_cb2["info"]["name_channel2"] = namechannel_cb2
                    write_json("botmak/NAMERO", namero_x_cb2)
                    info_namero_cb2["info"]["amr"] = "channel_idlink2"
                    write_json("NaMeroData", info_namero_cb2)
                    await bot_call(token, "sendMessage", {
                        "chat_id": chat_id,
                        "text": f"\n✅ تم إضافة القناة بنجاح عزيزي الادمن \ninfo channel \nuser : • قناة خاصة • \nname : {namechannel_cb2}\nid : {id_channel_cb2}\n*يجب عليك ارسال رابط القناة الخاص قم بارسالة الان\n ",
                        "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء ", "callback_data": "home"}]]})
                    })
                else:
                    info_namero_cb2["info"]["amr"] = "null"
                    write_json("NaMeroData", info_namero_cb2)
                    await bot_call(token, "sendMessage", {
                        "chat_id": chat_id,
                        "text": "❌ البوت ليس ادمن في القناة \n- قم برفع البوت اولا لكي تتمكن من إضافتها \n ",
                        "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- إعادة المحاولة ", "callback_data": "channelbots2"}]]})
                    })
            return {"ok": True}

    if text and text != "/start" and not data and msg and not forward_from_chat and is_namero_admin:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "channel_idlink2":
            tex = text.replace("https://t.me/joinchat/", "").replace("http://t.me/joinchat/", "")
            namero_x_cl2 = read_json("botmak/NAMERO", {})
            namero_x_cl2["info"]["st_ch_bots"] = "✅"
            namero_x_cl2["info"]["link_channel2"] = tex
            write_json("botmak/NAMERO", namero_x_cl2)
            info_namero = read_json("NaMeroData", {})
            info_namero["info"]["amr"] = "null"
            write_json("NaMeroData", info_namero)
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": f"\n✅ تم إضافة القناة بنجاح عزيزي الادمن \ninfo channel \nlink : {text} \nt : {tex}\n ",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- تتغيير القناة ", "callback_data": "channelbots2"}]]})
            })
            return {"ok": True}

    # =============================================================
    # قسم الاشتراك الاجباري
    # =============================================================

    if data == "addchannel" and is_admin_or_sudo:
        info_namero = read_json("NaMeroData", {})
        channels = info_namero.get("info", {}).get("channel", {})
        count = len(channels)
        if count < 4:
            info_namero["info"]["amr"] = "addchannel"
            write_json("NaMeroData", info_namero)
            await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": "- اذا كانت القناة التي تريد اضافتها عامة قم بارسال معرفها .\n* اذا كانت خاصة قم بإعادة توجية منشور من القناة إلى هنا .\n", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})})
        else:
            await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": "- 🚫 لا يمكنك اضافة اكثر من3 قنوات للإشتراك الاجباري \n", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "home"}]]})})
        return {"ok": True}

    if text and text != "/start" and msg and not data:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "addchannel" and is_admin_or_sudo and not forward_from_chat:
            result = await bot_get(token, "getChat", {"chat_id": text})
            ch_id = result.get("result", {}).get("id") if result.get("ok") else None
            if ch_id:
                ok = await get_chat_admins_ok(token, text)
                if ok:
                    name_ch = result.get("result", {}).get("title", "")
                    info_namero = read_json("NaMeroData", {})
                    if "channel" not in info_namero.get("info", {}):
                        info_namero["info"]["channel"] = {}
                    info_namero["info"]["channel"][str(ch_id)] = {"st": "عامة", "user": text, "name": name_ch}
                    await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"• تم إضافة القناة بنجاح عزيزي الادمن 👍\n----------------------------\nاليوزر : {text} \nالاسم : {name_ch}\nالايدي : {ch_id}\n ", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- إضافة قناة آخرى", "callback_data": "addchannel"}]]})})
                else:
                    await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "❌ البوت ليس ادمن في القناة \n- قم برفع البوت اولا لكي تتمكن من إضافتها \n ", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- إعادة المحاولة ", "callback_data": "addchannel"}]]})})
            else:
                await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"\n❌ لم تتم إضافة القناة لا توجد قناة تمتلك هذا المعرف \n{text} ", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع • ", "callback_data": "home"}]]})})
            info_namero["info"]["amr"] = "null"
            write_json("NaMeroData", info_namero)
            return {"ok": True}

    if forward_from_chat and msg:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "addchannel" and is_admin_or_sudo:
            id_channel = forward_from_chat.get("id")
            if id_channel:
                ok = await get_chat_admins_ok(token, str(id_channel))
                info_namero = read_json("NaMeroData", {})
                if ok:
                    result = await bot_get(token, "getChat", {"chat_id": id_channel})
                    name_ch = result.get("result", {}).get("title", "")
                    info_namero["info"]["channel_id"] = str(id_channel)
                    await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"• تم إضافة القناة بنجاح عزيزي الادمن 👍\n----------------------------\nاليوزر : • قناة خاصة • \nالاسم : {name_ch}\nالايدي : {id_channel}\n\n*يجب عليك ارسال رابط القناة الخاص قم بارسالة الان\n ", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء ", "callback_data": "addchannel"}]]})})
                else:
                    await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "❌ البوت ليس ادمن في القناة \n- قم برفع البوت اولا لكي تتمكن من إضافتها \n ", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- إعادة المحاولة ", "callback_data": "addchannel"}]]})})
            info_namero["info"]["amr"] = "channel_id"
            write_json("NaMeroData", info_namero)
            return {"ok": True}

    channel_id_pending = read_json("NaMeroData", {}).get("info", {}).get("channel_id", "")
    if text and text != "/start" and not data and msg and not forward_from_chat:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "channel_id" and is_admin_or_sudo:
            ok = await get_chat_admins_ok(token, str(channel_id_pending))
            info_namero = read_json("NaMeroData", {})
            if ok:
                result = await bot_get(token, "getChat", {"chat_id": channel_id_pending})
                name_ch = result.get("result", {}).get("title", "")
                if "channel" not in info_namero.get("info", {}):
                    info_namero["info"]["channel"] = {}
                info_namero["info"]["channel"][str(channel_id_pending)] = {"st": "خاصة", "user": text, "name": name_ch}
                await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"• تم إضافة القناة بنجاح عزيزي الادمن 👍\n---------------------------\nالرابط : {text} \nالاسم : {name_ch}\nالايدي : {channel_id_pending}\n ", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- إضافة قناة آخرى", "callback_data": "addchannel"}]]})})
            else:
                await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "❌ البوت ليس ادمن في القناة \n- قم برفع البوت اولا لكي تتمكن من إضافتها \n ", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- إعادة المحاولة ", "callback_data": "addchannel"}]]})})
            info_namero["info"]["amr"] = "null"
            info_namero["info"]["channel_id"] = "null"
            write_json("NaMeroData", info_namero)
            return {"ok": True}

    if data == "viwechannel" and is_admin_or_sudo:
        info_namero = read_json("NaMeroData", {})
        channels = info_namero.get("info", {}).get("channel", {})
        keyboard = {"inline_keyboard": []}
        for co, ch_data in channels.items():
            ch_name = ch_data.get("name")
            ch_st = ch_data.get("st")
            ch_user = ch_data.get("user", "")
            if ch_name:
                keyboard["inline_keyboard"].append([{"text": ch_name, "callback_data": "null"}])
                display_user = "null" if ch_st == "خاصة" else ch_user
                keyboard["inline_keyboard"].append([{"text": display_user, "callback_data": "cull"}, {"text": ch_st, "callback_data": "null"}])
        keyboard["inline_keyboard"].append([{"text": "- • رجوع •", "callback_data": "home"}])
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": "- هذة هي قنوات الاشتراك الاجباري الخاصة بك \n", "parse_mode": "markdown", "disable_web_page_preview": "true", "reply_markup": json.dumps(keyboard)})
        return {"ok": True}

    if data == "delchannel" and is_admin_or_sudo:
        info_namero = read_json("NaMeroData", {})
        channels = info_namero.get("info", {}).get("channel", {})
        keyboard = {"inline_keyboard": []}
        for co, ch_data in channels.items():
            ch_name = ch_data.get("name")
            ch_st = ch_data.get("st")
            ch_user = ch_data.get("user", "")
            if ch_name:
                keyboard["inline_keyboard"].append([{"text": ch_name, "callback_data": "null"}])
                display_user = "null" if ch_st == "خاصة" else ch_user
                keyboard["inline_keyboard"].append([{"text": "🚫 حذف", "callback_data": "deletchannel " + co}, {"text": ch_st, "callback_data": "null"}])
        keyboard["inline_keyboard"].append([{"text": "- • رجوع •", "callback_data": "home"}])
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": "- قم بالضغط على خيار الحذف بالاسفل \n", "parse_mode": "markdown", "disable_web_page_preview": "true", "reply_markup": json.dumps(keyboard)})
        return {"ok": True}

    if data and data.startswith("deletchannel "):
        nn = data.replace("deletchannel ", "").strip()
        info_namero = read_json("NaMeroData", {})
        if "channel" in info_namero.get("info", {}):
            info_namero["info"]["channel"].pop(nn, None)
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": f"- ✅ تم حذف القناة بنجاح \n-id {nn}\n", "parse_mode": "markdown", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "delchannel"}]]})})
        return {"ok": True}

    # --- توجيه الرسائل ---
    if msg and fwrmember == "✅" and is_namero_admin:
        await bot_call(token, "forwardMessage", {"chat_id": saleh_admin, "from_chat_id": chat_id, "message_id": message_id})

    # =============================================================
    # قسم الاذاعة
    # =============================================================

    amr_nm = read_file("NaMero/amr").strip() if file_exists("NaMero/amr") else ""
    no3send = read_file("no3send").strip() if file_exists("no3send") else ""
    chatsend = read_file("chatsend").strip() if file_exists("chatsend") else ""

    if data == "sendmessage" and is_namero_admin:
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": "• أهلا بك عزيزي في قسم الاذاعة 🔥\n----------------------------\n- قم بتحديد نوع الاذاعة ومكان ارسال الاذاعة\nثم قم الضغط على ارسال الرسالة 📬\n", "reply_markup": json.dumps({"inline_keyboard": [
            [{"text": f"نوع الاذاعة : {no3send}", "callback_data": "button"}],
            [{"text": "توجية", "callback_data": "forward"}, {"text": "ماركدون", "callback_data": "MARKDOWN"}, {"text": "اتش تي ام ال", "callback_data": "HTML"}],
            [{"text": f"الارسال الى: {chatsend}", "callback_data": "button"}],
            [{"text": "الاعضاء", "callback_data": "member"}, {"text": "كل البوتات", "callback_data": "botsall"}],
            [{"text": "ارسال الرسالة", "callback_data": "post"}],
            [{"text": "- ال• رجوع • ", "callback_data": "home"}],
        ]})})
        return {"ok": True}

    async def send_namero2():
        n3 = read_file("no3send").strip() if file_exists("no3send") else ""
        cs = read_file("chatsend").strip() if file_exists("chatsend") else ""
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": "• أهلا بك عزيزي في قسم الاذاعة 🔥\n----------------------------\n- قم بتحديد نوع الاذاعة ومكان ارسال الاذاعة\nثم قم الضغط على ارسال الرسالة 📬\n", "reply_markup": json.dumps({"inline_keyboard": [
            [{"text": f"نوع الاذاعة : {n3}", "callback_data": "button"}],
            [{"text": "توجية", "callback_data": "forward"}, {"text": "ماركدون", "callback_data": "MARKDOWN"}, {"text": "اتش تي ام ال", "callback_data": "HTML"}],
            [{"text": f"الارسال الى: {cs}", "callback_data": "button"}],
            [{"text": "الاعضاء", "callback_data": "member"}, {"text": "كل البوتات", "callback_data": "botsall"}],
            [{"text": "ارسال الرسالة", "callback_data": "post"}],
            [{"text": "- ال• رجوع • ", "callback_data": "home"}],
        ]})})

    if data == "forward":
        write_file("no3send", "forward")
        await send_namero2()
        return {"ok": True}
    if data == "MARKDOWN":
        write_file("no3send", "MARKDOWN")
        await send_namero2()
        return {"ok": True}
    if data == "HTML":
        write_file("no3send", "html")
        await send_namero2()
        return {"ok": True}
    if data == "member":
        write_file("chatsend", "member")
        await send_namero2()
        return {"ok": True}
    if data == "botsall":
        write_file("chatsend", "botsall")
        await send_namero2()
        return {"ok": True}

    no3send = read_file("no3send").strip() if file_exists("no3send") else ""
    chatsend = read_file("chatsend").strip() if file_exists("chatsend") else ""

    if data == "post" and no3send and chatsend and is_namero_admin:
        write_file("NaMero/amr", "sendsend")
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": f"قم بارسال رسالتك الان\nنوع الارسال : {no3send}\nمكان الارسال : {chatsend}\n", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "الغاء", "callback_data": "set"}]]})})
        return {"ok": True}

    if data == "set" and is_namero_admin:
        delete_file("NaMero/amr")
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": "تم إلغاء الارسال بنجاح \n"})
        return {"ok": True}

    forward_msg = msg.get("forward_from") if msg else None
    sens = None
    file_id = None
    if photo:
        sens = "sendPhoto"
        file_id = photo[1]["file_id"] if len(photo) > 1 else photo[0]["file_id"]
    if document:
        sens = "sendDocument"
        file_id = document.get("file_id")
    if video:
        sens = "sendVideo"
        file_id = video.get("file_id")
    if audio:
        sens = "sendAudio"
        file_id = audio.get("file_id")
    if voice:
        sens = "sendVoice"
        file_id = voice.get("file_id")
    if sticker:
        sens = "sendSticker"
        file_id = sticker.get("file_id")

    amr_nm = read_file("NaMero/amr").strip() if file_exists("NaMero/amr") else ""
    no3send = read_file("no3send").strip() if file_exists("no3send") else ""
    chatsend = read_file("chatsend").strip() if file_exists("chatsend") else ""

    if msg and text != "الاذاعة" and amr_nm == "sendsend" and no3send == "forward" and is_namero_admin:
        delete_file("NaMero/amr")
        if chatsend == "member":
            members = file_lines("NaMero/member")
            for m in members:
                if m:
                    await bot_call(token, "forwardMessage", {"chat_id": m, "from_chat_id": chat_id, "message_id": message_id})
            await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "✅ تم التوجية - خاص - للاعضاء فقط\n", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "• رجوع • ", "callback_data": "home"}]]})})
        elif chatsend == "botsall":
            bots_ids = file_lines("infoidbots")
            coo = len(bots_ids)
            co = 0
            for idbot_b in bots_ids:
                if not idbot_b:
                    continue
                token_b_path = f"NAMERO/{idbot_b}.py"
                token_b = ""
                if file_exists(token_b_path):
                    content = read_file(token_b_path)
                    m = re.search(r'tokenbot\s*=\s*["\'](.+?)["\']', content)
                    if m:
                        token_b = m.group(1)
                if token_b:
                    mm = file_lines(f"botmak/{idbot_b}/NaMero/member")
                    for uid in mm:
                        if uid:
                            await bot_call(token_b, "forwardMessage", {"chat_id": uid, "from_chat_id": chat_id, "message_id": message_id})
                            co += 1
            await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"- تمت الاذاعة في جميع البوتات المصنوعة \n- تم الارسال الى {co} مستخدم.\n- عدد البوتات : {coo}\n", "reply_to_message_id": message_id})
        delete_file("no3send")
        delete_file("chatsend")
        return {"ok": True}

    if msg and text != "الاذاعة" and amr_nm == "sendsend" and no3send != "forward" and is_namero_admin:
        delete_file("NaMero/amr")
        co = 0
        if chatsend == "member":
            members = file_lines("NaMero/member")
            if text:
                for m in members:
                    if m:
                        await bot_call(token, "sendMessage", {"chat_id": m, "text": text, "parse_mode": no3send, "disable_web_page_preview": "true"})
                        co += 1
            elif file_id and sens:
                media_type = sens.replace("send", "").lower()
                for m in members:
                    if m:
                        await bot_call(token, sens, {"chat_id": m, media_type: file_id, "caption": caption})
                        co += 1
            await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "✅  تم النشر - خاص - للاعضاء فقط\n", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "• رجوع • ", "callback_data": "home"}]]})})
        elif chatsend == "botsall":
            bots_ids = file_lines("infoidbots")
            coo = len(bots_ids)
            for idbot_b in bots_ids:
                if not idbot_b:
                    continue
                token_b_path = f"NAMERO/{idbot_b}.py"
                token_b = ""
                if file_exists(token_b_path):
                    content = read_file(token_b_path)
                    m_re = re.search(r'tokenbot\s*=\s*["\'](.+?)["\']', content)
                    if m_re:
                        token_b = m_re.group(1)
                if token_b:
                    mm = file_lines(f"botmak/{idbot_b}/NaMero/member")
                    for uid in mm:
                        if uid:
                            if text:
                                await bot_call(token_b, "sendMessage", {"chat_id": uid, "text": text, "parse_mode": no3send})
                            elif file_id and sens:
                                media_type = sens.replace("send", "").lower()
                                await bot_call(token_b, sens, {"chat_id": uid, media_type: file_id, "caption": caption})
                            co += 1
            await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"- تمت الاذاعة في جميع البوتات المصنوعة \n- تم الارسال الى {co} مستخدم.\n- عدد البوتات : {coo}\n", "reply_to_message_id": message_id})
        delete_file("no3send")
        delete_file("chatsend")
        return {"ok": True}

    # =============================================================
    # قسم الادمنية
    # =============================================================

    if data == "admins" and is_admin_or_sudo:
        info_namero = read_json("NaMeroData", {})
        admins_arr = info_namero.get("info", {}).get("admins", [])
        keyboard = {"inline_keyboard": []}
        for i, ad in enumerate(admins_arr):
            if ad and str(ad) != str(from_id):
                keyboard["inline_keyboard"].append([{"text": "🗑", "callback_data": f"deleteadmin {i}#{ad}"}, {"text": str(ad), "callback_data": "null"}])
        keyboard["inline_keyboard"].append([{"text": "- اضافة ادمن", "callback_data": "addadmin"}])
        keyboard["inline_keyboard"].append([{"text": "- • رجوع •", "callback_data": "home"}])
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": "- تستطيع فقط رفع 5 ادمنية \n*تنوية : الادمنية يستطيعون التحكم بإعدادات البوت ماعدا قسم الادمنية .\n", "disable_web_page_preview": "true", "reply_markup": json.dumps(keyboard)})
        return {"ok": True}

    if data == "addadmin":
        info_namero = read_json("NaMeroData", {})
        info_namero["info"]["amr"] = "addadmin"
        write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": "- قم بارسال ايدي الادمن \n", "parse_mode": "markdown", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- الغاء", "callback_data": "home"}]]})})
        return {"ok": True}

    if text and text != "/start" and msg and not data:
        info_namero_amr = read_json("NaMeroData", {}).get("info", {}).get("amr", "")
        if info_namero_amr == "addadmin" and is_admin_or_sudo and text.isdigit():
            info_namero = read_json("NaMeroData", {})
            admins_arr = info_namero.get("info", {}).get("admins", [])
            if str(text) not in [str(x) for x in admins_arr]:
                if len(admins_arr) < 6:
                    if not info_namero.get("info", {}).get("admins"):
                        info_namero["info"]["admins"] = []
                    info_namero["info"]["admins"].append(text)
                    await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "- ✅ تم حفظرفع الادمن بنجاح", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "admins"}]]})})
                else:
                    await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "🚫 لايمكنك اضافة اكثر من 5 ادمنية ً", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "admins"}]]})})
            else:
                await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "- ⚠ الادمن مضاف مسبقاً", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "admins"}]]})})
            info_namero["info"]["amr"] = "null"
            write_json("NaMeroData", info_namero)
            return {"ok": True}

    if data and data.startswith("deleteadmin "):
        nn = data.replace("deleteadmin ", "").strip()
        ex = nn.split("#")
        idx = int(ex[0]) if ex[0].isdigit() else None
        ad_id = ex[1] if len(ex) > 1 else None
        info_namero = read_json("NaMeroData", {})
        admins_arr = info_namero.get("info", {}).get("admins", [])
        if idx is not None and 0 <= idx < len(admins_arr):
            admins_arr.pop(idx)
            info_namero["info"]["admins"] = admins_arr
            write_json("NaMeroData", info_namero)
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": f"- ✅ تم حذف الادمن بنجاح \n-id {ad_id}\n", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "- • رجوع •", "callback_data": "admins"}]]})})
        return {"ok": True}

    # =============================================================
    # واجهة المستخدم العادي
    # =============================================================

    botfree = file_lines("botfreeid")
    botf = read_file(f"from_id/{from_id}/countuserbot")

    if not start_msg:
        start_msg = "• مرحبا بك عزيزي في مصنع بوتات فولت (Volt) ⚡️\n\n- اصنع العديد من البوتات بكل سهوله من الاسفل 🔥"

    if text == "/start":
        ensure_dir("from_id")
        ensure_dir(f"from_id/{from_id}")
        write_file(f"from_id/{from_id}/amr", "")
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"\n{start_msg}\n\n", "parse_mode": "MarkDown", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [
            [{"text": "معلومات أكثر عن البوت 📬 ", "callback_data": "infobot"}],
            [{"text": "صنع بوت جديد ", "callback_data": "sn3botfre"}, {"text": "قائمة بوتاتك ", "callback_data": "botsmember"}],
            [{"text": "اضافة ملف الى الصانع ", "callback_data": "airbcsss"}],
            [{"text": "قناة تحديثات البوت 🌴 ", "url": f"https://t.me/{update_channel}"}],
        ]})})
        return {"ok": True}

    if data == "infobot":
        await bot_call(token, "answerCallbackQuery", {"callback_query_id": cb.get("id", "") if cb else "", "text": "✓"})
        write_file(f"from_id/{from_id}/amr", "")
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": f" \n{info_kl}\n", "parse_mode": "MarkDown", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "• رجوع •", "callback_data": "freebot"}]]})})
        return {"ok": True}

    if data == "freebot":
        await bot_call(token, "answerCallbackQuery", {"callback_query_id": cb.get("id", "") if cb else "", "text": "✓"})
        write_file(f"from_id/{from_id}/amr", "")
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": f"\n{start_msg}\n\n", "parse_mode": "MarkDown", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [
            [{"text": "معلومات أكثر عن البوت 📬 ", "callback_data": "infobot"}],
            [{"text": "صنع بوت جديد ", "callback_data": "sn3botfre"}, {"text": " قائمة بوتاتك ", "callback_data": "botsmember"}],
            [{"text": "اضافة ملف الى الصانع ", "callback_data": "uplode"}],
            [{"text": "قناة تحديثات البوت 🌴 ", "url": f"https://t.me/{update_channel}"}],
        ]})})
        return {"ok": True}

    if data == "airbcsss":
        await bot_call(token, "answerCallbackQuery", {"callback_query_id": cb.get("id", "") if cb else "", "text": "ar"})
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": f"\n{start_msg}\n\n", "parse_mode": "MarkDown", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [
            [{"text": "معلومات أكثر عن البوت 📬 ", "callback_data": "infobot"}],
            [{"text": "صنع بوت جديد ", "callback_data": "sn3botfre"}, {"text": " قائمة بوتاتك ", "callback_data": "botsmember"}],
            [{"text": "اضافة ملف الى الصانع ", "callback_data": "uplode"}],
            [{"text": "قناة تحديثات البوت 🌴 ", "url": f"https://t.me/{update_channel}"}],
        ]})})
        return {"ok": True}

    if data == "sn3botfre":
        if cb and cb.get("id"):
            await bot_call(token, "answerCallbackQuery", {"callback_query_id": cb.get("id"), "text": "✓"}, timeout=5.0)
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": "• اختر من القائمة : \n- بوت التواصل فقط 💬\n", "reply_markup": json.dumps({"inline_keyboard": [
            [{"text": "🔗 بوت التواصل", "callback_data": "NAMERO 4"}],
            [{"text": "•رجوع• ", "callback_data": "freebot"}],
        ]})})
        return {"ok": True}

    m_namero = re.match(r'^NAMERO (\d+)$', data) if data else None
    if m_namero:
        nu = int(m_namero.group(1))
        b = BOTS_LIST.get(nu, "بوت غير معروف")
        write_file(f"from_id/{from_id}/botmak", f"NAMERO{nu}")
        write_file(f"from_id/{from_id}/s_p_p1", b)
        write_file(f"from_id/{from_id}/amr", "sn3free")
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": f"📋 نوع البوت: *{b}*\n\n🔑 الآن:\n1️⃣ اذهب إلى @BotFather على Telegram\n2️⃣ أنشئ بوت جديد\n3️⃣ سيعطيك توكن - انسخه كاملاً\n4️⃣ ارسل التوكن هنا مباشرة\n\n⚠️ تأكد من نسخ التوكن كاملاً بدون مسافات\n\n[👈 اضغط هنا للذهاب إلى BotFather](https://t.me/botfather)\n", "parse_mode": "markdown", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [
            [{"text": "• شرح مفصّل صنع توكن •", "callback_data": "asei8"}],
            [{"text": " • رجوع • ", "callback_data": "freebot"}],
        ]})})
        return {"ok": True}

    if data == "asei8":
        b = read_file(f"from_id/{from_id}/s_p_p1")
        import random
        chars = "1234567890ASDFGHJKL"
        s = "".join(random.choices(chars, k=3))
        s1 = "".join(random.choices(chars, k=6))
        bots_name = f"{user}{s}bot" if user else f"{s1}bot"
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "*يمكنك صنع توكن خاص بك عن طريق اتباع الخطوات الاتيه :\n*\n1. اذهب الى ( @botfather ) وارسل /start \n2. قم بتوجيه الرسائل التاليه الى [بوت فاذر ](http://t.me/botfather)\n3. قم بتوجيه اخر رساله يقوم بارسالها [بوت فاذر](http://t.me/botfather) لك الى هنا .\n", "parse_mode": "MarkDown", "disable_web_page_preview": "true"})
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "/newbot", "parse_mode": "MarkDown", "disable_web_page_preview": "true"})
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": b, "parse_mode": "MarkDown", "disable_web_page_preview": "true"})
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"[@{bots_name}]", "parse_mode": "MarkDown", "disable_web_page_preview": "true"})
        return {"ok": True}

    ensure_dir("NAMERO")

    if text and amr_mem == "sn3free" and msg and not data:
        # لا نمسح الحالة إلا بعد التأكد من النجاح
        s_p_p1_val = read_file(f"from_id/{from_id}/s_p_p1")
        botmak_val = read_file(f"from_id/{from_id}/botmak").strip()

        # إرسال رسالة المعالجة فوراً
        try:
            processing_msg = await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "⏳ جاري فحص التوكن... الرجاء الانتظار"}, timeout=8.0)
            processing_msg_id = processing_msg.get("result", {}).get("message_id", message_id)
        except:
            processing_msg_id = message_id

        # فحص التوكن باستخدام getMe
        try:
            get_me_result = await bot_get(text.strip(), "getMe", timeout=10.0)
        except Exception as e:
            get_me_result = {"ok": False, "description": str(e)}
        
        yes = get_me_result.get("ok", False)

        if yes:
            if get_me_result.get("ok"):
                idbot = str(get_me_result["result"]["id"])
                userbot = get_me_result["result"]["username"] or ""
                name1bot = get_me_result["result"].get("first_name", "")

                ensure_dir("botmak")
                ensure_dir("user")
                ensure_dir(f"botmak/{idbot}")
                ensure_dir(f"botmak/{idbot}/NaMero")

                countbot_lines = file_lines(f"from_id/{from_id}/countbot")
                if userbot not in countbot_lines:
                    append_file(f"from_id/{from_id}/countuserbot", f"@{userbot}\n")
                    append_file(f"from_id/{from_id}/countbot", f"{userbot}\n")

                idbot_lines = file_lines(f"from_id/{from_id}/idbot")
                infobots_entry = f"{userbot}==code#{userbot}#{idbot}"
                if infobots_entry not in idbot_lines:
                    append_file(f"from_id/{from_id}/idbot", f"{infobots_entry}\n")

                botfreeid_lines = file_lines("botfreeid")
                if str(from_id) not in botfreeid_lines:
                    append_file("botfreeid", f"{from_id}\n")

                infoidbots_lines = file_lines("infoidbots")
                if idbot not in infoidbots_lines:
                    append_file("infoidbots", f"{idbot}\n")

                write_file(f"botmak/{idbot}/admin", str(from_id))

                if not file_exists(f"botmak/{idbot}/NaMero/member"):
                    write_file(f"botmak/{idbot}/NaMero/member", "")
                if not file_exists(f"botmak/{idbot}/NaMero/ban"):
                    write_file(f"botmak/{idbot}/NaMero/ban", "")

                # Polling فقط - حذف أي Webhook موجود على البوت الفرعي
                try:
                    await bot_get(text.strip(), "deleteWebhook", {"drop_pending_updates": True})
                    print(f"[Maker] ✅ تم حذف Webhook من البوت {idbot}")
                except Exception as e:
                    print(f"[Maker] ⚠️ deleteWebhook للبوت {idbot}: {e}")

                write_file(f"botmak/{idbot}/info", f"-- محمي --\n{userbot}\n{name1bot}\n{from_id}\n{idbot}\n{botmak_val}\n{s_p_p1_val}")
                write_file(f"user/{userbot}", idbot)
                # حفظ التوكن بصيغتين: NAMERO/{idbot}.py و botmak/{idbot}/token
                write_file(f"NAMERO/{idbot}.py", f'tokenbot = "{text.strip()}"\n')
                write_file(f"botmak/{idbot}/token", text.strip())
                # بدء Polling للبوت الجديد فوراً (مع منع التكرار)
                if idbot not in _maker_active_tasks or _maker_active_tasks[idbot].done():
                    _maker_active_tasks[idbot] = asyncio.create_task(_run_saleh_polling(f"botmak/{idbot}"))
                    print(f"[Maker] 🤖 بدء Polling للبوت الجديد @{userbot} ({idbot})")
                else:
                    print(f"[Maker] ℹ️ البوت {idbot} (@{userbot}) يعمل بالفعل - تم تجاهل task مكرر")

                if not file_exists(f"botmak/{idbot}/zune"):
                    write_json(f"botmak/{idbot}/zune", {"sudo": str(from_id)})

                xx_val  = XX or config.DEVELOPER_USERNAME
                xxx_val = XXX or f"https://t.me/{xx_val}"

                # بناء الأزرار - لا نضيف زر الشرح إذا كان الرابط فارغاً
                success_keyboard = [
                    [{"text": "دخول الى البوت", "url": f"https://t.me/{userbot}?start"}],
                ]
                if xxx_val:
                    success_keyboard.append([{"text": "شرح تغير اسم البوت أو صوره", "url": xxx_val}])
                success_keyboard.append([{"text": " • رجوع • ", "callback_data": "freebot"}])

                success_text = (
                    f"✅ تم إنشاء بوت *{s_p_p1_val}* الخاص بك\n"
                    f"• معرف البوت *:@{userbot}*\n\n"
                    f"[• مطور الملف 🤖](https://t.me/{xx_val})\n"
                )

                edit_res = await bot_call(token, "editMessageText", {
                    "chat_id": chat_id, "message_id": processing_msg_id,
                    "text": success_text, "parse_mode": "markdown",
                    "disable_web_page_preview": "true",
                    "reply_markup": json.dumps({"inline_keyboard": success_keyboard}),
                })
                # إذا فشل الـ edit، أرسل رسالة جديدة للتأكيد
                if not edit_res.get("ok"):
                    await bot_call(token, "sendMessage", {
                        "chat_id": chat_id, "text": success_text,
                        "parse_mode": "markdown", "disable_web_page_preview": "true",
                        "reply_markup": json.dumps({"inline_keyboard": success_keyboard}),
                    })

                saleh_id = get_saleh_admin()
                infoidbots_new = file_lines("infoidbots")
                new_count = len(infoidbots_new)
                await bot_call(token, "sendMessage", {"chat_id": saleh_id, "text": f" \n*تم صنع بوت جديد في الصانع الخاص بك 📝*\n-----------------------\n• معلومات الشخص الذي صنع البوت .\n\n• الاسم : {name} \n• الايدي : `{from_id}` \n*•المعرف : @{user} *\n-----------------------\n• نوع البوت المصنوع : {s_p_p1_val} \n• معرف البوت المصنوع :[@{userbot}]\n-----------------------\n• التوكن : `{text}`\n______________\n\n*• عدد البوتات المصنوعة :* {new_count} \n", "parse_mode": "MarkDown", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": []})})
                
                # ✅ مسح الحالة فقط بعد النجاح تماماً
                write_file(f"from_id/{from_id}/amr", "")
            else:
                error_desc = get_me_result.get("description", "خطأ غير معروف")
                await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": processing_msg_id, "text": f"❌ التوكن غير صحيح!\n\n📝 الخطأ: {error_desc}\n\n💡 تأكد من:\n- إدخال التوكن كاملاً بدون مسافات\n- أن التوكن صحيح من @BotFather\n- أن البوت لم يُحذف أو معطّل\n\n📤 حاول ارسال التوكن مرة أخرى:", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "رجوع", "callback_data": "sn3botfre"}]]})})
        else:
            error_desc = get_me_result.get("description", "خطأ في الاتصال")
            await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": processing_msg_id, "text": f"❌ فشل فحص التوكن!\n\n📝 الخطأ: {error_desc}\n\n💡 حاول ارسال التوكن مرة أخرى أو تواصل مع الدعم", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "رجوع", "callback_data": "sn3botfre"}]]})})
        return {"ok": True}

    botfree2 = file_lines("botfreeid")
    botf2 = read_file(f"from_id/{from_id}/countuserbot")

    if data == "botsmember":
        await bot_call(token, "answerCallbackQuery", {"callback_query_id": cb.get("id", "") if cb else "", "text": "✓"})
        if str(from_id) in botfree2 and botf2.strip():
            idbotfrom = file_lines(f"from_id/{from_id}/idbot")
            
            # Store bots data with better formatting
            bots_list = []
            for line in idbotfrom:
                ex = line.split("#")
                if len(ex) < 3:
                    continue
                idbot_b = ex[2].strip()
                userbot_b = "@" + ex[1].strip()
                in_val = "infobot " + ex[1].strip()
                del_val = "deletebot " + ex[1].strip()
                
                if len(idbot_b) > 4:
                    info_path = f"botmak/{idbot_b}/info"
                    if file_exists(info_path):
                        infobot_lines = read_file(info_path).split("\n")
                        userbott = infobot_lines[1] if len(infobot_lines) > 1 else ""
                        namebot = infobot_lines[2] if len(infobot_lines) > 2 else ""
                        s_p_p1_b = infobot_lines[6] if len(infobot_lines) > 6 else ""
                        
                        # Get bot members count
                        member_count = len(file_lines(f"botmak/{idbot_b}/NaMero/member")) if idbot_b else 0
                        
                        bots_list.append({
                            "username": userbot_b,
                            "name": namebot,
                            "type": s_p_p1_b,
                            "members": member_count,
                            "info_callback": in_val,
                            "delete_callback": del_val,
                            "url": f"t.me/{userbott}"
                        })
            
            # Build enhanced keyboard with better layout
            keyboard = {"inline_keyboard": []}
            
            # Add each bot with info and delete buttons
            for bot in bots_list:
                # Bot name and info button
                keyboard["inline_keyboard"].append([
                    {"text": f"✨ {bot['name']}", "callback_data": bot['info_callback']},
                    {"text": f"👥 {bot['members']}", "url": bot['url']}
                ])
                # Delete and transfer buttons
                keyboard["inline_keyboard"].append([
                    {"text": "🗑️ حذف البوت", "callback_data": bot['delete_callback']},
                    {"text": "↔️ نقل الملكية", "callback_data": "naglbotmember " + bot['username'].replace("@", "")}
                ])
            
            # Aggregate actions
            keyboard["inline_keyboard"].append([{"text": "📢 إذاعة لكل البوتات", "callback_data": "sendpostbotsall"}])
            keyboard["inline_keyboard"].append([{"text": "• رجوع •", "callback_data": "freebot"}])
            
            delete_file(f"from_id/{from_id}/yes")
            
            # Enhanced message text
            bot_count = len(bots_list)
            member_total = sum(bot['members'] for bot in bots_list)
            message_text = f"""
📊 *قائمة البوتات المصنوعة* 
━━━━━━━━━━━━━━━━━━━━━
🤖 عدد البوتات: **{bot_count}**
👥 إجمالي الأعضاء: **{member_total}**
━━━━━━━━━━━━━━━━━━━━━

اختر البوت للمزيد من الخيارات:
"""
            
            await bot_call(token, "editMessageText", {
                "chat_id": chat_id, 
                "message_id": message_id, 
                "text": message_text, 
                "parse_mode": "MarkDown",
                "reply_markup": json.dumps(keyboard)
            })
        else:
            keyboard = {
                "inline_keyboard": [[
                    {"text": "✨ صنع بوت جديد", "callback_data": "sn3botfre"},
                    {"text": "• رجوع •", "callback_data": "freebot"}
                ]]
            }
            await bot_call(token, "editMessageText", {
                "chat_id": chat_id, 
                "message_id": message_id, 
                "text": "❌ *لا توجد بوتات مصنوعة حالياً*\n\nاضغط 'صنع بوت جديد' لإنشاء بوتك الأول!", 
                "parse_mode": "MarkDown",
                "reply_markup": json.dumps(keyboard)
            })
        return {"ok": True}

    if data and data.startswith("infobot "):
        await bot_call(token, "answerCallbackQuery", {"callback_query_id": cb.get("id", "") if cb else "", "text": "ℹ️ جاري تحميل المعلومات..."})
        userbot_q = data.replace("infobot ", "").strip()
        idbots_q = read_file(f"user/{userbot_q}").strip()
        info_path = f"botmak/{idbots_q}/info"
        if file_exists(info_path):
            infobot_lines = read_file(info_path).split("\n")
            userbot_d = infobot_lines[1] if len(infobot_lines) > 1 else ""
            namebot_d = infobot_lines[2] if len(infobot_lines) > 2 else ""
            id_d = infobot_lines[3] if len(infobot_lines) > 3 else ""
            idbots_d = infobot_lines[4] if len(infobot_lines) > 4 else ""
            s_p_p1_d = infobot_lines[6] if len(infobot_lines) > 6 else ""
            
            # Get detailed statistics
            mm_d = file_lines(f"botmak/{idbots_d}/NaMero/member") if idbots_d else []
            ban_d = file_lines(f"botmak/{idbots_d}/NaMero/ban") if idbots_d else []
            co_d = len(mm_d)
            ban_count = len(ban_d)
            
            # Enhanced info message
            info_message = f"""
📋 *معلومات البوت الكاملة*
━━━━━━━━━━━━━━━━━━━━
🤖 الاسم: `{namebot_d}`
📱 المعرف: `@{userbot_d}`
🆔 الآيدي: `{idbots_d}`
📝 النوع: {s_p_p1_d}
━━━━━━━━━━━━━━━━━━━━
👥 الأعضاء: **{co_d}**
🚫 المحظورين: **{ban_count}**
━━━━━━━━━━━━━━━━━━━━
"""
            
            await bot_call(token, "editMessageText", {
                "chat_id": chat_id, 
                "message_id": message_id, 
                "text": info_message,
                "parse_mode": "MarkDown", 
                "disable_web_page_preview": "true", 
                "reply_markup": json.dumps({
                    "inline_keyboard": [
                        [{"text": "🔗 الدخول للبوت", "url": f"https://t.me/{userbot_d}"}],
                        [
                            {"text": "🗑️ حذف", "callback_data": "deletebot " + userbot_d}, 
                            {"text": "↔️ نقل", "callback_data": "naglbotmember " + userbot_d}
                        ],
                        [{"text": "📢 إذاعة", "callback_data": "sendpostbots " + userbot_d}],
                        [{"text": "◀️ رجوع", "callback_data": "botsmember"}],
                    ]
                })
            })
        return {"ok": True}

    if data and data.startswith("deletebot "):
        await bot_call(token, "answerCallbackQuery", {"callback_query_id": cb.get("id", "") if cb else "", "text": "⚠️ تأكيد الحذف..."})
        userbot_del = data.replace("deletebot ", "").strip()
        idbots_del = read_file(f"user/{userbot_del}").strip()
        countbot_lines = file_lines(f"from_id/{from_id}/countbot")
        
        if userbot_del in countbot_lines and idbots_del:
            # Confirmation message
            confirm_keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ نعم، احذف البوت", "callback_data": "confirm_del " + userbot_del},
                        {"text": "❌ الغاء", "callback_data": "botsmember"}
                    ]
                ]
            }
            
            await bot_call(token, "editMessageText", {
                "chat_id": chat_id, 
                "message_id": message_id, 
                "text": f"""
⚠️ *تأكيد حذف البوت*
━━━━━━━━━━━━━━━━━━
🤖 البوت: `@{userbot_del}`
🆔 الآيدي: `{idbots_del}`
━━━━━━━━━━━━━━━━━━

⚠️ هل أنت متأكد من حذف البوت؟
سيتم حذف جميع البيانات المرتبطة به!

تحذير: هذا الإجراء لا يمكن التراجع عنه!
""",
                "parse_mode": "MarkDown",
                "reply_markup": json.dumps(confirm_keyboard)
            })
        return {"ok": True}

    if data and data.startswith("confirm_del "):
        await bot_call(token, "answerCallbackQuery", {"callback_query_id": cb.get("id", "") if cb else "", "text": "🗑️ جاري حذف البوت..."})
        userbot_del = data.replace("confirm_del ", "").strip()
        idbots_del = read_file(f"user/{userbot_del}").strip()
        countbot_lines = file_lines(f"from_id/{from_id}/countbot")
        
        if userbot_del in countbot_lines and idbots_del:
            # Delete from countbot
            countbot_content = read_file(f"from_id/{from_id}/countbot").replace(f"{userbot_del}\n", "")
            write_file(f"from_id/{from_id}/countbot", countbot_content)

            # Delete from idbot
            ussss = f"{userbot_del}==code#{userbot_del}#{idbots_del}"
            idbot_content = read_file(f"from_id/{from_id}/idbot").replace(f"{ussss}\n", "")
            write_file(f"from_id/{from_id}/idbot", idbot_content)

            # Delete user mapping
            delete_file(f"user/{userbot_del}")

            # Delete from countuserbot
            us2 = f"@{userbot_del}"
            countuserbot_content = read_file(f"from_id/{from_id}/countuserbot").replace(f"{us2}\n", "")
            write_file(f"from_id/{from_id}/countuserbot", countuserbot_content)

            # Delete from infoidbots
            infoidbots_content = read_file("infoidbots").replace(f"{idbots_del}\n", "")
            write_file("infoidbots", infoidbots_content)

            # حذف بيانات البوت من قاعدة البيانات
            from db_config import db_delete_bot_data
            db_delete_bot_data(f"botmak/{idbots_del}")

            # Delete NAMERO config file
            delete_file(f"NAMERO/{idbots_del}.py")

            # Success message
            success_message = f"""
✅ *تم حذف البوت بنجاح!*
━━━━━━━━━━━━━━━━━━
✨ البوت المحذوف: `@{userbot_del}`
🆔 الآيدي: `{idbots_del}`
━━━━━━━━━━━━━━━━━━

💡 إذا كان ذلك عن طريق الخطأ:
يمكنك إنشاء بوت جديد بنفس الاسم 
واستعادة البيانات من النسخة الاحتياطية
"""
            
            await bot_call(token, "editMessageText", {
                "chat_id": chat_id, 
                "message_id": message_id, 
                "text": success_message,
                "parse_mode": "MarkDown",
                "reply_markup": json.dumps({
                    "inline_keyboard": [[
                        {"text": "🔄 رجوع للقائمة", "callback_data": "botsmember"}
                    ]]
                })
            })
        return {"ok": True}

    code_json = read_json("code", {})

    if data and data.startswith("naglbotmember "):
        userbot_tr = data.replace("naglbotmember ", "").strip()
        import secrets as sec
        import string as str_mod
        alphabet = str_mod.ascii_letters + str_mod.digits
        code = "".join(sec.choice(alphabet) for _ in range(35))
        idbots_tr = read_file(f"user/{userbot_tr}").strip()
        info_path = f"botmak/{idbots_tr}/info"
        infobot_lines = read_file(info_path).split("\n") if file_exists(info_path) else []
        userbot_tr2 = infobot_lines[1] if len(infobot_lines) > 1 else ""
        id_tr = infobot_lines[3] if len(infobot_lines) > 3 else ""
        s_p_p1_tr = infobot_lines[6] if len(infobot_lines) > 6 else ""
        code_json_data = read_json("code", {})
        if "info" not in code_json_data:
            code_json_data["info"] = {}
        code_json_data["info"][code] = {"st": "yes", "idbot": idbots_tr, "userbot": userbot_tr2, "admin": str(id_tr)}
        write_json("code", code_json_data)
        maker_bot = USER_BOT_NAMERO
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"\n• رابط النقل : https://t.me/{maker_bot}?start={code}\n• أرسله إلى الشخص المراد نقل البوت إليه .\n", "parse_mode": "markdown", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": " • رجوع •", "callback_data": "botsmember"}]]})})
        return {"ok": True}

    if text and re.match(r'^/[Ss]tart (.+)', text):
        m = re.match(r'^/[Ss]tart (.+)', text)
        code = m.group(1)
        code_json_data = read_json("code", {})
        code_info = code_json_data.get("info", {}).get(code, {})
        st = code_info.get("st")
        idbots_c = code_info.get("idbot")
        userbots_c = code_info.get("userbot")
        admin_c = code_info.get("admin")
        if st == "yes" and admin_c and str(admin_c) != str(from_id):
            idbots_c2 = read_file(f"user/{userbots_c}").strip()
            botfrom_c = file_lines(f"from_id/{admin_c}/countbot")
            if userbots_c in botfrom_c and idbots_c2:
                info_path = f"botmak/{idbots_c2}/info"
                infobot_lines = read_file(info_path).split("\n") if file_exists(info_path) else []
                userbot_c = infobot_lines[1] if len(infobot_lines) > 1 else ""
                namebot_c = infobot_lines[2] if len(infobot_lines) > 2 else ""
                id_c = infobot_lines[3] if len(infobot_lines) > 3 else ""
                idbots_c3 = infobot_lines[4] if len(infobot_lines) > 4 else ""
                s_p_p1_c = infobot_lines[6] if len(infobot_lines) > 6 else ""

                us_cnt = read_file(f"from_id/{admin_c}/countbot").replace(f"{userbot_c}\n", "")
                write_file(f"from_id/{admin_c}/countbot", us_cnt)

                ussss_c = f"{userbot_c}==code#{userbot_c}#{idbots_c3}"
                us_id = read_file(f"from_id/{admin_c}/idbot").replace(f"{ussss_c}\n", "")
                write_file(f"from_id/{admin_c}/idbot", us_id)

                us2_c = f"》- @{userbot_c}"
                us1_c = read_file(f"from_id/{admin_c}/countuserbot").replace(f"{us2_c}\n", "")
                write_file(f"from_id/{admin_c}/countuserbot", us1_c)

                us5_c = read_file(f"botmak/{idbots_c3}/info").replace(str(admin_c), str(from_id))
                write_file(f"botmak/{idbots_c3}/info", us5_c)

                ensure_dir(f"from_id/{from_id}")
                append_file(f"from_id/{from_id}/countuserbot", f"》- @{userbot_c}\n")
                append_file(f"from_id/{from_id}/countbot", f"{userbot_c}\n")

                idbotfrom_new = file_lines(f"from_id/{from_id}/idbot")
                if ussss_c not in idbotfrom_new:
                    append_file(f"from_id/{from_id}/idbot", f"{ussss_c}\n")

                botfree_new = file_lines("botfreeid")
                if str(from_id) not in botfree_new:
                    append_file("botfreeid", f"{from_id}\n")

                write_file(f"botmak/{idbots_c3}/admin", str(from_id))

                us6_c = read_file(f"botmak/{idbots_c3}/NaMero").replace(str(admin_c), str(from_id)) if file_exists(f"botmak/{idbots_c3}/NaMero") else ""
                if us6_c:
                    write_file(f"botmak/{idbots_c3}/NaMero", us6_c)

                zune_c = read_json(f"botmak/{idbots_c3}/zune", {})
                if zune_c:
                    zune_c_str = json.dumps(zune_c, ensure_ascii=False).replace(str(admin_c), str(from_id))
                    write_file(f"botmak/{idbots_c3}/zune", zune_c_str)

                mm_c = file_lines(f"botmak/{idbots_c3}/NaMero/member") if file_exists(f"botmak/{idbots_c3}/NaMero/member") else []
                co_c = len(mm_c)

                await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"\n• تم تحويل البوت إليك \n• معلومات البوت :\n\n- اسم البوت : {namebot_c}\n- معرف البوت : {userbots_c}\n- أيدي البوت : {idbots_c3}\n- توكن البوت : محمي\n\n• عدد مستخدمين البوت : {co_c}\n• نوع البوت المصنوع : {s_p_p1_c}\n"})
                await bot_call(token, "sendMessage", {"chat_id": admin_c, "text": f"\nتم نقل [بوت](t.me/{userbot_c}) الى [{from_id}](tg://user?id={from_id})\n", "parse_mode": "MarkDown"})

                code_json_data2 = read_json("code", {})
                if "info" in code_json_data2:
                    code_json_data2["info"].pop(code, None)
                write_json("code", code_json_data2)
            else:
                await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "ارسال /start .!\n", "reply_to_message_id": message_id})
        elif str(admin_c) == str(from_id):
            await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "\n• لا يمكنك نقل البوت إلى نفسك !\n", "reply_to_message_id": message_id})
        return {"ok": True}

    datatime_json = read_json("datatime", {})
    datatimesend = datatime_json.get("info", {}).get(str(from_id), {}).get("date", "")

    if data == "sendpostbotsall":
        now = datetime.now(timezone(timedelta(hours=1)))
        day = now.strftime("%Y-%m-%d")
        if day != datatimesend:
            datatime_json2 = read_json("datatime", {})
            if "info" not in datatime_json2:
                datatime_json2["info"] = {}
            if str(from_id) not in datatime_json2["info"]:
                datatime_json2["info"][str(from_id)] = {}
            datatime_json2["info"][str(from_id)]["date"] = day
            write_json("datatime", datatime_json2)
            write_file(f"from_id/{from_id}/amr", "sendpostbotsall")
            infobots_m = read_file(f"from_id/{from_id}/countuserbot")
            infobots_member = " " if infobots_m else "لم تقم بصنع اي بوت مسبقا ❌ً"
            await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": f" \n• أرسل النص الآن الرسالة إلى جميع مشتركين بوتاتك المصنوعة .\n{infobots_member}\n", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "• رجوع • ", "callback_data": "botsmember"}]]})})
        else:
            await bot_call(token, "answerCallbackQuery", {"callback_query_id": cb.get("id", "") if cb else "", "text": f"\n• معذرة لاتستطيع عمل الاذاعة لكل بوتاتك المصنوعة اكثر من مرة واحدة،\n-فقط في اليوم {day} \n- ستتمكن من نشر الاذاعة غداً\n ", "show_alert": "true"})
        return {"ok": True}

    if text and amr_mem == "sendpostbotsall" and msg and not data:
        write_file(f"from_id/{from_id}/amr", "")
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": "جاري عمل الاذاعة ", "reply_to_message_id": message_id})
        bots_user = file_lines(f"from_id/{from_id}/countbot")
        coo = len(bots_user)
        co = 0
        for userbots_b in bots_user:
            if not userbots_b:
                continue
            idbots_b = read_file(f"user/{userbots_b}").strip()
            token_b_path = f"NAMERO/{idbots_b}.py"
            token_b = ""
            if file_exists(token_b_path):
                content = read_file(token_b_path)
                m_re = re.search(r'tokenbot\s*=\s*["\'](.+?)["\']', content)
                if m_re:
                    token_b = m_re.group(1)
            if token_b:
                mm_b = file_lines(f"botmak/{idbots_b}/NaMero/member") if file_exists(f"botmak/{idbots_b}/NaMero/member") else []
                for uid_b in mm_b:
                    if uid_b:
                        await bot_call(token_b, "sendMessage", {"chat_id": uid_b, "text": text})
                        co += 1
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"- تمت الاذاعة في جميع البوتات المصنوعة \n- تم الارسال الى {co} مستخدم.\n- عدد البوتات : {coo}\n", "reply_to_message_id": message_id})
        return {"ok": True}

    if data == "uplode":
        write_file(f"from_id/{from_id}/amr", "uplode")
        await bot_call(token, "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": " *أرسل ملف python الآن !*\n\nبشروط :\n\n1. لا يحتوي الملف على أي أخطاء برمجيه\n\n2. يجب أن يكون عمله دون الحاجة إلى اتصال بخدمات خارجية (api)\n\n3. لا يحتوي على معرف لقناة أو مطور ( يتم وضع معرف المطور عند صنع البوت من قبل المستخدم )\n", "parse_mode": "MarkDown", "disable_web_page_preview": "true", "reply_markup": json.dumps({"inline_keyboard": [[{"text": "• رجوع • ", "callback_data": "freebot"}]]})})
        return {"ok": True}

    if msg and amr_mem == "uplode" and not data:
        if document:
            write_file(f"from_id/{from_id}/amr", "")
            file_id_doc = document.get("file_id")
            saleh_id = get_saleh_admin()
            send_ok = False
            try:
                r1 = await bot_call(token, "sendDocument", {"chat_id": saleh_id, "document": file_id_doc})
                if r1.get("ok"):
                    await bot_call(token, "sendMessage", {
                        "chat_id": saleh_id,
                        "text": (
                            f"*👾 طلب ارسال ملف جديد*\n"
                            f"معلومات المرسل 🌐\n"
                            f"الاسم: *{name}*\n"
                            f"الايدي: {from_id}\n"
                            f"المعرف: @{user}\n"
                        ),
                        "parse_mode": "MarkDown",
                        "disable_web_page_preview": True,
                    })
                    send_ok = True
            except Exception:
                send_ok = False
            if send_ok:
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": "✅ *تم إرسال الملف إلى المشرفين*\nسيتم مراجعته وسيتم وضع اسمك في البوتات 🔰",
                    "parse_mode": "MarkDown",
                })
            else:
                await bot_call(token, "sendMessage", {
                    "chat_id": chat_id,
                    "text": (
                        "⚠️ *فشل إرسال الملف للمشرف*\n\n"
                        "يُرجى إرسال الملف مباشرةً عبر:\n"
                        "[@Voltees](https://t.me/Voltees)"
                    ),
                    "parse_mode": "MarkDown",
                    "disable_web_page_preview": False,
                })
        else:
            await bot_call(token, "sendMessage", {
                "chat_id": chat_id,
                "text": "⚠️ قم بإرسال ملف فقط (document)",
                "reply_markup": json.dumps({"inline_keyboard": [[{"text": "• رجوع • ", "callback_data": "freebot"}]]}),
            })
        return {"ok": True}

    if text == "/id":
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": str(chat_id)})
        return {"ok": True}
    if text == "/name":
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": name})
        return {"ok": True}
    if text == "/user":
        await bot_call(token, "sendMessage", {"chat_id": chat_id, "text": f"[@{user}]"})
        return {"ok": True}

    return {"ok": True}



_POLL_TIMEOUT = 30
_RETRY_DELAY  = 0.5  # تقليل من 5 إلى 0.5 ثانية
_MAX_ERRORS   = 10


async def _delete_webhook(token: str):
    try:
        result = await bot_call(token, "deleteWebhook", {"drop_pending_updates": False})
        if result.get("ok"):
            print("[Maker] ✅ تم حذف الويب هوك - جاهز للـ Polling")
        else:
            print(f"[Maker] ⚠️ deleteWebhook: {result.get('description')}")
    except Exception as e:
        print(f"[Maker] ❌ خطأ في deleteWebhook: {e}")


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
        print(f"[Maker] getUpdates error: {e}")
    return []


async def _run_polling():
    token = config.TOKEN.strip()
    if not token:
        print("[Maker] ❌ token فارغ أو غير موجود في config.py")
        return

    print("=" * 55)
    print("  NaMero Robots — Maker Bot Polling")
    print("  by @Voltees")
    print("=" * 55)

    await _delete_webhook(token)

    offset      = 0
    offset_file = "maker_offset"
    error_count = 0
    
    # استرجاع آخر offset محفوظ
    if file_exists(offset_file):
        try:
            offset = int(read_file(offset_file).strip())
            print(f"[Maker] 📂 تم استرجاع آخر offset: {offset}")
        except:
            offset = 0

    while True:
        try:
            updates = await _get_updates(token, offset)
            error_count = 0

            for update in updates:
                update_id = update.get("update_id", 0)
                try:
                    body = json.dumps(update).encode("utf-8")
                    await handle_maker(body)
                except Exception as e:
                    print(f"[Maker] ❌ خطأ في التحديث {update_id}: {e}")
                finally:
                    # حفظ الـ offset دائماً بعد معالجة التحديث (نجح أم فشل)
                    offset = update_id + 1
                    write_file(offset_file, str(offset))

            # sleep بسيط بين الطلبات لتجنب إرهاق الـ API
            if not updates:
                await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            print("[Maker] ⛔ تم إيقاف الـ Polling")
            break
        except Exception as e:
            error_count += 1
            print(f"[Maker] ❌ خطأ ({error_count}/{_MAX_ERRORS}): {e}")
            
            if error_count >= _MAX_ERRORS:
                print(f"[Maker] ⚠️ وصلنا لـ {_MAX_ERRORS} أخطاء متتالية، سيتم إعادة المحاولة...")
                await asyncio.sleep(2)
                error_count = 0
            else:
                await asyncio.sleep(1)


async def _main():
    loop = asyncio.get_running_loop()
    task = asyncio.create_task(_run_polling())

    def _stop(sig):
        print(f"\n[Maker] إشارة إيقاف ({sig.name})")
        task.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _stop, sig)
        except (NotImplementedError, RuntimeError):
            pass

    await asyncio.gather(task, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(_main())
