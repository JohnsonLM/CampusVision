from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import instance.config as app_config
db = SQLAlchemy()
from .api import api as api_blueprint
from .views import app as main_blueprint
from .auth import auth as auth_blueprint


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config)

    Session(app)

    # This section is needed for url_for("foo", _external=True) to automatically
    # generate http scheme when this sample is running on localhost,
    # and to generate https scheme when it is deployed behind reversed proxy.
    # See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(api_blueprint,  url_prefix='/api')

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app
