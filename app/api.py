import datetime
from pathlib import Path
from flask import request, Blueprint, session, abort, \
    redirect, url_for, jsonify, Flask, flash
import os
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
    """
    returns all the slides in a given feed that are scheduled to run on the current date
    :param feed: string
    :return: json
    """
    slide_set = []
    for slide in reversed(Slide.query.all()):
        start_date = datetime.datetime.strptime(slide.time_start, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(slide.time_end, '%Y-%m-%d').date()
        today_date = datetime.datetime.now().date()
        if (
            feed in slide.feeds.split(",")
            and slide.approval == 'Approved'
            and start_date <= today_date <= end_date
        ):
            slide_set.append('/static/uploads/' + slide.slide_path)
    return jsonify(slide_set)


@api.route('/slides/<slide_filter>/', methods=['GET'])
def get_slides(slide_filter):
    """
    returns last 500 slides submitted by approval status.
    :param slide_filter: string
    :return: json
    """
    if not session.get("user"):
        abort(401)
    if slide_filter == "None":
        data = Slide.query.order_by(Slide.id.desc()).limit(500)
    else:
        data = Slide.query.filter_by(
            approval=slide_filter
        ).order_by(Slide.id.desc()).limit(500)
    return {'data': [item.to_dict() for item in data]}


@api.route('/slides/<slide_id>/delete', methods=['POST'])
def delete_slide(slide_id):
    """
    Deletes slide by slide id.
    :param slide_id: int
    :return: Moderate view
    """
    if not session.get("user"):
        abort(401)
    elif User.query.filter_by(
            email=session.get("user")["preferred_username"]
    ).first().type == "Admin":
        slide = Slide.query.filter_by(id=slide_id)
        data = Slide.query.get(slide_id)
        data_path = "./static/uploads/" + data.slide_path
        base_path = Path(__file__).parent
        file_path = (base_path / data_path).resolve()
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            flash("The file for that item did not exist, deleting database record anyway...")
        slide.delete()
        db.session.commit()
        flash("The slide has been deleted.")
        return redirect(url_for("app.moderate"))
    else:
        abort(401)

@api.route('/slides/<slide_id>/approve', methods=['POST'])
def approve_slide(slide_id):
    """
    Sets slide as approved by slide id
    :param slide_id: int
    :return: Moderate view
    """
    if not session.get("user"):
        abort(401)
    elif User.query.filter_by(
            email=session.get("user")["preferred_username"]
    ).first().type == "Admin":
        data = Slide.query.get(slide_id)
        data.approval = "Approved"
        db.session.commit()
        flash(data.title + " has been approved.")
        return redirect(url_for("app.moderate"))
    else:
        abort(401)

@api.route('/slides/<slide_id>/deny', methods=['POST'])
def deny_slide(slide_id):
    """
    Sets slide as denied by slide id.
    :param slide_id: int
    :return: moderate view
    """
    if not session.get("user"):
        abort(401)
    elif User.query.filter_by(
            email=session.get("user")["preferred_username"]
    ).first().type == "Admin":
        data = Slide.query.get(slide_id)
        data.approval = "Denied"
        db.session.commit()
        flash(data.title + " has been denied.")
        return redirect(url_for("app.moderate"))
    else:
        abort(401)

@api.route('/slides/user/<name>/', methods=['GET'])
def get_user_slides(name):
    """
    Returns slides submitted by a user by name.
    :param name: string
    :return: json
    """
    if not session.get("user"):
        abort(401)
    data = Slide.query.filter_by(submitted_by=name).limit(500)
    return {'data': [item.to_dict() for item in data]}


@api.route('/messages', methods=['GET'])
def messages():
    """
    Returns messages for the current date.
    :return: json
    """
    if not session.get("user"):
        abort(401)
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
    """
    Deletes messages by id given in form.
    :return: messages view
    """
    if not session.get("user"):
        abort(401)
    data = Message.query.filter_by(id=request.form['message_id'])
    data.delete()
    db.session.commit()
    return redirect(url_for('app.messages'))


@api.route('/user/<email>/edit', methods=['POST'])
def edit_user(email):
    """
    :param email: string
    :return: user view
    """
    if not session.get("user"):
        abort(401)
    elif User.query.filter_by(
            email=session.get("user")["preferred_username"]
    ).first().type == "Admin":
        selected_user = User.query.filter_by(email=email).first()
        selected_user.name = request.form["name"]
        selected_user.type = request.form["type"]
        selected_user.groups = request.form["groups"]
        db.session.commit()
        return redirect(url_for("app.manager_users"))
    else:
        abort(401)


@api.route('/user/<email>/delete', methods=['POST'])
def delete_user(email):
    """
    Deletes user by email.
    :param email: string
    :return: user view
    """
    if not session.get("user"):
        abort(401)
    elif User.query.filter_by(
            email=session.get("user")["preferred_username"]
    ).first().type == "Admin":
        selected_user = User.query.filter_by(email=email)
        selected_user.delete()
        db.session.commit()
        return redirect(url_for("app.manager_users"))
    else:
        abort(401)


@api.route('/feeds/', methods=['GET'])
def feeds():
    """
    Get feeds list.
    :return: json
    """
    feeds = []
    for feed in Feed.query.all():
        feeds.append(feed.name)
    return jsonify(feeds)


@api.route('/feeds/add', methods=['POST'])
def add_feed():
    """
    Adds a new feed to the database list.
    :return: settings view
    """
    if not session.get("user"):
        abort(401)
    elif User.query.filter_by(
            email=session.get("user")["preferred_username"]
    ).first().type == "Admin":
        data = Feed(
            name=request.form["feed_name"],
            manager_group=request.form["feed_group"]
        )
        db.session.add(data)
        db.session.commit()
        flash(
            "The feed " + request.form["feed_name"] + " has been created")
        return redirect(url_for("app.settings"))
    else:
        abort(401)


@api.route('/feeds/delete', methods=['POST'])
def delete_feed():
    """
    Deletes feed by id provided by form.
    :return: settings view
    """
    if not session.get("user"):
        abort(401)
    elif User.query.filter_by(
            email=session.get("user")["preferred_username"]
    ).first().type == "Admin":
        selected = Feed.query.get(request.form["feed_id"])
        db.session.delete(selected)
        db.session.commit()
        flash("The feed " + selected.name + " has been deleted")
        return redirect(url_for("app.settings"))
    else:
        abort(401)


@api.route('/keys/openweathermap', methods=['POST'])
def update_weather_api():
    """
    Updates key in database by key provided in form.
    :return: settings view
    """
    if not session.get("user"):
        abort(401)
    elif User.query.filter_by(
            email=session.get("user")["preferred_username"]
    ).first().type == "Admin":
        key = Keys.query.filter_by(name="OpenWeatherMap").first()
        key.key = request.form['key']
        db.session.commit()
        return redirect(url_for("app.settings"))
    else:
        abort(401)


@api.route('/clients/register', methods=['POST'])
def update_clients():
    """

    :return:
    """
    if not session.get("user"):
        abort(401)
    elif User.query.filter_by(
            email=session.get("user")["preferred_username"]
    ).first().type == "Admin":
        data = request.json
        feed = Feed.query.filter_by(name=data['Feed']).first()
        feed.status = datetime.datetime.now().strftime("%D %H:%M:%S")
        db.session.commit()
        return jsonify(200)
    else:
        abort(401)
