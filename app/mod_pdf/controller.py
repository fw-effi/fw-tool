import pdfkit
import flask
from flask import Blueprint,Flask, render_template
# Import objects from the main app module
from app import auth_module, oidc
from ..mod_lodur import controller as lodur
from .appelliste import *

# Define the blueprint: 'pdf', set its url prefix: app.url/pdf
mod_pdf = Blueprint('mod_pdf',__name__, url_prefix='/pdf')

@mod_pdf.route("/appellliste/<gruppe>", methods=['GET'])
@oidc.require_login
def pdf_appellliste(gruppe):
    pdfcontent = lodur.export_appellliste()

    return render_alarmgruppe(pdfcontent,gruppe)