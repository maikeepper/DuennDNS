from flask import Flask, abort, request
import base64
import json
import logging
import requests
import os

############### Config ###############
BASIC_AUTHORIZATION = b'account:test'
ACCESS_TOKEN = 'dippedi_duppedi_f872634nd92hfs93741a0jjj_some_valid_access_token'
LIST_IDS_URL = 'https://api.digitalocean.com/v2/domains/example.com/records'
UPDATE_URL = 'https://api.digitalocean.com/v2/domains/example.com/records/'
######################################

app = Flask(__name__)

logger = logging.getLogger('werkzeug') # grabs underlying WSGI logger
handler = logging.FileHandler('logs/duennDns.log') # creates handler for the log file
logger.addHandler(handler) # adds handler to the werkzeug WSGI logger


@app.route('/nic/update')
def nic_update():

    if base64.b64decode(request.headers.get('Authorization', 'Basic .').split()[1]) != BASIC_AUTHORIZATION:
        abort(403)

    my_ip = request.args.get('myip', '')
    sending_server_ip = request.access_route[0]
    proxy_x_real_ip = request.environ.get('HTTP_X_REAL_IP', '')
    proxy_x_forwarded_for = request.environ.get('HTTP_X_FORWARDED_FOR', '')
    if my_ip != sending_server_ip or my_ip != proxy_x_real_ip or my_ip != proxy_x_forwarded_for:
        logger.error('Ignore myip ' + my_ip + ' != sending_server_ip: ' + sending_server_ip + ', headers: ' + json.dumps(dict(request.headers)))
        sendErrorMail('Ignore myip ' + my_ip + ' != sending_server_ip: ' + sending_server_ip + ', headers: ' + json.dumps(dict(request.headers)))
        abort(400)
    
    logger.debug(f'Update DuennDNS: {my_ip}')

    authorization_header = { 'Authorization': f'Bearer {ACCESS_TOKEN}' }
    # get usg ID from list-ids.sh
    try:
        usg_id_records = requests.get(LIST_IDS_URL, headers = authorization_header).json()
    except json.JSONDecodeError:
        logger.error('Can not list ids')
        sendErrorMail( 'Kein valides JSON von ' + LIST_IDS_URL + ' zurueckbekommen.' )
        abort(422)

    try:
        for record in usg_id_records['domain_records']:
            if record['name'] == 'usg':
                usg_id = record['id']
                break
    except KeyError:
        sendErrorMail( 'Keine domain_records von ' + LIST_IDS_URL + ' zurueckbekommen: ' + json.dumps( usg_id_records ) )

    logger.debug(f'Result: {usg_id}')

    # update record
    update_data = json.dumps({ 'data': f'{my_ip}' })
    response = requests.put(UPDATE_URL + f'{usg_id}', headers = authorization_header, data = update_data)
    response_content = json.loads(response.content.decode('utf-8'))
    if response.status_code < 200 or response.status_code >= 300:
        logger.error(f'Update-URL: {UPDATE_URL}{usg_id}')
        logger.error(f'  response -> [{response.status_code}] {response_content}')
        sendErrorMail(f'Update-URL: {UPDATE_URL}{usg_id} -> [{response.status_code}] {response_content}')
        return abort(response.status_code, response_content['message'])
    
    return response_content


def sendErrorMail(text):
    logger.info(text)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
