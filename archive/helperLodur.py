import requests
import lxml.html
from flask import Response


def lodur_get_usersContactInfos(req_session):
	"""
	:param req_session: requests session variable with the PHPSESSID from the login
	:return: E-Mail Adress from the User as String
	"""
	# Create object for the POST Request
	post_data = {
		"status": 1,
		"mannschaftslisten_info_adf_0": -1,
		"mannschaftslisten_info_adf_1": -1,
		"mannschaftslisten_info_adf_2": -1,
		"gruppe_0": -1,
		"zug_0": -1,
		"mannschaftslisten_info_field_sel_0_0": 104, #Grad
		"mannschaftslisten_info_field_sel_1_0": 102, #Anrede
		"mannschaftslisten_info_field_sel_2_0": 33, #Name
		"mannschaftslisten_info_field_sel_3_0": 103, #Vorname
		"mannschaftslisten_info_field_sel_4_0": 113, #Mobile Privat
		"mannschaftslisten_info_field_sel_5_0": 110, #Festnetz Privat
		"mannschaftslisten_info_field_sel_6_0": 114, #Mobile Arbeit
		"mannschaftslisten_info_field_sel_7_0": 111, #Festnetz Arbeit
		"mannschaftslisten_info_field_sel_8_0": 48, #E-Mail
		"mannschaftslisten_info_field_sel_9_0": 49, #2. E-Mail
		"rows": 1,
		"cols": 10,
		"adfs": 3,
		"gruppes": "1",
		"zugs": 1,
	}

	# Do the POST request for the table with the information
	html_page = req_session.post('https://lodur-zh.ch/iel/index.php?modul=25&what=339&anz=1', data=post_data)
	html_page.encoding = 'latin-1'

	result = []

	tbl_root = lxml.html.fromstring(html_page.content)

	for row in tbl_root.xpath('//*[@id="mann_tab"]/tbody/tr'):
		result.append({"grad":row.xpath('.//td[1]//text()')[0].split('\n',1)[0],
					   "anrede": row.xpath('.//td[2]//text()')[0].split('\n',1)[0],
					   "name": row.xpath('.//td[3]//text()')[0].split('\n',1)[0],
					   "vorname": row.xpath('.//td[4]//text()')[0].split('\n',1)[0],
					   "mobilePrivat": row.xpath('.//td[5]//text()')[0].split('\n',1)[0],
					   "festnetzPrivat": row.xpath('.//td[6]//text()')[0].split('\n',1)[0],
					   "mobileArbeit": row.xpath('.//td[7]//text()')[0].split('\n',1)[0],
					   "festnetzArbeit": row.xpath('.//td[8]//text()')[0].split('\n',1)[0],
					   "mail": row.xpath('.//td[9]//text()')[0].split('\n',1)[0],
					   "mail2": row.xpath('.//td[10]//text()')[0].split('\n',1)[0]
		})
#	print(result)
	return result
