from . import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class ChatbotKB(db.Model):
    __tablename__ = 'chatbot_kb'
    
    id = db.Column(db.Integer, primary_key=True)
    drug_id = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    data = db.Column(JSONB, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<ChatbotKB {self.drug_id}>'

class ChatbotLog(db.Model):
    __tablename__ = 'chatbot_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    query_text = db.Column(db.Text, nullable=False)
    intent = db.Column(db.Text)
    entities = db.Column(JSONB)
    response_text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    flagged = db.Column(db.Boolean, default=False)
    
    # Relationship
    user = db.relationship('User', backref='chatbot_logs', lazy=True)
    
    def __repr__(self):
        return f'<ChatbotLog {self.id}>'