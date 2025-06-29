import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from app_main import create_app, Config
from feedback_service import create_feedback_app

main_app = create_app(Config)
feedback_app = create_feedback_app()

application = DispatcherMiddleware(main_app, {
    "/feedback": feedback_app
})

if __name__ == "__main__":
    run_simple("localhost", 5000, application, use_reloader=True)
