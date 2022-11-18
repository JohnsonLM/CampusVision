import json
import logging
import os
import ast
from flask import render_template, request, Blueprint, flash, Flask, url_for, session
from flask_login import login_required, current_user
from sqlalchemy import desc
from werkzeug.utils import secure_filename, redirect
from .utils import mod_counter, alert_status, add_message, add_slide, allowed_file, appr_slide, \
    remove_slide, update_alert, get_slides, get_message, update_settings, get_settings, update_slide, get_video
from .models import Message, Slide, Room

# initialize view routes
main = Blueprint('main', __name__)
app = Flask(__name__, instance_relative_config=True)
# load app configuration from /instance/config.py
app.config.from_pyfile('config.py')

# set logging path
logging.basicConfig(filename='app.log', level=logging.INFO)


@main.route('/')
def index():
    """homepage for the app to display info and stats"""
    app.logger.info('Home Page Served')
    return render_template('home.html',
                           title='Dashboard',
                           mod_count=mod_counter(),
                           feeds=ast.literal_eval(get_settings().feeds),
                           clients=session.get('active_clients'),
                           name="Profile"
                           )


@main.route('/manager')
@login_required
def manager():
    """slide manager for users to view and edit submitted slides"""
    page = request.args.get('page', 1, type=int)
    posts = Slide.query.order_by(desc(Slide.id)).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.manager', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.manager', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('manager.html',
                           title='All Slides',
                           users=posts.items,
                           name=current_user.name,
                           filter=['Approved', 'Waiting Review', 'Denied'],
                           mod_count=mod_counter(),
                           next_url=next_url,
                           prev_url=prev_url)


@main.route('/manager/approved')
@login_required
def manager_approved():
    page = request.args.get('page', 1, type=int)
    posts = Slide.query.filter_by(approval='Approved').order_by(desc(Slide.id)).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.manager_approved', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.manager_approved', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('manager.html',
                           title='Approved Slides',
                           users=posts.items,
                           name=current_user.name,
                           filter=['Approved'],
                           mod_count=mod_counter(),
                           next_url=next_url,
                           prev_url=prev_url)


@main.route('/manager/waiting')
@login_required
def manager_waiting():
    page = request.args.get('page', 1, type=int)
    posts = Slide.query.filter_by(approval='Waiting Review').order_by(desc(Slide.id)).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.manager_waiting', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.manager_waiting', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('manager.html',
                           title='Waiting Slides',
                           users=posts.items,
                           name=current_user.name,
                           filter=['Waiting Review'],
                           mod_count=mod_counter(),
                           next_url=next_url,
                           prev_url=prev_url)


@main.route('/manager/denied')
@login_required
def manager_denied():
    page = request.args.get('page', 1, type=int)
    posts = Slide.query.filter_by(approval='Denied').order_by(desc(Slide.id)).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.manager_denied', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.manager_denied', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('manager.html',
                           title='Denied Slides',
                           users=posts.items,
                           name=current_user.name,
                           filter=['Denied'],
                           mod_count=mod_counter(),
                           next_url=next_url,
                           prev_url=prev_url)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, mod_count=mod_counter())


@main.route('/upload', methods=['GET'])
@login_required
def upload_file():
    return render_template('upload.html',
                           title='Upload a Slide',
                           name=current_user.name,
                           mod_count=mod_counter(),
                           feeds=ast.literal_eval(get_settings().feeds))


@main.route('/upload', methods=['POST'])
@login_required
def upload_file_post():
    if 'file' not in request.files:
        flash('No file part')
        app.logger.info('Slide upload failed')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        app.logger.info('Slide upload failed')
        return redirect(request.url)
    if file and allowed_file(file.filename, app.config["ALLOWED_EXTENSIONS"]):
        file.save(os.path.join(app.static_folder, 'uploads', secure_filename(file.filename)))
        time_start = request.form["time_start"]
        time_end = request.form["time_end"]
        title = request.form["title"]
        slide_path = secure_filename(file.filename)
        feed_list = request.form.getlist('feeds')
        add_slide(time_start, time_end, title, slide_path, feed_list)
        app.logger.info('Slide %s submitted successfully', title)
        return redirect(request.url)


