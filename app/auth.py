from .app import db
from flask import Blueprint, render_template, redirect, url_for, request, session
from .models import User
import msal
import requests
import instance.config as app_config

# initialize auth routes
auth = Blueprint('auth', __name__)

@auth.route("/signup", methods=['GET'])
def signup():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first():
        return redirect(url_for("app.index"))
    elif request.method == 'POST':
        data = User(
            email = session.get("user")["preferred_username"],
            name = session.get("user")["name"],
            type = "Viewer",
            eid = int(request.form['eid']))
        db.session.add(data)
        db.session.commit()
        return redirect(url_for("app.index"))
    else:
        name = session.get("user")["name"]
        return render_template('auth_signup.html', user=name, version=msal.__version__, title='Sign Up')


@auth.route("/signup", methods=['POST'])
def signup_post():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    elif User.query.filter_by(email=session.get("user")["preferred_username"]).first():
        return redirect(url_for("app.index"))
    data = User(
        email = session.get("user")["preferred_username"],
        name = session.get("user")["name"],
        type = "Viewer",
        eid = int(request.form['eid']))
    db.session.add(data)
    db.session.commit()
    return redirect(url_for("app.index"))


@auth.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    return render_template("auth_login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)


@auth.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("app.index"))


@auth.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("app.index", _external=True))


@auth.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("auth.login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return render_template('display.html', result=graph_data)


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)


def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("auth.authorized", _external=True))


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result
