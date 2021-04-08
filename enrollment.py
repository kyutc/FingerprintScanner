import picamera
import picamera.array
import cv2
# import python image library for grayscaling? or use OpenCV?
import numpy
import os
import time
import configuration
import api
from pathlib import Path
import subprocess
from ctypes import *
import camera_helper
import nbis
import tempfile

config = configuration.load()
tmp_path = Path(config['tmp'])
images_path = tmp_path / 'images'
templates_path = tmp_path / 'templates'
camera = camera_helper.get_camera()

try:
    tmp_path.mkdir(parents=True, exist_ok=True)
    images_path.mkdir(parents=True, exist_ok=True)
    templates_path.mkdir(parents=True, exist_ok=True)
except: pass


def enrollment():
    i = 0
    while True:
        start = time.time()
        i += 1
        fingername = 'finger%04d.png' % i
        camera_helper.capture_gray_raw(camera, images_path / fingername)
        quality = nbis.get_nfiq_quality(images_path / fingername)
        print("Quality: %d" % quality)
        if quality > config['nbis']['nfiq_quality_threshold']:
            continue
        (classification, confidence) = nbis.get_classification(images_path / fingername)
        print("Classification: %s, confidence: %f" % (classification, confidence))
        nbis.generate_mindtct_templates(images_path / fingername, templates_path / fingername)
        bozorth3_score = nbis.get_bozorth3_score(templates_path / (fingername + '.xyt'), templates_path / (fingername + '.xyt'))
        print("Self bozorth3 score: %d" % bozorth3_score)
        print("Took %f seconds" % (time.time() - start))


enrollment()