@main.route('/mod', methods=['GET'])
@login_required
def moderate():
    """
    check if user is logged in and is an admin
    if not then return user to login screen
    """
    if current_user.is_authenticated:
        # nested to prevent errors when users not logged in
        if current_user.is_admin:
            page = request.args.get('page', 1, type=int)
            posts = Slide.query.order_by(desc(Slide.id)).paginate(page, app.config['POSTS_PER_PAGE'], False)
            next_url = url_for('main.moderate', page=posts.next_num) \
                if posts.has_next else None
            prev_url = url_for('main.moderate', page=posts.prev_num) \
                if posts.has_prev else None
            return render_template('moderate.html',
                                   title='Slide Moderator',
                                   name=current_user.name,
                                   users=posts.items,
                                   filter=['Approved', 'Waiting Review', 'Denied'],
                                   mod_count=mod_counter(),
                                   next_url=next_url,
                                   prev_url=prev_url)
    return redirect(url_for('auth.login'))


@main.route('/mod', methods=['POST'])
@login_required
def moderate_post():
    """
    check if user is logged in and is an admin
    if not then return user to login screen
    """
    if current_user.is_authenticated:
        # nested to prevent errors when users not logged in
        if current_user.is_admin:
            if request.method == 'POST':
                if 'Approve' in request.form:
                    appr_slide('Approved', int(request.form['slide_id']))
                elif 'Deny' in request.form:
                    appr_slide('Denied', int(request.form['slide_id']))
                elif 'Delete' in request.form:
                    remove_slide(request.form['slide_id'])
            page = request.args.get('page', 1, type=int)
            posts = Slide.query.order_by(desc(Slide.id)).paginate(page, app.config['POSTS_PER_PAGE'], False)
            next_url = url_for('main.moderate', page=posts.next_num) \
                if posts.has_next else None
            prev_url = url_for('main.moderate', page=posts.prev_num) \
                if posts.has_prev else None
            return render_template('moderate.html',
                                   title='Slide Moderator',
                                   name=current_user.name,
                                   users=posts.items,
                                   filter=['Approved', 'Waiting Review', 'Denied'],
                                   mod_count=mod_counter(),
                                   next_url=next_url,
                                   prev_url=prev_url)
    return redirect(url_for('auth.login'))


@main.route('/mod/denied')
@login_required
def mod_denied():
    if current_user.is_authenticated:
        # nested to prevent errors when users not logged in
        if current_user.is_admin:
            if request.method == 'POST':
                if 'Approve' in request.form:
                    appr_slide('Approved', int(request.form['slide_id']))
                elif 'Deny' in request.form:
                    appr_slide('Denied', int(request.form['slide_id']))
                elif 'Delete' in request.form:
                    remove_slide(request.form['slide_id'])
            page = request.args.get('page', 1, type=int)
            posts = Slide.query.filter_by(approval='Denied').order_by(desc(Slide.id)).paginate(page, app.config['POSTS_PER_PAGE'], False)
            next_url = url_for('main.mod_denied', page=posts.next_num) \
                if posts.has_next else None
            prev_url = url_for('main.mod_denied', page=posts.prev_num) \
                if posts.has_prev else None
            return render_template('moderate.html',
                                   title='Denied Slides',
                                   users=posts.items,
                                   name=current_user.name,
                                   filter=['Denied'],
                                   mod_count=mod_counter(),
                                   next_url=next_url,
                                   prev_url=prev_url)
    return redirect(url_for('auth.login'))


