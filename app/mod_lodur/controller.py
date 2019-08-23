from flask import Blueprint, session, render_template
from flask import current_app as app
from .lodur import *
# Import objects from the main app module
from app import auth_module, oidc

# Define the blueprint: 'lodur', set its url prefix: app.url/lodur
mod_lodur = Blueprint('lodur', __name__, url_prefix='/lodur')

@mod_lodur.before_request
def before_request():
    lodur_init()

@mod_lodur.route("/reports/alarmgruppe", methods=['GET'])
@oidc.require_login
def report_alarmgruppe():
    return render_template("pages/report_alarmgruppe.html", user=auth_module.get_userobject(), adfs=get_appellliste())

def export_appellliste():
    return get_appellliste()