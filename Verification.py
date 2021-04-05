from api import *
import time
import picamera
from PIL import Image
import os
import subprocess

# Get config info from json file
with open('config.json') as f:
    data = json.load(f)

os.chdir(data['nbis']['bin'])  # Directory of NBIS software & where files are stored

# Prompt user for their username
username = input("Please enter your username")
i = 0
x = 0
z = 0

# Send API request to get templates of that user
templates = get_user_templates(username)  # Assuming this will return a list of templates
numTemplates = len(templates)

# Scan user's fingerprint continuously until a score meets the requires threshold.
while x == 0:
    print("Press finger to scanner to begin verification process")
    for i in range(11):
        if i == 11:
            print("Quality image was not found, please try again.")
            break
        time.sleep(1)
        camera.capture('finger.jpg')  ##Capture Image
        grey_img = Image.open('finger.jpg').convert('L')  ##Convert to greyscale
        grey_img.save('finger.jpg')  ##Save geyscale image over original

        result = subprocess.run(['./nfiq', 'finger.jpg'], stdout=subprocess.PIPE)  ##shell execute nfiq
        quality = result.stdout.decode()  ##Get output

        if quality > 3:
            continue
        else:
            print("Quality Image Accepted")
            x = 1

# Upon a match that meets the requirement, authenticate the user.
subprocess.run(['./mindtct', '-b', 'finger.jpg', 'finger'])  # Run mindtct on image to get xyt file
for template in templates:
    result = subprocess.run(['./bozorth3', '-b', 'finger.xyt', template],
                            stdout=subprocess.PIPE)  # Shell execute bozorth3
    score = result.stdout.decode()  # Get Score
    if score <= 40:        # Scores greater than 40 are considered a good match
        z += 1
        continue
    else:
        print("You have been authenticated as " + username)
        break
if z == numTemplates:
    print("You are not who you say you are.")
