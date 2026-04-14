# NaMero Bot Factory — مصنع بوتات ناميرو

## نظرة عامة
نظام مصنع بوتات Telegram مبني بـ Python. يسمح للمستخدمين بإنشاء وإدارة بوتات Telegram متخصصة عبر بوت "Maker" مركزي.

## الهيكل
```
bot-main/
├── run.py              # نقطة البدء الرئيسية - Polling Mode فقط
├── config.py           # جميع الإعدادات المركزية (توكن، IDs الأدمنية...)
├── bot_helper.py       # الأدوات المشتركة: httpx client، قراءة/كتابة الملفات
├── maker_handler.py    # معالج بوت الصانع الرئيسي
├── saleh_handler.py    # معالج البوتات الفرعية المصنوعة
├── namero4_handler.py  # handler إضافي
├── db_config.py        # نظام الإعدادات عبر SQLite (بديل الملفات النصية)
└── db/
    ├── database.py     # DatabaseManager الكامل
    └── __init__.py
```

## وضع التشغيل
**Polling فقط — لا يوجد Webhook إطلاقاً**
- البوت الرئيسي يبدأ polling عند `run.py`
- عند إنشاء بوت فرعي، تُشغَّل `asyncio.create_task(_run_saleh_polling(bot_dir))`

## الإعدادات (config.py)
- `TOKEN`: توكن البوت الرئيسي
- `DEVELOPER_ID`: 1116907157
- `DEVELOPER_USERNAME`: namero
- `ADMIN_IDS`: قائمة IDs الأدمنية

## قاعدة البيانات (SQLite - db/bot_data.db)
### جدول `system_config` (بديل الملفات النصية المحذوفة)
| المفتاح | الوصف |
|---|---|
| `saleh_admin` | ID المشرف العام (= DEVELOPER_ID) |
| `userbot` | يوزرنيم بوت الصانع (يُحدَّث تلقائياً من getMe) |
| `xx` | اسم المطور يظهر في رسائل البوت |
| `xxx` | رابط شرح صنع التوكن (اختياري) |
| `base_url` | رابط الويب هوك (غير مستخدم في Polling) |

## الإصلاحات المنجزة (آخر تحديث)

### 1. إصلاح البطء الشديد - persistent httpx client
**المشكلة**: كان `bot_helper.py` يفتح اتصال TCP+TLS جديد لكل طلب API واحد.
**الحل**: استخدام `httpx.AsyncClient` مشترك واحد مع connection pooling (100 اتصال، 30 keepalive).

### 2. إزالة الملفات النصية
**الملفات المحذوفة**: `userbot`, `xx`, `xxx`, `saleh_admin`, `base_url`
**البديل**: SQLite `system_config` عبر `db_config.py` مع fallback لـ `config.py`

### 3. إصلاح إنشاء البوتات الفرعية
- إصلاح رسالة النجاح: إذا فشل `editMessageText`، يُرسَل `sendMessage` جديد
- إصلاح زر URL الفارغ عند `XXX` = "" (يُعيد رابط المطور)
- حذف Webhook تلقائياً عند إنشاء كل بوت جديد

### 4. إعادة تحميل makerinve
`saleh_handler.py` الآن يُعيد تحميل إعدادات المصنع (`botmak/NAMERO`) في كل دورة polling.

### 5. إصلاح saleh_admin
`_run_polling` في `saleh_handler.py` يقرأ `saleh_admin` من قاعدة البيانات بدلاً من ملف.

### 6. TOKEN من config.py
`maker_handler._run_polling()` يستخدم `config.TOKEN` مباشرة بدلاً من `read_file("token")`.

## تشغيل البوت
```bash
cd bot-main
python run.py
```

## الاعتماديات
- `httpx` — HTTP client مع connection pooling
- `asyncio` — المعالجة غير المتزامنة
- `sqlite3` — مدمج في Python
