import pytest
from app import create_app
from app.database import db
from config import TestingConfig

@pytest.fixture
def app():
    """
    Creates a Flask application instance configured for testing.
    """
    # Use the TestingConfig which points to an in-memory SQLite database
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """
    A test client for the app.
    """
    return app.test_client()
