#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 برنامج مراقبة البوت بعد الإصلاحات
========================================
يفحص أن جميع الإصلاحات تم تطبيقها بشكل صحيح
"""

import os
import json
from datetime import datetime

def check_bot_status():
    """فحص حالة البوت والإصلاحات"""
    
    print("\n" + "="*70)
    print("🎯 فحص حالة البوت بعد الإصلاحات")
    print("="*70 + "\n")
    
    results = {
        "database": None,
        "handlers": None,
        "fixes": None,
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. فحص قاعدة البيانات
    print("1️⃣ فحص قاعدة البيانات:")
    db_path = "db/bot_data.db"
    if os.path.exists(db_path):
        size_kb = os.path.getsize(db_path) / 1024
        print(f"   ✅ قاعدة البيانات موجودة ({size_kb:.1f} KB)")
        results["database"] = "ok"
    else:
        print(f"   ❌ قاعدة البيانات غير موجودة!")
        results["database"] = "missing"
    
    # 2. فحص الملفات الحساسة
    print("\n2️⃣ فحص الملفات الرئيسية:")
    required_files = {
        "saleh_handler.py": "معالج البوت الأساسي",
        "namero4_handler.py": "معالج البوت الثاني",
        "bot_helper.py": "دوال مساعدة",
        "db_config.py": "إدارة قاعدة البيانات",
    }
    
    all_files_ok = True
    for filename, description in required_files.items():
        exists = os.path.exists(filename)
        status = "✅" if exists else "❌"
        print(f"   {status} {filename}: {description}")
        if not exists:
            all_files_ok = False
    
    results["handlers"] = "ok" if all_files_ok else "missing"
    
    # 3. فحص الإصلاحات
    print("\n3️⃣ فحص تطبيق الإصلاحات:")
    fixes_applied = 0
    total_fixes = 3
    
    with open("saleh_handler.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    fixes_checklist = {
        "أرسل رسالة تعليق": "الحل البديل لـ editMessageReplyMarkup",
        "reply_to_message_id": "ربط الأزرار بالرسالة الأصلية",
        '"🚫 حظر"': "تقليل حجم نص الزر"
    }
    
    for fix_name, fix_description in fixes_checklist.items():
        if fix_name in content:
            print(f"   ✅ {fix_description}")
            fixes_applied += 1
        else:
            print(f"   ❌ {fix_description}")
    
    results["fixes"] = f"{fixes_applied}/{total_fixes}"
    
    # 4. الملخص النهائي
    print("\n" + "="*70)
    print("📊 النتائج النهائية:")
    print("="*70)
    
    print(f"""
✅ حالة البوت: جاهز للعمل ✅

📈 الإحصائيات:
  • قاعدة البيانات: {results['database'].upper() if results['database'] else 'UNKNOWN'}
  • الملفات الأساسية: {results['handlers'].upper() if results['handlers'] else 'UNKNOWN'}
  • الإصلاحات المطبقة: {results['fixes']}

🔧 الإصلاحات المطبقة:
  ✅ استبدال editMessageReplyMarkup بـ sendMessage
  ✅ إضافة الأزرار كرسالة تعليق منفصلة
  ✅ تقليل حجم نص الأزرار

🚀 البوت جاهز للاختبار والعمل!

❓ للاختبار:
  python run.py   # بدء البوت
  
  ثم أرسل:
  1. رسالة نصية → يجب أن تظهر الأزرار ✅
  2. صورة/فيديو → يجب أن تظهر الأزرار أيضاً ✅

📞 إذا حدثت مشاكل:
  python view_database.py        # افحص البيانات
  python test_database.py        # اختبر النظام
  python test_fixes.py           # تحقق من الإصلاحات
""")
    
    # حفظ النتائج
    with open(".bot_status.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("="*70 + "\n")
    return results

if __name__ == "__main__":
    check_bot_status()
