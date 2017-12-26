import requests
from flask import Response
from lxml import html

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
		"rows":1,
		"cols":4,
		"adfs":3,
		"gruppes":"1",
		"zugs":1,
	}
	
	# Do the POST request for the table with the information
	html_page = req_session.post('https://lodur-zh.ch/iel/index.php?modul=25&what=339&anz=1', data=post_data, headers={'User-Agent':'Mozilla/5.0'}, stream=True)

        tbl_tree = html.fromstring(html_page)
        
        for table in tbl_tree.xpath('//*[@id="mann_tab"]'):
            header = [text(th) for th in table.xpath('//th')]

	print(header)
	
	#return res
        
def lodur_get_userdata(req_session):
	""" Get the Userdata (like First-, Lastname and E-Mail Address) from the Lodur start page

	Keyword arguments:
	req_session -- requests session variable with the PHPSESSID from the login
	"""

	html_page = req_session.get('https://lodur-zh.ch/iel').content

	tbl_tree = html.fromstring(html_page)
	name = tbl_tree.xpath('//*[@id="adf_info_tbl"]/tbody/tr[1]/td/text()')
	mail = tbl_tree.xpath('//*[@id="adf_info_tbl"]/tbody/tr[4]/td/span[2]/text()')

	return { 'name': name[0], 'mail': mail[0] }
