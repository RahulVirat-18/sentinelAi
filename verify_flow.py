#!/usr/bin/env python
"""Complete verification of the report generation flow"""

from app import create_app
from app.db_connector import get_db
import time

app = create_app()

with app.app_context():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    print("\n" + "="*80)
    print("COMPLETE DATABASE VERIFICATION")
    print("="*80)
    
    # 1. Show ALL evidence records (with and without reports)
    print("\n1️⃣  ALL EVIDENCE RECORDS (Including those without reports):")
    cursor.execute("""
        SELECT id, case_id, title, file_path,
               IF(analysis_report IS NULL, '❌ NO REPORT', '✅ HAS REPORT') as status,
               LENGTH(COALESCE(analysis_report, '')) as report_size,
               uploaded_at
        FROM evidence 
        WHERE case_id = 1
        ORDER BY uploaded_at DESC
    """)
    
    all_records = cursor.fetchall()
    print(f"\nTotal records for Case 1: {len(all_records)}")
    for i, record in enumerate(all_records, 1):
        print(f"  {i}. ID={record['id']}, Title='{record['title']}', Status={record['status']}, Size={record['report_size']} bytes, Date={record['uploaded_at']}")
    
    # 2. Show only records WITH reports (what saved_reports.html sees)
    print("\n2️⃣  ONLY RECORDS WITH REPORTS (What saved_reports page shows):")
    cursor.execute("""
        SELECT id, case_id, title, file_path,
               LENGTH(analysis_report) as report_size,
               uploaded_at
        FROM evidence 
        WHERE case_id = 1 AND analysis_report IS NOT NULL
        ORDER BY uploaded_at DESC
    """)
    
    reports = cursor.fetchall()
    print(f"\nReports visible in saved_reports page: {len(reports)}")
    for i, record in enumerate(reports, 1):
        print(f"  {i}. ID={record['id']}, Title='{record['title']}', Size={record['report_size']} bytes, Date={record['uploaded_at']}")
    
    # 3. Check the LATEST evidence in overview
    print("\n3️⃣  LATEST EVIDENCE (What overview.html shows):")
    cursor.execute("""
        SELECT id, title, analysis_report IS NOT NULL as has_report, uploaded_at
        FROM evidence 
        WHERE case_id = 1
        ORDER BY uploaded_at DESC 
        LIMIT 1
    """)
    latest = cursor.fetchone()
    if latest:
        print(f"  Latest: ID={latest['id']}, Title='{latest['title']}', Has_Report={latest['has_report']}, Date={latest['uploaded_at']}")
    else:
        print("  No evidence found!")
    
    # 4. Check filenames to see if timestamps are working
    print("\n4️⃣  FILE NAMING VERIFICATION (Check for timestamp prefixes):")
    cursor.execute("""
        SELECT id, file_path, title, uploaded_at
        FROM evidence 
        WHERE case_id = 1
        ORDER BY uploaded_at DESC
        LIMIT 5
    """)
    for record in cursor.fetchall():
        has_timestamp = record['file_path'].split('_')[0].isdigit()
        print(f"  ID={record['id']}: {record['file_path']} {'✅ HAS TIMESTAMP' if has_timestamp else '❌ NO TIMESTAMP'}")
    
    cursor.close()
    print("\n" + "="*80)
    print("END VERIFICATION")
    print("="*80 + "\n")
