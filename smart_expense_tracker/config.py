import os

class Config:
    SECRET_KEY = "smart_expense_tracker_secret_key"

    # MySQL Database Configuration
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "Password"
    MYSQL_DATABASE = "smart_expense_tracker"

    # Upload folder (optional for future features)
    UPLOAD_FOLDER = os.path.join("static", "uploads")