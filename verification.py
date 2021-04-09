import os
import tempfile
from pathlib import Path

import api
import nbis
import configuration
from camera_helper import CameraHelper
import enrollment


def write_out(file, content):
    file_h = Path.open(Path(file), 'w')
    file_h.write(content)
    file_h.close()


def verification(config):
    tmp_path = Path(config['tmp'])
    username = ''
    while username == '':
        username = input("Username: ")
        if not api.check_username_length(username):
            username = ''
    templates = api.get_user_templates(username)['result']
    if len(templates) == 0:
        return False

    while True:
        (_, classification, _, _, fingername) = enrollment.get_template('verification', 0, config)
        for template in templates:
            if template['classification'] != classification:
                continue
            write_out(tmp_path / 'verification.xyt', template['template'])
            bozorth3_score = nbis.get_bozorth3_score(tmp_path / (fingername + '.xyt'), tmp_path / 'verification.xyt')
            print("Score: %d" % bozorth3_score)

            if bozorth3_score >= config['nbis']['bozorth3_threshold']:
                print("Match found! %d" % bozorth3_score)
                return True
        print("No match found!")
    return False


if __name__ == '__main__':
    config = configuration.load()
    CameraHelper.init(config)
    verification(config)
