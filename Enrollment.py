import picamera
import time
import subprocess
import os
import operator
from PIL import Image
from api import *
import json

#Get config info from json file
with open('config.json') as f:
    data = json.load(f)

os.chdir(data['nbis']['bin']) #Directory of NBIS software & where files are stored

quality_dict = {}  #Holds greyscale fingerprint images with thier respective quality values
imgs = 5  #Number of images needed for enrollment
imgs2 = 5 #Number of images needed for enrollment. Needs to have same value as imgs
camera = picamera.PiCamera()  #Camera variable
username = ""  #Username variable

##Get username and ensure correct length
while username == "":
    username = input("Please enter your desired username: ")
    if not check_username_length(username):
        print("Please make sure your username is greater than 3 characters and less than 33 characters.")
        username = ""

##Get fingerprint images, saved locally under bin
while imgs != 0:
    print('Please place finger on scanner, the image will be taken in 5 seconds.')
    time.sleep(1)
    camera.capture('finger' + str(imgs) + '.jpg') ##Capture Image
    grey_img = Image.open('finger' + str(imgs) + '.jpg').convert('L') ##Convert to greyscale
    grey_img.save('finger' + str(imgs) + '.jpg')  ##Save geyscale image over original
    print('Image captured')
    print(str(imgs - 1) + ' more scan(s) required\n')
    imgs = imgs - 1

##Get image quality and store in dicionary
while imgs2 !=0:
    result = subprocess.run(['./nfiq', 'finger' + str(imgs2) + '.jpg'], stdout=subprocess.PIPE)  ##shell execute nfiq
    quality = result.stdout.decode()  ##Get output
    quality_dict['finger' + str(imgs2) + '.jpg'] = int(quality)  ##Key: Fingerprint image (string), Value: quality (int)
    imgs2 = imgs2 - 1

##Sort dictionary in descending order
sorted_d = dict(sorted(quality_dict.items(), key=operator.itemgetter(1), reverse=True))

##Get best quality image to b used for enrollment
enrollment_image = list(sorted_d.keys())[0]

##Need code here to run pcasys on enrollment_image to get classification to be stored in database


##Get xyt file from image to be used as template. Will always be titled 'finger'.
result = subprocess.run(['./mindtct', '-b', enrollment_image, 'finger'])

##This will be the file saved to the datbase, along with the username and classification
enrollment_template = 'finger.xyt'

##Remove unnecessary files from bin
os.remove("finger1.jpg")
os.remove("finger2.jpg")
os.remove("finger3.jpg")
os.remove("finger4.jpg")
os.remove("finger5.jpg")
