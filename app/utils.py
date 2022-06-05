"""
utils.py provides a number of helper functions to views.py and auth.py
including mostly database connectors and data checks.
"""
from .app import db
from flask_login import current_user
import datetime
from .models import Slide, Alert, Message, Settings


def mod_counter():
    """count how many slides need moderation attention

    Returns:
        the number of slides waiting to be moderated.
    """
    count = 0
    for slide in reversed(Slide.query.all()):
        if slide.approval == "Waiting Review":
            count += 1
    return count


def allowed_file(filename, allowed_ext):
    """check if upload has an allowed file type

    Args:
        filename (string): the filename to check
        allowed_ext (list): extensions that should be allowed in uploads
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_ext


def add_slide(time_start, time_end, title, slide_path, feeds):
    """Adds a slide to the database

    Args:
        time_start (string): date-time the slide should begin displaying.
        time_end (string): date-time the slide should stop displaying.
        title (string): name of the slide.
        slide_path (string): filename/path of the slide relate to the /static/uploads folder.
        feeds (list): feeds that the slide should be submitted to.

    Returns:
        None
    """
    approval = "Waiting Review"
    submitted_by = current_user.name
    slide_data = Slide(
        time_start=time_start,
        time_end=time_end,
        title=title,
        slide_path=slide_path,
        approval=approval,
        submitted_by=submitted_by,
        feeds=str(feeds),
    )
    db.session.add(slide_data)
    db.session.commit()
    return 1


def appr_slide(approval, slide_id):
    """approve slide in database

    Args:
        approval (string): the approval status of the slide.
        slide_id (integer): id of the slide to change.
    """
    selected_slide = Slide.query.get(slide_id)
    selected_slide.approval = approval
    db.session.commit()
    return 1


def remove_slide(slide_id):
    """
    remove slide from database
    does not remove image from uploads folder
    """
    selected_slide = Slide.query.get(slide_id)
    db.session.delete(selected_slide)
    db.session.commit()
    return 1


def get_slides(target_feed):
    """fetch slides from the database based on the desired feed"""
    slides = []
    for slide in reversed(Slide.query.all()):
        start_date = datetime.datetime.strptime(slide.time_start, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(slide.time_end, '%Y-%m-%d').date()
        today_date = datetime.datetime.now().date()
        if target_feed in slide.feeds and slide.approval == 'Approved':
            if start_date <= today_date <= end_date:
                slides.append(slide.slide_path)
    return slides


def update_slide(slide_id, slide_name, time_start, time_end, feeds):
    """update slide in the database"""
    slide_data = Slide.query.get(slide_id)
    slide_data.title = slide_name
    slide_data.time_start = time_start
    slide_data.time_end = time_end
    slide_data.feeds = feeds
    db.session.commit()
    return 1


def alert_status():
    """get the status of alert and alert content"""
    alert_data = Alert.query.get(1)
    if alert_data.alert_text is not None:
        return alert_data.alert_text
    else:
        return ""


def update_alert(alert_text):
    """update alert content and status"""
    alert_data = Alert.query.get(1)
    alert_data.alert_text = alert_text
    db.session.commit()
    return 1


def add_message(message_text, time_start, time_end):
    """add a message to the database"""
    data = Message(
        text=message_text,
        time_start=time_start,
        time_end=time_end
    )
    db.session.add(data)
    db.session.commit()
    return 1


def get_message():
    """get a message from the database"""
    messages = Message.query.all()
    message_send = []
    for item in messages:
        start_date = datetime.datetime.strptime(item.time_start, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(item.time_end, '%Y-%m-%d').date()
        today_date = datetime.datetime.now().date()
        if start_date <= today_date <= end_date:
            message_send.append(item.text)
    return message_send


def delete_message(message_id):
    """remove a message from the database"""
    data = Alert.query.get(message_id)
    db.session.delete(data)
    db.session.commit()
    return 1


def update_settings(duration, signups, feeds):
    """update the app settings"""
    data = Settings.query.get(1)
    data.duration = duration
    data.allow_signups = signups
    data.feeds = feeds
    db.session.commit()
    return 1


def get_settings():
    """fetch the app settings"""
    settings = Settings.query.all()
    return settings[0]


def signups_allowed():
    """fetch the signup setting"""
    settings = Settings.query.all()
    return settings[0].allow_signups
