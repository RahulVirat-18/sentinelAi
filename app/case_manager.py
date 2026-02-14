from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from .db_connector import get_db
from werkzeug.utils import secure_filename
import os
import time
import google.generativeai as genai

# Import our custom AI and Memory engines
from .ai_engine import analyze_video
from .memory_engine import save_memory, query_memory

# Define the Blueprint
case_bp = Blueprint('case_bp', __name__)

# --- HELPER FUNCTIONS ---

def login_required():
    """Checks if user is logged in. Returns True/False."""
    if 'user_id' not in session:
        return False
    return True

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ROUTES ---

@case_bp.route('/case/<int:case_id>/overview')
def overview(case_id):
    if not login_required():
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 1. Get Case Info
    cursor.execute("SELECT * FROM cases WHERE id = %s AND user_id = %s", (case_id, session['user_id']))
    case = cursor.fetchone()

    if not case:
        flash("Access Denied.", "error")
        return redirect(url_for('dashboard.index'))

    # 2. Get the LATEST uploaded evidence (for the Dashboard view)
    cursor.execute("SELECT * FROM evidence WHERE case_id = %s ORDER BY uploaded_at DESC LIMIT 1", (case_id,))
    latest_evidence = cursor.fetchone()

    return render_template('case/overview.html', case=case, latest_evidence=latest_evidence)


@case_bp.route('/case/<int:case_id>/evidence', methods=['GET', 'POST'])
def evidence(case_id):
    if not login_required():
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 1. Verify Case Ownership
    cursor.execute("SELECT * FROM cases WHERE id = %s AND user_id = %s", (case_id, session['user_id']))
    case = cursor.fetchone()
    if not case:
        return redirect(url_for('dashboard.index'))

    # 2. HANDLE FILE UPLOAD
    if request.method == 'POST':
        if 'video_file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
            
        file = request.files['video_file']
        
        if file.filename == '' or not allowed_file(file.filename):
            flash('Invalid file or format. Allowed: mp4, avi, mov, mkv', 'error')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            # Add timestamp to make each upload UNIQUE
            unique_filename = f"{int(time.time())}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            
            relative_path = f"uploads/{unique_filename}"
            
            # Save to MySQL
            cursor.execute(
                "INSERT INTO evidence (case_id, title, file_path) VALUES (%s, %s, %s)",
                (case_id, filename, relative_path)
            )
            db.commit()
            
            flash('Upload Successful! Evidence secured.', 'success')
            # Redirect to evidence page so user sees the new file immediately
            return redirect(url_for('case_bp.evidence', case_id=case_id))

    # 3. Fetch existing evidence list
    cursor.execute("SELECT * FROM evidence WHERE case_id = %s ORDER BY uploaded_at DESC", (case_id,))
    evidence_list = cursor.fetchall()

    return render_template('case/evidence.html', case=case, evidence_list=evidence_list)


@case_bp.route('/analyze/<int:evidence_id>', methods=['POST'])
def analyze_evidence(evidence_id):
    if not login_required():
        return jsonify({'error': 'Unauthorized'}), 401

    db = get_db()
    
    # 1. Fetch Evidence Info
    # We use a simple cursor here just to get the path
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM evidence WHERE id = %s", (evidence_id,))
    item = cursor.fetchone()
    cursor.close() # Close this cursor to be clean
    
    if not item:
        print(f"DEBUG: Evidence {evidence_id} NOT FOUND.")
        return jsonify({'error': 'Evidence not found'}), 404

    full_path = os.path.join(current_app.root_path, 'static', item['file_path'])
    print(f"DEBUG: Starting Analysis on {item['title']}...")
    
    try:
        # 2. Call AI Engine
        report = analyze_video(full_path)
        
        if not report:
            print("DEBUG: AI returned empty report!")
            return jsonify({'error': 'AI Analysis failed to generate text'}), 500

        print(f"DEBUG: AI Report Generated ({len(report)} chars). Saving to DB...")

        # 3. FORCE UPDATE MySQL (The Fix)
        # We open a NEW cursor specifically for the update to ensure it commits
        update_cursor = db.cursor()
        update_query = "UPDATE evidence SET analysis_report = %s WHERE id = %s"
        update_cursor.execute(update_query, (report, evidence_id))
        db.commit() # <--- THIS COMMAND SAVES IT TO DISK
        update_cursor.close()
        
        print(f"DEBUG: ✅ Database Successfully Updated for Evidence ID {evidence_id}")

        # 4. Save to Memory (ChromaDB)
        save_memory(case_id=item['case_id'], text=report, source="report")
        
        return jsonify({'success': True, 'report': report})
        
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        # Even if it fails, try to rollback so the DB doesn't get stuck
        db.rollback()
        return jsonify({'error': str(e)}), 500


