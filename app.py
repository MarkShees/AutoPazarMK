import os
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager
from models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok= True)
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok= True)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.cars import cars_bp
    from routes.favorites import favorites_bp
    from routes.messages import messages_bp
    from routes.reviews import reviews_bp
    from routes.payments import payments_bp
    from routes.admin import admin_bp
    from routes.reports import reports_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(cars_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reports_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.context_processor
    def inject_unread():
        from flask_login import current_user
        from models import Message 
        count = 0
        if current_user.is_authenticated:
            count = Message.query.filter_by(
                receiver_id=current_user.id, read_at = None
            ).count()
        return dict(unread_count=count)
    
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug= True)