from flask import Response
from mailjet_rest import Client
import os
import re
import smtplib

def remove_html_tags(text):
    """ Remove HTML Tages from a String

    Keyword arguments:
    text -> String with HTML Text
    """

    clean = re.compile('<.*?>')
    return re.sub(clean,'',text)

def mail_post_sendOneSmtp(request,user):
    message = """From: {0} <admin@scherer.me>
    To: {1}
    MIME-Version: 1.0
    Content-type: text/html
    Subject: {2}
    
    {3}
    
    {4}
    """.format(user['name'],request.form['mailTo'],request.form['mailSubject'],remove_html_tags(request.form['mailBody']),request.form['mailBody'])

    server = smtplib.SMTP('smtp.migadu.com',587)
    server.starttls()
    server.login('admin@scherer.me','Scan5415')
    result = server.sendmail("admin@scherer.me",request.form['mailTo'],message)
    server.quit()
    return result

def mail_post_sendOne(request,user):
    """ Send E-Mail from Webform to one Recipient

    Keyword arguments:

    """
    api_key = "9f8453e75fe91cfdce69de9f6d6df252"
    api_secret = "f43c420011116ea89ea5b0a1a70c5e68"
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "mailer@scherer.me",
                    "Name": user['name'].split(" ",1)[1]
                },
                "To": [
                    {
                        "Email": request.form['mailTo'],
                        "Name": ""
                    }
                ],
                "Subject": request.form['mailSubject'],
                "TextPart": remove_html_tags(request.form['mailBody']),
                "HTMLPart": request.form['mailBody'],
                "ReplyTo": {
                    "Email": user['mail'].split("|",1)[0],
                    "Name": user['name'].split(" ",1)[1]
                }
            }
        ]
    }
    result = mailjet.send.create(data=data)
    return result.json()
