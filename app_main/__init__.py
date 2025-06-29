from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from app_main.models import db 
from app_main.config import Config  


# Загрузка переменных окружения
load_dotenv()

# Инициализация расширений
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Защита от переопределения
    app.config.update({
        'MAIL_USE_SSL': False,
        'MAIL_USE_TLS': True
    })
    

    db.init_app(app)
    
    mail.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    # Регистрация blueprints
    from app_main.auth import auth_bp
    from app_main.teacher import teacher_bp
    from app_main.student import student_bp
    from app_main.expert import expert_bp
    from app_main.admin import admin_bp


    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(expert_bp, url_prefix='/expert')
    app.register_blueprint(admin_bp, url_prefix='/admin')


    # Обработчики ошибок
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': str(error) or 'Доступ запрещён'}), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    
    # Контекст для Flask Shell
    @app.shell_context_processor
    def make_shell_context():
        from app_main.models import User
        return {
            'db': db,
            'User': User,
            'mail': mail
        }

    return app