@main.route('/mod/approved')
@login_required
def mod_approved():
    if current_user.is_authenticated:
        # nested to prevent errors when users not logged in
        if current_user.is_admin:
            if request.method == 'POST':
                if 'Approve' in request.form:
                    appr_slide('Approved', int(request.form['slide_id']))
                elif 'Deny' in request.form:
                    appr_slide('Denied', int(request.form['slide_id']))
                elif 'Delete' in request.form:
                    remove_slide(request.form['slide_id'])
            page = request.args.get('page', 1, type=int)
            posts = Slide.query.filter_by(approval='Approved').order_by(desc(Slide.id)).paginate(page, app.config['POSTS_PER_PAGE'], False)
            next_url = url_for('main.mod_approved', page=posts.next_num) \
                if posts.has_next else None
            prev_url = url_for('main.mod_approved', page=posts.prev_num) \
                if posts.has_prev else None
            return render_template('moderate.html',
                                   title='Approved Slides',
                                   users=posts.items,
                                   name=current_user.name,
                                   filter=['Approved'],
                                   mod_count=mod_counter(),
                                   next_url=next_url,
                                   prev_url=prev_url)
    return redirect(url_for('auth.login'))


@main.route('/mod/waiting')
@login_required
def mod_waiting():
    if current_user.is_authenticated:
        # nested to prevent errors when users not logged in
        if current_user.is_admin:
            if request.method == 'POST':
                if 'Approve' in request.form:
                    appr_slide('Approved', int(request.form['slide_id']))
                elif 'Deny' in request.form:
                    appr_slide('Denied', int(request.form['slide_id']))
                elif 'Delete' in request.form:
                    remove_slide(request.form['slide_id'])
            page = request.args.get('page', 1, type=int)
            posts = Slide.query.filter_by(approval='Waiting Review').order_by(desc(Slide.id)).paginate(page, app.config['POSTS_PER_PAGE'], False)
            next_url = url_for('main.mod_waiting', page=posts.next_num) \
                if posts.has_next else None
            prev_url = url_for('main.mod_waiting', page=posts.prev_num) \
                if posts.has_prev else None
            return render_template('moderate.html',
                                   title='Waiting Slides',
                                   users=posts.items,
                                   name=current_user.name,
                                   filter=['Waiting Review'],
                                   mod_count=mod_counter(),
                                   next_url=next_url,
                                   prev_url=prev_url)
    return redirect(url_for('auth.login'))


@main.route('/edit/<id>', methods=['GET'])
@login_required
def edit(id):
    return render_template('edit.html',
                           title='Edit Slide',
                           slide_id=id,
                           slide=Slide.query.get(id),
                           name=current_user.name,
                           mod_count=mod_counter(),
                           feeds=ast.literal_eval(get_settings().feeds))


@main.route('/edit/<id>', methods=['POST'])
@login_required
def edit_post(id):
    update_slide(id,
                 request.form["title_text"],
                 request.form["time_start"],
                 request.form["time_end"],
                 str(request.form.getlist('feeds')))
    return render_template('edit.html',
                           title='Edit Slide',
                           slide_id=id,
                           slide=Slide.query.get(id),
                           name=current_user.name,
                           mod_count=mod_counter(),
                           feeds=ast.literal_eval(get_settings().feeds))


@main.route('/messages', methods=['GET'])
@login_required
def messages():
    if current_user.is_authenticated:
        # nested to prevent errors when users not logged in
        if current_user.is_admin:
            return render_template('messages.html',
                                   title='Messages',
                                   name=current_user.name,
                                   mod_count=mod_counter(),
                                   messages=Message.query.all())
    return redirect(url_for('auth.login'))


@main.route('/messages', methods=['POST'])
@login_required
def messages_post():
    if current_user.is_authenticated:
        # nested to prevent errors when users not logged in
        if current_user.is_admin:
            if request.method == 'POST':
                text = request.form["message_text"]
                start_time = request.form["time_start"]
                end_time = request.form["time_end"]
                add_message(text, start_time, end_time)
            return render_template('messages.html',
                                   title='Messages',
                                   name=current_user.name,
                                   mod_count=mod_counter(),
                                   messages=Message.query.all())
    return redirect(url_for('auth.login'))


@main.route('/alerts', methods=['GET'])
@login_required
def alerts():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return render_template('alerts.html',
                                   title='Submit an Emergency Alert',
                                   name=current_user.name,
                                   mod_count=mod_counter())
    return redirect(url_for('auth.login'))


