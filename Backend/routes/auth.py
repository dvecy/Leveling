from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from extensions import db, mail  
from models import User

auth = Blueprint('auth', __name__)

### Secure Token Serializer
def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

# ───────────────────────────────────────────────────────
# REGISTER ROUTE
# ───────────────────────────────────────────────────────
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists!', 'error')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

# ───────────────────────────────────────────────────────
# LOGIN ROUTE
# ───────────────────────────────────────────────────────
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Account not found. Please register first.', 'error')
            return redirect(url_for('auth.register'))
        
        if not check_password_hash(user.password_hash, password):
            flash('Incorrect password. Please try again.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))  # Make sure the dashboard route is defined in your main app

    return render_template('login.html')

# ───────────────────────────────────────────────────────
# LOGOUT ROUTE
# ───────────────────────────────────────────────────────
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

# ───────────────────────────────────────────────────────
# FORGOT PASSWORD ROUTE (Sends Reset Link)
# ───────────────────────────────────────────────────────
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            send_reset_email(user)
            flash('A password reset link has been sent to your email.', 'info')
        else:
            flash('No account found with that email.', 'error')

        return redirect(url_for('auth.forgot_password'))

    return render_template('forgot_password.html')

# ───────────────────────────────────────────────────────
# SEND RESET EMAIL FUNCTION
# ───────────────────────────────────────────────────────
def send_reset_email(user):
    """Generate a reset token and send password reset email"""
    serializer = get_serializer()
    token = serializer.dumps(user.email, salt='password-reset')
    reset_link = url_for('auth.reset_password', token=token, _external=True)

    msg = Message(
        "Password Reset Request",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],  # Ensure MAIL_DEFAULT_SENDER is set in your config
        recipients=[user.email]
    )
    msg.body = f'''To reset your password, click the link below:
{reset_link}

If you did not make this request, please ignore this email.
'''
    mail.send(msg)

# ───────────────────────────────────────────────────────
# PASSWORD RESET ROUTE (Uses Secure Token)
# ───────────────────────────────────────────────────────
@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    serializer = get_serializer()
    try:
        email = serializer.loads(token, salt='password-reset', max_age=1800)  # 30-minute expiry
    except SignatureExpired:
        flash('That is an expired token. Request a new password reset.', 'error')
        return redirect(url_for('auth.forgot_password'))
    except BadSignature:
        flash('Invalid token. Request a new password reset.', 'error')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()
    if user is None:
        flash('Invalid reset request.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')
