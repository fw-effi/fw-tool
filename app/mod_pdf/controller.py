import pdfkit
import flask
import json
import requests
import collections
from flask import Blueprint,Flask, render_template
# Import objects from the main app module
from app import auth_module, oidc, db
from ..mod_lodur import controller as lodur
from .appelliste import *

# Define the blueprint: 'pdf', set its url prefix: app.url/pdf
mod_pdf = Blueprint('mod_pdf',__name__, url_prefix='/pdf')

@mod_pdf.route("/appellliste/<gruppe>", methods=['GET'])
@oidc.require_login
def pdf_appellliste(gruppe):

    if gruppe == 'bag':
        content = {
            "bag1": lodur.getFirefightersPerAlarm('BAG1'),
            "bag2": lodur.getFirefightersPerAlarm('BAG2'),
            "bag3": lodur.getFirefightersPerAlarm('BAG3'),
            "konf": lodur.getFirefightersPerAlarm('Konf')
        }
    elif gruppe == 'spezZug':
        content = {
            "stab": lodur.getFirefightersPerAlarm('Stab'),
            "va": lodur.getFirefightersPerAlarm('VA'),
            "san": lodur.getFirefightersPerAlarm('San')
        }
    elif gruppe == 'spezGrp':
        content = {
            "stab": lodur.getFirefightersPerAlarm('Stab'),
            "fu": lodur.getFirefightersPerAlarm('Fu'),
            "srt": lodur.getFirefightersPerAlarm('SRT'),
            "adl": lodur.getFirefightersPerAlarm('ADL')
        }
    else:
        content = lodur.getFirefightersPerAlarm(gruppe)
    

    return render_alarmgruppe(content,gruppe)

@mod_pdf.route("/atemschutz/jahrauswertung",methods=['GET'])
@oidc.require_login
def pdf_atemschutz_jahrauswertung():
    result = db.engine.execute("SELECT Firefighter.vorname AS vorname,"
        "Firefighter.name AS name,"
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
        "FROM Firefighter "
        "GROUP BY Firefighter.id")
    year_statistics = result.fetchall()
    result.close()

    json_array = []
    for row in year_statistics:
        d = collections.OrderedDict()
        d['name'] = row.name.replace("\n        ","")
        d['vorname'] = row.vorname.replace("\n        ","")
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
    
    req_report_header = {'Authorization':'Basic b2ZlZTQyQGdtYWlsLmNvbTp0cGZmSndNVTc2SkpLTjR5TTdWNkxqaVRmRDZkY3hxNmZOUVBVTlZNSjlkNEc3V284', 'Content-Type':'application/json'}
    res_report = requests.post("https://fw-effi.jsreportonline.net/api/report",headers=req_report_header,json=req_jsondata)
    response = make_response(res_report.content)

    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % 'yourfilename'
    return response

@mod_pdf.route("/atemschutz/personalauswertung/<id>",methods=['GET'])
@oidc.require_login
def pdf_atemschutz_personalauswertung(id):
    # Fetch Personal information
    result = db.engine.execute("SELECT name, vorname FROM Firefighter WHERE id = :id", {'id': id})
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
        json_data = {"vorname":row.vorname, "name":row.name, "items":[]}
        req_jsondata['data'] = json.loads(json.dumps(json_data))
    
    json_array = []
    for row in data_items:
        json_data = {"id":row.id,"time":row.time,"datum":row.datum,"category_name":row.name}
        json_array.append(json_data)

    json_data = json.dumps(json_array, ensure_ascii=False)
    req_jsondata['data']['items'] = json.loads(json_data)

    req_report_header = {'Authorization':'Basic b2ZlZTQyQGdtYWlsLmNvbTp0cGZmSndNVTc2SkpLTjR5TTdWNkxqaVRmRDZkY3hxNmZOUVBVTlZNSjlkNEc3V284', 'Content-Type':'application/json'}
    res_report = requests.post("https://fw-effi.jsreportonline.net/api/report",headers=req_report_header,json=req_jsondata)
    response = make_response(res_report.content)

    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % 'yourfilename'
    return response