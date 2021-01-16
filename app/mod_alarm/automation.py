import imaplib
import email
import time
import googlemaps
from flask import current_app as app
from app.mod_core.push import *


def login_imap():
    try:
        client = imaplib.IMAP4_SSL(app.config['IMAP_SERVER'], app.config['IMAP_PORT'])
        client.login(app.config['IMAP_USERNAME'], app.config['IMAP_PASSWORD'])
        client.select('INBOX')
        print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - AlarmMails - IMAP Verbindung aktiv")

        return client

    except Exception as e:
        print(time.strftime("%d.%m.%Y %H:%M:%S") +
              ": INFO - BackgroundScheduler - AlarmMails - Failed to open a new IMAP Connection to {0} with error: {1}"
              .format(app.config['IMAP_SERVER'], str(e)))


def get_alarmPDF(client):
    try:
        status, response = client.search(None, 'ALL', '(UNSEEN)')
        mail_ids = response[0]
        unread_id_list = mail_ids.split()

        print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - AlarmMails - %d new Messages" %
              len(unread_id_list))

        # Loop trough unread mails
        for mail_id in unread_id_list:
            _, data = client.fetch(mail_id, '(RFC822)')
            email_message = data[0][1]
            mail = email.message_from_bytes(email_message)

            # downloading attachments
            for part in mail.walk():
                # this part comes from the snipped I don't understand yet...
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                fileName = part.get_filename()
                if "pdf" in fileName:
                    pdf_content = part.get_payload(decode=True)

                    # Filter Geo Tag from Google Maps Link in PDF
                    geo_tag = pdf_content.split(b'http://maps.google.ch/maps?q=')[1].split(b')')[0].decode('utf-8')

                    # Get Geo Information from geo_tag
                    gmaps = googlemaps.Client(key=app.config['MAP_API_KEY'])
                    geo_information = gmaps.reverse_geocode(geo_tag)[0]
                    sendNotification_fromAddress(geo_information['formatted_address'])
                    print(geo_information['formatted_address'])

    except Exception as e:
        print(time.strftime("%d.%m.%Y %H:%M:%S") +
              ": INFO - BackgroundScheduler - AlarmMails - Failed to read new Mails with error: {0}"
              .format(str(e)))


def start_alarmMails():
    # Login to IMAP Server
    client = login_imap()

    # Start Processing Mails
    get_alarmPDF(client)
