#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# DEVELOPED BY Di0nJ@ck - October 2019 - v3.0
__author__      = 'Di0nj@ck'
__version__     = 'v3.0'
__last_update__ = 'October 2019'

from fractions import Fraction
import argparse
import pathlib
import os,sys,subprocess,time

try:
    from PIL import Image #PYTHON IMAGE LIBRARY Pillow (PIL fork)
except:
    print ("[!] Please, ensure that you have installed PIL (Pillow) on your system" + "\n")


#TESSERACT MUST BE INSTALLED ON THE COMPUTER BEFORE RUNNING THIS SCRIPT, IT IS NEEDED FOR OCR RECOGNITION
try:
    subprocess.call('tesseract', stdout=subprocess.PIPE)
except OSError as e:
    if e.errno == os.errno.ENOENT:
        print("[!] Tesseract OCR software not found on this computer. You can install it with 'sudo apt install tesseract-ocr' command" + "\n")
    else:
        raise

#IMAGEMAGICK MUST BE INSTALLED ON THE COMPUTER BEFORE RUNNING THIS SCRIPT, IT IS NEEDED FOR IMAGE CONVERSION
try:
    subprocess.call('convert', stdout=subprocess.PIPE)
except OSError as e:
    if e.errno == os.errno.ENOENT:
        print("[!] ImageMagick software not found on this computer. You can install it with 'sudo apt install imagemagick ' command" + "\n")
    else:
        raise

#*** GLOBAL VARIABLES ***   
captcha_folder              = ""
decoded_list                = []
                             

#**** FUNCTIONS ***
#Read a TXT file with an item per line and returns a load Python list containing these items
def file_to_list(file_path): 
   
    my_list = []
    
    with open(file_path, 'r+', encoding="utf-8") as infile:
                    lines = filter(None, (line.rstrip() for line in infile))
                    for myline in lines: 
                            if not myline.startswith('#'): #FILTER OUT FILE COMMENTS
                                my_list.append(myline.strip('\n')) #DELETE NEWLINE CHARACTERS
    return my_list

#GET LIST OF FILES FROM A GIVEN OS DIR
def get_files_from_folder(dir_name):

    list_files = []

    for root, dirs, files in os.walk(os.path.abspath(dir_name)):
        for file in files:
            list_files.append(os.path.join(root, file))
    return list_files

#OCR RECOGNITION ON CAPTCHA IMAGE
def read_ocr_captcha(cap_cleaned_path):
    print ('** Analyzing captcha image with an OCR: ' + os.path.basename(cap_cleaned_path) + "\n") 

    #USE IMAGEMAGICK UNIX TOOL FOR RESIZING IMAGE BEFORE RECOGNITION
    command = "convert " + cap_cleaned_path + " -resize 300% " + cap_cleaned_path + "resized" #Resizing should be customized upon characteristics of each captcha
    try:
        os.system(command)
    except Exception as e:
        print("[!] Something went wrong when executing ImageMagick. " + str(e))
    time.sleep(1)

    #TESSERACT OCR FOR TEXT RECOGNITION
    command = "tesseract --psm 7 --oem 1 --tessdata-dir /usr/share/tesseract-ocr/4.00/tessdata " + cap_cleaned_path + "resized " + "out" #Tesseract arguments should be customized based upon captcha type (numeric, language, symbols,...)
    try:
        os.system(command)
    except Exception as e:
        print("[!] Something went wrong when executing Tesseract OCR. " + str(e))
    time.sleep(1)

#PREPARE CAPTCHA IMAGE BEFORE OCR RECOGNITION
def prepare_image(img,pixdata):
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][0] < 90:
                pixdata[x, y] = (0, 0, 0, 255)
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][1] < 136:
                pixdata[x, y] = (0, 0, 0, 255)
            for y in range(img.size[1]):         
                for x in range(img.size[0]):             
                    if pixdata[x, y][2] > 0:      
                        pixdata[x, y] = (255, 255, 255, 255)

