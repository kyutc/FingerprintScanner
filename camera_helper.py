from ctypes import *
import picamera
import picamera.array
import cv2
from pathlib import Path


class CameraHelper(object):
    camera: picamera.PiCamera = None
    config: {} = None
    arducam_vcm: CDLL = None

    @classmethod
    def init(cls, config: {}) -> None:
        if cls.camera is not None:
            return
        cls.config = config
        cls.arducam_vcm = CDLL(config['arducam']['lib'])
        cls.arducam_vcm.vcm_init()
        cls.camera = picamera.PiCamera()
        cls.camera.resolution = (config['arducam']['resolution']['x'], config['arducam']['resolution']['y'])
        cls.camera.shutter_speed = config['arducam']['shutterspeed']
        cls.set_focus(config['arducam']['focus'])
        cls.camera.start_preview()

    @classmethod
    def capture_gray_raw(cls, path: Path) -> None:
        raw = picamera.array.PiRGBArray(cls.camera)
        cls.camera.capture(raw, format="rgb", use_video_port=True)
        image = raw.array
        image = image[cls.config['crop']['y'][0]:cls.config['crop']['y'][1], cls.config['crop']['x'][0]:cls.config['crop']['x'][1]]
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        cv2.imwrite(str(path), image)

    @classmethod
    def set_focus(cls, focus: int) -> None:
        cls.arducam_vcm.vcm_write(focus)
