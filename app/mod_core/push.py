from onesignal_sdk.client import Client
from flask import current_app as app
from app import db
from app.mod_alarm.models import pushEntry


def init_oneSignal():
    client = Client(app_id=app.config['PUSH_APP_ID'], rest_api_key=app.config['PUSH_APP_KEY'])

    return client


# Search for Notification Messages base on address
def sendNotification_fromAddress(address):
    addressParts = address.split(',')

    for parts in addressParts:
        # Street with number (e.g. Schulstrasse 18)
        message = findNotificationMessages(parts)
        for entry in message:
            send_push("FW Effi - " + entry.category.name, entry.message, entry.category.name)

        street = parts.split(' ')
        for streetParts in street:
            # Parts of address (e.g. PLZ, Street or City)
            message = findNotificationMessages(streetParts)
            for entry in message:
                send_push("FW Effi - " + entry.category.name, entry.message, entry.category.name)


def findNotificationMessages(part):
    messages = pushEntry.query.filter(db.or_(
        pushEntry.selector.like(part + ',%'),
        pushEntry.selector.like('%,' + part + ',%'),
        pushEntry.selector.like('%,' + part),
        pushEntry.selector.like(part)
    )).all()

    return messages


def send_push(title, message, segment):
    client = init_oneSignal()

    # Prepare Notification
    notification_body = {
        'heading': {'en': title},
        'contents': {'en': message},
        'included_segments': [segment]
    }
    # Send Notification
    response = client.send_notification(notification_body)
    print(response.body)
