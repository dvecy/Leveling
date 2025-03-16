from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db, mail, login_manager, csrf
from config import Config
from models import User, Task
import math
from datetime import datetime, timedelta
from flask_migrate import Migrate  # Import Flask-Migrate

def get_level_title(level: int) -> str:
    if level <= 10:
        return "Rookie"
    elif level <= 20:
        return "Apprentice"
    elif level <= 30:
        return "Adept"
    elif level <= 40:
        return "Specialist"
    elif level <= 50:
        return "Expert"
    elif level <= 60:
        return "Champion"
    elif level <= 70:
        return "Master"
    elif level <= 80:
        return "Grandmaster"
    elif level <= 90:
        return "Legend"
    elif level <= 100:
        return "Mythic"
    else:
        return "Transcendent"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Initialize Flask-Migrate inside your factory:
    migrate = Migrate(app, db)
    
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Register auth blueprint
    from routes.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')
    
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        profile = current_user.profile
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        
        def calculate_level_progress(xp):
            level = 1
            required_xp = 100
            while xp >= required_xp:
                xp -= required_xp
                level += 1
                required_xp = math.floor(required_xp * 1.5)
            return level, required_xp, xp
        
        current_level, next_level_xp, current_level_xp = calculate_level_progress(profile.xp)
        xp_percentage = (current_level_xp / next_level_xp) * 100 if next_level_xp > 0 else 100
        level_title = get_level_title(current_level)
        
        return render_template('dashboard.html',
            user=current_user,
            profile=profile,
            tasks=tasks,
            xp_percentage=xp_percentage,
            current_level=current_level,
            next_level_xp=next_level_xp,
            level_title=level_title
        )
    
    @app.route('/tasks', methods=['POST'])
    @login_required
    def create_task():
        data = request.get_json()
        task = Task(
            description=data['description'],
            user_id=current_user.id,
            xp=20
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({
            'id': task.id,
            'description': task.description,
            'completed': task.completed
        }), 201
    
    @app.route('/tasks/<int:task_id>', methods=['DELETE', 'PATCH'])
    @login_required
    def manage_task(task_id):
        task = Task.query.get_or_404(task_id)
        if request.method == 'DELETE':
            db.session.delete(task)
            db.session.commit()
            return jsonify({'message': 'Task deleted'}), 200
        elif request.method == 'PATCH':
            if not task.completed:
                task.completed = True
                current_user.profile.xp += task.xp

                # Update daily streak:
                now = datetime.utcnow()
                if current_user.profile.last_completed_task:
                    last_date = current_user.profile.last_completed_task.date()
                    today = now.date()
                    if last_date == today:
                        # Same day: do nothing
                        pass
                    elif last_date == today - timedelta(days=1):
                        current_user.profile.streak += 1
                    else:
                        current_user.profile.streak = 1
                else:
                    current_user.profile.streak = 1
                current_user.profile.last_completed_task = now

                def calculate_level(xp):
                    level = 1
                    required_xp = 100
                    while xp >= required_xp:
                        xp -= required_xp
                        level += 1
                        required_xp = math.floor(required_xp * 1.5)
                    return level, required_xp, xp

                new_level, next_xp, current_level_xp = calculate_level(current_user.profile.xp)
                level_up = new_level != current_user.profile.level
                current_user.profile.level = new_level
                db.session.commit()
                
                return jsonify({
                    'total_xp': current_user.profile.xp,
                    'current_level': new_level,
                    'current_level_xp': current_level_xp,
                    'next_level_xp': next_xp,
                    'level_up': level_up,
                    'streak': current_user.profile.streak
                }), 200
            
            return jsonify({'message': 'Task already completed'}), 400
    
    @app.route('/update_xp', methods=['POST'])
    @login_required
    def update_xp():
        amount = request.json.get('amount', 0)
        current_user.profile.xp += amount
        
        def calculate_level(xp):
            level = 1
            required_xp = 100
            while xp >= required_xp:
                xp -= required_xp
                level += 1
                required_xp = math.floor(required_xp * 1.5)
            return level, required_xp, xp
        
        new_level, next_xp, current_level_xp = calculate_level(current_user.profile.xp)
        level_up = new_level != current_user.profile.level
        current_user.profile.level = new_level
        db.session.commit()
        
        return jsonify({
            'total_xp': current_user.profile.xp,
            'current_level': new_level,
            'current_level_xp': current_level_xp,
            'next_level_xp': next_xp,
            'level_up': level_up
        })
    
    @app.route('/delete_completed_tasks', methods=['POST'])
    @login_required
    def delete_completed_tasks():
        completed_tasks = Task.query.filter_by(user_id=current_user.id, completed=True).all()
        for t in completed_tasks:
            db.session.delete(t)
        db.session.commit()
        flash('Completed tasks have been deleted.', 'success')
        return jsonify({'message': 'Completed tasks deleted'}), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
