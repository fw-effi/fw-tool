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

    if gruppe == 'bag':
        content = {
            "bag1": lodur.getFirefightersPerAlarm('BAG1'),
            "bag2": lodur.getFirefightersPerAlarm('BAG2'),
            "bag3": lodur.getFirefightersPerAlarm('BAG3'),
            "konf": lodur.getFirefightersPerAlarm('Konf')
        }
    elif gruppe == 'spezZug':
        content = {
            "stab": lodur.getFirefightersPerAlarm('Stab'),
            "va": lodur.getFirefightersPerAlarm('VA'),
            "san": lodur.getFirefightersPerAlarm('San')
        }
    elif gruppe == 'spezGrp':
        content = {
            "stab": lodur.getFirefightersPerAlarm('Stab'),
            "fu": lodur.getFirefightersPerAlarm('Fu'),
            "srt": lodur.getFirefightersPerAlarm('SRT'),
            "adl": lodur.getFirefightersPerAlarm('ADL')
        }
    else:
        content = lodur.getFirefightersPerAlarm(gruppe)
    

    return render_alarmgruppe(content,gruppe)