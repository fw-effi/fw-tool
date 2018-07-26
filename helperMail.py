from flask import Response
from mailjet_rest import Client
import os

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
                "HTMLPart": request.form['mailBody']
            }
        ]
    }
    result = mailjet.send.create(data=data)
    return result.json()