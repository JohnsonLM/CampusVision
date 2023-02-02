"""
models.py defines the database models for the flask app.
"""
from flask_login import UserMixin
from .app import db


class User(UserMixin, db.Model):
    """defines user model"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(1000))
    type = db.Column(db.String(1000))
    eid = db.Column(db.String(100), unique=True)
    groups = db.Column(db.String(1000))


class Feed(db.Model):
    """defines feed model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=True)
    location = db.Column(db.String(1000))
    manager_group = db.Column(db.String(1000))
    status = db.Column(db.String(1000))


class Slide(db.Model):
    """defines slide model"""
    id = db.Column(db.Integer, primary_key=True)
    slide_path = db.Column(db.String(1000))
    time_start = db.Column(db.String(1000))
    time_end = db.Column(db.String(1000))
    title = db.Column(db.String(1000))
    approval = db.Column(db.String(1000))
    submitted_by = db.Column(db.String(1000))
    feeds = db.Column(db.String(1000))

    # function to recall the model from the api
    def to_dict(self):
        return {
            'id': self.id,
            'slide_path': self.slide_path,
            'time_start': self.time_start,
            'time_end': self.time_end,
            'title': self.title,
            'approval': self.approval,
            'submitted_by': self.submitted_by,
            'feeds': self.feeds,
        }


class Alert(db.Model):
    """defines alert model"""
    id = db.Column(db.Integer, primary_key=True)
    alert_text = db.Column(db.String(1000))


class Message(db.Model):
    """defines message model"""
    id = db.Column(db.Integer, primary_key=True)
    time_start = db.Column(db.String(1000))
    time_end = db.Column(db.String(1000))
    text = db.Column(db.String(1000))
    submitted_by = db.Column(db.String(1000))


class Room(db.Model):
    """defines settings model"""
    id = db.Column(db.String(1000), primary_key=True)
    title = db.Column(db.String(1000))
    status = db.Column(db.Integer)

class Keys(db.Model):
    """api keys"""
    id = db.Column(db.String(1000), primary_key=True)
    name = db.Column(db.String(1000))
    key = db.Column(db.String(1000))