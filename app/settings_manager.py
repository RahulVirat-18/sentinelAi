from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .db_connector import get_db

settings_bp = Blueprint('settings_bp', __name__)

def login_required():
    return 'user_id' in session

@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if not login_required():
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 1. SAVE CHANGES (POST)
    if request.method == 'POST':
        # Logic: Checkboxes only send data if they are Checked.
        
        # Theme: If checked -> Light, If unchecked -> Dark
        theme_val = 'light' if request.form.get('theme_toggle') else 'dark'
        
        # Security: If checked -> 1 (True), If unchecked -> 0 (False)
        two_fa_val = 1 if request.form.get('2fa_toggle') else 0
        alerts_val = 1 if request.form.get('alerts_toggle') else 0

        try:
            query = """
                UPDATE users 
                SET setting_theme = %s, 
                    is_2fa_enabled = %s, 
                    setting_login_alerts = %s
                WHERE id = %s
            """
            cursor.execute(query, (theme_val, two_fa_val, alerts_val, session['user_id']))
            db.commit()
            
            # Update Session immediately so the interface changes color right away
            session['theme'] = theme_val
            
            flash("Settings updated successfully.", "success")
        except Exception as e:
            flash(f"Error saving settings: {str(e)}", "error")
            
        return redirect(url_for('settings_bp.settings'))

    # 2. LOAD SETTINGS (GET)
    # We fetch the current user data to show the correct switch positions
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user_settings = cursor.fetchone()

    return render_template('dashboard/settings.html', settings=user_settings)

@settings_bp.after_request
def add_cache_control_headers(response):
    # Prevent caching so logged out users won't see settings via back/forward
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response