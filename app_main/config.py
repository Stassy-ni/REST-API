import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Config:
    # Секретный ключ
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Главная БД: путь до math_platform.db в корне проекта
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'math_platform.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Бин для feedback
    SQLALCHEMY_BINDS = {
        'feedback': os.getenv('FEEDBACK_DATABASE_URL', 'sqlite:///feedback_service/instance/feedback.db')
    }

    # Настройки почты
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'false'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
