"""
views.py contains the main view routing for the app.
"""
import json
import os
from flask import render_template, request, Blueprint, flash, url_for, session
from werkzeug.utils import secure_filename, redirect
from .utils import mod_counter, alert_status, add_message, add_slide, allowed_file, appr_slide, \
    remove_slide, update_alert, get_slides, get_message, update_slide, get_video, get_user
from .models import Message, Slide, User, Feed, Keys
import instance.config as app_config

# initialize view routes
app = Blueprint('app', __name__)


@app.route('/')
def index():
    """homepage for the app to display info and stats"""
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    return render_template('home.html',
                           title='Dashboard', # title of the page that appears in browser and heading.
                           name=session.get("user")["name"], # report the signed in user's name.
                           mod_count=mod_counter(), # report how many slides are pending moderation.
                           clients=Feed.query.filter_by().all() # report the current client statuses from the database.
                           )


@app.route('/help')
def help():
    """homepage for the app to display info and stats"""
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    return render_template('help.html',
                           title='Help',
                           name=session.get("user")["name"],
                           mod_count=mod_counter())


@app.route('/manager')
def manager():
    """slide manager for users to view and edit submitted slides"""
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    return render_template('manager.html', title='Your Slides', name=session.get("user")["name"], mod_count=mod_counter())


@app.route('/manager/users')
def manager_users():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Admin":
        users = User.query.all()
        return render_template('manager-users.html',
                               title="User Management",
                               users=users,
                               name=session.get("user")["name"],
                               mod_count=mod_counter())
    else:
        flash("Sorry, you are not allowed to view that page.")
        return redirect(url_for("app.index"))


@app.route('/manager/users/<user_id>')
def editor_user(user_id):
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Admin":
        return render_template('editor_user.html',
                               title="Edit User",
                               selected_user=User.query.filter_by(id=user_id).first(),
                               name=session.get("user")["name"],
                               mod_count=mod_counter())
    else:
        flash("Sorry, you are not allowed to view that page.")
        return redirect(url_for("app.index"))

@app.route('/manager/screens')
def manager_screens():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Admin":
        return render_template('screens.html',
                               title="Screen Generator",
                               name=session.get("user")["name"],
                               mod_count=mod_counter())
    else:
        flash("Sorry, you are not allowed to view that page.")
        return redirect(url_for("app.index"))

@app.route('/profile')
def profile():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    else:
        return render_template('profile.html',
                               name=session.get("user")["name"],
                               mod_count=mod_counter())


@app.route('/upload', methods=['GET'])
def upload_file():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Admin":
        return render_template('upload.html',
                               title='Upload a Slide',
                               name=session.get("user")["name"],
                               mod_count=mod_counter(),
                               feeds=Feed.query.all()
                               )
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Contributor":
        groups = User.query.filter_by(email=session.get("user")["preferred_username"]).first().groups.split(",")
        feeds = []
        for group in groups:
            feeds += Feed.query.filter_by(manager_group=group).all()
        return render_template('upload.html',
                               title='Upload a Slide',
                               name=session.get("user")["name"],
                               mod_count=mod_counter(),
                               feeds=feeds
                               )
    else:
        flash("Sorry! You don't have permission to access that page.")
        return redirect(url_for("app.index"))


@app.route('/upload', methods=['POST'])
def upload_file_post():
    # TODO convert to API request.
    if not session.get("user"): # if the user isn't logged in, send them to the login page.
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Viewer": # prevent view-only users from accessing the upload page.
        flash("Sorry! You don't have permission to access that page.")
        return redirect(url_for("app.index"))
    if 'file' not in request.files: # if no file is loaded in the request, flash a warning.
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '': # if no file is selected, flash a warning.
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename, app_config.ALLOWED_EXTENSIONS): # if the file exists and is an allowed type, save it and flash a success message.
        file.save(os.path.join(app.root_path, 'static/uploads', secure_filename(file.filename)))
        time_start = request.form["time_start"]
        time_end = request.form["time_end"]
        title = request.form["title"]
        slide_path = secure_filename(file.filename)
        feed_list = ','.join(map(str, request.form.getlist('feeds')))
        add_slide(time_start, time_end, title, slide_path, feed_list, session.get("user")["name"])
        flash('Slide submitted successfully', title)
        return redirect(request.url)


@app.route('/moderate', methods=['GET'])
def moderate():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Admin":
        return render_template('moderate.html', title='Slide Moderator', name=session.get("user")["name"])
    else:
        flash("Sorry, you are not allowed to view that page.")
        return redirect(url_for("app.index"))


@app.route('/moderate', methods=['POST'])
def moderate_post():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Admin":
        return render_template('moderate.html',
                               title='Slide Moderator',
                               name=session.get("user")["name"],
                               mod_count=mod_counter())
    else:
        flash("Sorry! You don't have permission to access that page.")
        return redirect(url_for("app.index"))


