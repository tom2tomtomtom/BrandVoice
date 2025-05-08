from flask import Flask
from flask_wtf.csrf import CSRFProtect
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-brand-voice-codifier')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    
    # Register blueprints
    from app.routes.home import home_bp
    from app.routes.document_upload import document_upload_bp
    from app.routes.brand_interview import brand_interview_bp
    from app.routes.web_scraper import web_scraper_bp
    from app.routes.dashboard import dashboard_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(document_upload_bp)
    app.register_blueprint(brand_interview_bp)
    app.register_blueprint(web_scraper_bp)
    app.register_blueprint(dashboard_bp)
    
    return app
