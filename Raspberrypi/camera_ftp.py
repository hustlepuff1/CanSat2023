from picamera2 import Picamera2
import time
import cv2
import object_detection_ftp as od
from libcamera import controls
from ftplib import FTP
import os
import logging

logging.basicConfig(filename='/home/cnu/tflite1/camlogfile.log', level=logging.INFO)

def shot(cnx,camera,num):
        try:    
                local_file_path_jpg = f'/home/cnu/tflite1/image/image{num}.jpg'
                camera.capture_file(local_file_path_jpg)
                ##od.object_detection(cnx,'Sample_TFLite_model', local_file_path_jpg) #model change
                od.object_detection(cnx,'Goheung_Model', local_file_path_jpg) #model change
                od.object_detection(cnx,'KAIST', local_file_path_jpg)
        except:
                pass

def Od(ftp,ftpnum):
    def upload_files_ftp(file_paths):
        for file_path in file_paths:
            with open(file_path, 'rb') as file:
                ftp.storbinary('STOR ' + os.path.basename(file_path), file)

            print(f"{os.path.basename(file_path)} uploaded successfully")
        
    local_file_path_jpg = f'/home/cnu/tflite1/image/image{ftpnum}.jpg'
    local_file_path_txt = f'/home/cnu/tflite1/image/image{ftpnum}.txt'
    # Upload the captured and processed image and .txt file to FTP server
        # Check if both files exist
    if os.path.exists(local_file_path_jpg) and os.path.exists(local_file_path_txt):
        # Upload the captured and processed image and .txt file to FTP server
        upload_files_ftp([local_file_path_jpg, local_file_path_txt])
    else:
        raise FileNotFoundError(f"Both files not found: {local_file_path_jpg} or {local_file_path_txt}")

##for num in range(10):
   ##     shot(num)
