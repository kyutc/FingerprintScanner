import urllib3
import json
import codecs

import configuration

config = configuration.load()
valid_classifications = ['l', 'r', 'a', 't', 'w', 's']


def request(api, args):
    reader = codecs.getreader('utf-8')
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=config['api']['crt'])

    fields = {'api_key': config['api']['key']}
    fields.update(args)

    response = http.request("POST",
                            config['api']['url'] + api,
                            fields=fields,
                            preload_content=False)

    result = json.load(reader(response))
    response.release_conn()
    return result


def check_username_length(username):
    return (len(username) >= 4) and (len(username) <= 32)


def enroll(username, classification, template):
    if not check_username_length(username):
        return False
    if classification not in valid_classifications:
        return False

    return request('enroll', {'username': username, 'classification': classification, 'template': template})


def get_user_templates(username):
    if not check_username_length(username):
        return False

    return request('get_user_templates', {'username': username})
