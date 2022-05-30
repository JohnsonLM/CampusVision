from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# initilize database
db = SQLAlchemy()


def create_app():
    """main app fuction"""
    # initialize app
    app = Flask(__name__, instance_relative_config=True)
    # load configuration from instance
    # be sure that a config exists in /instance/config.py
    app.config.from_pyfile('config.py')
    # start app using database
    db.init_app(app)

    # initialize login authentication
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # import user model
    from .models import User

    # load user
    @login_manager.user_loader
    def load_user(user_id):
        #  use user id to query for the user in the database using the user model
        return User.query.get(int(user_id))

    # blueprint for auth routes
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth routes
    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
