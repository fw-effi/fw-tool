# fw-tool
## Installation
1. Clone Repository to custom Folder
2. Install Python Requirements (incl. Depencies) from requirements.txt
````python
pip install -r requirements.txt
````
3. Setup Enviroment Variables from table below
4. Configure config.py File with settings from below
5. Run Software
````python
python3 run.py
````

## Configuration
### Configuration File
Use template configuration file from the repo and change it to your settings

### Enviroment Variables
|Variable|Values|
|--------|------|
|FWAPP_ENV|{prod/test/dev}|
|FWAPP_MAIL_PSW|SMTP Password|
|FWAPP_COOKIE_SECRET|Signing Secret|
|FWAPP_CSRF_SECRET|CSRF Secret|
|FWAPP_REPORT_BASIC|JsReport Basic Authentication in Base64|
