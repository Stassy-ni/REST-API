import os
from dotenv import load_dotenv

load_dotenv()  # Чтобы .env работал, как в main_app

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # БД
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'feedback.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ключ для логина и сессий (ОБЯЗАТЕЛЕН)
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev_secret_key'
