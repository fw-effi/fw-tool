from flask import current_app as app
from datetime import datetime


def datetimestrformat(datetime_str,format):
    datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')

    return datetime_object.strftime(format)