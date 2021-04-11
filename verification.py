import os
import tempfile
from pathlib import Path

import api
from nbis import NBIS
import configuration
from camera_helper import CameraHelper
import enrollment


def write_out(file: str, content: str) -> None:
    file_h = Path.open(Path(file), 'w')
    file_h.write(content)
    file_h.close()


def verification(config: dict) -> bool:
    tmp_path = Path(config['tmp'])
    username = ''
    while username == '':
        username = input("Username: ")
        if not api.check_username_length(username):
            username = ''
    templates = api.get_user_templates(username)['result']
    if len(templates) == 0:
        return False

    i = 0
    for template in templates:
        write_out(tmp_path / ('verification%04d.xyt' % i), template['template'])
        i += 1

    while True:
        i = 0
        (_, classification, _, _, fingername) = enrollment.get_template('verification', 0, config)
        for template in templates:
            if template['classification'] != classification:
                continue
            bozorth3_score = NBIS.get_bozorth3_score(tmp_path / (fingername + '.xyt'), tmp_path / ('verification%04d.xyt' % i))
            print("Score: %d" % bozorth3_score)

            if bozorth3_score >= config['nbis']['bozorth3_threshold']:
                print("Match found! %d" % bozorth3_score)
                return True
            i += 1
        print("No match found!")
    return False


if __name__ == '__main__':
    config = configuration.load()
    CameraHelper.init(config)
    NBIS.init(Path(config['nbis']['bin']))
    verification(config)
