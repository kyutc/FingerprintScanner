import picamera
import cv2
# import python image library for grayscaling? or use OpenCV?
import numpy
import os
import time
import configuration
from pathlib import Path

config = configuration.load()

os.mkdir(config['tmp']) #Dir where we are storing temporary files

