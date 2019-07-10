import os
import urllib.parse
import json
import sys
import pdfkit
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_oidc import OpenIDConnect
from flask_login import LoginManager, UserMixin, login_required
from helperLodur import *
from helperPDF import pdf_pages
from helperMail import *



app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported by modules and controllers
# And build the database, this will create the database file using SQLAlchemy
db = SQLAlchemy(app)
#db_session = scoped_session(sessionmaker(autocommit=False,autoflush=True,bind=db_engine))


# Define LoginManager and default Login View
lm = LoginManager(app)
lm.login_view = 'auth.do_login'
lm.session_protection = "strong"

# Register OpenID Library
oidc = OpenIDConnect(app)

# Import a module / component using its blueprint handler variable (mod_auth)
from .mod_auth import controller as auth_module

# Generate all DB Models
db.create_all()

# Register blueprint(s)
app.register_blueprint(auth_module.mod_auth)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route("/")
def home():
	if oidc.user_loggedin:
		return render_template("/admin/pages/index.html", error="error")
	else:
		return oidc.redirect_to_auth_server(None, request.values)

@app.route("/page/reports/alarmgruppe", methods=['GET'])
def get_page_report_alarmgruppe():
	""" Load Page
	"""

	if not session.get("logged_in"):
	    #If not loggedin redirect it to the login page
	    return render_template("admin/pages/login.html")
	else:
	    return render_template("admin/pages/report_alarmgruppe.html", user=appSettings._user, adfs=lodur_get_appellliste(appSettings._session))

@app.route("/page/communication/sendMail", methods=['GET'])
def get_page_communicaton_sendMail():
	""" Load Page
	"""

	if not session.get("logged_in"):
	    #If not loggedin redirect it to the login page
	    return render_template("admin/pages/login.html")
	else:
	    return render_template("admin/pages/communication_sendMail.html", user=appSettings._user)

@app.route("/page/communication/sendMail", methods=['POST'])
def post_page_communicaton_sendMail():
	""" Load Page
	"""

	if not session.get("logged_in"):
	    #If not loggedin redirect it to the login page
	    return render_template("admin/pages/login.html")
	else:
            mailer = mail_post_sendOneSmtp(request,appSettings._user)
            return render_template("admin/pages/communication_sendMail.html", user=appSettings._user, error=mailer)


@app.route("/page/settings/push", methods=['GET'])
def get_page_settings_push():
	""" Load Page
	"""

	if not session.get("logged_in"):
	    #If not loggedin redirect it to the login page
	    return render_template("admin/pages/login.html")
	else:
	    return render_template("admin/pages/settings_push.html", user=appSettings._user)