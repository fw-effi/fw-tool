import pdfkit
from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort

@app.route("/pdf/alarmgruppe/<gruppe>", methods=['GET'])
def pdf_get_alarmgruppe(gruppe):

	if not session.get("logged_in"):
		#If not loggedin redirect it to the login page
		return render_template("admin/pages/login.html")
	else:
            pdfcontent = lodur_get_appellliste(_session)
	    
            page = {
		'ka1': render_template("pdf/liste-alarmgruppe.html",adfs = pdfcontent["ka1"],gruppe = "KA 1"),
		'ka2': render_template("pdf/liste-alarmgruppe.html",adfs = pdfcontent["ka2"],gruppe = "KA 2"),
		'ka3': render_template("pdf/liste-alarmgruppe.html",adfs = pdfcontent["ka3"],gruppe = "KA 3"),
		'ka4': render_template("pdf/liste-alarmgruppe.html",adfs = pdfcontent["ka3"],gruppe = "KA 4"),
		'ka5': render_template("pdf/liste-alarmgruppe.html",adfs = pdfcontent["ka3"],gruppe = "KA 5"),
		'ka6': render_template("pdf/liste-alarmgruppe.html",adfs = pdfcontent["ka3"],gruppe = "KA 6")
	    }[gruppe]

            pdf = pdfkit.from_string(page, False)
            res = Response(pdf)
            res.headers['Content-Disposition'] = 'attachment; filename=test.pdf'
            res.mimetype='application/pdf'
	
	return res