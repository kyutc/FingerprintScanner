import picamera
import picamera.array
import cv2
import numpy
import os
import sys
import time
from pathlib import Path
import subprocess
from ctypes import *
import glob
import os
from typing import Union

from api import API
from nbis import NBIS
from camera_helper import CameraHelper
from util_helper import *


class FingerprintScanner:
    tmp_path: Path = None
    nfiq_quality_threshold: int = None
    bozorth3_threshold: int = None
    pcasys_confidence_threshold: float = None
    enrollment_candidates_target: int = None

    @classmethod
    def init(cls, tmp_path: Path, nfiq_quality_threshold: int, bozorth3_threshold: int,
             pcasys_confidence_threshold: float, enrollment_candidates_target: int) -> None:
        cls.tmp_path = tmp_path
        cls.nfiq_quality_threshold = nfiq_quality_threshold
        cls.bozorth3_threshold = bozorth3_threshold
        cls.pcasys_confidence_threshold = pcasys_confidence_threshold
        cls.enrollment_candidates_target = enrollment_candidates_target

    @classmethod
    def _discard(cls, prefix: str, i: int) -> None:
        files = glob.glob(str(cls.tmp_path / cls._fingername(prefix, i)))
        for file in files:
            os.remove(file)

    @classmethod
    def _fingername(cls, prefix: str, i: int) -> str:
        return prefix + 'finger%04d.png' % i

    @classmethod
    def get_template(cls, prefix: str, i: int) -> (int, str, float, int, str):
        while True:
            fingername = cls._fingername(prefix, i)
            CameraHelper.capture_gray_raw(cls.tmp_path / fingername)
            quality = NBIS.get_nfiq_quality(cls.tmp_path / fingername)
            print("Quality: %d" % quality)
            if quality > cls.nfiq_quality_threshold:
                print("Quality must be %d or better (lower), discarding." % cls.nfiq_quality_threshold)
                cls._discard(prefix, i)
                continue

            (classification, confidence) = NBIS.get_classification(cls.tmp_path / fingername)
            print("Classification: %s, confidence: %1.2f%%" % (classification, confidence * 100))
            if confidence < cls.pcasys_confidence_threshold:
                print("Confidence must be %1.2f%% or better, discarding." % cls.pcasys_confidence_threshold)
                cls._discard(prefix, i)
                continue

            NBIS.generate_mindtct_templates(cls.tmp_path / fingername, cls.tmp_path / fingername)

            bozorth3_score = NBIS.get_bozorth3_score(cls.tmp_path / (fingername + '.xyt'), cls.tmp_path / (fingername + '.xyt'))
            print("Self bozorth3 score: %d" % bozorth3_score)
            if bozorth3_score < 300:
                print("Bozorth3 self score must be 300 or better, discarding." % bozorth3_score)
                cls._discard(prefix, i)
                continue
            break
        return quality, classification, confidence, bozorth3_score, fingername

    @classmethod
    def enrollment(cls) -> None:
        username = ''
        while len(username) == 0:
            username = input("Username: ")
            if not API.check_username_length(username):
                username = ''

        bozorth3_matrix = [[0 for i in range(cls.enrollment_candidates_target)]
                           for j in range(cls.enrollment_candidates_target)]
        bozorth3_averages = [0.0 for i in range(cls.enrollment_candidates_target)]

        i = 0
        while i < cls.enrollment_candidates_target:
            (_, classification, confidence, _, _) = cls.get_template('enrollment', i)
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
                bozorth3_matrix[i][k] = NBIS.get_bozorth3_score(cls.tmp_path / (cls._fingername('enrollment', i) + '.xyt'),
                                                                cls.tmp_path / (cls._fingername('enrollment', k) + '.xyt'))
                bozorth3_matrix[k][i] = bozorth3_matrix[i][k]
                sum += bozorth3_matrix[i][k]
            bozorth3_averages[i] = sum / (cls.enrollment_candidates_target - 1)

        template = read_file(cls.tmp_path / (cls._fingername('enrollment',
                                                            bozorth3_averages.index(max(bozorth3_averages))) + '.xyt'))
        result = API.enroll(username, classification, template)
        print("Round-robin average bozorth3 scores: ")
        print(bozorth3_averages)
        print(result['message'])

    @classmethod
    def verification(cls) -> bool:
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
            write_file(cls.tmp_path / ('verification%04d.xyt' % i), template['template'])
            i += 1

        while True:
            i = -1
            (_, classification, _, _, fingername) = cls.get_template('verification', 0)
            for template in templates:
                i += 1
                if template['classification'] != classification:
                    continue
                bozorth3_score = NBIS.get_bozorth3_score(cls.tmp_path / (fingername + '.xyt'),
                                                         cls.tmp_path / ('verification%04d.xyt' % i))
                print("Score: %d" % bozorth3_score)

                if bozorth3_score >= cls.bozorth3_threshold:
                    print("Match found! %d" % bozorth3_score)
                    return True
            print("No match found!")
        return False

    @classmethod
    def identification(cls) -> Union[dict, bool]:
        templates = API.get_all_templates()['result']
        if len(templates) == 0:
            return False

        i = 0
        for template in templates:
            write_file(cls.tmp_path / ('identification%04d.xyt' % i), template['template'])
            i += 1

        while True:
            i = -1
            (_, classification, _, _, fingername) = cls.get_template('identification', 0)
            for template in templates:
                i += 1
                if template['classification'] != classification:
                    continue
                bozorth3_score = NBIS.get_bozorth3_score(cls.tmp_path / (fingername + '.xyt'),
                                                         cls.tmp_path / ('identification%04d.xyt' % i))
                print("Score: %d" % bozorth3_score)

                if bozorth3_score >= cls.bozorth3_threshold:
                    print("Match found! %d" % bozorth3_score)
                    print("User identified: %s" % template['name'])
                    return template
            print("No match found!")
        return False
