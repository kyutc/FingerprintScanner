import time
from ctypes import *
import configuration
import picamera

config = configuration.load()
arducam_vcm = CDLL(config['arducam']['lib'])


def get_camera():
    arducam_vcm.vcm_init()
    camera = picamera.PiCamera()
    camera.resolution = (config['arducam']['resolution']['x'], config['arducam']['resolution']['y'])
    camera.shutter_speed = config['arducam']['shutterspeed']
    set_focus(config['arducam']['focus'])
    return camera


def set_focus(focus):
    arducam_vcm.vcm_write(focus)
