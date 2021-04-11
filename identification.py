from pathlib import Path
from typing import Union

import api
from nbis import NBIS
import configuration
from camera_helper import CameraHelper
import enrollment


def write_out(file: str, content: str) -> None:
    file_h = Path.open(Path(file), 'w')
    file_h.write(content)
    file_h.close()


def identification(config: dict) -> Union[dict, bool]:
    tmp_path = Path(config['tmp'])

    templates = api.get_all_templates()['result']
    if len(templates) == 0:
        return False

    i = 0
    for template in templates:
        write_out(tmp_path / ('identification%04d.xyt' % i), template['template'])
        i += 1

    while True:
        i = -1
        (_, classification, _, _, fingername) = enrollment.get_template('identification', 0, config)
        for template in templates:
            i += 1
            if template['classification'] != classification:
                continue
            bozorth3_score = NBIS.get_bozorth3_score(tmp_path / (fingername + '.xyt'), tmp_path / ('identification%04d.xyt' % i))
            print("Score: %d" % bozorth3_score)

            if bozorth3_score >= config['nbis']['bozorth3_threshold']:
                print("Match found! %d" % bozorth3_score)
                print("User identified: %s" % template['name'])
                return template
        print("No match found!")
    return False


if __name__ == '__main__':
    config = configuration.load()
    CameraHelper.init(config)
    NBIS.init(Path(config['nbis']['bin']))
    identification(config)
