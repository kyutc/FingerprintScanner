from pathlib import Path

from camera_helper import CameraHelper
from api import API
from nbis import NBIS
from fingerprint_scanner import FingerprintScanner
import configuration


def main():
    config = configuration.load()
    CameraHelper.init(config)
    API.init(config['api']['key'], config['api']['url'], Path(config['api']['crt']))
    NBIS.init(Path(config['nbis']['bin']))
    FingerprintScanner.init(Path(config['tmp']))
    FingerprintScanner.enrollment(config)
    FingerprintScanner.verification(config)
    FingerprintScanner.identification(config)


if __name__ == '__main__':
    main()
