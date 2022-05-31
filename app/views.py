import json
import os
from flask import render_template, request, Blueprint, flash, Flask, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename, redirect
from .utils import mod_counter, alert_status, add_message, add_slide, allowed_file, appr_slide, remove_slide, update_alert, get_slides, get_message, update_settings, get_settings, update_slide
from .models import Message, Slide

# initialize view routes
main = Blueprint('main', __name__)
app = Flask(__name__, instance_relative_config=True)
# load app configuration from /instance/config.py
app.config.from_pyfile('config.py')


@main.route('/')
def index():
    return render_template('home.html', title='Dashboard', mod_count=mod_counter())


@main.route('/manager')
@login_required
def manager():
    page = request.args.get('page', 1, type=int)
    posts = Slide.query.paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.manager', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.manager', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('manager.html',
                           title='All Slides',
                           users=reversed(posts.items),
                           name=current_user.name,
                           filter=['Approved', 'Waiting Review', 'Denied'],
                           mod_count=mod_counter(),
                           next_url=next_url,
                           prev_url=prev_url)


@main.route('/manager/approved')
@login_required
def manager_approved():
    page = request.args.get('page', 1, type=int)
    posts = Slide.query.filter_by(approval='Approved').paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.manager_approved', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.manager_approved', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('manager.html',
                           title='Approved Slides',
                           users=reversed(posts.items),
                           name=current_user.name,
                           filter=['Approved'],
                           mod_count=mod_counter(),
                           next_url=next_url,
                           prev_url=prev_url)


@main.route('/manager/waiting')
@login_required
def manager_waiting():
    page = request.args.get('page', 1, type=int)
    posts = Slide.query.filter_by(approval='Waiting Review').paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.manager_waiting', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.manager_waiting', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('manager.html',
                           title='Waiting Slides',
                           users=reversed(posts.items),
                           name=current_user.name,
                           filter=['Waiting Review'],
                           mod_count=mod_counter(),
                           next_url=next_url,
                           prev_url=prev_url)


@main.route('/manager/denied')
@login_required
def manager_denied():
    page = request.args.get('page', 1, type=int)
    posts = Slide.query.filter_by(approval='Denied').paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.manager_denied', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.manager_denied', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('manager.html',
                           title='Denied Slides',
                           users=reversed(posts.items),
                           name=current_user.name,
                           filter=['Denied'],
                           mod_count=mod_counter(),
                           next_url=next_url,
                           prev_url=prev_url)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, mod_count=mod_counter())


@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, app.config["ALLOWED_EXTENSIONS"]):
            file.save(os.path.join(app.static_folder, 'uploads', secure_filename(file.filename)))
            time_start = request.form["time_start"]
            time_end = request.form["time_end"]
            title = request.form["title"]
            slide_path = secure_filename(file.filename)
            feeds = request.form.getlist('feeds')
            add_slide(time_start, time_end, title, slide_path, feeds)
            return redirect(request.url)
    return render_template('upload.html', title='Upload a Slide', name=current_user.name, mod_count=mod_counter())


@main.route('/mod', methods=['GET', 'POST'])
@login_required
def moderate():
    if current_user.is_authenticated:
        if current_user.is_admin:
            if request.method == 'POST':
                if 'Approve' in request.form:
                    appr_slide('Approved', request.form['slide_id'])
                elif 'Deny' in request.form:
                    appr_slide('Denied', request.form['slide_id'])
                elif 'Delete' in request.form:
                    remove_slide(request.form['slide_id'])
            page = request.args.get('page', 1, type=int)
            posts = Slide.query.paginate(page, app.config['POSTS_PER_PAGE'], False)
            next_url = url_for('main.moderate', page=posts.next_num) \
                if posts.has_next else None
            prev_url = url_for('main.moderate', page=posts.prev_num) \
                if posts.has_prev else None
            return render_template('moderate.html',
                                   title='Slide Moderator',
                                   name=current_user.name,
                                   users=reversed(posts.items),
                                   filter=['Approved', 'Waiting Review', 'Denied'],
                                   mod_count=mod_counter(),
                                   next_url=next_url,
                                   prev_url=prev_url)
    return redirect(url_for('auth.login'))