#CRACK THE CAPTCHA WITH OCR RECOGNITION
def crack_captcha(cap_path):               

    cap_name = os.path.basename(cap_path) #extract filename from path
    captcha_cleaned_folder      = os.path.join(os.path.dirname(__file__), 'cleaned_captchas')
    pathlib.Path(captcha_cleaned_folder).mkdir(exist_ok=True) #create subfolder
    cap_cleaned_path = captcha_cleaned_folder + "/" + cap_name


    #LOAD CAPTCHA IMAGE AND RGB - MATRIX CONVERSION
    print ('** Processing CAPTCHA: ' + cap_name + "\n")
    img = Image.open(cap_path)
    print ("      - Converting image to RGB..." + "\n")
    img = img.convert("RGB")
    pixdata = img.load()

    #PROCESS IMAGE BEFORCE OCR RECOGNITION
    print ("      - Image is being transformed... (wait a moment, please)" + "\n")
    prepare_image(img, pixdata)
    print ("           * Pixel matrix successfully transformed" + "\n")
    img.save(cap_cleaned_path)
    print ("           * Clean captcha version saved on disk" + "\n")  

    #OCR TEXT RECOGNITION
    read_ocr_captcha(cap_cleaned_path)
    Text  = open ("out.txt","r")
    decoded = Text.readline().strip('\n')
    decoded_list.append(decoded) #DECODED TEXT IS STORED
    print ('\n' + '[+} EXTRACTED CAPTCHA TEXT IS:  ' + decoded + "\n\n")

#CAPTCHA EFFICIENCY ANALYSIS
def captcha_efficiency(captcha_solved_file,num_total):

    nonsolved = 0
    solved = 0
    i = 0

    #READ MANUALLY SOLVED CAPTCHAS FILE
    manual_captchas_text = file_to_list(captcha_solved_file)


    while i < num_total:
        if not decoded_list[i] == manual_captchas_text[i]:
            nonsolved = nonsolved + 1
        i += 1

    captcha_efficiency =  float(Fraction(nonsolved, num_total)) * 100
    solved = num_total - nonsolved
    print ("The efficiency of CAPTCHA system analyzed is of: " + str(captcha_efficiency) + '%' + "\n")
    print ("       - Captchas successfully recognized: " + str(solved) + " CAPTCHAS" + "\n")
    print ("       - Failed captchas: " + str(nonsolved) + " CAPTCHAS" + "\n")
    
# BANNER
def banner():
    print ("""
           _   _ _______ _____       _____          _____ _______ _____ _    _          
     /\   | \ | |__   __|_   _|     / ____|   /\   |  __ \__   __/ ____| |  | |   /\    
    /  \  |  \| |  | |    | |______| |       /  \  | |__) | | | | |    | |__| |  /  \   
   / /\ \ | . ` |  | |    | |______| |      / /\ \ |  ___/  | | | |    |  __  | / /\ \  
  / ____ \| |\  |  | |   _| |_     | |____ / ____ \| |      | | | |____| |  | |/ ____ \ 
 /_/    \_\_| \_|  |_|  |_____|     \_____/_/    \_\_|      |_|  \_____|_|  |_/_/    \_\
                                                                                        
                                                                            by DI0NJ@CK              

    """)

# *** MAIN CODE ***
if __name__ == '__main__':  

    #ARG PARSER
    description =  "Anticaptcha v3.0 - {__author__}"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('captcha_img')
    parser.add_argument('-d', '--directory' , help="specify a folder for loading all captcha images to solve (e.g '/home/myuser/mycaptchafolder')", metavar='directory', dest='directory', action='store')
    parser.add_argument('-e', '--efficiency' , help="enables captcha system efficiency calculator (a path to the file containing solved captcha text must be specified here)", dest='efficiency', action='store')
    parser.add_argument('-v', help='displays the current version', action='version', version=__version__)
    args = parser.parse_args()

    #BANNER
    banner()

    #CHECK INPUT ARGS
    captcha_img_list = []

    if args.directory:
        captcha_folder = args.directory

        #GET LIST OF CAPTCHA IMAGES TO PROCESS
        files_list = get_files_from_folder(args.directory)
        for a_file in files_list:
            if not a_file[0] == ".": #Avoid storing hidden system files
                captcha_img_list.append(a_file)
    else:
        captcha_img_list.append(args.captcha_img)

    #TRY TO CRACK EACH CAPTCHA IMAGE AND EXTRACT TEXT
    for captcha_path in captcha_img_list:
        crack_captcha(captcha_path) 
         
    #CAPTCHA SYSTEM EFFICIENCY ANALYSIS (OPTIONAL, CAN BE SKIPPED)
    if args.efficiency:
        captcha_efficiency(args.efficiency,len(captcha_img_list))