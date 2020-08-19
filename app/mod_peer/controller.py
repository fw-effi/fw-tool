from flask import Blueprint, session, request, redirect, render_template, make_response, jsonify
from flask import current_app as app
import sys, os, re
# Import objects from the main app module
from app import db, oidc, auth_module
# Import module models (i.e. User)
from app.mod_auth.models import auth_groups, auth_roles

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_peer = Blueprint('peer', __name__, url_prefix='/peer')

@mod_peer.route("/konzept", methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('Peer_Konzept')
def get_konzept():
    return render_template("mod_peer/konzept.html", user=auth_module.get_userobject())

@mod_peer.route("/peers",methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('Peer_Peers')
def get_peers():
    return render_template("mod_peer/peers.html", user=auth_module.get_userobject())