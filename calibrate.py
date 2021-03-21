import sys
import cv2
import numpy as py
import os
import time
import json
import jsonmerge
from ctypes import *

with open("config.json" if os.path.exists("config.json") else "config.default.json", "r") as config_file, \
        open("config.default.json", "r") as default_config_file:
    default_config = json.load(default_config_file)
    config = json.load(config_file)
    config = jsonmerge.merge(default_config, config)

arducam_vcm = CDLL(config['arducam']['lib'])

try:
    import picamera
    from picamera.array import PiRGBArray
except:
    sys.exit(0)

# Setup the camera using the currently save or default configuration
arducam_vcm.vcm_init()
camera = picamera.PiCamera()
camera.resolution = (config['arducam']['resolution']['x'], config['arducam']['resolution']['y'])
time.sleep(0.1)
arducam_vcm.vcm_write(config['arducam']['focus'])
time.sleep(0.1)
camera.shutter_speed = config['arducam']['shutterspeed']
time.sleep(0.1)


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
        time.sleep(0.1)
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
        time.sleep(0.1)
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
        arducam_vcm.vcm_write(config['arducam']['focus'])
        time.sleep(0.1)
    camera.stop_preview()


def calibrate_transform():
    print("NOT IMPLEMENTED")


def save_config():
    cmd = ""
    while cmd.lower() != "n" and cmd.lower() != "y":
        cmd = input("Write to config.json? [y/N]: ")
    if cmd.lower()[0] == "y":
        with open("config.json.tmp", "w") as config_file:
            try:
                json.dump(config, config_file)
            except:
                os.remove("config.json.tmp")
                sys.exit(1)
        os.replace("config.json.tmp", "config.json")  # json.dump will garble files on error


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
