import sys
import cv2
import numpy as py
import time
from ctypes import *

import configuration
from camera_helper import CameraHelper

config = configuration.load()
CameraHelper.init(config)
camera = CameraHelper.camera


def calibrate_resolution():
    camera.start_preview()
    cmd = ""
    while not isinstance(cmd, str) or cmd.lower() != "done":
        print("Calibrate Resolution: %dx%d" % (
            config['arducam']['resolution']['x'], config['arducam']['resolution']['y']))
        print("Options: Positive or Negative number to add/subtract resolution, or DONE to end.")
        cmd = input("Command: ")
        try:
            cmd = int(cmd)
        except:
            continue
        # 1944 is the max Y resolution, but we're doing a square
        config['arducam']['resolution']['x'] = int(py.clip(config['arducam']['resolution']['x'] + cmd, 100, 1944))
        config['arducam']['resolution']['y'] = config['arducam']['resolution']['x']
        camera.resolution = (config['arducam']['resolution']['x'], config['arducam']['resolution']['y'])
        time.sleep(0.5)
    camera.stop_preview()


def calibrate_shutterspeed():
    camera.start_preview()
    cmd = ""
    while not isinstance(cmd, str) or cmd.lower() != "done":
        print("Calibrate Shutter Speed: %d" % (config['arducam']['shutterspeed']))
        print("Options: Positive or Negative number to add/subtract shutter speed, or DONE to end.")
        cmd = input("Command: ")
        try:
            cmd = int(cmd)
        except:
            continue
        # TODO: Confirm range
        config['arducam']['shutterspeed'] = int(py.clip(config['arducam']['shutterspeed'] + cmd, 1000, 200000))
        camera.shutter_speed = config['arducam']['shutterspeed']
        time.sleep(0.5)
    camera.stop_preview()


def calibrate_focus():
    camera.start_preview()
    cmd = ""
    while not isinstance(cmd, str) or cmd.lower() != "done":
        print("Calibrate Focus: %d" % (config['arducam']['focus']))
        print("Options: Positive or Negative number to add/subtract focus, or DONE to end.")
        cmd = input("Command: ")
        try:
            cmd = int(cmd)
        except:
            continue
        config['arducam']['focus'] = int(py.clip(config['arducam']['focus'] + cmd, 0, 1023))  # TypeError if not cast
        CameraHelper.set_focus(config['arducam']['focus'])
        time.sleep(0.5)
    camera.stop_preview()


def calibrate_transform():
    print("NOT IMPLEMENTED")


def save_config():
    cmd = ""
    while cmd.lower() != "n" and cmd.lower() != "y":
        cmd = input("Write to config.json? [y/N]: ")
    if cmd.lower()[0] == "y":
        configuration.save(config)


while True:
    print("\nOptions:")
    print("[0] Calibrate everything")
    print("[1] Calibrate resolution")
    print("[2] Calibrate shutter speed")
    print("[3] Calibrate focus")
    print("[4] Calibrate transform (NOT IMPLEMENTED)")
    print("[8] Save configuration")
    print("[9] Exit")

    try:
        cmd = int(input("Option: "))
    except:
        continue
    # switch statements are coming in Python 3.10...
    if cmd == 0 or cmd == 1:
        calibrate_resolution()
    if cmd == 0 or cmd == 2:
        calibrate_shutterspeed()
    if cmd == 0 or cmd == 3:
        calibrate_focus()
    if cmd == 0 or cmd == 4:
        calibrate_transform()
    if cmd == 8:
        save_config()
    if cmd == 9:
        sys.exit(0)
