#!/usr/bin/env python
"""Debug script to inspect the evidence table and recent reports"""

from app import create_app
from app.db_connector import get_db

app = create_app()

with app.app_context():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    print("\n" + "="*80)
    print("EVIDENCE TABLE SCHEMA")
    print("="*80)
    cursor.execute("DESC evidence")
    for row in cursor.fetchall():
        print(row)
    
    print("\n" + "="*80)
    print("ALL EVIDENCE RECORDS (Latest 10)")
    print("="*80)
    cursor.execute("""
        SELECT id, case_id, title, file_path, 
               IF(analysis_report IS NULL, 'NO REPORT', 'HAS REPORT') as report_status,
               LENGTH(analysis_report) as report_length,
               uploaded_at 
        FROM evidence 
        ORDER BY uploaded_at DESC 
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(row)
    
    print("\n" + "="*80)
    print("REPORTS WITH ANALYSIS (Case 1)")
    print("="*80)
    cursor.execute("""
        SELECT id, title, 
               IF(analysis_report IS NULL, 'NULL', 'HAS DATA') as report_status,
               LENGTH(COALESCE(analysis_report, '')) as report_length,
               uploaded_at 
        FROM evidence 
        WHERE case_id = 1 AND analysis_report IS NOT NULL 
        ORDER BY uploaded_at DESC
    """)
    rows = cursor.fetchall()
    print(f"Total Reports: {len(rows)}")
    for row in rows:
        print(row)
    
    cursor.close()
