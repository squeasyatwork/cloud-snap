import simplejson as json
import boto3
import base64
import numpy as np
import cv2
import uuid
from urllib.parse import unquote_plus

def lambda_handler(event, context):
    # Initialize AWS resources
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('images')
    s3 = boto3.client('s3')
    
    # Process each record from the event
    for record in event['Records']:
        # Get bucket and key information from the S3 event record
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
    
        # Image processing
        # Read image from S3, encode it as base64, and get the image URL
        image = base64.b64encode(s3.get_object(Bucket=bucket, Key=key)["Body"].read()).decode("utf-8")
        image_url = "https://" + str(bucket) + ".s3.amazonaws.com/" + str(key)
        # Generate a unique ID for the image
        image_id = str(uuid.uuid5(uuid.NAMESPACE_OID, image))
        
        # Retrieve YOLO configuration and weights files from S3
        LABELS = s3.get_object(Bucket="fit5225-assignment2", Key="yolo_tiny_configs/coco.names")["Body"].read().decode('utf-8').strip().split("\n")
        s3.download_file("fit5225-assignment2", "yolo_tiny_configs/yolov3-tiny.cfg", "/tmp/yolov3-tiny.cfg")
        s3.download_file("fit5225-assignment2", "yolo_tiny_configs/yolov3-tiny.weights", "/tmp/yolov3-tiny.weights")
        
        # Decode and process the image using OpenCV
        decoded_data = base64.b64decode(image)
        np_data = np.fromstring(decoded_data,np.uint8)
        img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
        
        npimg=np.array(img)
        image=npimg.copy()
        image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        
        # Load YOLO model using the configuration and weights files
        net = cv2.dnn.readNetFromDarknet("/tmp/yolov3-tiny.cfg", "/tmp/yolov3-tiny.weights")
        confthres = 0.3
        nmsthres = 0.1

        (H, W) = image.shape[:2]
        # determine only the *output* layer names that we need from YOLO
        ln = net.getLayerNames()
        ln = [ln[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

        # construct a blob from the input image and then perform a forward
        # pass of the YOLO object detector, giving us our bounding boxes and
        # associated probabilities
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        layerOutputs = net.forward(ln)

        # initialize our lists of detected bounding boxes, confidences, and
        # class IDs, respectively
        boxes = []
        confidences = []
        classIDs = []

        # loop over each of the layer outputs
        for output in layerOutputs:
            # loop over each of the detections
            for detection in output:
                # extract the class ID and confidence (i.e., probability) of
                # the current object detection
                scores = detection[5:]
                classID = np.argmax(scores)
                # print(classID)
                confidence = scores[classID]

                # filter out weak predictions by ensuring the detected
                # probability is greater than the minimum probability
                if confidence > confthres:
                    # scale the bounding box coordinates back relative to the
                    # size of the image, keeping in mind that YOLO actually
                    # returns the center (x, y)-coordinates of the bounding
                    # box followed by the boxes' width and height
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")

                    # use the center (x, y)-coordinates to derive the top and
                    # and left corner of the bounding box
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    # update our list of bounding box coordinates, confidences,
                    # and class IDs
                    boxes.append([x, y, int(width), int(height)])

                    confidences.append(float(confidence))
                    classIDs.append(classID)

                # apply non-maxima suppression to suppress weak, overlapping bounding boxes
                idxs = cv2.dnn.NMSBoxes(boxes, confidences, confthres, nmsthres)
                
                # Initialize a list to store detected objects
                objects = []
                if len(idxs) > 0:
                    # loop over the indexes we are keeping
                    for i in idxs.flatten():
                        # Create a dictionary for each detected object
                        objects.append(
                            {"label": LABELS[classIDs[i]], "accuracy": confidences[i], 
                            "rectangle": {"height": boxes[i][3], "left": boxes[i][0], "top": boxes[i][1], "width": boxes[i][2]}}
                            )
        
        # Count the number of objects per label
        tags = {}
        for obj in objects:
            if obj["accuracy"] > 0.6:
                if obj["label"] not in tags:
                    tags[obj["label"]] = 1
                else:
                    tags[obj["label"]] += 1
        
        
    
        # Insert item into table
        table.put_item(
            Item={
                'id': image_id,
                'image_url': str(image_url),
                'objects': tags
                }
            )
    
    return str(image)
