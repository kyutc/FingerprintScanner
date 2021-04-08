import picamera
import picamera.array
import cv2
# import python image library for grayscaling? or use OpenCV?
import numpy
import os
import sys
import time
import configuration
import api
from pathlib import Path
import subprocess
from ctypes import *
import camera_helper
import nbis
import tempfile
import glob

config = configuration.load()
tmp_path = Path(config['tmp'])
camera = camera_helper.get_camera()

try:
    tmp_path.mkdir(exist_ok=True)
except:
    sys.exit(1)


def _discard(i):
    files = glob.glob(str(tmp_path / _fingername(i)))
    for file in files:
        os.remove(file)


def _fingername(i):
    return 'finger%04d.png' % i


def enrollment():
    username = ''
    while len(username) == 0:
        username = input("Username: ")
        if not api.check_username_length(username):
            username = ''

    bozorth3_matrix = [[0 for i in range(config['nbis']['enrollment_candidates_target'])]
                       for j in range(config['nbis']['enrollment_candidates_target'])]

    i = 0
    bozorth3_averages = [0 for i in range(config['nbis']['enrollment_candidates_target'])]
    while i < (config['nbis']['enrollment_candidates_target']):
        fingername = _fingername(i)
        camera_helper.capture_gray_raw(camera, tmp_path / fingername)
        quality = nbis.get_nfiq_quality(tmp_path / fingername)
        print("Quality: %d" % quality)
        if quality > config['nbis']['nfiq_quality_threshold']:
            print("Quality must be %d or better (lower), discarding." % config['nbis']['nfiq_quality_threshold'])
            _discard(i)
            continue

        (classification, confidence) = nbis.get_classification(tmp_path / fingername)
        print("Classification: %s, confidence: %1.2f%%" % (classification, confidence * 100))
        if confidence < config['nbis']['pcasys_confidence_threshold']:
            print("Confidence must be %1.2f%% or better, discarding." % config['nbis']['pcasys_confidence_threshold'])
            _discard(i)
            continue

        nbis.generate_mindtct_templates(tmp_path / fingername, tmp_path / fingername)

        bozorth3_score = nbis.get_bozorth3_score(tmp_path / (fingername + '.xyt'), tmp_path / (fingername + '.xyt'))
        print("Self bozorth3 score: %d" % bozorth3_score)
        if bozorth3_score < 300:
            print("Bozorth3 self score must be 300 or better, discarding." % bozorth3_score)
            _discard(i)
            continue

        # Choosing not to include self-bozorth3 since minimum self is checked and it'll affect
        # the real-world average score
        bozorth3_matrix[i][i] = 0
        i += 1

    for i in range(len(bozorth3_matrix)):
        sum = 0
        for k in range(len(bozorth3_matrix[i])):
            if i == k:
                continue
            if bozorth3_matrix[i][k] != 0 or bozorth3_matrix[k][i] != 0:
                sum += bozorth3_matrix[i][k]
                continue
            # Per the documentation, comparing A to B and B to A is not worthwhile
            bozorth3_matrix[i][k] = nbis.get_bozorth3_score(tmp_path / (_fingername(i) + '.xyt'),
                                                            tmp_path / (_fingername(k) + '.xyt'))
            bozorth3_matrix[k][i] = bozorth3_matrix[i][k]
            sum += bozorth3_matrix[i][k]
        bozorth3_averages[i] = sum / (config['nbis']['enrollment_candidates_target'] - 1)

    template_file_h = Path.open(tmp_path / (_fingername(bozorth3_averages.index(max(bozorth3_averages))) + '.xyt'), 'r')
    template = template_file_h.read()
    template_file_h.close()
    result = api.enroll(username, classification, template)
    print(result['message'])


enrollment()
