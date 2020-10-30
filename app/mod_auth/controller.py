from flask import Blueprint, session, request, redirect, flash, g, render_template
from flask import current_app as app
import sys, os
from functools import wraps
# Import objects from the main app module
from app import db, oidc
# Import module models (i.e. User)
from app.mod_auth.models import User,auth_roles,auth_groups
from app.mod_lodur.models import Firefighter,Lodur_General

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

def get_userobject():
    try:
        if session.get('user_id') is not None:
            user,firefighter = db.session.query(User, Firefighter).outerjoin(Firefighter, User.email == Firefighter.mail).filter(User.open_id==session['user_id']).first()
            general = db.session.query(Lodur_General).all()

            return user,firefighter, os.environ['FWAPP_ENV'],general
        else:
            logout()
    except:
        return {"name":"Lodur nicht synchronisiert"},{'name':'Lodur nicht synchronisiert'}

@mod_auth.route('/callback/lodur')
@oidc.custom_callback
def callback(data):
    
    session_state = request.args.get("state")
    print("oauth. Start Callback")
    try:
        access_token = oidc.get_access_token()
        #print("oauth callback. accesstoken ", access_token)
        #print("oauth callback. id_token: ",g.oidc_id_token)
        user_id = oidc.user_getfield('sub',access_token)
        session['user_id'] = user_id
        user_permission = oidc.user_getfield('role',access_token)
        #print("oauth callback. Roles: ", user_permission)
        # Manage die Lodur Gruppe in der DB
        lodurGroupsToDB(user_permission)
    
        user = User.query.filter_by(open_id=session['user_id']).first()
        if user is not None:
            # User existiert bereits, aktualisieren
            user.username = oidc.user_getfield('user_name',access_token)
            user.email = oidc.user_getfield('email',access_token)
        else:
            # User existiert noch nicht, neu anlegen
            user = User(
                oidc.user_getfield('user_name',access_token),
                oidc.user_getfield('email',access_token),
                user_id
            )
            if user_id in oidc.credentials_store:
                db.session.add(user)
                db.session.commit()
                
            else:
                return "ERROR: User can't find in Credentials Store."
        
        
    except:
        print("oauth. Error found" + sys.exc_info())
        return redirect('/')
    
    return redirect('/')

@mod_auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('access_token', None)
    oidc.logout()
    return redirect('/')

def lodurGroupsToDB(groups):
    if not isinstance(groups, (list, tuple)): # Prüfe ob der Paramter ein String oder eine Liste ist
        #Prüfe ob die Sicherheitsgruppe bereits existiert
        if db.session.query(auth_roles.id).filter_by(name=groups).scalar() is None:
            new_grp = auth_roles(
                groups
            )
            db.session.add(new_grp)
    else: # Wenn der Parameter eine Liste ist, verarbeite jeden Eintrag
        for group in groups:
            # Prüfe ob die Sicherheitsgruppe bereits in der DB existiert
            if db.session.query(auth_roles.id).filter_by(name=group).scalar() is None:
                # Wenn nicht, lege die Gruppe an
                new_grp = auth_roles(
                    group
                )
                db.session.add(new_grp)
    
    # Write changes to DB
    db.session.commit()

class check_role_permission:
    def __init__(self, role_required):
        self.role_required = role_required

    def __call__(self, func):
        def decorated_function(*args,**kwargs):
            #Lese gültige Rollen für die Berechtigungsgruppe
            
            auth_group = db.session.query(auth_groups).filter_by(name=self.role_required).first() # Find auth_group DB Entry with that name

            #Lese die verfügbaren Rollen vom Benutzer
            access_token = oidc.get_access_token()
            user_permission = oidc.user_getfield('role',access_token)
            # Check is access_token still valid and roles are able to export from access_token
            if user_permission is None:
                #If not, forward to authentication server
                return oidc.redirect_to_auth_server(None, request.values)
            
            #If user has role "admin", anything is allowed
            if 'admin' in user_permission:
                print("oauth role. User has Admin Permission")
                #Welcher return Befehl muss hier hin??!!!

            for role in auth_group.roles:
                if role.name in user_permission:
                    print("Oauth role. User has required Permission")
                    return func(*args,**kwargs)
                else:
                    print("Oauth role: User has no Role ")
            return render_template("mod_auth/403.html", user=get_userobject())
        
        #Rename function namen, otherwise got error "override existing endpoint function"
        decorated_function.__name__ = func.__name__
        return decorated_function