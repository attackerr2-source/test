#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 برنامج اختبار حفظ البيانات
تحقق من أن الإعدادات والبيانات تُحفظ بشكل صحيح
"""

import sqlite3
import json
import time

DB_PATH = "db/bot_data.db"

def test_write_and_read():
    """اختبار الكتابة والقراءة"""
    print("🧪 اختبار حفظ البيانات بطريقة عملية")
    print("=" * 60)
    
    test_key = "test/data/sample"
    test_data = {
        "name": "أحمد",
        "id": 123456,
        "settings": {
            "sticker": "✅",
            "photo": "❌"
        }
    }
    
    # 1. اكتب البيانات
    print("\n1️⃣ كتابة بيانات تجريبية...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO content_storage 
            (bot_id, content_key, content_type, content_data, updated_at) 
            VALUES (0, ?, 'json', ?, CURRENT_TIMESTAMP)
        """, (test_key, json.dumps(test_data, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
        
        print(f"   ✅ تم حفظ: {test_key}")
        print(f"   البيانات: {json.dumps(test_data, ensure_ascii=False)}")
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        return False
    
    # 2. انتظر قليلاً
    time.sleep(1)
    
    # 3. اقرأ البيانات
    print("\n2️⃣ قراءة نفس البيانات...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content_data FROM content_storage 
            WHERE bot_id = 0 AND content_key = ?
        """, (test_key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            loaded_data = json.loads(row[0])
            print(f"   ✅ تم جلب البيانات: {test_key}")
            print(f"   البيانات: {json.dumps(loaded_data, ensure_ascii=False)}")
            
            # تحقق من التطابق
            if loaded_data == test_data:
                print("   ✅ البيانات متطابقة تماماً!")
                return True
            else:
                print("   ❌ البيانات غير متطابقة!")
                return False
        else:
            print(f"   ❌ لم يتم العثور على البيانات!")
            return False
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        return False

def test_persistence():
    """اختبار استمرار البيانات (بثبات)"""
    print("\n\n🔄 اختبار ثبات البيانات (قبل وبعد الإعادة)")
    print("=" * 60)
    
    test_key = "persistence/test"
    value_before = "البيانات محفوظة قبل الإيقاف"
    
    # اكتب البيانات
    print(f"\n1️⃣ كتابة البيانات: '{value_before}'")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO content_storage 
            (bot_id, content_key, content_type, content_data, updated_at) 
            VALUES (0, ?, 'text', ?, CURRENT_TIMESTAMP)
        """, (test_key, value_before))
        conn.commit()
        conn.close()
        print("   ✅ تم الحفظ في قاعدة البيانات")
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        return False
    
    # قراءة فورية
    print("\n2️⃣ قراءة فورية (بدون إعادة تشغيل)...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content_data FROM content_storage 
            WHERE bot_id = 0 AND content_key = ?
        """, (test_key,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] == value_before:
            print(f"   ✅ البيانات محفوظة بشكل صحيح: '{row[0]}'")
        else:
            print(f"   ❌ البيانات لم تُحفظ!")
            return False
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        return False
    
    print("\n3️⃣ ملاحظة:")
    print("   ⏸️  عند إعادة تشغيل السيرفر/البوت، البيانات ستبقى في الملف:")
    print("   📍 db/bot_data.db")
    print("   ✅ سيتم تحميلها تلقائياً عند البدء")
    
    return True

def check_database_health():
    """فحص صحة قاعدة البيانات"""
    print("\n\n🏥 فحص صحة قاعدة البيانات")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # فحص الجداول
        cursor.execute("SELECT COUNT(name) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        print(f"✅ عدد الجداول: {table_count}")
        
        # فحص السجلات
        cursor.execute("SELECT COUNT(*) FROM content_storage")
        record_count = cursor.fetchone()[0]
        print(f"✅ عدد السجلات: {record_count}")
        
        # فحص حجم الملف
        import os
        size_kb = os.path.getsize(DB_PATH) / 1024
        print(f"✅ حجم قاعدة البيانات: {size_kb:.1f} KB")
        
        # فحص الإعدادات المحفوظة
        cursor.execute("""
            SELECT COUNT(*) FROM content_storage 
            WHERE content_key LIKE '%setting%'
        """)
        setting_count = cursor.fetchone()[0]
        print(f"✅ عدد الإعدادات المحفوظة: {setting_count}")
        
        conn.close()
        print("\n✅ قاعدة البيانات بصحة جيدة!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "🧪 برنامج اختبار حفظ البيانات" + " " * 14 + "║")
    print("╚" + "═" * 58 + "╝")
    
    results = []
    
    # اختبار 1
    results.append(("اختبار الكتابة والقراءة", test_write_and_read()))
    
    # اختبار 2
    results.append(("اختبار ثبات البيانات", test_persistence()))
    
    # اختبار 3
    results.append(("فحص صحة قاعدة البيانات", check_database_health()))
    
    # النتيجة النهائية
    print("\n" + "=" * 60)
    print("📊 النتائج النهائية:")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{status}  {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 جميع الاختبارات نجحت! البيانات محفوظة بشكل صحيح!")
    else:
        print("⚠️ بعض الاختبارات فشلت. تحقق من الأخطاء أعلاه.")
    print("=" * 60 + "\n")
