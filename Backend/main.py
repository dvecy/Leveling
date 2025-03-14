from flask import Flask, render_template, jsonify, request
from flask_login import LoginManager, login_required, current_user
from extensions import db, mail, login_manager, csrf
from config import Config
from models import User, Task

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Set login view
    login_manager.login_view = 'auth.login'
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Import and register blueprints
    from routes.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')
    
    # Routes
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        profile = current_user.profile
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html',
            user=current_user,
            profile=profile,
            tasks=tasks,
            xp_percentage=(profile.xp / profile.next_level_xp) * 100 if profile.next_level_xp else 0
        )
    
    # Task routes
    @app.route('/tasks', methods=['POST'])
    @login_required
    def create_task():
        data = request.get_json()
        task = Task(
            description=data['description'],
            user_id=current_user.id,
            xp=20  # Default XP for each task
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
            task.completed = not task.completed
            if task.completed:
                current_user.profile.xp += task.xp
                if current_user.profile.xp >= current_user.profile.next_level_xp:
                    current_user.profile.level += 1
                    current_user.profile.next_level_xp = int(current_user.profile.next_level_xp * 1.5)
            db.session.commit()
            return jsonify({
                'xp': current_user.profile.xp,
                'level': current_user.profile.level,
                'next_level_xp': current_user.profile.next_level_xp
            }), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)