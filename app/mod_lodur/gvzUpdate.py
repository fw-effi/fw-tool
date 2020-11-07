import requests
import lxml.html
from flask import session
from flask import current_app as app
from datetime import datetime
import lxml.html
from app import db
from app.mod_alarm.models import GVZupdate, GVZnotAvailable
from app.mod_core.controller import notifications

def gvz_init():
    sess_login = requests.session()
    # Url with the Login Form - used to get the first PHPSESSID Cookie
    url_form = "https://status.feuerwehr-gvz.ch/login"
    # Url for the POST Request with the form data
    url_login = "https://status.feuerwehr-gvz.ch/login"

    #request the login from - genereate PHPSESSID cookie and read the csrf token
    req_form = sess_login.get(url_form)
    lxml_root = lxml.html.fromstring(req_form.text)
    csrf = lxml_root.xpath('//input[@name="_csrf_token"]/@value')[0]
    print('GVZinit - CSRF Before: %s' % (csrf))

    # Create object with login data (url encoding automaticly by python)
    form_data = '_csrf_token='+csrf+'&organization=559&password='+app.config['LODUR_PASSWORD']+'&username='+app.config['LODUR_USERNAME']
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    # save the PHPSESSID Cookie bevor we do the login
    phpsess_bevor = requests.utils.dict_from_cookiejar(sess_login.cookies)

    #do the login (POST Request)
    req_login = sess_login.post(url_login, data=form_data, headers=headers)
    # extract csrf token from response page
    lxml_root = lxml.html.fromstring(req_login.text)
    #print(req_login.text)
    csrf = lxml_root.xpath('//input[@id="organization_report__token"]/@value')[0]
    print('GVZinit - CSRF After Login: %s' % (csrf))

    #save the PHPSESSID Cookie after the login (it should be different from the first one)
    phpsess_after = requests.utils.dict_from_cookiejar(sess_login.cookies)

    return phpsess_after

def do_gvz_request(url,method,params=None):

    phpsess_after = gvz_init()

    req_form = requests.get(url,cookies=phpsess_after)
    lxml_root = lxml.html.fromstring(req_form.text)
    csrf = lxml_root.xpath('//input[@id="organization_report__token"]/@value')[0]
    print('GVZrequest - CSRF: ' + csrf)
    postdata = params + '&organization_report%5B_token%5D='+csrf
    if method == "POST":
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
            }
        response = requests.post(url=url,cookies=phpsess_after, data=postdata,headers=headers)

    return response

def send_FwStatus():
    generalSettings = db.session.query(GVZupdate).order_by(GVZupdate.id.desc()).first()
    # Get all unavailable AdFs
    result = db.engine.execute("SELECT COUNT(*) FROM Alarm_GVZnotAvailable WHERE date(datumvon) <= date('now') AND date(datumbis) >= date('now')")
    NaAdf = result.fetchall()[0][0]
    # Get all unavailable Drivers C1/118
    result = db.engine.execute("SELECT COUNT(*) FROM Alarm_GVZnotAvailable WHERE date(datumvon) <= date('now') AND date(datumbis) >= date('now') AND isDriver = 1")
    NaDriver = result.fetchall()[0][0]
    result = db.engine.execute("SELECT COUNT(*) FROM Alarm_GVZnotAvailable WHERE date(datumvon) <= date('now') AND date(datumbis) >= date('now') AND isKader = 1")
    NaKader = result.fetchall()[0][0]
    result.close()

    einsatzbereit = "0"
    mat_ready = "0"
    if generalSettings.einsatzbereit:
        einsatzbereit = "1"
    if generalSettings.mat_ready:
        mat_ready ="1"

    # Create object for the POST Request
    post_data = 'organization_report%5BauxiliaryServices%5D%5B%5D=28&'\
        'organization_report%5BauxiliaryServices%5D%5B%5D=30&'\
        'organization_report%5Bcomment%5D=&'\
        'organization_report%5BdriversC1%5D='+str(generalSettings.anzahlFahrer - NaDriver)+'&'\
        'organization_report%5BequipmentOperational%5D='+mat_ready+'&'\
        'organization_report%5BequipmentRequiredInfo%5D=&'\
        'organization_report%5BmemberNonOperationalCadre%5D='+str(NaKader)+'&'\
        'organization_report%5BmemberNonOperational%5D='+str(NaAdf)+'&'\
        'organization_report%5Boperational%5D='+einsatzbereit+'&'\
        'organization_report%5BotherAuxiliaryServicesInfo%5D='

    if(generalSettings.rd_fahrer):
        post_data += '&organization_report%5BauxiliaryServices%5D%5B%5D=29'

    print(post_data)
    # Do the POST request for the table with the information
    resp = do_gvz_request(url='https://status.feuerwehr-gvz.ch/organization', method="POST", params=post_data)

    notifications.create("Lodur", "Einsatzbereitschaft", "Info an GVZ gesendet", "/alarm/statusUpdate")