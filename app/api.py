import logging
import datetime
from flask import Blueprint, Flask, jsonify
from .models import Slide, Message

# initialize view routes
api = Blueprint('api', __name__, url_prefix='/api')
# load flask app
app = Flask(__name__, instance_relative_config=True)
# load app configuration from /instance/config.py
app.config.from_pyfile('config.py')
# set logging path
logging.basicConfig(filename='app.log', level=logging.INFO)


@api.route('/slides/<feed>', methods=['GET'])
def slides(feed):
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
