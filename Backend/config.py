import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///leveling.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ Gmail SMTP Settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    # ✅ Load Credentials Securely
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    # ✅ Set Default Sender
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
