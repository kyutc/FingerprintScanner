import urllib3
import json
import codecs
from typing import Union
from pathlib import Path


class API:
    key: str = None
    url: str = None
    crt: Path = None

    @classmethod
    def init(cls, key: str, url: str, crt: Path):
        cls.key = key
        cls.url = url
        cls.crt = crt

    @classmethod
    def request(cls, api: str, args: dict) -> dict:
        reader = codecs.getreader('utf-8')
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                   ca_certs=str(cls.crt))

        fields = {'api_key': cls.key}
        fields.update(args)

        response = http.request("POST",
                                cls.url + api,
                                fields=fields,
                                preload_content=False)

        result = json.load(reader(response))
        response.release_conn()
        return result

    @classmethod
    def enroll(cls, username: str, classification: str, template: str) -> Union[dict, bool]:
        return cls.request('enroll', {'username': username, 'classification': classification, 'template': template})

    @classmethod
    def get_user_templates(cls, username: str) -> Union[dict, bool]:
        return cls.request('get_user_templates', {'username': username})

    @classmethod
    def get_all_templates(cls) -> Union[dict]:
        return cls.request('get_all_templates', {})
