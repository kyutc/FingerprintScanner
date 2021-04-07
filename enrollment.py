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

config = configuration.load()
arducam_vcm = CDLL(config['arducam']['lib'])
tmp = Path(config['tmp'])

try:
    os.mkdir(config['tmp'])  # Dir where we are storing temporary files
except:
    print("Directory exists")


camera = camera_helper.get_camera()


def enrollment():
    nbis_path = Path(config['nbis']['bin'])
    candidates = []

    ### NFIQ
    i = 0
    while len(candidates) < 10:
        while False:
            username = input("Username: ")
            if api.check_username_length(username): break
            print("Username must be within 4-32 characters.")

        raw = picamera.array.PiRGBArray(camera)
        camera.capture(raw, format="bgr", use_video_port=True)
        image = raw.array
        image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        i += 1
        fingername = 'finger' + str(i) + '.png'
        cv2.imwrite(str(tmp / fingername), image_gray)

        quality = int(subprocess.run([str(nbis_path / 'nfiq'), str(tmp / fingername)], stdout=subprocess.PIPE).stdout.decode())
        print("Quality: " + str(quality) + " count: " + str(len(candidates)))
        if (quality <= 3):
            candidates.insert(i, {'name': fingername, 'quality': quality})

    print(candidates)

    ### MINDTCT
    try:
        os.chdir(config['tmp'])
    except:
        print("Failed to change directory")
        sys.exit(1)

    for candidate in candidates:
        subprocess.run([str(nbis_path / 'mindtct'), candidate['name'], str(tmp / candidate['name'])], stdout=subprocess.PIPE)
        print("MINDTCT has ran, check output directory!")

    ## BOZORTH3




enrollment()