@main.route('/mod/denied')
@login_required
def mod_denied():
    if current_user.is_authenticated:
        if current_user.is_admin:
            if request.method == 'POST':
                if 'Approve' in request.form:
                    appr_slide('Approved', request.form['slide_id'])
                elif 'Deny' in request.form:
                    appr_slide('Denied', request.form['slide_id'])
                elif 'Delete' in request.form:
                    remove_slide(request.form['slide_id'])
            page = request.args.get('page', 1, type=int)
            posts = Slide.query.filter_by(approval='Denied').paginate(page, app.config['POSTS_PER_PAGE'], False)
            next_url = url_for('main.mod_denied', page=posts.next_num) \
                if posts.has_next else None
            prev_url = url_for('main.mod_denied', page=posts.prev_num) \
                if posts.has_prev else None
            return render_template('moderate.html',
                                   title='Denied Slides',
                                   users=reversed(posts.items),
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
        if current_user.is_admin:
            if request.method == 'POST':
                if 'Approve' in request.form:
                    appr_slide('Approved', request.form['slide_id'])
                elif 'Deny' in request.form:
                    appr_slide('Denied', request.form['slide_id'])
                elif 'Delete' in request.form:
                    remove_slide(request.form['slide_id'])
            page = request.args.get('page', 1, type=int)
            posts = Slide.query.filter_by(approval='Approved').paginate(page, app.config['POSTS_PER_PAGE'], False)
            next_url = url_for('main.mod_approved', page=posts.next_num) \
                if posts.has_next else None
            prev_url = url_for('main.mod_approved', page=posts.prev_num) \
                if posts.has_prev else None
            return render_template('moderate.html',
                                   title='Approved Slides',
                                   users=reversed(posts.items),
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
        if current_user.is_admin:
            if request.method == 'POST':
                if 'Approve' in request.form:
                    appr_slide('Approved', request.form['slide_id'])
                elif 'Deny' in request.form:
                    appr_slide('Denied', request.form['slide_id'])
                elif 'Delete' in request.form:
                    remove_slide(request.form['slide_id'])
            page = request.args.get('page', 1, type=int)
            posts = Slide.query.filter_by(approval='Waiting Review').paginate(page, app.config['POSTS_PER_PAGE'], False)
            next_url = url_for('main.mod_waiting', page=posts.next_num) \
                if posts.has_next else None
            prev_url = url_for('main.mod_waiting', page=posts.prev_num) \
                if posts.has_prev else None
            return render_template('moderate.html',
                                   title='Waiting Slides',
                                   users=reversed(posts.items),
                                   name=current_user.name,
                                   filter=['Waiting Review'],
                                   mod_count=mod_counter(),
                                   next_url=next_url,
                                   prev_url=prev_url)
    return redirect(url_for('auth.login'))


@main.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        update_slide(request.form["id_number"], request.form["title_text"])
    return render_template('edit.html', title='Edit Slide', slide_id='10', name=current_user.name, mod_count=mod_counter())


@main.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    if current_user.is_authenticated:
        if current_user.is_admin:
            if request.method == 'POST':
                text = request.form["message_text"]
                start_time = request.form["time_start"]
                end_time = request.form["time_end"]
                add_message(text, start_time, end_time)
            return render_template('messages.html', title='Messages', name=current_user.name, mod_count=mod_counter(), messages=Message.query.all())
    return redirect(url_for('auth.login'))


@main.route('/alerts', methods=['GET', 'POST'])
@login_required
def alerts():
    if current_user.is_authenticated:
        if current_user.is_admin:
            if request.method == 'POST':
                status = request.form["alert_status"]
                if status == "Enable":
                    update_alert(request.form["alert_text"])
                elif status == "Disable":
                    update_alert("")
            return render_template('alerts.html', title='Submit an Emergency Alert', name=current_user.name, mod_count=mod_counter())
    return redirect(url_for('auth.login'))


@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.is_authenticated:
        if current_user.is_admin:
            if request.method == 'POST':
                duration_time = request.form["duration"]
                allow_signups = request.form["allow_signups"]
                update_settings(duration_time, allow_signups)
            return render_template('settings.html', title='System Settings', name=current_user.name, mod_count=mod_counter())
    return redirect(url_for('auth.login'))

## feed routes for feeds 1-10
@main.route('/feed')
def feed():
    interval = get_settings()
    return render_template('feed.html', title='', slides=get_slides('feed00'), alert_status=alert_status(), interval=interval, messages=json.dumps(get_message()), background='bg.jpg')


@main.route('/feed01')
def feed01():
    interval = 7000
    return render_template('feed.html', title='Admissions', slides=get_slides('feed01'), alert_status=alert_status(), interval=interval, messages=json.dumps(get_message()), background='bg.jpg')


@main.route('/feed02')
def feed02():
    interval = get_settings()
    return render_template('feed.html', title='I.T. Services Service Desk', slides=get_slides('feed02'), alert_status=alert_status(), interval=interval, messages=json.dumps(get_message()), background='bg.jpg')


@main.route('/feed03')
def feed03():
    interval = get_settings()
    return render_template('feed.html', title='', slides=get_slides('feed03'), alert_status=alert_status(), interval=interval, messages=json.dumps(get_message()), background='bg.jpg')


@main.route('/feed04')
def feed04():
    interval = get_settings()
    return render_template('feed.html', title='', slides=get_slides('feed04'), alert_status=alert_status(), interval=interval, messages=json.dumps(get_message()), background='bg.jpg')


@main.route('/feed05')
def feed05():
    interval = get_settings()
    return render_template('feed.html', title='', slides=get_slides('feed05'), alert_status=alert_status(), interval=interval, messages=json.dumps(get_message()), background='bg.jpg')


@main.route('/feed06')
def feed06():
    interval = get_settings()
    return render_template('feed.html', title='Feed Six', slides=get_slides('feed06'), alert_status=alert_status(), interval=interval, messages=json.dumps(get_message()), background='bg.jpg')


@main.route('/feed07')
def feed07():
    interval = get_settings()
    return render_template('feed.html', title='', slides=get_slides('feed07'), alert_status=alert_status(), interval=interval, messages=json.dumps(get_message()), background='bg.jpg')


@main.route('/feed08')
def feed08():
    interval = get_settings()
    return render_template('feed.html', title='', slides=get_slides('feed08'), alert_status=alert_status(), interval=interval, messages=json.dumps(get_message()), background='bg.jpg')


@main.route('/feed09')
def feed09():
    interval = get_settings()
    return render_template('feed.html', title='', slides=get_slides('feed09'), alert_status=alert_status(), interval=interval, messages=json.dumps(get_message()), background='bg.jpg')


@main.route('/feed10')
def feed10():
    interval = get_settings()
    return render_template('feed.html', title='', slides=get_slides('feed10'), alert_status=alert_status(), interval=interval, messages=json.dumps(get_message()), background='bg.jpg')
