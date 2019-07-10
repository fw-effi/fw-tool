import json
from flask import Blueprint, render_template, session, request, redirect, g
from flask import current_app as app
from flask_login import login_user, logout_user, current_user, login_required
from .oAuth import *
import sys
# Import the database object from the main app module
from app import db, oidc
# Import module models (i.e. User)
from app.mod_auth.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

@mod_auth.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.filter_by(open_id=session['user_id']).first()

@mod_auth.route("/login", methods=['GET'])
def do_login():
    return 'Welcome %s' % oidc.user_getfield('email')


@mod_auth.route('/callback/lodur')
@oidc.custom_callback
def callback(data):
    if g.user is None:
        session['access_token'] = oidc.get_access_token()
        session['user_id'] = oidc.user_getfield('sub',session['access_token'])

        username = oidc.user_getfield('user',session['access_token'])
        email = oidc.user_getfield('email',session['access_token'])
        user_id = session['user_id']
        print('userinfo %s,%s,%s' % (username,email,user_id))
        
        if user_id in oidc.credentials_store:
            try:
                db.add(User(user_id,username,email))
                db.commit()
                user = User.query.filter_by(open_id=user_id).first()
                g.user = user
                return 'Hello. You logged in %s' % user.username
            except:
                return "Could not create User Object in DB"
    else:
        return 'Hello. Not logged in but You submitted %s' % data

@mod_auth.route('/logout')
@login_required
def logout():
    logout_user()
    logout_url = oxc.get_logout_uri()
    return redirect(logout_url)

@mod_auth.route('/logout_callback/')
def logout_callback():
    """Route called by the OpenID provider when user logs out.
    Clear the cookies here.
    """
    resp = make_response('Logging Out')
    resp.set_cookie('sub', 'null', expires=0)
    resp.set_cookie('session_id', 'null', expires=0)
    return resp


@mod_auth.route('/post_logout/')
def post_logout():
    return redirect(url_for('index'))