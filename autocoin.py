import hashlib
import hmac
import time
import requests
import uuid
import sys
import json


def get_address():
    return "0"


def post(url_path='', url_query='', payload={}, content_type=''):
    with open('secrets.json') as secrets_file:
        secrets = json.load(secrets_file)

    # client_id = secrets['client_id']
    api_key = secrets['api_key']
    API_SECRET = str.encode(secrets['api_key_secret'])

    timestamp = str(int(round(time.time() * 1000)))
    nonce = str(uuid.uuid4())

    if sys.version_info.major >= 3:
        from urllib.parse import urlencode
    else:
        from urllib import urlencode

    payload_string = urlencode(payload)

    message = 'BITSTAMP ' + api_key + \
        'POST' + \
        'www.bitstamp.net' + \
        url_path + \
        url_query + \
        content_type + \
        nonce + \
        timestamp + \
        'v2' + \
        payload_string
    message = message.encode('utf-8')
    signature = hmac.new(API_SECRET,
                         msg=message,
                         digestmod=hashlib.sha256).hexdigest()
    headers = {
        'X-Auth': 'BITSTAMP ' + api_key,
        'X-Auth-Signature': signature,
        'X-Auth-Nonce': nonce,
        'X-Auth-Timestamp': timestamp,
        'X-Auth-Version': 'v2',
        'Content-Type': content_type
    }
    r = requests.post(
        'https://www.bitstamp.net' + url_path,
        headers=headers,
        data=payload_string
        )
    if not r.status_code == 200:
        print(r)
        raise Exception('Status code not 200')

    string_to_sign = (nonce + timestamp + r.headers.get('Content-Type'))
    string_to_sign = string_to_sign.encode('utf-8') + r.content
    signature_check = hmac.new(API_SECRET,
                               msg=string_to_sign,
                               digestmod=hashlib.sha256).hexdigest()
    if not r.headers.get('X-Server-Auth-Signature') == signature_check:
        raise Exception('Signatures do not match')

    return r


def get_balance():
    url_path = '/api/v2/balance/'
    url_query = ''
    payload = {}
    content_type = ''
    r = post(url_path=url_path,
             url_query=url_query,
             payload=payload,
             content_type=content_type)
    r_dict = r.json()
    return r_dict


def buy_btc(eur_balance):
    url_path = '/api/v2/buy/instant/btceur/'
    url_query = ''
    payload = {'amount': str(eur_balance)}
    content_type = 'application/x-www-form-urlencoded'
    r = post(url_path=url_path,
             url_query=url_query,
             payload=payload,
             content_type=content_type)
    r_dict = r.json()
    return r_dict


def withdraw_btc(btc_balance, address):
    with open('secrets.json') as secrets_file:
        secrets = json.load(secrets_file)

    nonce = int(time.time())
    client_id = secrets['client_id']
    api_key = secrets['api_key']
    API_SECRET = secrets['api_key_secret']
    message = str(nonce) + client_id + api_key
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256).hexdigest().upper()
    url = 'https://bitstamp.net/api/bitcoin_withdrawal/'
    payload = {'key': api_key,
               'signature': signature,
               'nonce': nonce,
               'amount': btc_balance,
               'address': address}
    r = requests.post(url, data=payload)
    r_dict = r.json()
    return r_dict


while __name__ == "__main__":
    if not (last_balance := globals().get('last_balance')):
        last_balance = time.time()

    if time.time() - last_balance >= 3600:
        last_balance = time.time()
        balance = get_balance()
        eur_balance = balance['eur_available']
        eur_balance = float(eur_balance)

        btc_balance = balance['btc_available']
        btc_balance = float(btc_balance)

        if eur_balance > 25:
            buy_btc(eur_balance)
        if btc_balance > 0:
            address = get_address()
            withdraw_btc(btc_balance, address)

    time.sleep(10)
