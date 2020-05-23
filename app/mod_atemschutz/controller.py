from flask import Blueprint, session, render_template, request, make_response, jsonify
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import exc, func
# Import module models (i.e. User)
from app.mod_atemschutz.models import *
from app.mod_lodur.models import Firefighter, FF_Zug
# Import objects from the main app module
from app import auth_module, oidc, db
import collections
import requests
import json

# Define the blueprint: 'atemschutz', set its url prefix: app.url/atemschutz
mod_atemschutz = Blueprint('atemschutz', __name__, url_prefix='/atemschutz')

@mod_atemschutz.route("/",methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('AS_Index')
def uebersicht():
    result = db.engine.execute("SELECT Firefighter.grad AS Firefighter_grad,"
        "Firefighter.vorname AS vorname,"
        "Firefighter.name AS name,"
        "FF_Zug.name AS zug,"
        "(SELECT sum(AS_Entry.time) AS sum_1 FROM AS_Entry "
        "WHERE AS_Entry.member_id = Firefighter.id AND AS_Entry.datum > date('now','start of year')) AS time "
        "FROM Firefighter, FF_Zugmapping AS FF_Zugmapping_1, FF_Zug, alarmgroups "
        "WHERE FF_Zugmapping_1.ff_zug_id == FF_Zug.id AND FF_Zugmapping_1.firefighter_id == Firefighter.id "
        "AND alarmgroups.firefighter_id = Firefighter.id AND "
        "alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'Atemschutz') "
        "AND Firefighter.is_deleted = 0 "
        "ORDER BY grad_sort")
    
    as_statistics = result.fetchall()
    result.close()
    return render_template("mod_atemschutz/index.html", user=auth_module.get_userobject(), 
        statistics=as_statistics,
        entries=Entry.query.all(), 
        categories=Category.query.all(), 
        firefighters=Firefighter.query.filter_by(is_deleted=False).all()
    )

@mod_atemschutz.route("/auswertung",methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('AS_Auswertung')
def auswertung():
    result = db.engine.execute("SELECT Firefighter.grad_sort as grad_sort, Firefighter.id as id,"
        "Firefighter.vorname AS vorname,"
        "Firefighter.name AS name,"
        "Firefighter.eintritt AS eintritt,"
        "IFNULL((SELECT SUM(Sub1.time) FROM AS_Entry AS Sub1 "
            "WHERE Sub1.datum BETWEEN strftime('%Y-01-01','now','-1 year') AND strftime('%Y-12-31','now','-1 year') "
            "AND Sub1.member_id = Firefighter.id),0) AS 'one_year', "
        "IFNULL((SELECT SUM(Sub1.time) FROM AS_Entry AS Sub1 LEFT JOIN AS_Category As Sub2 ON (Sub1.category_id = Sub2.id) "
            "WHERE Sub1.datum BETWEEN strftime('%Y-01-01','now','-1 year') AND strftime('%Y-12-31','now','-1 year') "
            "AND Sub2.training = 1 "
            "AND Sub1.member_id = Firefighter.id),0) AS 'one_year_training', "
        "IFNULL((SELECT SUM(Sub1.time) FROM AS_Entry AS Sub1  "
            "WHERE Sub1.datum BETWEEN strftime('%Y-01-01','now','-2 year') AND strftime('%Y-12-31','now','-2 year') "
            "AND Sub1.member_id = Firefighter.id),0) AS 'two_year', "
        "IFNULL((SELECT SUM(Sub1.time) FROM AS_Entry AS Sub1 LEFT JOIN AS_Category As Sub2 ON (Sub1.category_id = Sub2.id) "
            "WHERE Sub1.datum BETWEEN strftime('%Y-01-01','now','-2 year') AND strftime('%Y-12-31','now','-2 year') "
            "AND Sub2.training = 1 "
            "AND Sub1.member_id = Firefighter.id),0) AS 'two_year_training', "
        "IFNULL((SELECT SUM(Sub1.time) FROM AS_Entry AS Sub1 "
            "WHERE Sub1.datum BETWEEN strftime('%Y-01-01','now','-3 year') AND strftime('%Y-12-31','now','-3 year') "
            "AND Sub1.member_id = Firefighter.id),0) AS 'three_year', "
        "IFNULL((SELECT SUM(Sub1.time) FROM AS_Entry AS Sub1 LEFT JOIN AS_Category As Sub2 ON (Sub1.category_id = Sub2.id) "
            "WHERE Sub1.datum BETWEEN strftime('%Y-01-01','now','-3 year') AND strftime('%Y-12-31','now','-3 year') "
            "AND Sub2.training = 1 "
            "AND Sub1.member_id = Firefighter.id),0) AS 'three_year_training', "
        "IFNULL((SELECT SUM(Sub1.time) FROM AS_Entry AS Sub1 "
            "WHERE Sub1.datum BETWEEN strftime('%Y-01-01','now','-4 year') AND strftime('%Y-12-31','now','-4 year') "
            "AND Sub1.member_id = Firefighter.id),0) AS 'four_year', "
        "IFNULL((SELECT SUM(Sub1.time) FROM AS_Entry AS Sub1 LEFT JOIN AS_Category As Sub2 ON (Sub1.category_id = Sub2.id) "
            "WHERE Sub1.datum BETWEEN strftime('%Y-01-01','now','-4 year') AND strftime('%Y-12-31','now','-4 year') "
            "AND Sub2.training = 1 "
            "AND Sub1.member_id = Firefighter.id),0) AS 'four_year_training', "
        "strftime('%Y','now','-1 year') AS 'one_year_name', "
        "strftime('%Y','now','-2 year') AS 'two_year_name', "
        "strftime('%Y','now','-3 year') AS 'three_year_name', "
        "strftime('%Y','now','-4 year') AS 'four_year_name' "
        "FROM Firefighter, alarmgroups "
        "WHERE alarmgroups.firefighter_id = Firefighter.id "
        "AND alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'Atemschutz') "
        "AND Firefighter.is_deleted = 0 "
        "GROUP BY Firefighter.id ORDER BY Firefighter.grad_sort, Firefighter.name")
    year_statistics = result.fetchall()
    result.close()

    return render_template("mod_atemschutz/auswertung.html", user=auth_module.get_userobject(),
        statistics=year_statistics,
        entries=Entry.query.all(), 
        categories=Category.query.all(), 
        firefighters=Firefighter.query.all()
    )

@mod_atemschutz.route("/settings",methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('AS_Setting')
def settings():
    return render_template("mod_atemschutz/settings.html", user=auth_module.get_userobject(), categories=db.session.query(Category).all())

@mod_atemschutz.route("/category",methods=['POST'])
@oidc.require_login
@auth_module.check_role_permission('AS_Setting')
def category_NewEdit():
    try:
        if request.form.get('category_training') == 'true':
            training = 1
        else:
            training = 0
        
        if request.form.get('category_id') == "":
            db.session.add(Category(request.form.get('category_name'), training))
        else:
            category = Category.query.get(request.form.get('category_id'))
            category.name = request.form.get('category_name')
            category.training = training

        db.session.commit()
        return make_response(jsonify(message='OK'),200)
    except exc.IntegrityError:
        return make_response(jsonify(message="Doppelter Eintrag in der Datenbank gefunden."),500)
    except Exception as e:
        return make_response(jsonify(message=str(e)),500)
    
@mod_atemschutz.route("/category/<id>",methods=['DELETE'])
@oidc.require_login
@auth_module.check_role_permission('AS_Setting')
def category_Delete(id):
    try:
        Category.query.filter_by(id=id).delete()
        db.session.commit()

        return make_response(jsonify(message='OK'),200)
    except Exception as e:
        return make_response(jsonify(message=str(e)),500)

@mod_atemschutz.route("/entry",methods=['POST'])
@oidc.require_login
@auth_module.check_role_permission('AS_Index')
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
@auth_module.check_role_permission('AS_Index')
def centry_Delete(id):
    try:
        Entry.query.filter_by(id=id).delete()
        db.session.commit()

        return make_response(jsonify(message='OK'),200)
    except Exception as e:
        return make_response(jsonify(message=str(e)),500)
