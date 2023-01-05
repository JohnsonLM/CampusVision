import datetime
from flask import request, Blueprint, session, abort, redirect, url_for, flash, jsonify, json, Flask
from .models import Slide, Message
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


@api.route('/slides/', methods=['GET'])
def get_slides():
    data = Slide.query.limit(1000)
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
