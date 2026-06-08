import logging
from flask import Flask
from .database import db
from config import Config

def create_app(config_class=Config):
    """
    Application factory for creating a Flask app instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("TradeSync application starting...")

    # Register blueprints/routes
    from .routes import webhook_bp
    app.register_blueprint(webhook_bp)

    # Create tables (for development/testing)
    with app.app_context():
        db.create_all()

    return app
