from flask import Blueprint, session, request, redirect, render_template, make_response, jsonify
from flask import current_app as app
import sys, os, re
import datetime
import json
# Import objects from the main app module
from app import db, oidc, auth_module
# Import module models (i.e. User)
from app.mod_auth.models import auth_groups, auth_roles, User
from app.mod_core.models import *

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_core = Blueprint('core', __name__, url_prefix='/core')

class notifications:
    # Create needed DB entries for a new Notification
    def create(sender_type, title, message,url):
        
        # Loop through all members in sender_type
        category = notifications_category.query.filter_by(name=sender_type).first()
        payload = {
            "title" : title,
            "message" : message
        }
        for receiver in category.recipients:
            message = notifications_messages(
                receiver.id,
                datetime.datetime.now(),
                json.dumps(payload),
                url
            )
            db.session.add(message)
        db.session.commit()
        
        return True
    
    # Return last 10 Messages
    @mod_core.route("/notifications/<count>", methods=['GET'])
    @oidc.require_login
    def get_Messages(count):
        notifications = notifications_messages.query.filter_by(user_id=auth_module.get_userobject()[0].id).order_by(db.desc(notifications_messages.date_created)).limit(count).all()
        
        json_array = []
        for message in notifications:
            json_array.append(message.to_dict())
        return json.dumps(json_array)

    @mod_core.route("/notifications/count", methods=['GET'])
    @oidc.require_login
    def get_newMessagesCount():

        notifications = 0
        if auth_module.get_userobject()[0].notification_lastread is None:
            notifications = notifications_messages.query.filter_by(user_id=auth_module.get_userobject()[0].id).count()
        else:
            notifications = notifications_messages.query.filter_by(user_id=auth_module.get_userobject()[0].id).\
                filter(notifications_messages.date_created >= auth_module.get_userobject()[0].notification_lastread).count()
        
        return jsonify([{'message_count': notifications}])

    @mod_core.route("/notifications/lastread",methods=['POST'])
    @oidc.require_login
    def get_lastread():
        # Add current time as lastread time in the user Profile
        current_user = User.query.filter_by(id=auth_module.get_userobject()[0].id).first()
        current_user.notification_lastread = datetime.datetime.now()
        db.session.commit()

        return "OK"
    
@mod_core.route("/settings", methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('Core_Setting')
def get_settings():
    return render_template("mod_core/settings.html", user=auth_module.get_userobject(), 
        permissions=db.session.query(auth_groups).filter_by(is_deleted=False).all(),
        permissions_roles=db.session.query(auth_roles).filter_by(is_deleted=False).all(),
        notifications=db.session.query(notifications_category).filter_by(is_deleted=False).all(),
        notifications_users=db.session.query(User).all())

@mod_core.route("/settings/permission",methods=['POST'])
@oidc.require_login
@auth_module.check_role_permission('Core_Setting')
def post_permission():
    try:
        req = request.form.to_dict(flat=False)
        print(req)
        for key in req:
            group = re.search('''(?<=')\s*[^']+?\s*(?=')''', key).group() #Extract Group Name from "roles['<groupName>']"
            
            auth_group = db.session.query(auth_groups).filter_by(name=group).first() # Find auth_group DB Entry with that name
            auth_group.roles.clear()

            for value in req[key]:
                auth_group.roles.append(auth_roles.query.filter_by(id=value).first())
            
        db.session.commit()
        return make_response(jsonify(message='OK'),200)
    except Exception as e:
        return make_response(jsonify(message=str(e)),500)

@mod_core.route("/notifications",methods=['GET'])
@oidc.require_login
def get_notifications():
    current_user = auth_module.get_userobject()

    notifications = Notifications_messages.query.filter(
        Notifications_messages.timestamp > current_user.notification_lastread).order_by(Notifications_messages.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp,
        'url': n.url
    } for n in notifications])

@mod_core.route("/settings/notifications",methods=['POST'])
@oidc.require_login
@auth_module.check_role_permission('Core_Setting')
def post_notifications():
    try:
        req = request.form.to_dict(flat=False)
        print(req)
        for key in req:
            category = re.search('''(?<=')\s*[^']+?\s*(?=')''', key).group() #Extract Category Name from "roles['<categoryName>']"
            
            notification_category = db.session.query(notifications_category).filter_by(name=category).first() # Find Notification Category DB Entry with that name
            notification_category.recipients.clear()
            
            for value in req[key]:
                notification_category.recipients.append(User.query.filter_by(id=value).first())
            
        db.session.commit()
        return make_response(jsonify(message='OK'),200)
    except Exception as e:
        return make_response(jsonify(message=str(e)),500)