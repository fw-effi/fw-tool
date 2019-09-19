from flask import Blueprint, session, render_template
from flask import current_app as app
from .lodur import *
# Import objects from the main app module
from app import auth_module, oidc
# Import module models (i.e. User)
import app.mod_lodur.models

# Define the blueprint: 'lodur', set its url prefix: app.url/lodur
mod_lodur = Blueprint('lodur', __name__, url_prefix='/lodur')


@mod_lodur.route("/updateData",methods=['POST'])
@oidc.require_login
def update_data():
    fetch_update_lodur()
    return "OK"

@mod_lodur.route("/reports/alarmgruppe", methods=['GET'])
@oidc.require_login
def report_alarmgruppe():

    return render_template("pages/report_alarmgruppe.html", user=auth_module.get_userobject(), groups=AlarmGroup.query.all())

def getFirefightersPerAlarm(gruppe):

    if gruppe == 'all':
        firefighters = Firefighter.query.all()
    else:
        firefighters = Firefighter.query.filter(Firefighter.alarmgroups.any(name=gruppe))

    return firefighters