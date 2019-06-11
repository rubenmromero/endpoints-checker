#!/usr/bin/env python3

# -*- coding: utf-8 -*-

#
# Modules Import
#
import atexit
import json
import os
import requests
import shutil
import sys
import yaml

from flask import Flask
from flask import jsonify
from apscheduler.schedulers.background import BackgroundScheduler

#
# Function to load configuration schema file
#
def load_config_schema():
    # Define parameters template & file
    schema_file = 'schema.yml'
    schema_template = schema_file + '.dist'

    # If schema file does not exist, create it from schema template
    if not os.path.isfile(schema_file):
        shutil.copy2(schema_template, schema_file)

    # Decode YAML file
    with open(schema_file) as file:
        try:
            schema = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print("\nMalformed YAML in '" + os.path.basename(schema_file) + "'\n", file=sys.stderr)
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                print("Error position: (%s:%s)" % (mark.line+1, mark.column+1), file=sys.stderr)
            exit(-1)

    return schema

#
# Function to check a service based on defined request parameters
#
def check_service(request_params):
    # Initialize request parameters
    endpoint = request_params['endpoint']
    method = request_params['method']
    body = ''
    auth_user = ''
    auth_passwd = ''
    if 'body' in request_params:
        body = request_params['body']
    if 'auth' in request_params:
        auth_user = request_params['auth']['user']
        auth_passwd = request_params['auth']['passwd']

    if method == 'GET':
        try:
            response = requests.get(endpoint, data=body, auth=(auth_user, auth_passwd))
        except requests.exceptions.RequestException as err:
            response = 'ko'
    elif method == 'POST':
        try:
            response = requests.post(endpoint, data=body, auth=(auth_user, auth_passwd))
        except requests.exceptions.RequestException as err:
            response = 'ko'
    else:
        response = 'bad_method'

    return response

#
# Function to check if a request response is ok or ko based on defined response parameters
#
def check_response(service_name, response_params, response):
    if (response != 'ko') and (response != 'bad_method'):
        # Initialize status to 'ko'
        status = 'ko'

        if 'code' in response_params['ok']:
            if response_params['ok']['code'] == response.status_code:
                status = 'ok'

        if 'body' in response_params['ok']:
            if response_params['ok']['body'] == response.text:
                status = 'ok'

        if 'header' in response_params['ok']:
            header_key = response_params['ok']['header']['key']
            header_value = response_params['ok']['header']['value']
            if response.headers[header_key] == header_value:
                status = 'ok'
    else:
        status = response

    # Send test notification to a notification server if status is not 'ok'
    if status != 'ok':
        server_endpoint = 'https://interview-notifier-svc.spotahome.net/api/v1/notification'
        auth_header = { 'Authorization': 'Bearer ' + os.environ['NOTIF_TOKEN'] }
        notification = { "service": service_name, "description" : "Failed with '" + status + "' status" }

        try:
            response = requests.post(server_endpoint, headers=auth_header, data=json.dumps(notification))
            print("\n" + response.text + "\n", file=sys.stderr)
        except requests.exceptions.RequestException as err:
            print("\nError sending notification to the notification server\n", file=sys.stderr)

    return { 'service': service_name, 'status': status }

#
# Main
#
app = Flask(__name__)

@app.route('/')
def check_endpoints():
    schema = load_config_schema()

    # Initialize 'result' dictionary
    result = { 'checks': [ ] }

    for service in schema['checks']:
        response = check_service(service['request'])
        result['checks'].append(check_response(service['service'], service['response'], response))

    return jsonify(result)

def execute_checks():
    with app.app_context():
        check_endpoints()

scheduler = BackgroundScheduler()
scheduler.add_job(func=execute_checks, trigger="interval", seconds=60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

@app.route('/check')
def healthcheck():
    result = { 'status': 'ok' }
    return jsonify(result)

if __name__ == '__main__':
    app.run()
