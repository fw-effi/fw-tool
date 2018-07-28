import smtplib
import imaplib
import email
import sys
import requests
from helperLodur import *

imap_host = "imap.migadu.com"
smtp_host = "smtp-mail.outlook.com"
smtp_port = 587
user = "admin@scherer.me"
passwd = "Scan5415"
lodur_user = "andsche"
lodur_passwd = "9SG2uxqnfhQafwiM3qYT"
lodur_session = requests.session()

def find_user(list,firstname,lastname):
    for l in range(0,len(list)):
        listX = list[l]

        if listX['name'].lower() == lastname.lower() and listX['vorname'].lower() == firstname.lower():
            return l

# open IMAP connection and fetch all new messages
# store message data in email_data
print("IMAP starten...")
try:
    client = imaplib.IMAP4_SSL(imap_host,993)
    client.login(user,passwd)
    client.select('INBOX')
except:
    print("Unexpected error:",sys.exc_info()[0])

print("IMAP gestartet")

# open new SMTP Connection to forward received mails
print("SMTP Verbinden...")
server = smtplib.SMTP(smtp_host,smtp_port)
server.starttls()
server.login("andy.scherer@outlook.com","7eLAx!oZYrhf")
print("SMTP Verbindung aktiv")

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
