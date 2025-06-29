from app_main import create_app
from app_main.models import db, User  
from app_main.config import Config

app = create_app(Config)

with app.app_context():
    from app_main import db
    db.create_all()  

app.run(debug=True)
