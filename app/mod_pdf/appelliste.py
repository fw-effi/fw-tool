import pdfkit
from flask import render_template, make_response, request


def render_alarmgruppe(pdfcontent, gruppe):

    if gruppe == 'bag':
        page = render_template("pdf/liste-alarmgruppe-bag.html",adfs = pdfcontent,gruppe = 'BAG')
    elif gruppe == 'spezZug':
        page = render_template("pdf/liste-alarmgruppe-spez.html",adfs = pdfcontent,gruppe = 'Spez. Zug')
    elif gruppe == 'spezGrp':
        page = render_template("pdf/liste-alarmgruppe-spezGrp.html",adfs = pdfcontent,gruppe = 'Spez. Gruppen')
    elif gruppe == 'all':
        page = render_template("pdf/liste-alarmgruppe-ka.html",adfs = pdfcontent,gruppe = 'Alle')
    else:
        page = render_template("pdf/liste-alarmgruppe-ka.html",adfs = pdfcontent,gruppe = gruppe)

    pdf = pdfkit.from_string(page, False)
    res = make_response(pdf)
    res.headers['Content-Disposition'] = 'attachment; filename=' + str(gruppe) + '.pdf'
    res.mimetype='application/pdf'
	
    return res