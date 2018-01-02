import pdfkit
import appSettings
import helperLodur
import requests
import flask
from flask import Blueprint,Flask, flash, redirect, render_template, request, session, abort

pdf_pages = Blueprint('pdf_pages',__name__)

@pdf_pages.route("/pdf/alarmgruppe/<gruppe>", methods=['GET'])
def pdf_get_alarmgruppe(gruppe):

            pdfcontent = helperLodur.lodur_get_appellliste(appSettings._session)
	    
            page = {
		'ka1': render_template("pdf/liste-alarmgruppe-ka.html",adfs = pdfcontent["ka1"],gruppe = "KA 1"),
		'ka2': render_template("pdf/liste-alarmgruppe-ka.html",adfs = pdfcontent["ka2"],gruppe = "KA 2"),
		'ka3': render_template("pdf/liste-alarmgruppe-ka.html",adfs = pdfcontent["ka3"],gruppe = "KA 3"),
		'ka4': render_template("pdf/liste-alarmgruppe-ka.html",adfs = pdfcontent["ka3"],gruppe = "KA 4"),
		'ka5': render_template("pdf/liste-alarmgruppe-ka.html",adfs = pdfcontent["ka3"],gruppe = "KA 5"),
		'ka6': render_template("pdf/liste-alarmgruppe-ka.html",adfs = pdfcontent["ka3"],gruppe = "KA 6"),
		'bag': render_template("pdf/liste-alarmgruppe-bag.html",adfs = pdfcontent["bag"],gruppe = "Bagatell"),
		'all': render_template("pdf/liste-alarmgruppe-bag.html",adfs = pdfcontent["all"],gruppe = "Alle")
	    }[gruppe]

            pdf = pdfkit.from_string(page, False)
            res = flask.Response(pdf)
            res.headers['Content-Disposition'] = 'attachment; filename=' + str(gruppe) + '.pdf'
            res.mimetype='application/pdf'
	
            return res
