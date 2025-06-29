from flask import Flask
from flask_smorest import Api
import os

from .config import Config
from .db import db
from .views.html_views import views_feedback_bp

def create_feedback_app():
    app = Flask(__name__)


    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'instance', 'feedback.db')}"
    app.config["API_TITLE"] = "Feedback API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    db.init_app(app)

    from .api.v1.routes import blp as feedback_blp  # <-- ВАЖНО: импорт после создания Flask и Api
    api = Api(app)
    api.register_blueprint(feedback_blp)
    app.register_blueprint(views_feedback_bp)  # HTML-шаблоны
    
    return app
