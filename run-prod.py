#!/usr/bin/env python3
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# Run a test server.
from app import app
app.run(host='0.0.0.0', port=8080, debug=False)