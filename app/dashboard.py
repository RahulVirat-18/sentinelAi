from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .db_connector import get_db
import mysql.connector

dashboard = Blueprint('dashboard', __name__)

def login_required():
    if 'user_id' not in session:
        return False
    return True

@dashboard.route('/dashboard')
def index():
    if not login_required():
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch cases sorted by newest first
    cursor.execute("SELECT * FROM cases WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
    cases = cursor.fetchall()
    
    return render_template('dashboard/dashboard.html', cases=cases, user_name=session.get('user_name'))

@dashboard.route('/create_case', methods=['POST'])
def create_case():
    if not login_required():
        return redirect(url_for('auth.login'))

    # Get data from form
    unique_id = request.form['case_unique_id'].strip()
    case_name = request.form['case_name'].strip()
    description = request.form['description'].strip()
    user_id = session['user_id']

    db = get_db()
    cursor = db.cursor()
    
    try:
        query = "INSERT INTO cases (user_id, case_unique_id, case_name, description) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (user_id, unique_id, case_name, description))
        db.commit()
        flash("Case created successfully!", "success")
    except mysql.connector.IntegrityError:
        # This error catches Duplicate Case IDs
        flash(f"Error: Case ID '{unique_id}' already exists. Please choose a unique ID.", "error")
    except Exception as e:
        flash(f"System Error: {str(e)}", "error")

    return redirect(url_for('dashboard.index'))

@dashboard.route('/delete_case/<int:case_id>')
def delete_case(case_id):
    if not login_required():
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor()

    # Secure deletion
    cursor.execute("DELETE FROM cases WHERE id = %s AND user_id = %s", (case_id, session['user_id']))
    db.commit()

    flash("Case deleted permanently.", "success")
    return redirect(url_for('dashboard.index'))

@dashboard.after_request
def add_cache_control_headers(response):
    # Prevent caching so browser back/forward won't show stale authenticated pages after logout
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response