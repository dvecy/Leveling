from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from extensions import db, mail
from models import User

app = Flask(__name__)
app.config.from_object('config.Config')

# ✅ Initialize Extensions
db.init_app(app)
mail.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# ✅ Add This Function Below
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ Import Blueprints
from routes.auth import auth
app.register_blueprint(auth, url_prefix='/auth')

@app.route('/users')
@login_required
def view_users():
    # ✅ Only Allow Admins to Access
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))  # Redirect normal users away

    users = User.query.all()  # Get all users from the database
    return render_template('users.html', users=users)


@app.route('/')
def home():
    return render_template('index.html')

# ✅ Define Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
