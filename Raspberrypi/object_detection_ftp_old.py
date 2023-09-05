import os
import argparse
import cv2
import numpy as np
import sys
import glob
import importlib.util
import math
import mysql.connector



def object_detection(cnx,modeldir,imagename,threshold=0.5,save=True):

    MODEL_NAME = modeldir

    GRAPH_NAME = 'detect.tflite'

    LABELMAP_NAME = 'labelmap.txt'



    min_conf_threshold = threshold

    use_TPU = False



    save_results = save 
    show_results = False



    IM_NAME = imagename



    # Import TensorFlow libraries

    # If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow

    # If using Coral Edge TPU, import the load_delegate library

    pkg = importlib.util.find_spec('tflite_runtime')

    if pkg:

        from tflite_runtime.interpreter import Interpreter

        if use_TPU:

            from tflite_runtime.interpreter import load_delegate

    else:

        from tensorflow.lite.python.interpreter import Interpreter

        if use_TPU:

            from tensorflow.lite.python.interpreter import load_delegate



    # If using Edge TPU, assign filename for Edge TPU model

    if use_TPU:

        # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'

        if (GRAPH_NAME == 'detect.tflite'):

            GRAPH_NAME = 'edgetpu.tflite'





    # Get path to current working directory

    CWD_PATH = os.getcwd()

    if IM_NAME:

        PATH_TO_IMAGES = os.path.join(CWD_PATH,IM_NAME)

        images = glob.glob(PATH_TO_IMAGES)

        if save_results:

            RESULTS_DIR = 'image'



    # Create results directory if user wants to save results

    if save_results:

        RESULTS_PATH = os.path.join(CWD_PATH,RESULTS_DIR)

        if not os.path.exists(RESULTS_PATH):

            os.makedirs(RESULTS_PATH)



    # Path to .tflite file, which contains the model that is used for object detection

    PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)



    # Path to label map file

    PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)



    # Load the label map

    with open(PATH_TO_LABELS, 'r') as f:

        labels = [line.strip() for line in f.readlines()]



    # Have to do a weird fix for label map if using the COCO "starter model" from

    # https://www.tensorflow.org/lite/models/object_detection/overview

    # First label is '???', which has to be removed.

    if labels[0] == '???':

        del(labels[0])



    # Load the Tensorflow Lite model.

    # If using Edge TPU, use special load_delegate argument

    if use_TPU:

        interpreter = Interpreter(model_path=PATH_TO_CKPT,

                                experimental_delegates=[load_delegate('libedgetpu.so.1.0')])

        print(PATH_TO_CKPT)

    else:

        interpreter = Interpreter(model_path=PATH_TO_CKPT)



    interpreter.allocate_tensors()



    # Get model details

    input_details = interpreter.get_input_details()

    output_details = interpreter.get_output_details()

    height = input_details[0]['shape'][1]

    width = input_details[0]['shape'][2]



    floating_model = (input_details[0]['dtype'] == np.float32)



    input_mean = 127.5

    input_std = 127.5



    # Check output layer name to determine if this model was created with TF2 or TF1,

    # because outputs are ordered differently for TF2 and TF1 models

    outname = output_details[0]['name']



    if ('StatefulPartitionedCall' in outname): # This is a TF2 model

        boxes_idx, classes_idx, scores_idx = 1, 3, 0

    else: # This is a TF1 model

        boxes_idx, classes_idx, scores_idx = 0, 1, 2



    # Loop over every image and perform detection

    for image_path in images:



        # Load image and resize to expected shape [1xHxWx3]

        image = cv2.imread(image_path)

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        imH, imW, _ = image.shape 

        image_resized = cv2.resize(image_rgb, (width, height))

        input_data = np.expand_dims(image_resized, axis=0)



        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)

        if floating_model:

            input_data = (np.float32(input_data) - input_mean) / input_std



        # Perform the actual detection by running the model with the image as input

        interpreter.set_tensor(input_details[0]['index'],input_data)

        interpreter.invoke()



        # Retrieve detection results

        boxes = interpreter.get_tensor(output_details[boxes_idx]['index'])[0] # Bounding box coordinates of detected objects

        classes = interpreter.get_tensor(output_details[classes_idx]['index'])[0] # Class index of detected objects

        scores = interpreter.get_tensor(output_details[scores_idx]['index'])[0] # Confidence of detected objects



        detections = []



        # Loop over all detections and draw detection box if confidence is above minimum threshold

        for i in range(len(scores)):

            if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):



                # Get bounding box coordinates and draw box

                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()

                ymin = int(max(1,(boxes[i][0] * imH)))

                xmin = int(max(1,(boxes[i][1] * imW)))

                ymax = int(min(imH,(boxes[i][2] * imH)))

                xmax = int(min(imW,(boxes[i][3] * imW)))

                

                cv2.rectangle(image, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)



                # Draw label

                object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index

                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'

                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size

                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window

                cv2.rectangle(image, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in

                cv2.putText(image, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text



                detections.append([object_name, scores[i], (xmin+xmax)/2, (ymin+ymax)/2])



        # All the results have been drawn on the image, now display the image

        if show_results:

            cv2.imshow('Object detector', image)
            

            # Press any key to continue to next image, or press 'q' to quit

            if cv2.waitKey(0) == ord('q'):

                break



        # Save the labeled image to results folder if desired

        if save_results:



            # Get filenames and paths

            image_fn = os.path.basename(image_path)

            image_savepath = os.path.join(CWD_PATH,RESULTS_DIR,image_fn)

            

            base_fn, ext = os.path.splitext(image_fn)

            txt_result_fn = base_fn +'.txt'

            txt_savepath = os.path.join(CWD_PATH,RESULTS_DIR,txt_result_fn)

            # Add red dot at the center of the image
            cv2.circle(image, (imW//2, imH//2), radius=10, color=(0, 0, 255), thickness=-1)

            # Save image

            cv2.imwrite(image_savepath, image)
 
            cursor = cnx.cursor()
            query = 'SELECT elapsed_time, ax, ay, az, gx, gy, gz, angx, angy, HEADING, temp, pressure, alt, lat, longi, gpsalt, light FROM SENSOR ORDER BY elapsed_time DESC LIMIT 1'
            cursor.execute(query)
            row = cursor.fetchone()
            elapsed_time, ax, ay, az, gx, gy, gz, angx, angy, HEADING, temp, pressure, alt, lat, longi, gpsalt, light=row
            
            # Write results to text file
            # (Using format defined by https://github.com/Cartucho/mAP, which will make it easy to calculate mAP)

            with open(txt_savepath,'w') as f:
                f.write('status variables\n')
                f.write(f'{row}\n')
                f.write('name concordance x_pix y_pix x_coo y_coo x_cali y_cali longitude latitude \n')
                
                R=6371000 #Radius of Earth (m)
                if len(detections)>0:
                    for detection in detections:
                        height=0.44 #m
                        x=height*math.tan((detection[2]-960)*0.001041)
                        y=-height*math.tan((detection[3]-540)*0.001316)
                        calx=0.980759819*x+0.000917887032*y-0.0055717019
                        caly=0.02244757*x+0.89012411*y+0.010873488495384623
                        
                        theta = math.radians(HEADING) # 각도를 라디안으로 변환
                        rotation_matrix = [[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]
                        
                        # 회전 행렬을 적용하여 새로운 좌표를 계산
                        x_rotated = rotation_matrix[0][0] * x + rotation_matrix[0][1] * y
                        y_rotated = rotation_matrix[1][0] * x + rotation_matrix[1][1] * y
                        calx_rotated = rotation_matrix[0][0] * calx + rotation_matrix[0][1] * caly
                        caly_rotated = rotation_matrix[1][0] * calx + rotation_matrix[1][1] * caly
                        
                        # 위도 변환
                        lat_diff = caly_rotated / R 
                        lat_diff_degrees = math.degrees(lat_diff)

                        # 경도 변환
                        lon_diff = calx_rotated / (R * math.cos(math.radians(lat))) # lat is the latitude of the place where measurements are made
                        lon_diff_degrees = math.degrees(lon_diff)
                        
                        # 이름, 일치도, x pixel, y pixel, x coord, y coord, calibrated x coord, calibrated y coord, longitude, latitude
                        f.write('%s %.4f %d %d %.2f %.2f %.2f %.2f %.5f %.5f\n' % (detection[0], detection[1], detection[2], detection[3],x_rotated,y_rotated,calx_rotated,caly_rotated,longi+lon_diff_degrees,lat+lat_diff_degrees)) 
                        
                else:
                    f.write('Nothing 0 0 0 0 0 0 0 0 0\n')
                    
                    

cv2.destroyAllWindows()
