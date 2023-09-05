from picamera2 import Picamera2
from time import sleep
import cv2
import object_detection as od
from libcamera import controls
from ftplib import FTP
import os


def upload_files_ftp(hostname, username, password, port, file_paths, remote_directory):
    try:
        ftp = FTP()
        ftp.connect(hostname, port)
        ftp.login(username, password)

        print('FTP connection established')

        ftp.cwd(remote_directory)

        print('Directory changed')

        for file_path in file_paths:
            with open(file_path, 'rb') as file:
                ftp.storbinary('STOR ' + os.path.basename(file_path), file)

            print(f"{os.path.basename(file_path)} uploaded successfully")

        ftp.quit()

    except Exception as e:
        print("Error occurred while uploading files.")
        print(e)


camera = Picamera2()
config = camera.create_preview_configuration({"size": (1920, 1080)})
config["main"]
camera.align_configuration(config)
camera.configure(config)
camera.set_controls(
    {"AfMode": controls.AfModeEnum.Continuous, "ExposureTime": 40000})

# Run the operations for a specified number of iterations (5 in this case)
for i in range(5):
    camera.start(show_preview=True)
    sleep(1)
    local_file_path_jpg = f'/home/cnu/tflite1/image/image{i}.jpg'
    camera.capture_file(local_file_path_jpg)
    camera.stop()

    od.object_detection('Sample_TFLite_model', local_file_path_jpg)

    # Corresponding .txt file
    local_file_path_txt = f'/home/cnu/tflite1/image/image{i}.txt'

    # Upload the captured and processed image and .txt file to FTP server
    upload_files_ftp('bifrost0602.duckdns.org', 'bifrost', '1234',
                     2025, [local_file_path_jpg, local_file_path_txt], '/home/bifrost/Documents')
    sleep(1)
