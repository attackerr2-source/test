"""
Central Configuration File - ملف التكوين المركزي
جميع الإعدادات الأساسية في مكان واحد
"""

from pathlib import Path

# ============ المسارات ============
BASE_DIR = Path.cwd()
DB_DIR = BASE_DIR / "db"
LOGS_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / ".cache"

DB_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# ============ قاعدة البيانات ============
DATABASE_PATH = str(DB_DIR / "bot_data.db")

# ============ بيانات الاعتماد ============
TOKEN = "6509626440:AAEdFCWwvnpGDVB785FA6Noco9cu5ulGFCI"
DEVELOPER_ID = 1116907157
DEVELOPER_USERNAME = "namero"
ADMIN_IDS = [1116907157, 123456789, 987654321]

TELEGRAM_API_URL = "https://api.telegram.org"

# ============ إعدادات كانت في ملفات نصية (تم نقلها هنا) ============
# يمكن تجاوز هذه القيم من قاعدة البيانات عبر system_config
SALEH_ADMIN = str(DEVELOPER_ID)
USER_BOT_NAMERO = ""        # يوزرنيم بوت الصانع (يُحدَّث من DB)
XX = DEVELOPER_USERNAME     # اسم المطور يظهر في رسائل البوت
XXX = ""                    # رابط فيديو شرح صنع التوكن
BASE_URL = ""               # رابط الويب هوك (غير مستخدم في polling)

# ============ إعدادات الأداء ============
POLLING_TIMEOUT = 30
POLLING_INTERVAL = 1
MAX_RETRIES = 3
RETRY_DELAY = 5
CONNECTION_POOL_SIZE = 50
REQUEST_TIMEOUT = 30.0

# ============ إعدادات الإذاعة ============
BROADCAST_BATCH_SIZE = 50
BROADCAST_DELAY = 0.1

# ============ أنماط البوتات المدعومة ============
BOT_TYPES = {
    "1": "تواصل",
    "2": "متجر",
    "3": "تذكير",
    "4": "إحصائيات",
    "5": "ألعاب",
}

# قائمة القنوات الإلزامية
REQUIRED_CHANNELS = []

REQUIRED_CHANNELS_MESSAGE = (
    "🛡️ لتستخدم بوت المصنع، يرجى الاشتراك في القنوات التالية أولاً:\n\n"
    "بعد الإشتراك، أرسل /start مجدداً."
)

# ============ الرسائل الافتراضية ============
DEFAULT_MESSAGES = {
    "welcome": "👋 مرحباً {name}! أهلاً بك في البوت.",
    "start": "🚀 البوت يعمل الآن.",
    "bot_off": "🔌 البوت موقوف حالياً. حاول لاحقاً.",
    "not_admin": "❌ هذا الأمر مخصص للأدمنية فقط.",
    "broadcast_sent": "✅ تمّت الإذاعة! تم الإرسال إلى: {success}, فشل: {failed}",
}

# ============ إعدادات السجل ============
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============ إعدادات الكاش ============
CACHE_TTL = 3600
CACHE_SIZE = 1000

# ============ إعدادات الأمان ============
MAX_MESSAGE_LENGTH = 4096
MAX_BROADCAST_SIZE = 1000
RATE_LIMIT = 30


# ============ وظائف المساعدة ============
def get_database_path() -> str:
    return DATABASE_PATH

def get_admin_ids() -> list:
    return ADMIN_IDS

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def get_bot_type_name(bot_type_id: str) -> str:
    return BOT_TYPES.get(bot_type_id, "غير معروف")

def get_all_admin_ids_str() -> list:
    """قائمة جميع IDs الأدمنية كنص"""
    return [str(x) for x in ADMIN_IDS if x]
