"""
Construction Legal Assistant
Main Flask Application

Developer: Andel Albdesk
Copyright (c) 2026 Andel Albdesk. All rights reserved.

This application helps construction companies understand their contracts
and Albanian construction laws using AI-powered question answering.
"""

from flask import Flask, send_from_directory, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager
from backend.db.database import db, User, init_db
from backend.routes.auth import auth_bp
from backend.routes.projects import projects_bp
from backend.routes.upload_contract import upload_contract_bp
from backend.routes.upload_law import upload_law_bp
from backend.routes.query import query_bp
from backend.routes.conversations import conversations_bp
import logging
import os
from pathlib import Path

# Absolute paths resolved from this file's location
BASE_DIR = Path(__file__).resolve().parent.parent          # project root
FRONTEND_DIR = BASE_DIR / 'frontend'
LOGS_DIR = BASE_DIR / 'logs'
UPLOADS_DIR = BASE_DIR / 'uploads'
VECTOR_DB_DIR = BASE_DIR / 'vector_db_storage'

# Ensure directories exist before anything else runs (gunicorn doesn't hit __main__)
LOGS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(exist_ok=True)

# Configure logging (FileHandler now uses absolute path)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(LOGS_DIR / 'app.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__,
                static_folder=str(FRONTEND_DIR / 'static'),
                template_folder=str(FRONTEND_DIR))

    # Load configuration
    from backend import config
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE_MB * 1024 * 1024  # Max file size

    # Enable CORS
    CORS(app, supports_credentials=True)

    # Initialize database
    init_db(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'index'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(upload_contract_bp)
    app.register_blueprint(upload_law_bp)
    app.register_blueprint(query_bp)
    app.register_blueprint(conversations_bp)

    # Serve frontend pages
    @app.route('/')
    def index():
        """Serve login/register page"""
        return send_from_directory(str(FRONTEND_DIR), 'index.html')

    @app.route('/dashboard')
    def dashboard():
        """Serve dashboard page"""
        return send_from_directory(str(FRONTEND_DIR), 'dashboard.html')

    @app.route('/upload/contract')
    def upload_contract_page():
        """Serve contract upload page"""
        return send_from_directory(str(FRONTEND_DIR), 'upload_contract.html')

    @app.route('/upload/law')
    def upload_law_page():
        """Serve law upload page"""
        return send_from_directory(str(FRONTEND_DIR), 'upload_law.html')

    @app.route('/query')
    def query_page():
        """Serve query page"""
        return send_from_directory(str(FRONTEND_DIR), 'query.html')

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Construction Legal Assistant API is running'}, 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(413)
    def file_too_large(error):
        return {'error': 'File too large. Maximum file size is 50MB.'}, 413

    logger.info("Flask application created successfully")

    return app


if __name__ == '__main__':
    app = create_app()

    port = int(os.environ.get('PORT', 5000))

    logger.info("Starting Construction Legal Assistant")
    logger.info("=" * 60)
    logger.info(f"Server running on http://0.0.0.0:{port}")
    logger.info("=" * 60)

    # Run application (local dev only — production uses gunicorn)
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('DEBUG', 'False') == 'True'
    )
