import json
from flask import Blueprint, render_template, session, request, redirect, g, flash
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

def get_userobject():
    if session.get('user_id') is not None:
        return User.query.filter_by(open_id=session['user_id']).first()
    else:
        logout()

@mod_auth.route('/callback/lodur')
@oidc.custom_callback
def callback(data):
    session_state = request.args.get("state")

    access_token = oidc.get_access_token()
    user_id = oidc.user_getfield('sub',access_token)
    session['user_id'] = user_id

    user = User.query.filter_by(open_id=session['user_id']).first()
    if user is not None:
        g.user = user
        flash("Welcome back. You logged in %s" % user.username,"success")
    else:
        username = oidc.user_getfield('user_name',access_token)
        email = oidc.user_getfield('email',access_token)

        if user_id in oidc.credentials_store:
            db.session.add(User(username,email, user_id))
            db.session.commit()
            user = User.query.filter_by(open_id=user_id).first()
            g.user = user
        else:
            return "ERROR: User can't find in Credentials Store."
    
    return redirect('/')

@mod_auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('access_token', None)
    oidc.logout()
    return 'Hi, you have been logged out! <a href="/">Return</a>'