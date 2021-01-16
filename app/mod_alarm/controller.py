from flask import Blueprint, session, render_template, request, make_response, jsonify
from flask import current_app as app
from datetime import datetime
# Import objects from the main app module
from app import auth_module, oidc, db
# Import module models (i.e. User)
from app.mod_alarm.models import *
from app.mod_lodur.models import AlarmGroup, Firefighter

# Define the blueprint: 'alarm', set its url prefix: app.url/lodur
mod_alarm = Blueprint('alarm', __name__, url_prefix='/alarm')

@mod_alarm.route("/alarmgruppe", methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_Report')
def get_alarmgruppe():

    return render_template("mod_alarm/alarmgruppe.html", user=auth_module.get_userobject(), groups=db.session.query(AlarmGroup).all())

@mod_alarm.route("/statusUpdate", methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_GVZStatus')
def get_gvzUpdate():

    return render_template("mod_alarm/gvzStatus.html", user=auth_module.get_userobject(), 
    firefighters=Firefighter.query.all(),
    settings=db.session.query(GVZupdate).order_by(GVZupdate.id.desc()).first(),
    entries=db.session.query(GVZnotAvailable).all())

@mod_alarm.route("/statusUpdate",methods=['POST'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_GVZStatus')
def post_gvzUpdate():
    try:
        if request.form.get('bolFwBereit') == 'true':
            bolFwBereit = 1
        else:
            bolFwBereit = 0
        
        if request.form.get('bolMatBereit') == 'true':
            bolMatBereit = 1
        else:
            bolMatBereit = 0

        if request.form.get('bolRdFahrer') == 'true':
            bolRdFahrer = 1
        else:
            bolRdFahrer = 0
        
        db.session.add(GVZupdate(bolFwBereit,request.form.get('anzahlGrossfahrer'),bolMatBereit,0,bolRdFahrer))

        db.session.commit()
        return make_response(jsonify(message='OK'),200)
    except Exception as e:
        print(str(e))
        return make_response(jsonify(message=str(e)),500)

@mod_alarm.route("/statusUpdate/entry",methods=['POST'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_GVZStatus')
def post_statusUpdateEntry():
    try:
        
        isDriver = Firefighter.query.filter(Firefighter.id.is_(request.form.get('firefighters')))\
            .join(Firefighter.alarmgroups, aliased=True)\
            .filter_by(name='Grossfahrzeuge').scalar() is not None #Check if Firefighter is Driver
        isKader = Firefighter.query.filter(db.and_(Firefighter.id.is_(request.form.get('firefighters')),\
            Firefighter.grad_sort<6)).scalar() is not None
            
        
        if isDriver == True:
            isDriver = 1
        else:
            isDriver = 0
        
        if isKader == True:
            isKader = 1
        else:
            isKader = 0

        if request.form.get('entry_id') == "":
            db.session.add(GVZnotAvailable(
                request.form.get('firefighters'),
                datetime.strptime(request.form.get('datumvon'),'%d.%m.%Y'),
                datetime.strptime(request.form.get('datumbis'),'%d.%m.%Y'),
                request.form.get('art'),
                isDriver,
                isKader,
                auth_module.get_userobject()[0].username #reportedby
            ))
        else:
            entry = GVZnotAvailable.query.get(request.form.get('entry_id'))
            entry.id = request.form.get('entry_id')
            entry.datumvon = datetime.strptime(request.form.get('datumvon'),'%d.%m.%Y')
            entry.datumbis = datetime.strptime(request.form.get('datumbis'),'%d.%m.%Y')
            entry.member_id = request.form.get('firefighters')
            entry.art = request.form.get('art')
            entry.isDriver = isDriver
            entry.isKader = isKader
            #entry.reportedby = str(auth_module.get_userobject()[0].username)

        db.session.commit()
        return make_response(jsonify(message='OK'),200)
    #except exc.IntegrityError:
    #    return make_response(jsonify(message="Doppelter Eintrag in der Datenbank gefunden."),500)
    except Exception as e:
        return make_response(jsonify(message=str(e)),500)

@mod_alarm.route("/statusUpdate/entry/<id>",methods=['DELETE'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_GVZStatus')
def delete_statusUpdateEntry(id):
    try:
        GVZnotAvailable.query.filter_by(id=id).delete()
        db.session.commit()

        return make_response(jsonify(message='OK'),200)
    except Exception as e:
        return make_response(jsonify(message=str(e)),500)


@mod_alarm.route("/pushUser", methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_PushUser')
def get_pushuser():
    return render_template("mod_alarm/push_user.html", user=auth_module.get_userobject(), oneSignalKey=app.config['PUSH_APP_ID'])


@mod_alarm.route("/pushSettings", methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_PushSettings')
def get_pushsettings():
    return render_template("mod_alarm/push_settings.html", user=auth_module.get_userobject(),
                           entries=db.session.query(pushEntry).all(),
                           categories=db.session.query(pushCategory).all())


@mod_alarm.route("/push/entry", methods=['POST'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_PushSettings')
def post_pushentry():
    try:
        if request.form.get('entry_id') == "-1":
            db.session.add(pushEntry(
                request.form.get('selektor'),
                request.form.get('info'),
                request.form.get('category')
            ))
        else:
            entry = pushEntry.query.get(request.form.get('entry_id'))
            entry.selector = request.form.get('selektor')
            entry.message = request.form.get('info')
            entry.category_id = request.form.get('category')

        db.session.commit()
        return make_response(jsonify(message='OK'), 200)

    except Exception as e:
        return make_response(jsonify(message=str(e)), 500)


@mod_alarm.route("/push/entry/<id>", methods=['DELETE'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_PushSettings')
def delete_pushentry(id):
    try:
        pushEntry.query.filter_by(id=id).delete()
        db.session.commit()

        return make_response(jsonify(message='OK'), 200)
    except Exception as e:
        return make_response(jsonify(message=str(e)), 500)


@mod_alarm.route("/push/category", methods=['POST'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_PushSettings')
def post_pushcategory():
    try:
        if request.form.get('category_id') == "-1":
            db.session.add(pushCategory(
                request.form.get('name'),
                request.form.get('tag')
            ))
        else:
            entry = pushCategory.query.get(request.form.get('category_id'))
            entry.name = request.form.get('name')
            entry.tag = request.form.get('tag')

        db.session.commit()
        return make_response(jsonify(message='OK'), 200)

    except Exception as e:
        return make_response(jsonify(message=str(e)), 500)


@mod_alarm.route("/push/category/<id>", methods=['DELETE'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_PushSettings')
def delete_pushcategory(id):
    try:
        pushCategory.query.filter_by(id=id).delete()
        db.session.commit()

        return make_response(jsonify(message='OK'), 200)
    except Exception as e:
        return make_response(jsonify(message=str(e)), 500)
