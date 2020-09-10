"""Retreive available fiat/BTC every 5 seconds. Immediately convert fiat to BTC
and send BTC to withdraw address once available"""
import hashlib
import hmac
import time
import requests
import uuid
import sys
import json
import setadd


# Set the fiat currency used by the script
with open("fiat.json") as fiat_file:
    fiat = json.load(fiat_file)


def post(url_path='', url_query='', payload={}, content_type=''):
    """Make post requests to the Bitstamp API

    For further explanation, consult the Bitstamp
    API documentation at https://bitstamp.net/api"""
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
        print("Status code not 200")
        time.sleep(10)
        raise Exception("Status code not 200")

    string_to_sign = (nonce + timestamp + r.headers.get('Content-Type'))
    string_to_sign = string_to_sign.encode('utf-8') + r.content
    signature_check = hmac.new(API_SECRET,
                               msg=string_to_sign,
                               digestmod=hashlib.sha256).hexdigest()
    if not r.headers.get('X-Server-Auth-Signature') == signature_check:
        print("Signatures do not match")
        raise Exception('Signatures do not match')

    return r


def get_balance():
    """Ask Bitstamp to return available account balances"""
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


def buy_btc(fiat_balance):
    """Make an instant order"""
    url_path = '/api/v2/buy/instant/btceur/'
    url_query = ''
    payload = {'amount': str(fiat_balance)}
    content_type = 'application/x-www-form-urlencoded'
    r = post(url_path=url_path,
             url_query=url_query,
             payload=payload,
             content_type=content_type)
    r_dict = r.json()
    return r_dict


def withdraw_btc(amount, address):
    """Withdraw Bitcoin to address in address.json"""
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
    url = 'https://www.bitstamp.net/api/bitcoin_withdrawal/'
    payload = {'key': api_key,
               'signature': signature,
               'nonce': nonce,
               'amount': amount,
               'address': address}
    r = requests.post(url, data=payload)
    r_dict = r.json()
    if not sys.argv[1] == "reuse":
        with open('addresses.json') as addresses_file:
            addresses = json.load(addresses_file)
        setadd.setadd(addresses.pop(0))
        with open('addresses.json', "w") as addresses_file:
            json.dump(addresses, addresses_file, indent=4)
    return r_dict


while __name__ == "__main__":
    try:
        balance = get_balance()
        fiat_balance = balance[f'{fiat.lower()}_available']
        fiat_balance = float(fiat_balance)

        btc_balance = balance['btc_available']
        btc_balance = float(btc_balance)

        current_timestamp = time.time()

        minutes, seconds = divmod(current_timestamp, 60)
        hours, minutes = divmod(minutes, 60)
        hours %= 24
        hours_s = f"{int(hours):02d}"
        minutes_s = f"{int(minutes):02d}"
        seconds_s = f"{int(seconds):02d}"
        timestr = f"{hours_s}:{minutes_s}:{seconds_s}"

        print(f"\n{timestr}\tUpdating...\n")
        print("Funds available:")
        print(f"\tBTC\t{btc_balance} BTC")
        print(f"\t{fiat}\t{fiat_balance} {fiat}\n")

        options = ["y", "n"]

        if fiat_balance > 25:
            choice = None
            while choice not in options:
                choice = input("Buy BTC with all available {fiat}? (y/n) ")
            if choice == "y":
                buy_btc(fiat_balance)
            choice = None
        if btc_balance > 0.002:
            choice = None
            with open("address.json") as address_file:
                address = json.load(address_file)
            amount = round(btc_balance - 0.0005, 8)
            while choice not in options:
                choice = input(f"Witdraw {amount} BTC to {address}? (y/n) ")
            if choice == "y":
                r_dict = withdraw_btc(amount, address)
                print(r_dict)
        choice = None

        time.sleep(5)
    except KeyboardInterrupt:
        print("\tShutting down...")
        break
    except Exception as e:
        print(e)
        continue
