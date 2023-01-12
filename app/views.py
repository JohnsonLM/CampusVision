import json
import os
from flask import render_template, request, Blueprint, flash, url_for, session
from sqlalchemy import desc
from werkzeug.utils import secure_filename, redirect
from .utils import mod_counter, alert_status, add_message, add_slide, allowed_file, appr_slide, \
    remove_slide, update_alert, get_slides, get_message, update_slide, get_video, get_user
from .models import Message, Slide, Room, User, Feed
import instance.config as app_config

# initialize view routes
app = Blueprint('app', __name__)


@app.route('/')
def index():
    """homepage for the app to display info and stats"""
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    return render_template('home.html',
                           title='Dashboard',
                           mod_count=mod_counter(),
                           feeds=Feed.query.all(),
                           name=session.get("user")["name"])


@app.route('/manager')
def manager():
    """slide manager for users to view and edit submitted slides"""
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    page = request.args.get('page', 1, type=int)
    posts = Slide.query.order_by(desc(Slide.id)).paginate(page=page, per_page=app_config.POSTS_PER_PAGE, error_out=False)
    next_url = url_for('app.manager', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('app.manager', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('manager.html',
                           title='Your Slides',
                           users=posts.items,
                           name=session.get("user")["name"],
                           filter=['Approved', 'Waiting Review', 'Denied'],
                           mod_count=mod_counter(),
                           next_url=next_url,
                           prev_url=prev_url)


@app.route('/manager/users')
def manager_users():
    users = User.query.all()
    return render_template('manager-users.html',
                           title="User Management",
                           users=users,
                           name=session.get("user")["name"],
                           mod_count=mod_counter())


@app.route('/manager/users/<user_id>')
def editor_user(user_id):

    return render_template('editor_user.html',
                           title="Edit User",
                           selected_user=User.query.filter_by(id=user_id).first(),
                           name=session.get("user")["name"],
                           mod_count=mod_counter())

@app.route('/manager/screens')
def manager_screens():
    return render_template('screens.html',
                           title="Screen Generator",
                           feeds=Feed.query.all(),
                           name=session.get("user")["name"],
                           mod_count=mod_counter())


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
    return render_template('upload.html',
                           title='Upload a Slide',
                           name=session.get("user")["name"],
                           mod_count=mod_counter(),
                           feeds=Feed.query.all()
                           )


@app.route('/upload', methods=['POST'])
def upload_file_post():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename, app_config.ALLOWED_EXTENSIONS):
        file.save(os.path.join(app.root_path, 'static/uploads', secure_filename(file.filename)))
        time_start = request.form["time_start"]
        time_end = request.form["time_end"]
        title = request.form["title"]
        slide_path = secure_filename(file.filename)
        feed_list = request.form.getlist('feeds')
        add_slide(time_start, time_end, title, slide_path, feed_list, session.get("user")["name"])
        flash('Slide submitted successfully', title)
        return redirect(request.url)


@app.route('/moderate', methods=['GET'])
def moderate():
    """
    check if user is logged in and is an admin
    if not then return user to login screen
    """
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif session.get("user"):
        page = request.args.get('page', 1, type=int)
        posts = Slide.query.order_by(desc(Slide.id)).paginate(page=page, per_page=app_config.POSTS_PER_PAGE, error_out=False)
        next_url = url_for('app.moderate', page=posts.next_num) \
            if posts.has_next else None
        prev_url = url_for('app.moderate', page=posts.prev_num) \
            if posts.has_prev else None
        return render_template('moderate.html',
                               title='Slide Moderator',
                               name=session.get("user")["name"],
                               users=posts.items,
                               filter=['Approved', 'Waiting Review', 'Denied'],
                               mod_count=mod_counter(),
                               next_url=next_url,
                               prev_url=prev_url)
    else:
        return redirect(url_for('app.index'))


@app.route('/moderate', methods=['POST'])
def moderate_post():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
        # nested to prevent errors when users not logged in
    if request.method == 'POST':
        if 'Approve' in request.form:
            appr_slide('Approved', int(request.form['slide_id']))
        elif 'Deny' in request.form:
            appr_slide('Denied', int(request.form['slide_id']))
        elif 'Delete' in request.form:
            remove_slide(request.form['slide_id'])
    page = request.args.get('page', 1, type=int)
    posts = Slide.query.order_by(desc(Slide.id)).paginate(page=page, per_page=app_config.POSTS_PER_PAGE, error_out=False)
    next_url = url_for('app.moderate', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('app.moderate', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('moderate.html',
                           title='Slide Moderator',
                           name=session.get("user")["name"],
                           users=posts.items,
                           filter=['Approved', 'Waiting Review', 'Denied'],
                           mod_count=mod_counter(),
                           next_url=next_url,
                           prev_url=prev_url)


@app.route('/edit/<slide_id>', methods=['GET'])
def edit(slide_id):
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    return render_template('edit.html',
                           title='Edit Slide',
                           slide=Slide.query.get(slide_id),
                           name=session.get("user")["name"],
                           mod_count=mod_counter(),
                           feeds=Feed.query.all())


@app.route('/edit/<slide_id>', methods=['POST'])
def edit_post(slide_id):
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    update_slide(slide_id,
                 request.form["title_text"],
                 request.form["time_start"],
                 request.form["time_end"],
                 str(request.form.getlist('feeds')))
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
    elif get_user(session.get("user")).type:
        return render_template('manager-messages.html',
                               title='Messages',
                               name=session.get("user")["name"],
                               mod_count=mod_counter(),
                               messages=Message.query.all())
    else:
        return redirect(url_for("app.index"))


@app.route('/messages', methods=['POST'])
def messages_post():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    if get_user(session.get("user")).type:
        if request.method == 'POST':
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
    else:
        return render_template('alerts.html',
                               title='Submit an Emergency Alert',
                               name=session.get("user")["name"],
                               mod_count=mod_counter())


@app.route('/alerts', methods=['POST'])
def alerts_post():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    if request.method == 'POST':
        status = request.form["alert_status"]
        if status == "Enable":
            update_alert(request.form["alert_text"])
        elif status == "Disable":
            update_alert("")
    return render_template('alerts.html',
                           title='Submit an Emergency Alert',
                           name=session.get("user")["name"],
                           mod_count=mod_counter())


@app.route('/settings')
def settings():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    return render_template('settings.html',
                           title='Feed Settings',
                           name=session.get("user")["name"],
                           mod_count=mod_counter(),
                           feeds=Feed.query.all())


@app.route('/clients')
def clients():
    return render_template('clients.html',
                           title='Clients',
                           mod_count=mod_counter(),
                           clients=session.get('active_clients'))


@app.route('/status')
def status():
    return render_template('status.html', title='Operational Status', rooms=Room.query.all())


@app.route('/feeds/standard/<title>', methods=['GET'])
def feeds(title):
    return render_template('feed-ajax.html',
                           title=title,
                           alert_status=alert_status(),
                           messages=json.dumps(get_message()),
                           background=title + '.webp',
                           weather_key=app_config.WEATHER_KEY
                           )


@app.route('/feeds/vertical/<title>', methods=['GET'])
def feeds_vertical(title):
    return render_template('feed_vertical.html',
                           title=title,
                           slides=get_slides(title),
                           alert_status=alert_status(),
                           messages=json.dumps(get_message()),
                           background='bg.jpg',
                           weather_key=app_config.WEATHER_KEY)


@app.route('/feeds/video/<title>', methods=['GET'])
def feeds_video(title):
    return render_template('feed-video.html',
                           title=title,
                           video=get_video(title),
                           alert_status=alert_status(),
                           messages=json.dumps(get_message()),
                           background=title + '.webp',
                           weather_key=app_config.WEATHER_KEY)
