import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Default to SQLite for easy local development
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///tradesync.db'
    )
    
    # Shared secret for HMAC Webhook Verification
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'tradesync-dev-secret-key')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
