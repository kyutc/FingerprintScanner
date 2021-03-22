import picamera 
import time
import subprocess
import os
import operator
from PIL import Image

os.chdir('/media/pi/usb/Rel_5.0.0/bin') #Directory of NBIS software & where files are stored

quality_dict = {}  ##Holds greyscale fingerprint images with thier respective quality values
imgs = 5  ##Number of images needed for enrollment
imgs2 = 5 ##Number of images needed for enrollment. Needs to have same value as imgs
camera = picamera.PiCamera()  ##Camera variable

##Get fingerprint images, saved locally under Rel_5.0.0/bin
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
sorted_d = dict( sorted(quality_dict.items(), key=operator.itemgetter(1),reverse=True))

##Get best quality image to b used for enrollment
enrollment_image = list(sorted_d.keys())[0]

##Get xyt file from image to be used as template. Will always be titled 'finger'.
result = subprocess.run(['./mindtct', '-b', enrollment_image, 'finger'])

##This will be the file saved to the datbase
enrollment_template = 'finger.xyt'
