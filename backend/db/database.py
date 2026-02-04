"""
Construction Legal Assistant
Database Models

Developer: Andel Albdesk
Copyright (c) 2026 Andel Albdesk. All rights reserved.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    projects = db.relationship('Project', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Project(db.Model):
    """Project model - each project contains contracts and laws"""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Vector DB index paths
    contract_index_path = db.Column(db.String(500))
    law_index_path = db.Column(db.String(500))

    # Relationships
    contracts = db.relationship('Contract', backref='project', lazy=True, cascade='all, delete-orphan')
    laws = db.relationship('Law', backref='project', lazy=True, cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='project', lazy=True, cascade='all, delete-orphan')
    queries = db.relationship('Query', backref='project', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Project {self.name}>'


class Contract(db.Model):
    """Contract document model"""
    __tablename__ = 'contracts'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    original_filename = db.Column(db.String(300), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    pages = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    processing_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    error_message = db.Column(db.Text)

    # Metadata
    contract_type = db.Column(db.String(100))  # e.g., "Concrete Delivery", "Construction Agreement"
    parties = db.Column(db.Text)  # JSON or comma-separated

    def __repr__(self):
        return f'<Contract {self.original_filename}>'


class Law(db.Model):
    """Law document model"""
    __tablename__ = 'laws'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    original_filename = db.Column(db.String(300), nullable=False)
    file_size = db.Column(db.Integer)
    pages = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    processing_status = db.Column(db.String(50), default='pending')
    error_message = db.Column(db.Text)

    # Law metadata
    law_number = db.Column(db.String(50))  # e.g., "32/5"
    law_title = db.Column(db.String(300))  # e.g., "Albanian Construction Safety Law"
    year = db.Column(db.Integer)
    update_version = db.Column(db.String(50))

    def __repr__(self):
        return f'<Law {self.law_number} - {self.law_title}>'


class Conversation(db.Model):
    """Conversation/Chat session model"""
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))  # Auto-generated from first question
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = db.relationship('Query', backref='conversation', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Conversation {self.id} - {self.title}>'


class Query(db.Model):
    """Query/Message in a conversation"""
    __tablename__ = 'queries'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=True)  # Nullable for backwards compatibility
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    language = db.Column(db.String(5))  # 'sq' or 'en'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Citations
    contract_citations = db.Column(db.Text)  # JSON
    law_citations = db.Column(db.Text)  # JSON

    # Performance metrics
    response_time = db.Column(db.Float)  # seconds

    def __repr__(self):
        return f'<Query {self.id} - {self.question[:50]}>'


def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
