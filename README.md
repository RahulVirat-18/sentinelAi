# Senti - AI-Powered Sentiment Analysis Platform

A comprehensive web-based application for sentiment analysis and case management powered by Google's Generative AI and Chroma Vector Database.

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup](#setup)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **AI-Powered Analysis**: Sentiment analysis using Google's Generative AI
- **Case Management**: Organize and manage analysis cases
- **User Authentication**: Secure login with 2FA support
- **Dashboard**: Comprehensive dashboard for tracking and insights
- **Evidence Management**: Store and manage evidence for cases
- **Memory Engine**: Persistent memory storage using Chroma Vector Database
- **Profile Management**: User profile and settings management
- **Email Notifications**: Automated email service for alerts
- **Responsive UI**: Modern, responsive web interface

## 🔧 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.x** (Python 3.8 or higher recommended)
- **pip** (Python package manager)
- **Git** (for version control)
- **Google Generative AI API Key** (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

## 📦 Installation

Follow these steps to set up the project on your local machine:

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd senti
```

### Step 2: Create and Activate Virtual Environment

**On Windows:**

```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
env\Scripts\activate
```

**On macOS/Linux:**

```bash
# Create virtual environment
python3 -m venv env

# Activate virtual environment
source env/bin/activate
```

**Note:** Your terminal prompt should now show `(env)` prefix, indicating the virtual environment is active.

### Step 3: Upgrade pip

```bash
# Windows
python -m pip install --upgrade pip

# macOS/Linux
python3 -m pip install --upgrade pip
```

### Step 4: Install Dependencies

```bash
# Install all required packages from requirements.txt
pip install -r requirements.txt
```

This will install all necessary packages including:
- Flask (Web framework)
- Google Generative AI (AI capabilities)
- Chromadb (Vector database)
- SQLAlchemy (Database ORM)
- And other dependencies

## ⚙️ Setup

### Step 1: Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
# On Windows
echo. > .env

# On macOS/Linux
touch .env
```

Add the following environment variables to the `.env` file:

```env
# Google Generative AI Configuration
GOOGLE_API_KEY=your_google_generative_ai_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_APP=run.py

# Database Configuration
DATABASE_URL=sqlite:///senti.db

# Email Configuration (if using email service)
MAIL_SERVER=your_mail_server
MAIL_PORT=587
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password

# Security
SECRET_KEY=your_secret_key_here

# Other configurations
APP_NAME=Senti
```

**Important:** Never commit `.env` file to version control. It's already included in `.gitignore`.

### Step 2: Initialize Database (if needed)

```bash
# Run database initialization script
python debug_db.py
```

## 🚀 Running the Application

### Step 1: Ensure Virtual Environment is Activated

```bash
# Windows
env\Scripts\activate

# macOS/Linux
source env/bin/activate
```

### Step 2: Run the Application

```bash
python run.py
```

The application should start and display output similar to:

```
 * Serving Flask app 'run'
 * Running on http://127.0.0.1:5000
```

### Step 3: Access the Application

Open your web browser and navigate to:

```
http://127.0.0.1:5000
```

You should see the Senti landing page. Register a new account and start using the application!

## 📁 Project Structure

```
senti/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app initialization
│   ├── ai_engine.py             # AI/ML processing with Google Generative AI
│   ├── auth.py                  # Authentication and user management
│   ├── case_manager.py          # Case management logic
│   ├── dashboard.py             # Dashboard functionality
│   ├── db_connector.py          # Database connection and queries
│   ├── email_service.py         # Email notifications
│   ├── memory_engine.py         # Vector database operations (Chroma)
│   ├── profile_manager.py       # User profile management
│   ├── settings_manager.py      # Application settings
│   ├── static/                  # Static files (CSS, JS, images)
│   │   ├── theme.css            # Styling
│   │   ├── js/
│   │   │   └── ui_modals.js    # UI components and modals
│   │   └── uploads/             # User uploaded files
│   └── templates/               # HTML templates
│       ├── landing.html         # Landing page
│       ├── features.html        # Features page
│       ├── privacy.html         # Privacy policy
│       ├── auth/                # Authentication templates
│       │   ├── login.html
│       │   ├── register.html
│       │   ├── forgot_password.html
│       │   ├── reset_password.html
│       │   └── verify_2fa.html
│       ├── case/                # Case management templates
│       │   ├── layout.html
│       │   ├── overview.html
│       │   ├── evidence.html
│       │   └── saved_reports.html
│       └── dashboard/           # Dashboard templates
│           ├── dashboard.html
│           ├── profile.html
│           └── settings.html
├── chroma_db/                   # Vector database storage
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── debug_db.py                  # Database debugging utilities
├── verify_flow.py              # Flow verification script
├── view_memory.py              # Memory inspection utility
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 📚 Key Components

### app/ai_engine.py
Handles all AI-related operations including sentiment analysis using Google's Generative AI.

### app/memory_engine.py
Manages the Chroma Vector Database for storing and retrieving embeddings and semantic search.

### app/auth.py
Handles user authentication, registration, password reset, and 2FA verification.

### app/case_manager.py
Manages case creation, updating, and retrieval with associated evidence.

### app/dashboard.py
Provides dashboard functionality for displaying analytics and insights.

## 🔄 Common Commands

### Deactivate Virtual Environment

```bash
deactivate
```

### Reinstall Dependencies

```bash
pip install -r requirements.txt --force-reinstall
```

### Update Dependencies

```bash
pip install -r requirements.txt --upgrade
```

### Generate Requirements File (if updating dependencies)

```bash
pip freeze > requirements.txt
```

### Run Database Debugging

```bash
python debug_db.py
```

### Verify Application Flow

```bash
python verify_flow.py
```

### Check Memory/Database

```bash
python view_memory.py
```

## 🔐 Security Considerations

1. **Never commit `.env` file** - Keep sensitive information secure
2. **Use strong SECRET_KEY** - Generate a secure key for Flask sessions
3. **Enable HTTPS** - Use HTTPS in production
4. **Validate inputs** - Always validate user inputs on both frontend and backend
5. **Rate limiting** - Implement rate limiting for API endpoints
6. **Regular updates** - Keep dependencies updated for security patches

## 🐛 Troubleshooting

### Issue: "python: command not found"
- **Solution**: Ensure Python is installed and added to PATH. Try `python3` instead on macOS/Linux.

### Issue: "No module named 'flask'"
- **Solution**: Activate the virtual environment and run `pip install -r requirements.txt`

### Issue: Virtual environment not activating
- **Solution**: 
  - Windows: Try `env\Scripts\activate.bat` or `env\Scripts\Activate.ps1`
  - macOS/Linux: Try `source env/bin/activate`

### Issue: Port 5000 already in use
- **Solution**: Flask will try to use port 5000. Modify `run.py` to use a different port:
  ```python
  app.run(port=5001)  # Use port 5001 instead
  ```

### Issue: Google API Key not working
- **Solution**: 
  - Verify API key is valid in `.env` file
  - Ensure Google Generative AI API is enabled in Google Cloud Console
  - Check that the API key has appropriate permissions

### Issue: Database connection errors
- **Solution**: 
  - Verify `DATABASE_URL` in `.env` is correct
  - Ensure database file exists or run `python debug_db.py`
  - Check database permissions

### Issue: Email service not working
- **Solution**: 
  - Verify MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD in `.env`
  - For Gmail, use app-specific password instead of regular password
  - Ensure "Less secure app access" is enabled (if using Gmail)

## 📝 Development Workflow

1. Activate virtual environment
2. Make code changes
3. Test locally at `http://127.0.0.1:5000`
4. Run debugging utilities if needed (`debug_db.py`, `verify_flow.py`)
5. Commit changes to git
6. Push to repository

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Submit a pull request with a detailed description

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📧 Support

For issues, questions, or suggestions, please create an issue in the repository or contact the development team.

---

**Happy coding! 🚀**

Last Updated: February 2026
