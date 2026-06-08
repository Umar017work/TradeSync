from datetime import datetime
from .database import db

class WebhookEvent(db.Model):
    """
    Stores metadata about received webhooks for idempotency and auditing.
    """
    __tablename__ = 'webhook_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending') # pending, processed, error, duplicate

    def __repr__(self):
        return f"<WebhookEvent {self.event_id} ({self.event_type})>"

class Account(db.Model):
    """
    Stores account information received from trading platforms.
    """
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    broker = db.Column(db.String(100))
    platform = db.Column(db.String(100))
    account_type = db.Column(db.String(50))
    balance = db.Column(db.Float)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Account {self.account_id} - {self.user_name}>"
