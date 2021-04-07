import configuration
from pathlib import Path
import subprocess

config = configuration.load()

nbis_path = Path(config['nbis']['bin'])
tmp_path = Path(config['tmp'])


def get_nfiq_quality(image_file):
    return int(subprocess.run([str(nbis_path / 'nfiq'), str(image_file)], stdout=subprocess.PIPE,
                              cwd=tmp_path).stdout.decode())
