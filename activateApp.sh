#!/bin/bash
# Use to activate application, which will be on http://127.0.0.1:5000
# assumes you are at top level of repo
cd client
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
python app.py

# control-c to deactivate