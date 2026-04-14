#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 برنامج نسخ احتياطي تلقائي للبيانات
يحفظ نسخة من قاعدة البيانات كل ساعة
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime
import time
import threading

DB_PATH = "db/bot_data.db"
BACKUP_DIR = "db_backups"

def create_backup_dir():
    """إنشاء مجلد النسخ الاحتياطية"""
    os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_database():
    """إنشاء نسخة احتياطية من قاعدة البيانات"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"bot_data_{timestamp}.db")
        
        # نسخ ملف قاعدة البيانات
        shutil.copy2(DB_PATH, backup_file)
        print(f"✅ تم إنشاء نسخة احتياطية: {backup_file}")
        
        # أيضاً حفظ نسخة JSON للقراءة
        export_to_json(f"db_backups/backup_{timestamp}.json")
        
        # احتفظ بآخر 10 نسخ فقط
        cleanup_old_backups()
        
    except Exception as e:
        print(f"❌ خطأ في النسخ الاحتياطي: {e}")

def export_to_json(output_file):
    """تصدير البيانات إلى ملف JSON قابل للقراءة"""
    try:
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
        
        conn.close()
        print(f"✅ تم تصدير إلى JSON: {output_file}")
    except Exception as e:
        print(f"❌ خطأ في التصدير: {e}")

def cleanup_old_backups(keep=10):
    """حذف النسخ القديمة (احتفظ بـ 10 فقط)"""
    try:
        if not os.path.exists(BACKUP_DIR):
            return
        
        files = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('bot_data_')])
        
        if len(files) > keep:
            for old_file in files[:-keep]:
                os.remove(os.path.join(BACKUP_DIR, old_file))
                print(f"🗑️  حذفت النسخة القديمة: {old_file}")
    except Exception as e:
        print(f"⚠️ خطأ في تنظيف النسخ: {e}")

def auto_backup_every_hour():
    """برنامج نسخ احتياطي كل ساعة"""
    create_backup_dir()
    
    while True:
        backup_database()
        print(f"⏰ النسخة التالية في: {datetime.now().strftime('%H:%M:%S')}")
        time.sleep(3600)  # كل ساعة

def start_background_backup():
    """بدء النسخ الاحتياطي في الخلفية"""
    thread = threading.Thread(target=auto_backup_every_hour, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    print("💾 برنامج النسخ الاحتياطي للبيانات")
    print("=" * 50)
    
    # إنشاء أول نسخة احتياطية
    create_backup_dir()
    backup_database()
    
    print("\n✅ يمكنك تشغيل هذا الملف في الخلفية:")
    print("  nohup python backup_database.py &")
    print("\nأو استخدمه في البرنامج الرئيسي:")
    print("  from backup_database import start_background_backup")
    print("  start_background_backup()")
