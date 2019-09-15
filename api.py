import requests
import json

def is_online(b):
    url = "https://tapi.telstra.com/v2/messages/sms/heathcheck"

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': "Bearer {}".format(b),
        'cache-control': "no-cache",
        }

    x = requests.request("GET", url, headers=headers)
    return x.json()["status"] == "up"

def get_status(b, msg_id):
    url = "https://tapi.telstra.com/v2/messages/sms/{}/status".format(msg_id)

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': "Bearer {}".format(b),
        'cache-control': "no-cache",
        }

    return requests.request("GET", url, headers=headers)

def get_bearer(key, secret):
    url = "https://tapi.telstra.com/v2/oauth/token"

    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
        }

    body = {
        'grant_type': "client_credentials",
        'client_id': key,
        'client_secret': secret
    } 

    return requests.request("POST", url, data=body, headers=headers)

def get_messages(b):
    url = "https://tapi.telstra.com/v2/messages/sms"

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': "Bearer {}".format(b),
        'cache-control': "no-cache",
        }

    return requests.request("GET", url, headers=headers)

def get_number(b):
    url = "https://tapi.telstra.com/v2/messages/provisioning/subscriptions"
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': "Bearer {}".format(b),
        'cache-control': "no-cache",
        }

    return requests.request("GET", url, headers=headers)

def new_number(b):
    url = "https://tapi.telstra.com/v2/messages/provisioning/subscriptions"

    payload = ""
    headers = {
        'accept': "application/json",
        'content-type': "application/x-www-form-urlencoded",
        'authorization': "Bearer {}".format(b),
        'cache-control': "no-cache"
        }

    return requests.request("POST", url, data=payload, headers=headers)

def send_message(b, dest, msg, validity=5, wait=0):
    url = "https://tapi.telstra.com/v2/messages/sms"

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': "Bearer {}".format(b),
        'cache-control': "no-cache",
        }

    body = {
        'to': dest,
        'body': msg,
        'validity': validity
    }
    
    if wait > 0:
        body['scheduledDelivery'] = wait
    payload = json.dumps(body)

    return requests.request("POST", url, data=payload, headers=headers)

if __name__ == "__main__":
    import argparse
    import readline
    import code

    parser = argparse.ArgumentParser(description="Interactive console to interface with the Telstra SMS API.")
    parser.add_argument("key", help="client key")
    parser.add_argument("secret", help="client secret")
    args = parser.parse_args()

    b = get_bearer(args.key, args.secret).json()['access_token']
    num_info = get_number(b).json()
    number = num_info['destinationAddress']

    print("{} expiring in {} day(s)".format(number, num_info['activeDays']))
    print("bearer stored in `b` variable")
    code.InteractiveConsole({**globals(), **locals()}).interact()