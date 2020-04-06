import time
# Import objects from the main app module
from app import app, os, cron
from .mod_lodur import gvzUpdate as gvzUpdate

# Check add_jobs at th end of this file!

def gvz_statusUpdate():
    gvzUpdate.gvz_init()

def print_date_time():
    print("BackgroundScheduler - DEBUG - " + time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

def gvzUpdate_24h():
    #Send update to GVZ always 20:00
    with app.app_context():
        gvzUpdate.send_FwStatus()

    print("BackgroundScheduler - GVZUpdate FINISH - " + time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    #cron.add_job(func=print_date_time, trigger="interval", seconds=3)
    cron.add_job(func=gvzUpdate_24h, trigger="cron",hour=20, minute=00)
    cron.start()