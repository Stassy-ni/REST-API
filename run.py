from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        from app.models import User
        db.create_all()

    app.run(debug=True)