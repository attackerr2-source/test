#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 أداة لعرض وفحص قاعدة البيانات
استخدام: python view_database.py
"""

import sqlite3
import json
import sys

DB_PATH = "db/bot_data.db"

def view_all_data():
    """عرض جميع البيانات في قاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("🔍 عرض قاعدة البيانات الكاملة")
    print("=" * 70)
    
    cursor.execute("""
        SELECT content_key, content_type, content_data 
        FROM content_storage 
        ORDER BY content_key
    """)
    
    rows = cursor.fetchall()
    
    if not rows:
        print("❌ لا توجد بيانات")
        return
    
    for i, (key, ctype, data) in enumerate(rows, 1):
        print(f"\n{i}. 📌 {key}")
        print(f"   النوع: {ctype}")
        print(f"   الحجم: {len(data)} بايت")
        
        if ctype == 'json' and data:
            try:
                parsed = json.loads(data)
                print(f"   البيانات:")
                for line in json.dumps(parsed, ensure_ascii=False, indent=6).split('\n'):
                    print(f"   {line}")
            except:
                print(f"   البيانات: {data}")
        elif data:
            print(f"   البيانات: {data}")
        else:
            print(f"   البيانات: (فارغة)")
    
    print("\n" + "=" * 70)
    print(f"✅ المجموع: {len(rows)} عنصر")
    print("=" * 70)
    
    conn.close()

def search_key(search_term):
    """البحث عن مفتاح معين"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT content_key, content_type, content_data 
        FROM content_storage 
        WHERE content_key LIKE ?
        ORDER BY content_key
    """, (f"%{search_term}%",))
    
    rows = cursor.fetchall()
    
    if not rows:
        print(f"❌ لم يتم العثور على '{search_term}'")
        return
    
    print(f"\n✅ نتائج البحث عن '{search_term}':\n")
    
    for key, ctype, data in rows:
        print(f"📌 {key} ({ctype}):")
        if ctype == 'json' and data:
            try:
                parsed = json.loads(data)
                print(json.dumps(parsed, ensure_ascii=False, indent=2))
            except:
                print(data)
        else:
            print(data if data else "(فارغة)")
        print()
    
    conn.close()

def export_to_file(output_file="database_backup.json"):
    """تصدير جميع البيانات إلى ملف JSON"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT content_key, content_type, content_data FROM content_storage")
    rows = cursor.fetchall()
    
    backup = {}
    for key, ctype, data in rows:
        if ctype == 'json':
            try:
                backup[key] = json.loads(data)
            except:
                backup[key] = data
        else:
            backup[key] = data
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)
    
    print(f"✅ تم تصدير البيانات إلى {output_file}")
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "search" and len(sys.argv) > 2:
            search_key(sys.argv[2])
        elif sys.argv[1] == "export":
            export_to_file(sys.argv[2] if len(sys.argv) > 2 else "database_backup.json")
        else:
            print("الاستخدام:")
            print("  python view_database.py              # عرض جميع البيانات")
            print("  python view_database.py search setting    # البحث عن كلمة")
            print("  python view_database.py export file.json  # تصدير البيانات")
    else:
        view_all_data()
