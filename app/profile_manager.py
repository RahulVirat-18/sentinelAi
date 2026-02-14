from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .db_connector import get_db
import bcrypt

# Define the Blueprint
profile_bp = Blueprint('profile_bp', __name__)

def login_required():
    if 'user_id' not in session:
        return False
    return True

@profile_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not login_required():
        return redirect(url_for('auth.login'))

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # 1. HANDLE UPDATES (POST)
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        new_password = request.form.get('password') # Optional field

        try:
            # Update Basic Info
            if new_password:
                # If user typed a new password, hash it and update everything
                hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute(
                    "UPDATE users SET full_name = %s, email = %s, password_hash = %s WHERE id = %s",
                    (full_name, email, hashed_pw, session['user_id'])
                )
            else:
                # Only update Name/Email
                cursor.execute(
                    "UPDATE users SET full_name = %s, email = %s WHERE id = %s",
                    (full_name, email, session['user_id'])
                )
            
            db.commit()
            
            # Update Session so the "Welcome, Name" text changes immediately
            session['user_name'] = full_name
            flash("Profile updated successfully!", "success")
            
        except Exception as e:
            flash(f"Error updating profile: {str(e)}", "error")
            
        return redirect(url_for('profile_bp.profile'))

    # 2. FETCH CURRENT DETAILS (GET)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    return render_template('dashboard/profile.html', user=user)

@profile_bp.after_request
def add_cache_control_headers(response):
    # Prevent caching so logged out users won't see profile via back/forward
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response