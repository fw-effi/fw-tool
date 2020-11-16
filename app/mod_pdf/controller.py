import flask
import json
import requests
import collections
from flask import Blueprint,Flask, render_template, make_response
from flask import current_app as app
from sqlalchemy.sql import text
# Import objects from the main app module
from app import auth_module, oidc, db
# Import module models (i.e. User)
from ..mod_lodur import controller as lodur

# Define the blueprint: 'pdf', set its url prefix: app.url/pdf
mod_pdf = Blueprint('mod_pdf',__name__, url_prefix='/pdf')


@mod_pdf.route("/appellliste/<gruppe>", methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('Alarm_Report')
def pdf_appellliste(gruppe):

    if gruppe == 'BAG':
        result = db.engine.execute("SELECT Firefighter.id AS id,"
        "Firefighter.vorname AS vorname,"
        "Firefighter.name AS name,"
        "Firefighter.grad AS grad,"
        "Firefighter.grad_sort AS grad_sort, "
        "(SELECT Name FROM AlarmGroup WHERE AlarmGroup.id = alarmgroups.alarmgroup_id) AS gruppe "
        "FROM Firefighter, alarmgroups "
        "WHERE alarmgroups.firefighter_id = Firefighter.id "
        "AND (alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'BAG1') "
            "OR alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'BAG2') "
            "OR alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'BAG3') "
            "OR alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'Konf') ) "
        "AND Firefighter.is_deleted = 0 "
        "GROUP BY Firefighter.id ORDER BY Firefighter.grad_sort, Firefighter.name")

        req_jsondata = json.loads('{"template":{"shortid":"Bkeu4GNwBD"}}')
        
    elif gruppe == 'Spez-Zug':
        result = db.engine.execute("SELECT Firefighter.id AS id,"
        "Firefighter.vorname AS vorname,"
        "Firefighter.name AS name,"
        "Firefighter.grad AS grad,"
        "Firefighter.grad_sort AS grad_sort, "
        "(SELECT Name FROM AlarmGroup WHERE AlarmGroup.id = alarmgroups.alarmgroup_id) AS gruppe "
        "FROM Firefighter, alarmgroups "
        "WHERE alarmgroups.firefighter_id = Firefighter.id "
        "AND (alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'Stab') "
            "OR alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'VA') "
            "OR alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'San') ) "
        "AND Firefighter.is_deleted = 0 "
        "GROUP BY Firefighter.id ORDER BY Firefighter.grad_sort, Firefighter.name")

        req_jsondata = json.loads('{"template":{"shortid":"Bkeu4GNwBD"}}')

    elif gruppe == 'Spez-Gruppen':
        result = db.engine.execute("SELECT Firefighter.id AS id,"
        "Firefighter.vorname AS vorname,"
        "Firefighter.name AS name,"
        "Firefighter.grad AS grad,"
        "Firefighter.grad_sort AS grad_sort, "
        "(SELECT Name FROM AlarmGroup WHERE AlarmGroup.id = alarmgroups.alarmgroup_id) AS gruppe "
        "FROM Firefighter, alarmgroups "
        "WHERE alarmgroups.firefighter_id = Firefighter.id "
        "AND (alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'Stab') "
            "OR alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'Fu') "
            "OR alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'ADL') "
            "OR alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = 'SRT') ) "
        "AND Firefighter.is_deleted = 0 "
        "GROUP BY Firefighter.id ORDER BY Firefighter.grad_sort, Firefighter.name")

        req_jsondata = json.loads('{"template":{"shortid":"Bkeu4GNwBD"}}')

    elif gruppe == 'Alle':
        result = db.engine.execute("SELECT Firefighter.id AS id,"
        "Firefighter.vorname AS vorname,"
        "Firefighter.name AS name,"
        "Firefighter.grad AS grad,"
        "Firefighter.grad_sort AS grad_sort, "
        "'' AS gruppe "
        "FROM Firefighter, alarmgroups "
        "WHERE alarmgroups.firefighter_id = Firefighter.id "
        "AND Firefighter.is_deleted = 0 "
        "GROUP BY Firefighter.id ORDER BY Firefighter.grad_sort, Firefighter.name")

        req_jsondata = json.loads('{"template":{"shortid":"BJlXA4rzSD"}}')

    else:
        result = db.engine.execute("SELECT Firefighter.id AS id,"
        "Firefighter.vorname AS vorname,"
        "Firefighter.name AS name,"
        "Firefighter.grad AS grad,"
        "Firefighter.grad_sort AS grad_sort, "
        "'' AS gruppe "
        "FROM Firefighter, alarmgroups "
        "WHERE alarmgroups.firefighter_id = Firefighter.id "
        "AND alarmgroups.alarmgroup_id = (SELECT ID From AlarmGroup WHERE Name = '"+gruppe+"') "
        "AND Firefighter.is_deleted = 0 "
        "GROUP BY Firefighter.id ORDER BY Firefighter.grad_sort, Firefighter.name")

        req_jsondata = json.loads('{"template":{"shortid":"BJlXA4rzSD"}}')
    
    
    firefighters = result

    json_array = []
    for row in firefighters:
        d = collections.OrderedDict()
        d['id'] = row.id
        d['grad'] = row.grad.replace("\n        ","")
        d['name'] = row.name.replace("\n        ","")
        d['vorname'] = row.vorname.replace("\n        ","")
        d['grad_sort'] = row.grad_sort
        d['gruppe'] = row.gruppe
        json_array.append(d)
    
    req_jsondata['data'] = json.loads('{"items": []}')
    req_jsondata['data'] = json.loads('{"header": []}')
    json_data = json.dumps(json_array, ensure_ascii=False)
    req_jsondata['data']['header'] = json.loads('{"title":"'+gruppe+'"}')
    req_jsondata['data']['items'] = json.loads(json_data)
    result.close()
    
    req_report_header = {'Authorization': app.config['JSREPORT_AUTH'], 'Content-Type': 'application/json'}
    res_report = requests.post("https://fw-effi.jsreportonline.net/api/report",headers=req_report_header,json=req_jsondata)
    response = make_response(res_report.content)

    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % gruppe
    return response

@mod_pdf.route("/atemschutz/jahrauswertung",methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('AS_Auswertung')
def pdf_atemschutz_jahrauswertung():
    result = db.engine.execute("SELECT Firefighter.vorname AS vorname,"
        "Firefighter.name AS name,"
        "Firefighter.eintritt as eintritt,"
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

    json_array = []
    for row in year_statistics:
        d = collections.OrderedDict()
        d['name'] = row.name.replace("\n        ","")
        d['vorname'] = row.vorname.replace("\n        ","")
        d['eintritt'] = row.eintritt
        d['one_year'] = row.one_year
        d['one_year_training'] = row.one_year_training
        d['one_year_name'] = row.one_year_name
        d['two_year'] = row.two_year
        d['two_year_training'] = row.two_year_training
        d['two_year_name'] = row.two_year_name
        d['three_year'] = row.three_year
        d['three_year_training'] = row.three_year_training
        d['three_year_name'] = row.three_year_name
        d['four_year'] = row.four_year
        d['four_year_training'] = row.four_year_training 
        d['four_year_name'] = row.four_year_name
        json_array.append(d)
    req_jsondata = json.loads('{"template":{"shortid":"BkxAueIWUL"}}')
    req_jsondata['data'] = json.loads('{"items": []}')
    json_data = json.dumps(json_array, ensure_ascii=False)
    req_jsondata['data']['items'] = json.loads(json_data)
    
    req_report_header = {'Authorization': app.config['JSREPORT_AUTH'], 'Content-Type': 'application/json'}
    res_report = requests.post("https://fw-effi.jsreportonline.net/api/report",headers=req_report_header,json=req_jsondata)
    response = make_response(res_report.content)

    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % 'yourfilename'
    return response

@mod_pdf.route("/atemschutz/personalauswertung/<id>",methods=['GET'])
@oidc.require_login
@auth_module.check_role_permission('AS_Auswertung')
def pdf_atemschutz_personalauswertung(id):
    # Fetch Personal information
    result = db.engine.execute("SELECT name, vorname,eintritt FROM Firefighter WHERE id = :id", {'id': id})
    data_personal = result.fetchall()
    result.close()

    # Fetch AS Entries
    result = db.engine.execute("SELECT AS_Entry.id, AS_Entry.time, strftime('%d.%m.%Y',AS_Entry.datum) AS datum, AS_Category.name FROM AS_Entry LEFT JOIN AS_Category ON (AS_Entry.category_id = AS_Category.id) "
	    "WHERE AS_Entry.datum BETWEEN strftime('%Y-01-01','now','-4 year') AND strftime('%Y-12-31','now') AND AS_Entry.member_id = :id",
        {'id': id})
    data_items = result.fetchall()
    result.close()

    req_jsondata = json.loads('{"template":{"shortid":"Bkesse6IUU"}}')

    for row in data_personal:
        json_data = {"vorname":row.vorname, "name":row.name, "eintritt":row.eintritt, "items":[]}
        req_jsondata['data'] = json.loads(json.dumps(json_data))
    
    json_array = []
    for row in data_items:
        json_data = {"id":row.id,"time":row.time,"datum":row.datum,"category_name":row.name}
        json_array.append(json_data)

    json_data = json.dumps(json_array, ensure_ascii=False)
    req_jsondata['data']['items'] = json.loads(json_data)

    req_report_header = {'Authorization': app.config['JSREPORT_AUTH'], 'Content-Type': 'application/json'}
    res_report = requests.post("https://fw-effi.jsreportonline.net/api/report",headers=req_report_header,json=req_jsondata)
    response = make_response(res_report.content)

    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % 'Persönliche Auswertung'
    return response