import requests
import lxml.html
import datetime
import uuid
from flask import session
from flask import current_app as app
from app import db
from app.mod_core.controller import notifications
from app.mod_atemschutz.controller import entry_AutoNew
from app.mod_lodur.models import Firefighter, AlarmGroup, FF_Zug, Lodur_General, Kurs_Definitions, Kurs_Members

def lodur_init():
    sess_login = requests.session()
    # Url with the Login Form - used to get the first PHPSESSID Cookie
    url_form = "https://lodur-zh.ch/iel/index.php"
    # Url for the POST Request with the form data
    url_login = "https://lodur-zh.ch/iel/index.php?modul=9"
    # Create object with login data (url encoding automaticly by python)
    print("Lodur Login - Username: " + app.config['LODUR_USERNAME'])

    form_data = { "login_member_name": app.config['LODUR_USERNAME'], "login_member_pwd": app.config['LODUR_PASSWORD'], "sms_mannschaft_id": ""}
    #request the login from - genereate PHPSESSID cookie
    req_form = sess_login.get(url_form)
    # save the PHPSESSID Cookie bevor we do the login
    phpsess_bevor = requests.utils.dict_from_cookiejar(sess_login.cookies)

    #do the login (POST Request)
    req_login = sess_login.post(url_login, data=form_data, headers={'User-Agent':'Mozilla/5.0'})
    #save the PHPSESSID Cookie after the login (it should be different from the first one)
    phpsess_after = requests.utils.dict_from_cookiejar(sess_login.cookies)
    print('Bevor: %s \nAfter: %s' % (phpsess_bevor, phpsess_after))

    return phpsess_after

def do_lodur_request(url,method,params=None):

    #if session.get('lodur_phpsess') is None:
    lodur_phpsess = lodur_init()

    if method == "POST":
        response = requests.post(url=url, cookies=lodur_phpsess, data=params)
    if method == "GET":
        response = requests.get(url=url, cookies=lodur_phpsess)

    return response

def fetch_kurse():
    """ Get list of all registered courses and the current status

    Keyword arguments:
    None
    """
    # Generate Unique Sync ID
    sync_id = str(uuid.uuid4())

    # Do the GET request for the table with the information
    resp = do_lodur_request(url='https://lodur-zh.ch/iel/index.php?modul=59', method="GET")
    resp.encoding = 'latin-1'
    html_page = resp.text
    tbl_root = lxml.html.fromstring(html_page)

    for row in tbl_root.xpath('//*[@id="teilnehmerlisten"]/tbody/tr'):
        grad = row.xpath('.//td[1]//text()')[0]
        name = row.xpath('.//td[2]//text()')[0]
        vorname = row.xpath('.//td[3]//text()')[0]
        datum = row.xpath('.//td[4]//text()')[0]
        datum = datetime.datetime.strptime(datum.split('\n')[0], "%d.%m.%Y")
        dauer = row.xpath('.//td[5]//text()')[0]
        kurs = row.xpath('.//td[7]//text()')[0]
        kurs = kurs.split('/')[1]
        status = row.xpath('.//td[9]//text()')[0]
        status = status.split('\n')[0]
    
        # Get Firefighter from given information
        member = Firefighter.query.filter_by(grad=grad,name=name,vorname=vorname).first()

        # Check if Kurs already exist
        if db.session.query(Kurs_Definitions.id).filter_by(name=kurs).scalar() is None:
            # Create new Kurs
            db_kurs = Kurs_Definitions(
                kurs,
                0
            )
            db.session.add(db_kurs)

            notifications.create("AS_general", "Neuer Kurs", "Kurs: %s" % kurs, "/atemschutz/settings")
        db.session.flush()
        db_kurs = Kurs_Definitions.query.filter_by(name=kurs).first()

        # Check if Entry already exist
        if db.session.query(Kurs_Members.id).filter_by(datum=datum,dauer=dauer,kurs_id=db_kurs.id,member_id=member.id).scalar() is None:
            # Create new Kurs Member Entry
            kurs_member = Kurs_Members(
                member.id,
                datum,
                dauer,
                db_kurs.id,
                status,
                sync_id,
                datetime.datetime.now() #Set last sync DateTime
            )
            db.session.add(kurs_member)
        else:
            firefighter = Kurs_Members.query.filter_by(datum=datum,dauer=dauer,kurs_id=db_kurs.id,member_id=member.id).first()
            kurs_member = firefighter
            # Check if Kurs new Status "bestanden"
            if kurs_member.status != "bestanden" and status == "bestanden":
                entry_AutoNew(firefighter.member_id,datum,db_kurs)

            # Update existing Entry
            kurs_member.datum = datum
            kurs_member.dauer = dauer
            kurs_member.status = status
            kurs_member.sync_id = sync_id
            kurs_member.last_sync = datetime.datetime.now() #Set last sync DateTime



    # Mark all not updated entry as deleted
    result = db.session.query(Kurs_Members)\
        .filter(db.or_(Kurs_Members.sync_uid!=sync_id, Kurs_Members.sync_uid == None))\
        .update(dict(is_deleted=True))
    
    db.session.commit()

