import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Default to SQLite for easy local development, 
    # but use PostgreSQL if DATABASE_URL is provided (e.g., in production)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///tradesync.db'
    )

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG = True
