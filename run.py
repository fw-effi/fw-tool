#!/usr/bin/env python3
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# Run a test server.
from app import app
if os.environ['FWAPP_ENV'] == "dev":
    print("# Starting in DEVELOPMENT Mode")
    print("####################")
    app.run(host='0.0.0.0', port=8080, debug=True)
elif os.environ['FWAPP_ENV'] == "test":
    print("Starting in TEST Mode")
    print("####################")
    app.run(host='0.0.0.0', port=8081, debug=True)
else:
    print("Starting in PRODUCTION Mode")
    print("####################")
    app.run(host='0.0.0.0', port=8080, debug=False)