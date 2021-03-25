import urllib3
import json
import codecs

import configuration

config = configuration.load()


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
