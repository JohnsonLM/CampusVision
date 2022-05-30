"""
utils.py provides a number of helper fuctions to views.py and auth.py
including mostly database connectors and data checks.
"""
from .app import db
from flask_login import current_user
import datetime
from .models import Slide, Alert, Message, Settings


def mod_counter():
    """count how many slides need moderation attention"""
    count = 0
    for slide in reversed(Slide.query.all()):
        if slide.approval == "Waiting Review":
            count += 1
    return count


def allowed_file(filename, allowed_ext):
    """check if upload has an allowed file type"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_ext


def add_slide(time_start, time_end, title, slide_path, feeds):
    """adds a slide to the database"""
    approval = "Waiting Review"
    submitted_by = current_user.name
    feed00 = "False"
    feed01 = "False"
    feed02 = "False"
    feed03 = "False"
    feed04 = "False"
    feed05 = "False"
    feed06 = "False"
    feed07 = "False"
    feed08 = "False"
    feed09 = "False"
    feed10 = "False"
    for feed in feeds:
        if feed == "feed00":
            feed00 = "True"
        if feed == "feed01":
            feed01 = "True"
        if feed == "feed02":
            feed02 = "True"
        if feed == "feed03":
            feed03 = "True"
        if feed == "feed04":
            feed04 = "True"
        if feed == "feed05":
            feed05 = "True"
        if feed == "feed06":
            feed06 = "True"
        if feed == "feed07":
            feed07 = "True"
        if feed == "feed08":
            feed08 = "True"
        if feed == "feed09":
            feed09 = "True"
        if feed == "feed10":
            feed10 = "True"
    slide_data = Slide(
        time_start=time_start,
        time_end=time_end,
        title=title,
        slide_path=slide_path,
        approval=approval,
        feed00=feed00,
        feed01=feed01,
        feed02=feed02,
        feed03=feed03,
        feed04=feed04,
        feed05=feed05,
        feed06=feed06,
        feed07=feed07,
        feed08=feed08,
        feed09=feed09,
        feed10=feed10,
        submitted_by=submitted_by)
    db.session.add(slide_data)
    db.session.commit()
    return 1


def appr_slide(approval, slide_id):
    """approve slide in database"""
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
        if target_feed == 'feed00' and slide.feed00 == "True":
            if slide.approval == 'Approved':
                if today_date >= start_date:
                    if today_date <= end_date:
                        slides.append(slide.slide_path)
        elif target_feed == 'feed01' and slide.feed01 == "True":
            if slide.approval == 'Approved':
                if today_date >= start_date:
                    if today_date <= end_date:
                        slides.append(slide.slide_path)
        elif target_feed == 'feed02' and slide.feed02 == "True":
            if slide.approval == 'Approved':
                if today_date >= start_date:
                    if today_date <= end_date:
                        slides.append(slide.slide_path)
        elif target_feed == 'feed03' and slide.feed03 == "True":
            if slide.approval == 'Approved':
                if today_date >= start_date:
                    if today_date <= end_date:
                        slides.append(slide.slide_path)
        elif target_feed == 'feed04' and slide.feed04 == "True":
            if slide.approval == 'Approved':
                if today_date >= start_date:
                    if today_date <= end_date:
                        slides.append(slide.slide_path)
        elif target_feed == 'feed05' and slide.feed05 == "True":
            if slide.approval == 'Approved':
                if today_date >= start_date:
                    if today_date <= end_date:
                        slides.append(slide.slide_path)
        elif target_feed == 'feed06' and slide.feed06 == "True":
            if slide.approval == 'Approved':
                if today_date >= start_date:
                    if today_date <= end_date:
                        slides.append(slide.slide_path)
        elif target_feed == 'feed07' and slide.feed07 == "True":
            if slide.approval == 'Approved':
                if today_date >= start_date:
                    if today_date <= end_date:
                        slides.append(slide.slide_path)
        elif target_feed == 'feed08' and slide.feed08 == "True":
            if slide.approval == 'Approved':
                if today_date >= start_date:
                    if today_date <= end_date:
                        slides.append(slide.slide_path)
        elif target_feed == 'feed09' and slide.feed09 == "True":
            if slide.approval == 'Approved':
                if today_date >= start_date:
                    if today_date <= end_date:
                        slides.append(slide.slide_path)
        elif target_feed == 'feed10' and slide.feed10 == "True":
            if slide.approval == 'Approved':
                if today_date >= start_date:
                    if today_date <= end_date:
                        slides.append(slide.slide_path)
    return slides


def update_slide(slide_id, slide_name):
    """update slide in the database"""
    slide_data = Slide.query.get(slide_id)
    slide_data.title = slide_name
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
        if today_date >= start_date:
            if today_date <= end_date:
                message_send.append(item.text)
    return message_send


def delete_message(message_id):
    """remove a message from the database"""
    data = Alert.query.get(message_id)
    db.session.delete(data)
    db.session.commit()
    return 1


def update_settings(duration):
    """update the app settings"""
    data = Settings.query.get(1)
    data.duration = duration
    db.session.commit()
    return 1


def get_settings():
    """fetch the app settings"""
    settings = Settings.query.all()
    return settings[0].duration
