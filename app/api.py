import datetime
from flask import request, Blueprint, session, abort, redirect, url_for, jsonify, Flask
from .models import Slide, Message, User, Feed, Keys
from .app import db

# initialize view routes
api = Blueprint('api', __name__, url_prefix='/api')
# load flask app
app = Flask(__name__, instance_relative_config=True)
# load app configuration from /instance/config.py
app.config.from_pyfile('config.py')


@api.route('/slides/<feed>', methods=['GET'])
def get_feed_slides(feed):
    slide_set = []
    for slide in reversed(Slide.query.all()):
        start_date = datetime.datetime.strptime(slide.time_start, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(slide.time_end, '%Y-%m-%d').date()
        today_date = datetime.datetime.now().date()
        if (
            feed in slide.feeds
            and slide.approval == 'Approved'
            and start_date <= today_date <= end_date
        ):
            slide_set.append('/static/uploads/' + slide.slide_path)
    return jsonify(slide_set)


@api.route('/slides/<slide_filter>/', methods=['GET'])
def get_slides(slide_filter):
    if slide_filter == "None":
        data = Slide.query.limit(500)
    else:
        data = Slide.query.filter_by(approval=slide_filter).limit(500)
    return {'data': [item.to_dict() for item in data]}


@api.route('/slides/user/<name>/', methods=['GET'])
def get_user_slides(name):
    data = Slide.query.filter_by(submitted_by=name).limit(500)
    return {'data': [item.to_dict() for item in data]}


@api.route('/messages', methods=['GET'])
def messages():
    message_set = []
    for item in Message.query.all():
        start_date = datetime.datetime.strptime(item.time_start, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(item.time_end, '%Y-%m-%d').date()
        today_date = datetime.datetime.now().date()
        if start_date <= today_date <= end_date:
            message_set.append(item.text)
    return jsonify(message_set)


@api.route('/messages/delete', methods=['POST'])
def delete_messages():
    data = Message.query.filter_by(id=request.form['message_id'])
    data.delete()
    db.session.commit()
    return redirect(url_for('app.messages'))

@api.route('/user/<email>/edit', methods=['POST'])
def edit_user(email):
    if not session.get("user"):
        abort(401)
    selected_user = User.query.filter_by(email=email).first()
    selected_user.name = request.form["name"]
    selected_user.type = request.form["type"]
    db.session.commit()
    return redirect(url_for("app.manager_users"))

@api.route('/feeds/', methods=['GET'])
def feeds():
    feeds = []
    for feed in Feed.query.all():
        feeds.append(feed.name)
    return jsonify(feeds)


@api.route('/feeds/add', methods=['POST'])
def add_feed():
    if not session.get("user"):
        abort(401)
    data = Feed(name=request.form["feed_name"])
    db.session.add(data)
    db.session.commit()
    return redirect(url_for("app.settings"))


@api.route('/feeds/delete', methods=['POST'])
def delete_feed():
    if not session.get("user"):
        abort(401)
    selected = Feed.query.get(request.form["feed_id"])
    db.session.delete(selected)
    db.session.commit()
    return redirect(url_for("app.settings"))


@api.route('/keys/openweathermap', methods=['POST'])
def update_weather_api():
    if not session.get("user"):
        abort(401)
    key = Keys.query.filter_by(name="OpenWeatherMap").first()
    key.key = request.form['key']
    db.session.commit()
    return redirect(url_for("app.settings"))

@api.route('/clients/register', methods=['POST'])
def update_clients():
    data = request.json
    feed = Feed.query.filter_by(name=data['Feed']).first()
    feed.status = datetime.datetime.now().strftime("%D %H:%M:%S")
    db.session.commit()
    return jsonify(200)