@case_bp.route('/case/<int:case_id>/chat', methods=['POST'])
def chat_api(case_id):
    if not login_required():
        return jsonify({'response': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_message = data.get('message', '')

    # 1. RETRIEVE (RAG)
    # Search ChromaDB for facts related to the user's question
    context = query_memory(case_id, user_message)
    
    # 2. AUGMENT (Add context to prompt)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    system_instruction = f"""
    You are an intelligent Forensic Assistant for Case #{case_id}.
    
    YOUR KNOWLEDGE BASE (Facts retrieved from video reports & past corrections):
    {context}
    
    INSTRUCTIONS:
    1. Answer based strictly on the knowledge base above.
    2. If the user corrects a fact (e.g., "The car was actually red"), ACCEPT it and acknowledge the update.
    3. Be professional, concise, and objective.
    """
    
    # 3. GENERATE (Ask Gemini)
    try:
        response = model.generate_content(f"{system_instruction}\n\nUser Question: {user_message}")
        ai_reply = response.text
    except Exception as e:
        ai_reply = "I am having trouble connecting to the AI model."

    # 4. MEMORIZE (Learning Loop)
    # If user used correction words, save the new fact to ChromaDB immediately.
    correction_triggers = ["actually", "no", "correction", "wrong", "mistake", "change", "it was", "incorrect"]
    if any(word in user_message.lower() for word in correction_triggers):
        print(f"--- RAG: Detected Correction in Case {case_id} ---")
        save_memory(case_id, f"USER CORRECTION: {user_message}", source="user_correction")

    return jsonify({'response': ai_reply})

@case_bp.route('/case/<int:case_id>/email_report', methods=['POST'])
def email_report(case_id):
    if not login_required():
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    report_text = data.get('report')

    # TODO: Phase 11 - Implement SMTP Email Sending here.
    # For now, we simulate success so the UI feedback works.
    print(f"--- MOCK EMAIL SENT ---")
    print(f"Case: {case_id}")
    print(f"User: {session.get('user_name')}")
    print(f"Content Length: {len(report_text)} chars")
    
    return jsonify({'success': True, 'message': 'Email dispatched to registered address.'})

@case_bp.route('/case/<int:case_id>/reports')
def saved_reports(case_id):
    if not login_required():
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM cases WHERE id = %s AND user_id = %s", (case_id, session['user_id']))
    case = cursor.fetchone()
    if not case:
        return redirect(url_for('dashboard.index'))

    # SIMPLIFIED QUERY: Just check if report is not NULL
    cursor.execute("""
        SELECT * FROM evidence 
        WHERE case_id = %s 
        AND analysis_report IS NOT NULL 
        ORDER BY uploaded_at DESC
    """, (case_id,))
    
    reports = cursor.fetchall()

    return render_template('case/saved_reports.html', case=case, reports=reports)

@case_bp.after_request
def add_cache_control_headers(response):
    # Prevent caching of case pages so browser back/forward won't show stale authenticated pages after logout
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response