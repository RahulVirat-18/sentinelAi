import mysql.connector
from flask import current_app, g
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db():
    """
    Opens a new database connection if there is none for the current context.
    Stores it in the 'g' object (Flask's global temporary storage).
    """
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
        except mysql.connector.Error as err:
            print(f"Error connecting to Database: {err}")
            return None
    return g.db

def close_db(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()