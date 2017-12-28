#!/usr/env/python

import os
import urllib.parse
import cookiejar
import json
import sys
import pdfkit
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_debugtoolbar import DebugToolbarExtension
from helper import *

app = Flask(__name__)
_session = requests.session()
_user = None

@app.route("/")
def home():
	"""Default Page
	Check the login state first - if not loggedin redirect it to the login page
	
	Keyword Arguments:
	none
	"""
	
	if not session.get("logged_in"):
		#If not loggedin redirect it to the login page
		return render_template("admin/pages/login.html")
	else:
		return render_template("admin/index.html", user=_user)

@app.route("/login", methods=['POST'])
def do_admin_login():
	""" User send Login information by POST
	forward it to the helper function (lodur_login) with the Username and Password from the webform

	Keyword Arguments:
	none
	"""
	global _session
	global _user
	
	_session = requests.session()
	login = lodur_login(request.form['username'],request.form['password'],_session)

	if login['result']:
		# If the result value from the response array are true, set the session state and go to the homepage
		session['logged_in'] = True
		# Save the session variable in the global variable
		_session = login['session']

		# Save User information in global variable
		_user = lodur_get_userdata(_session)
		
		return home()
	else:
		# Are the login failed, give back the following error message - used by the template
		error="Benutzername oder Passwort falsch!"

	return render_template("/admin/pages/login.html", error=error)

@app.route("/logout", methods=['GET'])
def do_admin_logout():
	""" User logout - change session Variable
	"""

	session['logged_in'] = False

	return render_template("/admin/pages/login.html", error="Logout erfolgreich!")


@app.route("/download/excel/alarm_group", methods=['GET'])
def do_excel_alarm_group():
	""" Get Excel List with Alarmgroups per Person
	"""

	if not session.get("logged_in"):
		#If not loggedin redirect it to the login page
		return render_template("admin/pages/login.html")
	else:
		return render_template("admin/pages/excel_alarm_person.html", user=_user)

@app.route("/test/pdf", methods=['GET'])
def get_excel_alarm_group():

	if not session.get("logged_in"):
		#If not loggedin redirect it to the login page
		return render_template("admin/pages/login.html")
	else:
            pdfcontent = lodur_get_appellliste(_session)
            page = render_template("pdf/appellliste.html",adfs = pdfcontent)
            #pdf = pdfkit.from_string(page, False)
            #res = Response(pdf)
            #res.headers['Content-Disposition'] = 'attachment; filename=test.pdf'
            #res.mimetype='application/pdf'
	
	return page

if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.debug = True
	toolbar = DebugToolbarExtension(app)
	app.run(debug=True,host='0.0.0.0',port=80)

