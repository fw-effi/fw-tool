from flask import Blueprint, session, request, redirect, render_template, make_response, jsonify
from flask import current_app as app
import sys, os, re
# Import objects from the main app module
from app import db, oidc, auth_module
# Import module models (i.e. User)
from app.mod_auth.models import auth_groups, auth_roles

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_core = Blueprint('core', __name__, url_prefix='/core')

@mod_core.route("/settings", methods=['GET'])
@oidc.require_login
def get_settings():
    return render_template("mod_core/settings.html", user=auth_module.get_userobject(), 
        groups=db.session.query(auth_groups).filter_by(is_deleted=False).all(),
        roles=db.session.query(auth_roles).filter_by(is_deleted=False).all())

@mod_core.route("/settings/permission",methods=['POST'])
@oidc.require_login
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