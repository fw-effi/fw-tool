from flask import Blueprint, session, render_template, request, make_response, jsonify
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import exc, func
# Import module models (i.e. User)
from app.mod_atemschutz.models import *
from app.mod_lodur.models import Firefighter
# Import objects from the main app module
from app import auth_module, oidc, db

# Define the blueprint: 'atemschutz', set its url prefix: app.url/atemschutz
mod_atemschutz = Blueprint('atemschutz', __name__, url_prefix='/atemschutz')


@mod_atemschutz.route("/",methods=['GET'])
@oidc.require_login
def own_overview():
    

    return render_template("mod_atemschutz/index.html", user=auth_module.get_userobject())

@mod_atemschutz.route("/kontrolle",methods=['GET'])
@oidc.require_login
def kontrolle():
    as_statistics = db.session.query(
        Firefighter.grad,
        Firefighter.vorname,
        Firefighter.name,
        func.sum(Entry.time).label('time')
    ).outerjoin(Entry).group_by(Firefighter.id).all()
    #print(db_result)
    return render_template("mod_atemschutz/kontrolle.html", user=auth_module.get_userobject(), 
        statistics=as_statistics,
        entries=Entry.query.all(), 
        categories=Category.query.all(), 
        firefighters=Firefighter.query.all()
    )

@mod_atemschutz.route("/settings",methods=['GET'])
@oidc.require_login
def settings():
    return render_template("mod_atemschutz/settings.html", user=auth_module.get_userobject(), categories=db.session.query(Category).all())

@mod_atemschutz.route("/category",methods=['POST'])
@oidc.require_login
def category_NewEdit():
    try:
        if request.form.get('category_id') == "":
            db.session.add(Category(request.form.get('category_name')))
        else:
            category = Category.query.get(request.form.get('category_id'))
            category.name = request.form.get('category_name')

        db.session.commit()
        return make_response(jsonify(message='OK'),200)
    except exc.IntegrityError:
        return make_response(jsonify(message="Doppelter Eintrag in der Datenbank gefunden."),500)
    except Exception as e:
        return make_response(jsonify(message=str(e)),500)
    
@mod_atemschutz.route("/category/<id>",methods=['DELETE'])
@oidc.require_login
def category_Delete(id):
    try:
        Category.query.filter_by(id=id).delete()
        db.session.commit()

        return make_response(jsonify(message='OK'),200)
    except Exception as e:
        return make_response(jsonify(message=str(e)),500)

@mod_atemschutz.route("/entry",methods=['POST'])
@oidc.require_login
def entry_NewEdit():
    try:
        if request.form.get('entry_id') == "":
            firefighters = request.form.getlist('firefighters[]')
            for firefighter in firefighters:
                db.session.add(Entry(
                    firefighter,
                    datetime.strptime(request.form.get('datum'),'%d.%m.%Y'),
                    request.form.get('category'),
                    request.form.get('dauer')
                ))
        else:
            entry = Entry.query.get(request.form.get('entry_id'))
            entry.id = request.form.get('entry_id')
            entry.datum = datetime.strptime(request.form.get('datum'),'%d.%m.%Y')
            entry.member_id = request.form.getlist('firefighters[]')[0]
            entry.category_id = request.form.get('category')
            entry.time = request.form.get('dauer')

        db.session.commit()
        return make_response(jsonify(message='OK'),200)
    #except exc.IntegrityError:
    #    return make_response(jsonify(message="Doppelter Eintrag in der Datenbank gefunden."),500)
    except Exception as e:
        return make_response(jsonify(message=str(e)),500)

@mod_atemschutz.route("/entry/<id>",methods=['DELETE'])
@oidc.require_login
def centry_Delete(id):
    try:
        Entry.query.filter_by(id=id).delete()
        db.session.commit()

        return make_response(jsonify(message='OK'),200)
    except Exception as e:
        return make_response(jsonify(message=str(e)),500)
