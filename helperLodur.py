import requests
import lxml.html
from flask import Response

def lodur_login(username,password,sess_login):
	""" Login User in Lodur. Use the Username and Password from the Webform

	Keyword arguments:
	username   -- Username from Webform
	password   -- Password from Webform
	sess_login -- global variable for requests session information
	"""

	# Url with the Login Form - used to get the first PHPSESSID Cookie
	url_form = "https://lodur-zh.ch/iel/index.php?modul=9"
	# Url for the POST Request with the form data
	url_login = "https://lodur-zh.ch/iel/index.php"
	# Create object with login data (url encoding automaticly by python)
	form_data = { "login_member_name": username, "login_member_pwd": password }

	#request the login from - genereate PHPSESSID cookie
	req_form = sess_login.get(url_form)
	# save the PHPSESSID Cookie bevor we do the login
	phpsess_bevor = requests.utils.dict_from_cookiejar(sess_login.cookies)

	#do the login (POST Request)
	req_login = sess_login.post(url_login, data=form_data, headers={'User-Agent':'Mozilla/5.0'})
	#save the PHPSESSID Cookie after the login (it should be different from the first one)
	phpsess_after = requests.utils.dict_from_cookiejar(sess_login.cookies)

	# create array with the needed information for the return command
	result = {"result": not phpsess_bevor == phpsess_after, "session": sess_login}
	
	return result

def lodur_get_appellliste(req_session):
	""" Get the excel list from Lodur used for the 'Appellblaetter'

	Keyword arguments:
	req_session -- requests session variable with the PHPSESSID from the login
	"""

	print(requests.utils.dict_from_cookiejar(req_session.cookies))

	# Create object for the POST Request
	post_data = {
		"status": 1,
		"mannschaftslisten_info_adf_0": -1,
		"mannschaftslisten_info_adf_1": -1,
		"mannschaftslisten_info_adf_2": -1,
		"gruppe_0": -1,
		"zug_0": -1,
		"mannschaftslisten_info_field_sel_0_0":104,
		"mannschaftslisten_info_field_sel_1_0":33,
		"mannschaftslisten_info_field_sel_2_0":103,
		"mannschaftslisten_info_field_sel_3_0":86,
		"mannschaftslisten_info_field_sel_4_0":83,
		"rows":1,
		"cols":5,
		"adfs":3,
		"gruppes":"1",
		"zugs":1,
	}
	
	# Do the POST request for the table with the information
	html_page = req_session.post('https://lodur-zh.ch/iel/index.php?modul=25&what=339&anz=1', data=post_data)
	html_page.encoding = 'latin-1'

	result = {}
	result.update({'ka1': []})
	result.update({'ka2': []})
	result.update({'ka3': []})
	result.update({'ka4': []})
	result.update({'ka5': []})
	result.update({'ka6': []})
	result.update({'bag': {'bag1':[],'bag2':[],'bag3':[],'konf':[]}})
	result.update({'spezZug': {'va': [],'san': []}})
	result.update({'spezGrp': {'adl': [],'srt': [], 'fu': [], 'stab':[]}})
	result.update({'all': []})
	
	tbl_root = lxml.html.fromstring(html_page.content)

	for row in tbl_root.xpath('//*[@id="mann_tab"]/tbody/tr'):
		grad = row.xpath('.//td[1]//text()')[0]
		name = row.xpath('.//td[2]//text()')[0]
		vorname = row.xpath('.//td[3]//text()')[0]
		gruppe = row.xpath('.//td[4]//text()')[0]
		zug = row.xpath('.//td[5]//text()')[0]

		result["all"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'KA 1' in gruppe:
			result["ka1"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'KA 2' in gruppe:
			result["ka2"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'KA 3' in gruppe:
			result["ka3"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'KA 4' in gruppe:
			result["ka4"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'KA 5' in gruppe:
			result["ka5"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'KA 6' in gruppe:
			result["ka6"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'Bag 1' in gruppe:
			result["bag"]["bag1"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'Bag 2' in gruppe:
			result["bag"]["bag2"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'Bag 3' in gruppe:
			result["bag"]["bag3"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'Konf Gr' in gruppe:
			result["bag"]["konf"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'SRT' in gruppe:
			result["spezGrp"]["srt"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'Verkehrsabteilung' in gruppe:
			result["spezZug"]["va"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'ADL' in gruppe:
			result["spezGrp"]["adl"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'Sanitätsabteilung' in gruppe:
			result["spezZug"]["san"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'Führungsunterstützung' in zug:
			result["spezGrp"]["fu"].append({"grad":grad,"name":name,"vorname":vorname})
		if 'Stab' in zug:
			result["spezGrp"]["stab"].append({"grad":grad,"name":name,"vorname":vorname})
	return result

def lodur_get_userdata(req_session):
	""" Get the Userdata (like First-, Lastname and E-Mail Address) from the Lodur start page

	Keyword arguments:
	req_session -- requests session variable with the PHPSESSID from the login
	"""

	html_page = req_session.get('https://lodur-zh.ch/iel').content

	tbl_tree = lxml.html.fromstring(html_page)
	name = tbl_tree.xpath('//*[@id="adf_info_tbl"]/tbody/tr[1]/td/text()')
	mail = tbl_tree.xpath('//*[@id="adf_info_tbl"]/tbody/tr[4]/td/span[2]/text()')

	return { 'name': name[0], 'mail': mail[0] }
