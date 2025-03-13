from main import app, db  # Import from main.py instead of app.py

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
