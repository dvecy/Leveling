from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://your_user:your_password@localhost/your_db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # Attach the database to the app

# Import models AFTER initializing db
from models import User, Task, WeeklyQuest

if __name__ == "__main__":
    app.run(debug=True)
