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

from nbis import NBIS
from camera_helper import CameraHelper
from util_helper import *
from fingerprint_status_interface import FingerprintStatusInterface


class FingerprintScanner:
    status: FingerprintStatusInterface = None
    tmp_path: Path = None
    nfiq_quality_threshold: int = None
    bozorth3_threshold: int = None
    pcasys_confidence_threshold: float = None
    enrollment_candidates_target: int = None

    @classmethod
    def init(cls, status: FingerprintStatusInterface, tmp_path: Path, nfiq_quality_threshold: int,
             bozorth3_threshold: int, pcasys_confidence_threshold: float, enrollment_candidates_target: int) -> None:
        cls.status = status
        cls.tmp_path = tmp_path
        cls.nfiq_quality_threshold = nfiq_quality_threshold
        cls.bozorth3_threshold = bozorth3_threshold
        cls.pcasys_confidence_threshold = pcasys_confidence_threshold
        cls.enrollment_candidates_target = enrollment_candidates_target

    @classmethod
    def _discard(cls, prefix: str, i: int) -> None:
        files = glob.glob(str(cls.tmp_path / cls._fingername(prefix, i, True)))
        for file in files:
            os.remove(file)

    @classmethod
    def _fingername(cls, prefix: str, i: int, glob_: bool = False) -> str:
        if glob_:
            postfix = '*'
        else:
            postfix = '.png'
        return prefix + ('finger%04d' % i) + postfix

    @classmethod
    def get_template(cls, prefix: str, i: int) -> (int, str, float, int, str):
        while True:
            fingername = cls._fingername(prefix, i)
            CameraHelper.capture_gray_raw(cls.tmp_path / fingername)
            quality = NBIS.get_nfiq_quality(cls.tmp_path / fingername)
            if quality > cls.nfiq_quality_threshold:
                cls.status.on_quality(False, cls.nfiq_quality_threshold, quality)
                cls._discard(prefix, i)
                continue
            cls.status.on_quality(True, cls.nfiq_quality_threshold, quality)

            (classification, confidence) = NBIS.get_classification(cls.tmp_path / fingername)
            if confidence < cls.pcasys_confidence_threshold:
                cls.status.on_classification(False, classification, cls.pcasys_confidence_threshold, confidence)
                cls._discard(prefix, i)
                continue
            cls.status.on_classification(True, classification, cls.pcasys_confidence_threshold, confidence)

            NBIS.generate_mindtct_templates(cls.tmp_path / fingername, cls.tmp_path / fingername)

            bozorth3_score = NBIS.get_bozorth3_score(cls.tmp_path / (fingername + '.xyt'), cls.tmp_path / (fingername + '.xyt'))
            if bozorth3_score < 300:
                cls.status.on_scoring_self(False, 300, bozorth3_score)
                cls._discard(prefix, i)
                continue
            cls.status.on_scoring_self(True, 300, bozorth3_score)
            break
        return quality, classification, confidence, bozorth3_score, fingername

    @classmethod
    def enrollment(cls) -> (str, str):
        bozorth3_matrix = [[0 for i in range(cls.enrollment_candidates_target)]
                           for j in range(cls.enrollment_candidates_target)]
        bozorth3_averages = [0.0 for i in range(cls.enrollment_candidates_target)]

        i = 0
        while i < cls.enrollment_candidates_target:
            (_, classification, confidence, _, _) = cls.get_template('enrollment', i)
            cls.status.on_enrollment_update(i+1, cls.enrollment_candidates_target)
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
        cls.status.on_enrollment_result(True, bozorth3_averages)
        return classification, template

    @classmethod
    def verification(cls, templates: dict) -> bool:
        i = 0
        for template in templates:
            write_file(cls.tmp_path / ('verification%04d.xyt' % i), template['template'])
            i += 1

        i = -1
        (_, classification, _, _, fingername) = cls.get_template('verification', 0)
        for template in templates:
            i += 1
            if template['classification'] != classification:
                continue
            bozorth3_score = NBIS.get_bozorth3_score(cls.tmp_path / (fingername + '.xyt'),
                                                     cls.tmp_path / ('verification%04d.xyt' % i))
            if bozorth3_score >= cls.bozorth3_threshold:
                cls.status.on_verification_result(True)
                return True
        cls.status.on_verification_result(False)
        return False

    @classmethod
    def identification(cls, templates: dict) -> Union[dict, bool]:
        i = 0
        for template in templates:
            write_file(cls.tmp_path / ('identification%04d.xyt' % i), template['template'])
            i += 1

        i = -1
        (_, classification, _, _, fingername) = cls.get_template('identification', 0)
        for template in templates:
            i += 1
            if template['classification'] != classification:
                continue
            bozorth3_score = NBIS.get_bozorth3_score(cls.tmp_path / (fingername + '.xyt'),
                                                     cls.tmp_path / ('identification%04d.xyt' % i))
            if bozorth3_score >= cls.bozorth3_threshold:
                cls.status.on_identification_result(True, template['name'])
                return template
        cls.status.on_identification_result(False, None)
        return False
