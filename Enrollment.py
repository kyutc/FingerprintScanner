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

config = configuration.load()
arducam_vcm = CDLL(config['arducam']['lib'])
tmp = Path(config['tmp'])

try:
    os.mkdir(config['tmp'])  # Dir where we are storing temporary files
except:
    print("Directory exists")


arducam_vcm.vcm_init()
camera = picamera.PiCamera()
time.sleep(0.5)
camera.resolution = (config['arducam']['resolution']['x'], config['arducam']['resolution']['y'])
time.sleep(0.5)
arducam_vcm.vcm_write(config['arducam']['focus'])
time.sleep(0.5)
camera.shutter_speed = config['arducam']['shutterspeed']
time.sleep(0.5)


def enrollment():
    nbis_path = Path(config['nbis']['bin'])
    candidates = []

    # Obtain higher quality images
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


enrollment()
