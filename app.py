import os
import urllib.parse
import cookiejar
import json
import sys
import pdfkit
import appSettings
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_debugtoolbar import DebugToolbarExtension
from helperLodur import *
from helperPDF import pdf_pages

app = Flask(__name__)

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
		return render_template("admin/index.html", user=appSettings._user)

@app.route("/login", methods=['POST'])
def do_admin_login():
	""" User send Login information by POST
	forward it to the helper function (lodur_login) with the Username and Password from the webform

	Keyword Arguments:
	none
	"""
	
	appSettings._session = requests.session()
	login = lodur_login(request.form['username'],request.form['password'],appSettings._session)

	if login['result']:
		# If the result value from the response array are true, set the session state and go to the homepage
		session['logged_in'] = True
		# Save the session variable in the global variable
		appSettings._session = login['session']

		# Save User information in global variable
		appSettings._user = lodur_get_userdata(appSettings._session)
		
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


@app.route("/page/reports/alarmgruppe", methods=['GET'])
def get_page_report_alarmgruppe():
	""" Get Excel List with Alarmgroups per Person
	"""

	if not session.get("logged_in"):
		#If not loggedin redirect it to the login page
		return render_template("admin/pages/login.html")
	else:
		return render_template("admin/pages/report_alarmgruppe.html", user=appSettings._user)




if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.register_blueprint(pdf_pages)
	app.debug = False
	toolbar = DebugToolbarExtension(app)
	app.run(host='0.0.0.0',port=80)