@main.route('/alerts', methods=['POST'])
@login_required
def alerts_post():
    if current_user.is_authenticated:
        # nested to prevent errors when users not logged in
        if current_user.is_admin:
            if request.method == 'POST':
                status = request.form["alert_status"]
                if status == "Enable":
                    update_alert(request.form["alert_text"])
                elif status == "Disable":
                    update_alert("")
            return render_template('alerts.html',
                                   title='Submit an Emergency Alert',
                                   name=current_user.name,
                                   mod_count=mod_counter())
    return redirect(url_for('auth.login'))


@main.route('/settings', methods=['GET'])
@login_required
def settings():
    if current_user.is_authenticated:
        # nested to prevent errors when users not logged in
        if current_user.is_admin:
            return render_template('settings.html',
                                   title='System Settings',
                                   name=current_user.name,
                                   mod_count=mod_counter(),
                                   settings=get_settings())
    return redirect(url_for('auth.login'))


@main.route('/settings', methods=['POST'])
@login_required
def settings_post():
    if current_user.is_authenticated:
        # nested to prevent errors when users not logged in
        if current_user.is_admin:
            if request.method == 'POST':
                duration_time = request.form["duration"]
                allow_signups = request.form["allow_signups"]
                feed_list = request.form["feeds"]
                update_settings(duration_time, allow_signups, feed_list)
            return render_template('settings.html',
                                   title='System Settings',
                                   name=current_user.name,
                                   mod_count=mod_counter(),
                                   settings=get_settings())
    return redirect(url_for('auth.login'))


@main.route('/feeds/<title>', methods=['GET'])
def feeds(title):
    """Feed route

    Args:
        template (string): The template name to use for the feed.
        title (string): title for the page. This is not displayed but should be declared.
        slides (list): slides to display.
        alert_status (string): if not none then overrides slide content to show the string.
        interval (integer): rate in milliseconds to rotate slides.
        messages (string): messages for the ticker display.
        background (string): name of background image for the sidebar located in the static folder.

    Returns:
    template: the feed template with supplied content
    """

    return render_template('feed.html',
                           title=title,
                           slides=get_slides(title),
                           alert_status=alert_status(),
                           interval=get_settings().duration,
                           messages=json.dumps(get_message()),
                           background=title + '.webp',
                           weather_key=app.config['WEATHER_KEY'])


@main.route('/feeds-vertical/<title>', methods=['GET'])
def feeds_vertical(title):
    """Feed route

        Args:
            template (string): The template name to use for the feed.
            title (string): title for the page. This is not displayed but should be declared.
            slides (list): slides to display.
            alert_status (string): if not none then overrides slide content to show the string.
            interval (integer): rate in milliseconds to rotate slides.
            messages (string): messages for the ticker display.
            background (string): name of background image for the sidebar located in the static folder.

        Returns:
        template: the feed template with supplied content
        """
    return render_template('feed_vertical.html',
                           title=title,
                           slides=get_slides(title),
                           alert_status=alert_status(),
                           interval=get_settings().duration,
                           messages=json.dumps(get_message()),
                           background='bg.jpg',
                           weather_key=app.config['WEATHER_KEY'])


@main.route('/clients')
def clients():
    """
    Route for client page
    """
    return render_template('clients.html',
                           title='Clients',
                           mod_count=mod_counter(),
                           clients=session.get('active_clients'))

@main.route('/feeds_video/<title>', methods=['GET'])
def feeds_video(title):
    """Feed route

    Args:
        template (string): The template name to use for the feed.
        title (string): title for the page. This is not displayed but should be declared.
        slides (list): slides to display.
        alert_status (string): if not none then overrides slide content to show the string.
        interval (integer): rate in milliseconds to rotate slides.
        messages (string): messages for the ticker display.
        background (string): name of background image for the sidebar located in the static folder.

    Returns:
    template: the feed template with supplied content
    """
    return render_template('feed-video.html',
                           title=title,
                           video=get_video(title),
                           alert_status=alert_status(),
                           interval=get_settings().duration,
                           messages=json.dumps(get_message()),
                           background=title + '.webp',
                           weather_key=app.config['WEATHER_KEY'])

@main.route('/status')
def status():
    """
    Route for client page
    """
    return render_template('status.html', title='Operational Status', rooms=Room.query.all())
