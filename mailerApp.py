import smtplib
import imaplib
import email
import sys
import requests
from helperLodur import *

imap_host = "imap.migadu.com"
smtp_host = "smtp.migadu.com"
#smtp_host = "smtp-mail.outlook.com"
smtp_port = 587
smtp_user = "admin@scherer.me"
smtp_passwd = "Scan5415"
admin_mail = "andy.scherer@outlook.com"
lodur_user = "andsche"
lodur_passwd = "9SG2uxqnfhQafwiM3qYT"
lodur_session = requests.session()

def find_user(list,firstname,lastname):
    for l in range(0,len(list)):
        listX = list[l]

        if listX['name'].lower() == lastname.lower() and listX['vorname'].lower() == firstname.lower():
            return l

def send_bounceMail(orginal_sender,errorMessage):
    bounceMessage = MIMEMultipart()
    bounceMessage['From'] = "{0} <{1}>".format("Feuerwehr Mailer",smtp_user)
    bounceMessage['To'] = orginal_sender
    bounceMessage['Subject'] = "Feuerwehr Mailer: Error E-Mail nicht versendet!"
    bounceBody = """
    <html><body><h1>Versand von E-Mail via FW Backend fehlgeschlagen</h1>
    <p>Der Feurwehr Mailer Deamon wurde mit folgendem Fehler abgebrochen:</p>
    <p>{0}</p>
    </body></html>
    """.format(errorMessage)
    message.attach(MIMEText(bounceBody, 'html'))
    server.sendmail(smtp_user, orginal_sender, bounceMessage.as_string())

# open new SMTP Connection to forward received mails
try:
    print("INFO: SMTP Verbinden...")
    server = smtplib.SMTP(smtp_host,smtp_port)
    server.starttls()
    server.login(smtp_user,smtp_passwd)
    print("INFO: SMTP Verbindung aktiv")
except Exception as e:
    sys.exit("ERROR: Failed to open a new SMTP Connection to {0} with error: {1}".format(smtp_host,str(e)))

# open IMAP connection and fetch all new messages
# store message data in email_data
print("INFO: IMAP Verbinden...")
try:
    client = imaplib.IMAP4_SSL(imap_host,993)
    client.login(user,passwd)
    client.select('INBOXdd')
    print("INFO: IMAP Verbindung aktiv")
except Exception as e:
    send_bounceMail(admin_mail,str(e))
    server.quit()
    sys.exit("ERROR: Failed to open a new IMAP Connection to {0} with error: {1}".format(imap_host, str(e)))


# Login to Lodur for Maillist details
print("Lodur Login durchfuehren...")
lodur = lodur_login(lodur_user, lodur_passwd, lodur_session)
lodur_session = lodur['session']
lodur_userdata = lodur_get_usersContactInfos(lodur_session)
print("Lodur Login erfolgreich")

# Use search(), to get all unreaded messages
status, response = client.search(None, None,'(UNSEEN)')
unread_msg_nums = response[0].split()
print("%d neue Nachrichten" % len(unread_msg_nums))

# Loop through all messages
for e_id in unread_msg_nums:
    _, data = client.fetch(e_id, '(RFC822)')
    email_data = data[0][1]

    #create new Message instance from the email_data
    message = email.message_from_bytes(email_data)

    #find related User Informationen. Read for that the part of the mail address befor @ and split in to first- and lastname
    userFirstname = message['To'].split('@',1)[0].split('.',1)[0]
    userLastname = message['To'].split('@',1)[0].split('.',1)[1]
    userId = find_user(lodur_userdata,userFirstname,userLastname)
    if userId != None:
        user = lodur_userdata[userId]
    else:
        print("Kein User gefunden! {0} {1}".format(userFirstname,userLastname))

    #replace headers for the new E-Mail
    message.add_header("Reply-to",message['From'])
    message.replace_header("From","andy.scherer@outlook.com")
    message.replace_header("To",user['mail'])

    print("E-Mail an neue Mail Adresse senden: %s" % user['mail'])
    #send Mail with new Headers
    #server.sendmail(user,to,message.as_string())

server.quit()
client.close()
client.logout()
