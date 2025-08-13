"""Flask application factory."""

import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .config import config
from .models.database import db


def create_app(config_name=None):
    """Create and configure the Flask application.
    
    Args:
        config_name: Configuration to use (development, production, testing)
    
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    JWTManager(app)
    
    # Create tables (for development - in production use migrations)
    with app.app_context():
        # Import models to ensure they're registered
        from .models import entities
        
        # Create all tables
        db.create_all()
    
    # Register blueprints
    # TODO: Add blueprints here once created
    # from .blueprints.auth import auth_bp
    # from .blueprints.users import users_bp
    # from .blueprints.meals import meals_bp
    # 
    # app.register_blueprint(auth_bp, url_prefix=f"{app.config['API_PREFIX']}/auth")
    # app.register_blueprint(users_bp, url_prefix=f"{app.config['API_PREFIX']}/users")
    # app.register_blueprint(meals_bp, url_prefix=f"{app.config['API_PREFIX']}/meals")
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return {'status': 'healthy'}, 200
    
    return app
