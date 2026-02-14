from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import bcrypt
import random
from datetime import datetime, timedelta
from .db_connector import get_db
from .email_service import send_email

auth = Blueprint('auth', __name__)

def generate_otp():
    return str(random.randint(100000, 999999))

# --- LOGIN ROUTE (Updated for 2FA) ---
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            
            # CHECK 1: IS 2FA ENABLED?
            if user['is_2fa_enabled']:
                # Generate OTP
                otp = generate_otp()
                expiry = datetime.now() + timedelta(minutes=10)
                
                cursor.execute("UPDATE users SET otp_code=%s, otp_expiry=%s WHERE id=%s", (otp, expiry, user['id']))
                db.commit()
                
                # Send Email
                send_email(user['email'], "Sentinel AI - Verification Code", 
                           f"<h3>Your OTP is: <b>{otp}</b></h3><p>Valid for 10 minutes.</p>")
                
                # Store ID temporarily in session and redirect to verification
                session['temp_user_id'] = user['id']
                return redirect(url_for('auth.verify_2fa'))

            # CHECK 2: LOGIN ALERTS
            if user['setting_login_alerts']:
                send_email(user['email'], "Security Alert: New Login", 
                           f"<p>New sign-in detected for your account at {datetime.now()}.</p>")

            # NO 2FA -> LOG THEM IN DIRECTLY
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['theme'] = user.get('setting_theme', 'dark')
            
            return redirect(url_for('dashboard.index'))
            
        else:
            flash('Invalid Email or Password', 'error')
            
    try:
        forgot_url = url_for('auth.forgot_password')
    except Exception:
        forgot_url = '/forgot-password'
    return render_template('auth/login.html', forgot_password_url=forgot_url)

# --- 2FA VERIFICATION PAGE ---
@auth.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'temp_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        entered_otp = request.form['otp']
        user_id = session['temp_user_id']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        
        # Check Validity
        if user['otp_code'] == entered_otp and user['otp_expiry'] > datetime.now():
            # SUCCESS
            session.pop('temp_user_id', None) # Clear temp
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['theme'] = user.get('setting_theme', 'dark')
            
            # Clear OTP from DB
            cursor.execute("UPDATE users SET otp_code=NULL WHERE id=%s", (user_id,))
            db.commit()
            
            # Send Alert if enabled
            if user['setting_login_alerts']:
                send_email(user['email'], "Security Alert: Login Successful", "<p>2FA Verification complete.</p>")
            
            return redirect(url_for('dashboard.index'))
        else:
            flash("Invalid or Expired OTP", "error")

    return render_template('auth/verify_2fa.html')

# --- FORGOT PASSWORD FLOW ---
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        
        if user:
            otp = generate_otp()
            expiry = datetime.now() + timedelta(minutes=10)
            
            cursor.execute("UPDATE users SET otp_code=%s, otp_expiry=%s WHERE id=%s", (otp, expiry, user['id']))
            db.commit()
            
            send_email(email, "Reset Password Request", f"<h3>Reset Code: <b>{otp}</b></h3>")
            session['reset_email'] = email
            return redirect(url_for('auth.reset_password'))
        else:
            flash("Email not found", "error")
            
    return render_template('auth/forgot_password.html')

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_email' not in session:
        return redirect(url_for('auth.forgot_password'))
        
    if request.method == 'POST':
        otp = request.form['otp']
        new_pass = request.form['password']
        email = session['reset_email']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        
        if user['otp_code'] == otp and user['otp_expiry'] > datetime.now():
            # Hash new password
            hashed = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("UPDATE users SET password_hash=%s, otp_code=NULL WHERE id=%s", (hashed, user['id']))
            db.commit()
            
            session.pop('reset_email', None)
            flash("Password Reset Successful. Please Login.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Invalid Code", "error")

    return render_template('auth/reset_password.html')

# --- STANDARD ROUTES ---
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        db = get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute("INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)", 
                           (full_name, email, hashed_password))
            db.commit()
            flash('Registration Successful! Please Login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Email already exists.', 'error')
            
    return render_template('auth/register.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))