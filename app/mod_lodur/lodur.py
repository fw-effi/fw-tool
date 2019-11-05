import requests
import lxml.html
from flask import session
from flask import current_app as app
from app import db
from app.mod_lodur.models import Firefighter, AlarmGroup, FF_Zug

def lodur_init():
    sess_login = requests.session()
    # Url with the Login Form - used to get the first PHPSESSID Cookie
    url_form = "https://lodur-zh.ch/iel/index.php"
    # Url for the POST Request with the form data
    url_login = "https://lodur-zh.ch/iel/index.php?modul=9"
    # Create object with login data (url encoding automaticly by python)
    form_data = { "login_member_name": app.config['LODUR_USERNAME'], "login_member_pwd": app.config['LODUR_PASSWORD'] }
    #request the login from - genereate PHPSESSID cookie
    req_form = sess_login.get(url_form)
    # save the PHPSESSID Cookie bevor we do the login
    phpsess_bevor = requests.utils.dict_from_cookiejar(sess_login.cookies)

    #do the login (POST Request)
    req_login = sess_login.post(url_login, data=form_data, headers={'User-Agent':'Mozilla/5.0'})
    #save the PHPSESSID Cookie after the login (it should be different from the first one)
    phpsess_after = requests.utils.dict_from_cookiejar(sess_login.cookies)
    print('Bevor: %s \nAfter: %s' % (phpsess_bevor, phpsess_after))

    session['lodur_phpsess'] = phpsess_after

def do_lodur_request(url,method,params=None):

    #if session.get('lodur_phpsess') is None:
    lodur_init()

    if method == "POST":
        response = requests.post(url=url, cookies=session['lodur_phpsess'], data=params)

    return response

def fetch_update_lodur():
    """ Get the excel list from Lodur used for the 'Appellblaetter'

    Keyword arguments:
    None
    """
    # Create object for the POST Request
    post_data = {
        "status": 1,
        "mannschaftslisten_info_adf_0": -1,
        "mannschaftslisten_info_adf_1": -1,
        "mannschaftslisten_info_adf_2": -1,
        "gruppe_0": -1,
        "zug_0": -1,
        "mannschaftslisten_info_field_sel_0_0":104,
        "mannschaftslisten_info_field_sel_1_0":33,
        "mannschaftslisten_info_field_sel_2_0":103,
        "mannschaftslisten_info_field_sel_3_0":86,
        "mannschaftslisten_info_field_sel_4_0":83,
        "mannschaftslisten_info_field_sel_5_0":48,
        "mannschaftslisten_info_field_sel_6_0":35,
        "rows":1,
        "cols":7,
        "adfs":3,
        "gruppes":"1",
        "zugs":1,
    }
    
    # Do the POST request for the table with the information
    resp = do_lodur_request(url='https://lodur-zh.ch/iel/index.php?modul=25&what=339&anz=1', method="POST", params=post_data)
    resp.encoding = 'latin-1'
    html_page = resp.text
    #print(html_page)
    
    tbl_root = lxml.html.fromstring(html_page)

    for row in tbl_root.xpath('//*[@id="mann_tab"]/tbody/tr'):
        grad = row.xpath('.//td[1]//text()')[0]
        name = row.xpath('.//td[2]//text()')[0]
        vorname = row.xpath('.//td[3]//text()')[0]
        gruppe = row.xpath('.//td[4]//text()')[0]
        zug = row.xpath('.//td[5]//text()')[0]
        mail = row.xpath('.//td[6]//text()')[0]
        uid = row.xpath('.//td[7]//text()')[0]

        # If User with Personalnumber from Lodur no exist
        if db.session.query(Firefighter.id).filter_by(uid=uid).scalar() is None:
            # Then add a new Entry
            firefighter = Firefighter(
                uid,
                grad,
                vorname,
                name,
                mail
            )
            db.session.add(firefighter)
        else:
            #Update existing Entry
            firefighter = Firefighter.query.filter_by(uid=uid).first()
            firefighter.grad = grad
            firefighter.vorname = vorname
            firefighter.name = name
            firefighter.mail = mail

        # Mapping Zug Zugehörigkeit
        if 'Zug 1' in zug:
            firefighter.zug.append(FF_Zug.query.filter_by(name='Zug 1').first())
        if 'Zug 2' in zug:
            firefighter.zug.append(FF_Zug.query.filter_by(name='Zug 2').first())
        if 'Zug 3' in zug:
            firefighter.zug.append(FF_Zug.query.filter_by(name='Zug 3').first())
        if 'Spez Zug' in zug:
            firefighter.zug.append(FF_Zug.query.filter_by(name='Spez Zug').first())
        if 'Führungsunterstützung' in zug:
            firefighter.zug.append(FF_Zug.query.filter_by(name='FU').first())

        #Mapping Alarmgruppen
        if 'KA 1' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='KA1').first())
        if 'KA 2' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='KA2').first())
        if 'KA 3' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='KA3').first())
        if 'KA 4' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='KA4').first())
        if 'KA 5' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='KA5').first())
        if 'KA 6' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='KA6').first())
        if 'Bag 1' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='BAG1').first())
        if 'Bag 2' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='BAG2').first())
        if 'Bag 3' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='BAG3').first())
        if 'Konf Gr' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='Konf').first())
        if 'SRT' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='SRT').first())
        if 'Verkehrsgruppe' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='VA').first())
        if 'ADL' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='ADL').first())
        if 'Sanitätsabteilung' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='San').first())
        if 'Führungsunterstützung' in zug:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='Fu').first())
        if 'Stab' in zug:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='Stab').first())
    
    # Write changes to DB
    db.session.commit()