@app.route('/edit/<slide_id>', methods=['GET'])
def edit(slide_id):
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Viewer":
        flash("Sorry, you are not allowed to view that page.")
        return redirect(url_for("app.index"))
    else:
        return render_template('edit.html',
                               title='Edit Slide',
                               slide=Slide.query.get(slide_id),
                               name=session.get("user")["name"],
                               mod_count=mod_counter(),
                               feeds=Feed.query.all())


@app.route('/edit/<slide_id>', methods=['POST'])
def edit_post(slide_id):
    # TODO convert to API request.
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Viewer":
        flash("Sorry, you are not allowed to view that page.")
        return redirect(url_for("app.index"))
    else:
        update_slide(slide_id,
                     request.form["title_text"],
                     request.form["time_start"],
                     request.form["time_end"],
                     ','.join(map(str, request.form.getlist('feeds'))))
        return render_template('edit.html',
                               title='Edit Slide',
                               slide_id=id,
                               slide=Slide.query.get(slide_id),
                               name=session.get("user")["name"],
                               mod_count=mod_counter(),
                               feeds=Feed.query.all())


@app.route('/messages', methods=['GET'])
def messages():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Viewer":
        flash("Sorry, you are not allowed to view that page.")
        return redirect(url_for("app.index"))
    else:
        return render_template('manager-messages.html',
                               title='Messages',
                               name=session.get("user")["name"],
                               mod_count=mod_counter(),
                               messages=Message.query.all())


@app.route('/messages', methods=['POST'])
def messages_post():
    # TODO convert to API request.
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Viewer":
        flash("Sorry, you are not allowed to view that page.")
        return redirect(url_for("app.index"))
    else:
        text = request.form["message_text"]
        start_time = request.form["time_start"]
        end_time = request.form["time_end"]
        add_message(text, start_time, end_time)
        return render_template('manager-messages.html',
                               title='Messages',
                               name=session.get("user")["name"],
                               mod_count=mod_counter(),
                               messages=Message.query.all())


@app.route('/alerts', methods=['GET'])
def alerts():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Admin":
        return render_template('alerts.html',
                               title='Submit an Emergency Alert',
                               name=session.get("user")["name"],
                               mod_count=mod_counter())
    else:
        flash("Sorry, you are not allowed to view that page.")
        return redirect(url_for("app.index"))

@app.route('/alerts', methods=['POST'])
def alerts_post():
    # TODO convert to API request.
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Admin":
        if request.form["alert_status"] == "Enable":
            update_alert(request.form["alert_text"])
        else:
            update_alert("")
        return render_template('alerts.html',
                               title='Submit an Emergency Alert',
                               name=session.get("user")["name"],
                               mod_count=mod_counter())
    else:
        flash("Sorry, you are not allowed to view that page.")
        return redirect(url_for("app.index"))


@app.route('/settings')
def settings():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first().type == "Admin":
        return render_template('settings.html',
                               title='Settings',
                               name=session.get("user")["name"],
                               mod_count=mod_counter(),
                               feeds=Feed.query.all())
    else:
        flash("Sorry, you are not allowed to view that page.")
        return redirect(url_for("app.index"))

@app.route('/feeds/standard/<title>', methods=['GET'])
def feeds(title):
    return render_template('feed-ajax.html',
                           title=title,
                           alert_status=alert_status(),
                           messages=json.dumps(get_message()),
                           background=title + '.webp',
                           weather_key=Keys.query.filter_by(name="OpenWeatherMap").first().key)


@app.route('/feeds/vertical/<title>', methods=['GET'])
def feeds_vertical(title):
    return render_template('feed_vertical.html',
                           title=title,
                           slides=get_slides(title),
                           alert_status=alert_status(),
                           messages=json.dumps(get_message()),
                           background='bg.jpg',
                           weather_key=Keys.query.filter_by(name="OpenWeatherMap").first().key)


@app.route('/feeds/video/<title>', methods=['GET'])
def feeds_video(title):
    return render_template('feed-video.html',
                           title=title,
                           video=get_video(title),
                           alert_status=alert_status(),
                           messages=json.dumps(get_message()),
                           background=title + '.webp',
                           weather_key=Keys.query.filter_by(name="OpenWeatherMap").first().key)


@app.route('/feeds/directory/<title>', methods=['GET'])
def feeds_directory(title):
    return render_template('feed-directory.html',
                           title=title,
                           alert_status=alert_status(),
                           messages=json.dumps(get_message()),
                           background=title + '.webp',
                           weather_key=Keys.query.filter_by(name="OpenWeatherMap").first().key)

@app.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='404')
