from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def create_app():
    ## initialize app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    # initialize database
    db.init_app(app)
    # initialize login authentication
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
