import time
# Import objects from the main app module
from app import app, os, cron
from app.mod_lodur import gvzUpdate, lodur
from app.mod_alarm import automation

# Check add_jobs at th end of this file!


def gvz_statusUpdate():
    gvzUpdate.gvz_init()


def print_date_time():
    print("BackgroundScheduler - DEBUG - " + time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


def gvzUpdate_24h():
    # Send update to GVZ always 20:00
    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - GVZUpdate START")
    with app.app_context():
        gvzUpdate.send_FwStatus()

    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - GVZUpdate FINISH")


def lodurUpdate_3h():
    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - LodurUpdate START")
    # Update Lodur Data hourly
    with app.app_context():
        lodur.fetch_update_lodur()

    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - LodurUpdate FINISH")


def kurseUpdate_3h():
    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - KurseUpdate START")
    # Update Lodur Data hourly
    with app.app_context():
        lodur.fetch_kurse()

    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - KurseUpdate FINISH")


def AlarmMails_2min():
    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - AlarmMail START")
    # Update Lodur Data hourly
    with app.app_context():
        automation.start_alarmMails()

    print(time.strftime("%d.%m.%Y %H:%M:%S") + ": INFO - BackgroundScheduler - AlarmMail FINISH")


if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' and os.environ.get('FWAPP_ENV') == 'dev':
    print("####################")
    print("# Scheduler started in Development Mode")
    # cron.add_job(func=print_date_time, trigger="interval", seconds=3)
    # cron.add_job(func=gvzUpdate_24h, trigger="interval", minutes=1)
    cron.add_job(func=lodurUpdate_3h, trigger="interval", hours=8)
    cron.add_job(func=kurseUpdate_3h, trigger="interval", hours=8)
    cron.add_job(func=AlarmMails_2min, trigger="interval", minutes=1)
    cron.start()

# Scheduler for productive system
if os.environ.get('FWAPP_ENV') == 'prod':
    cron.add_job(func=gvzUpdate_24h, trigger="cron", hour=20, minute=00)
    cron.add_job(func=lodurUpdate_3h, trigger="interval", hours=3)
    cron.add_job(func=kurseUpdate_3h, trigger="interval", hours=3)
    cron.add_job(func=AlarmMails_2min, trigger="interval", minutes=2)
    cron.start()
