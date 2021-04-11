from pathlib import Path
import sys
import atexit
import shutil

from camera_helper import CameraHelper
from api import API
from nbis import NBIS
from fingerprint_scanner import FingerprintScanner
from fingerprint_status import FingerprintStatus
import configuration
from util_helper import *

def main(config):
    try:
        Path.mkdir(Path(config['tmp']), 0o700, True, True)
    except:
        sys.exit(1)
    atexit.register(_unmain, config)

    CameraHelper.init(config)
    API.init(config['api']['key'], config['api']['url'], Path(config['api']['crt']))
    NBIS.init(Path(config['nbis']['bin']))
    FingerprintScanner.init(FingerprintStatus(), Path(config['tmp']), config['nbis']['nfiq_quality_threshold'],
                            config['nbis']['bozorth3_threshold'], config['nbis']['pcasys_confidence_threshold'],
                            config['nbis']['enrollment_candidates_target'])

    while True:
        print("Options:")
        print("[E]nroll")
        print("[V]erify")
        print("[I]dentify")
        print("[Q]uit")
        cmd = input_forever("Option: ", ['e', 'enroll', 'v', 'verify', 'i', 'identify', 'q', 'quit'])

        if cmd in ['e', 'enroll']:
            try:
                (classification, template) = FingerprintScanner.enrollment()
                while True:
                    username = input("Username: ")
                    response = API.enroll(username, classification, template)
                    if response['error']:  # TODO: Currently assumes any error is just a username error
                        print(response['error_message'])
                        continue
                    break
            except KeyboardInterrupt:
                continue
        if cmd in ['v', 'verify']:
            try:
                while True:
                    username = input("Username: ")
                    response = API.get_user_templates(username)
                    if response['error']:
                        print(response['error_message'])
                        continue
                    templates = response['result']
                    verified = False
                    while not verified:
                        verified = FingerprintScanner.verification(templates)
                    break
            except KeyboardInterrupt:
                continue
        if cmd in ['i', 'identify']:
            try:
                templates = API.get_all_templates()['result']
                while True:
                    identified = FingerprintScanner.identification(templates)
                    if isinstance(identified, dict):
                        break
            except KeyboardInterrupt:
                continue
        if cmd in ['q', 'quit']:
            break

    _unmain(config)


def _unmain(config):
    try:
        shutil.rmtree(config['tmp'], True)
    except:
        sys.exit(1)


if __name__ == '__main__':
    config = configuration.load()
    try:
        main(config)
    except:
        _unmain(config)
        raise
