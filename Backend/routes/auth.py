from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import datetime
import os
from extensions import db, mail, csrf
from models import User, UserProfile

auth = Blueprint('auth', __name__)

def get_serializer():
    """Create a URL-safe serializer for token generation."""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists!', 'error')
            return redirect(url_for('auth.register'))

        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Create user profile
        new_profile = UserProfile(user_id=new_user.id)
        db.session.add(new_profile)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
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
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Handle user profile updates."""
    if request.method == 'POST' and 'photo' in request.files:
        file = request.files['photo']
        if file and allowed_file(file.filename):
            # Save new profile photo
            filename = secure_filename(
                f"user_{current_user.id}_{datetime.now().timestamp()}.{file.filename.rsplit('.', 1)[1].lower()}"
            )
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Remove old profile photo if it exists
            if current_user.profile_photo != 'default_avatar.png':
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.profile_photo)
                if os.path.exists(old_path):
                    os.remove(old_path)

            # Update user profile photo
            current_user.profile_photo = filename
            db.session.commit()
            flash('Profile photo updated!', 'success')
        else:
            flash('Invalid file type. Allowed: PNG, JPG, JPEG, GIF', 'error')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('profile.html')

@auth.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset requests."""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            send_reset_email(user)
            flash('Password reset link sent to your email.', 'info')
        else:
            flash('Email not found.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    return render_template('forgot_password.html')

def send_reset_email(user):
    """Send a password reset email."""
    serializer = get_serializer()
    token = serializer.dumps(user.email, salt='password-reset')
    reset_link = url_for('auth.reset_password', token=token, _external=True)

    msg = Message(
        "Password Reset Request",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )
    msg.body = f'''To reset your password, visit:
{reset_link}

This link expires in 30 minutes.
'''
    mail.send(msg)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset."""
    try:
        serializer = get_serializer()
        email = serializer.loads(token, salt='password-reset', max_age=1800)  # 30-minute expiry
    except SignatureExpired:
        flash('The password reset link has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))
    except BadSignature:
        flash('Invalid password reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Invalid user.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html')