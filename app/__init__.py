from flask import Flask, session, redirect, url_for
from .db_connector import close_db

def create_app():
    app = Flask(__name__)
    
    import os
    # Default key for dev, but in prod use .env
    app.secret_key = os.getenv('SECRET_KEY', 'dev_key')

    # Configure Upload Folder
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # 1. Register Auth
    from .auth import auth
    app.register_blueprint(auth)

    # 2. Register Dashboard
    from .dashboard import dashboard
    app.register_blueprint(dashboard)

    # 3. Register Case Manager
    from .case_manager import case_bp
    app.register_blueprint(case_bp)

    # 4. Register Profile Manager (THIS WAS MISSING)
    from .profile_manager import profile_bp
    app.register_blueprint(profile_bp)

    # THIS MUST BE HERE
    from .settings_manager import settings_bp
    app.register_blueprint(settings_bp)

    app.teardown_appcontext(close_db)

    # --- NEW ROUTE ---
    from flask import render_template
    
    @app.route('/features')
    def features():
        return render_template('features.html')

    # --- NEW ROUTE ---
    @app.route('/privacy')
    def privacy():
        return render_template('privacy.html')
    # -----------------

    @app.route('/')
    def home():
        # If user is already logged in, send them straight to Dashboard
        from flask import session, redirect, url_for, render_template
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))
        
        # If not logged in, show the Landing Page
        return render_template('landing.html')

    return app