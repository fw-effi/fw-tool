import os
import json
import sys
import pdfkit
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_oidc import OpenIDConnect
from celery import Celery

app = Flask(__name__)

# Configurations
app.config.from_object('config')

#app.debug = True
#toolbar = DebugToolbarExtension(app)

# Define the database object which is imported by modules and controllers
# And build the database, this will create the database file using SQLAlchemy
db = SQLAlchemy(app)
db_migrate = Migrate(app,db)

# Register OpenID Library
oidc = OpenIDConnect(app)

# Import a module / component using its blueprint handler variable (mod_auth)
from .mod_auth import controller as auth_module
from .mod_lodur import controller as lodur_module
from .mod_pdf import controller as pdf_module
from .mod_atemschutz import controller as atemschutz_module

# Generate all DB Models
db.create_all()

# Register blueprint(s)
app.register_blueprint(auth_module.mod_auth)
app.register_blueprint(lodur_module.mod_lodur)
app.register_blueprint(pdf_module.mod_pdf)
app.register_blueprint(atemschutz_module.mod_atemschutz)

# Sample HTTP error handling
#@app.errorhandler(404)
#def not_found(error):
#    return render_template('404.html'), 404


@app.route("/")
def home():
	print("Login Status: %s",oidc.user_loggedin)
	if oidc.user_loggedin:
		return render_template("index.html", user=auth_module.get_userobject())
	else:
		return oidc.redirect_to_auth_server(None, request.values)

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