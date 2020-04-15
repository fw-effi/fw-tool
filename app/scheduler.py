import time
# Import objects from the main app module
from app import app, os, cron
from .mod_lodur import gvzUpdate, lodur

# Check add_jobs at th end of this file!

def gvz_statusUpdate():
    gvzUpdate.gvz_init()

def print_date_time():
    print("BackgroundScheduler - DEBUG - " + time.strftime("%A, %d. %B %Y %I:%M:%S %p"))

def gvzUpdate_24h():
    #Send update to GVZ always 20:00
    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - GVZUpdate START")
    with app.app_context():
        gvzUpdate.send_FwStatus()

    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - GVZUpdate FINISH")

def lodurUpdate_1h():
    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - LodurUpdate START")
    #Update Lodur Data hourly
    with app.app_context():
        lodur.fetch_update_lodur()
    
    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - LodurUpdate FINISH")

if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    #cron.add_job(func=print_date_time, trigger="interval", seconds=3)
    #cron.add_job(func=gvzUpdate_24h, trigger="cron",hour=20, minute=00)
    cron.add_job(func=lodurUpdate_1h, trigger="interval", hours=1)
    cron.start()

# Scheduler for productive system
if not app.debug:
    cron.add_job(func=gvzUpdate_24h, trigger="cron",hour=20, minute=00)
    cron.add_job(func=lodurUpdate_1h, trigger="interval", hours=1)
    cron.start()