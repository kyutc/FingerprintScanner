from ctypes import *
import configuration
import picamera
import cv2
from pathlib import Path

config = configuration.load()
arducam_vcm = CDLL(config['arducam']['lib'])


def get_camera():
    arducam_vcm.vcm_init()
    camera = picamera.PiCamera()
    camera.resolution = (config['arducam']['resolution']['x'], config['arducam']['resolution']['y'])
    camera.shutter_speed = config['arducam']['shutterspeed']
    set_focus(config['arducam']['focus'])
    return camera


def capture_gray_raw(camera, path):
    raw = picamera.array.PiRGBArray(camera)
    camera.capture(raw, format="bgr", use_video_port=True)
    image = raw.array
    image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    cv2.imwrite(str(path), image_gray)


def set_focus(focus):
    arducam_vcm.vcm_write(focus)
