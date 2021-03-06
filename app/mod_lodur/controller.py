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
    fetch_kurse()
    return "OK"

@mod_lodur.route("/reports/alarmgruppe", methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_Report')
def report_alarmgruppe():

    return render_template("pages/report_alarmgruppe.html", user=auth_module.get_userobject(), groups=db.session.query(AlarmGroup).all())

def getFirefightersPerAlarm(gruppe):

    if gruppe == 'all':
        firefighters = Firefighter.query.order_by(Firefighter.grad_sort,Firefighter.name,Firefighter.vorname).all()
    else:
        firefighters = Firefighter.query.filter(Firefighter.alarmgroups.any(name=gruppe)).order_by(Firefighter.grad_sort,Firefighter.name,Firefighter.vorname)

    return firefighters