# config.py

import os
import dotenv

dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

"""
Application Configuration
Database connection settings and application constants
"""

# Database Configuration
DB_CONFIG = {
    "dsn": DATABASE_URL
}

# Application Settings
APP_TITLE = "University Management System"
APP_VERSION = "1.0.0"
APP_WIDTH = 400
APP_HEIGHT = 300
WINDOW_RESIZABLE = True

# UI Constants
FONT_TITLE = ("Arial", 16, "bold")
FONT_SUBTITLE = ("Arial", 12, "bold")
FONT_NORMAL = ("Arial", 10)
FONT_SMALL = ("Arial", 9)

# Colors
COLOR_PRIMARY = "#2c3e50"
COLOR_SECONDARY = "#3498db"
COLOR_SUCCESS = "#27ae60"
COLOR_DANGER = "#e74c3c"
COLOR_WARNING = "#f39c12"
COLOR_LIGHT = "#ecf0f1"
COLOR_TEXT = "#2c3e50"

# Button Sizes
BTN_WIDTH = 20
BTN_HEIGHT = 2
BTN_PADX = 10
BTN_PADY = 5

# Validation Messages
MSG_FILL_FIELDS = "Please fill in all required fields!"
MSG_INVALID_EMAIL = "Invalid email format!"
MSG_INVALID_PHONE = "Phone number should be numeric and 10-11 digits!"
MSG_INVALID_PASSWORD = "Password must be at least 6 characters!"
MSG_SUCCESS = "Operation completed successfully!"
MSG_ERROR = "An error occurred. Please try again!"

# Role Constants
ROLE_ADMIN = "Admin"
ROLE_LECTURER = "Lecturer"
ROLE_STUDENT = "Student"

# Session timeout in minutes
SESSION_TIMEOUT = 30

# PostgreSQL Tools
PG_DUMP_PATH = r"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"