def fetch_update_lodur():
    """ Get the excel list from Lodur used for the 'Appellblaetter'

    Keyword arguments:
    None
    """
    # Generate Unique Sync ID
    sync_id = str(uuid.uuid4())

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
        "mannschaftslisten_info_field_sel_7_0":51,
        "rows":1,
        "cols":8,
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
        grad_id = 99 #Höchste Zahl, daher wenn der Grad nicht gemamppet werden kann, landet die Person zu unterst auf der Liste -> Wird für die Sortierung verwendet
        name = row.xpath('.//td[2]//text()')[0]
        vorname = row.xpath('.//td[3]//text()')[0]
        gruppe = row.xpath('.//td[4]//text()')[0]
        zug = row.xpath('.//td[5]//text()')[0]
        mail = row.xpath('.//td[6]//text()')[0]
        uid = row.xpath('.//td[7]//text()')[0]
        eintritt = row.xpath('.//td[8]//text()')[0]
        eintritt = datetime.datetime.strptime(eintritt.split('\n')[0], "%d.%m.%Y")

        #Füge anhand vom Rand eine passende Integer Zahl hinzu. Damit danach nach Rang sortiert werden kann
        if 'Hptm' in grad:
            grad_id = 1
        if 'Oblt' in grad:
            grad_id = 2
        if 'Lt' in grad:
            grad_id = 3
        if 'Wm' in grad:
            grad_id = 4
        if 'Kpl' in grad:
            grad_id = 5
        if 'Sdt' in grad:
            grad_id = 6
        
        # If User with Personalnumber from Lodur no exist
        if db.session.query(Firefighter.id).filter_by(uid=uid).scalar() is None:
            # Then add a new Entry
            firefighter = Firefighter(
                uid,
                grad,
                grad_id,
                vorname,
                name,
                mail,
                eintritt,
                sync_id,
                datetime.datetime.now() #Set last sync DateTime
            )
            db.session.add(firefighter)
        else:
            #Update existing Entry
            firefighter = Firefighter.query.filter_by(uid=uid).first()
            firefighter.grad = grad
            firefighter.grad_sort = grad_id
            firefighter.vorname = vorname
            firefighter.name = name
            firefighter.mail = mail
            firefighter.eintritt = eintritt
            firefighter.sync_uid = sync_id
            firefighter.last_sync = datetime.datetime.now() #Update last Sync DateTime

        # Mapping Zug Zugehörigkeit
        firefighter.zug.clear()
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
        firefighter.alarmgroups.clear()
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
        if 'ADL Gruppe' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='ADL').first())
        if 'Sanitätsabteilung' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='San').first())
        if 'Führungsunterstützung' in zug:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='Fu').first())
        if 'Stab' in zug:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='Stab').first())
        if 'Atemschutz' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='Atemschutz').first())
        if 'Fahrer Grossfahrzeuge' in gruppe:
            firefighter.alarmgroups.append(AlarmGroup.query.filter_by(name='Grossfahrzeuge').first())

    # Write changes to DB
    db.session.commit()

    # Mark all not updated entry as deleted
    result = db.session.query(Firefighter)\
        .filter(db.or_(Firefighter.sync_uid!=sync_id, Firefighter.sync_uid == None))\
        .update(dict(is_deleted=True))
    
    # Update General Table with last Sync DateTime
    general = db.session.query(Lodur_General).filter(Lodur_General.name == "LastLodurSync").first()
    
    general.value = str(datetime.datetime.now())

    db.session.commit()