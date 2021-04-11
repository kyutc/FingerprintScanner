import os
import tempfile
from pathlib import Path

from api import API
from nbis import NBIS
import configuration
from camera_helper import CameraHelper
import enrollment
from util_helper import *


def verification(config: dict) -> bool:
    tmp_path = Path(config['tmp'])
    username = ''
    while username == '':
        username = input("Username: ")
        if not API.check_username_length(username):
            username = ''
    templates = API.get_user_templates(username)['result']
    if len(templates) == 0:
        return False

    i = 0
    for template in templates:
        write_file(tmp_path / ('verification%04d.xyt' % i), template['template'])
        i += 1

    while True:
        i = -1
        (_, classification, _, _, fingername) = enrollment.get_template('verification', 0, config)
        for template in templates:
            i += 1
            if template['classification'] != classification:
                continue
            bozorth3_score = NBIS.get_bozorth3_score(tmp_path / (fingername + '.xyt'), tmp_path / ('verification%04d.xyt' % i))
            print("Score: %d" % bozorth3_score)

            if bozorth3_score >= config['nbis']['bozorth3_threshold']:
                print("Match found! %d" % bozorth3_score)
                return True
        print("No match found!")
    return False


if __name__ == '__main__':
    config = configuration.load()
    CameraHelper.init(config)
    API.init(config['api']['key'], config['api']['url'], Path(config['api']['crt']))
    NBIS.init(Path(config['nbis']['bin']))
    verification(config)
