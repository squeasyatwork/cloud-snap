import simplejson as json
import boto3
import base64
import numpy as np
import sys
import time
import cv2
import copy

def lambda_handler(event, context):
    # Connecting to images table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('images-table')
    body = table.scan()
    dbRecords = body['Items']
    
    # Find images based on the tags
    if str(event['resource']) == "/api/images/search/tags" and str(event['httpMethod']) == "POST":
        requestBody = json.loads(event['body'])
        tagBundles = requestBody['tags']
        
        result = []
        tags = {}
    
        for tagBundle in tagBundles:
            tags[tagBundle['tag']] = tagBundle['count'] if "count" in tagBundle else 1

        for dbRecord in dbRecords:
            if all(tag in dbRecord["objects"].keys() for tag in tags.keys()):
                if all(dbRecord["objects"][tag] >= tags[tag] for tag in tags.keys()):
                    result.append(dbRecord["image_url"])
        
        return {
            'statusCode': 200,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({"links": result})
        }
    # Find images based on the tags of an image
    elif str(event['resource']) == "/api/images/search/image" and str(event['httpMethod']) == "POST":
        
        # Get image tags
        image = json.loads(event["body"])["image"]
        
       
        # Image processing
        # image_id = str(uuid.uuid5(uuid.NAMESPACE_OID, image))
    
        s3 = boto3.client('s3')
        yolo_bucket = "yolo-files-bucket-team-20"
        LABELS = s3.get_object(Bucket=yolo_bucket, Key="coco.names")["Body"].read().decode('utf-8').strip().split("\n")
        s3.download_file(yolo_bucket, "yolov3-tiny.cfg", "/tmp/yolov3-tiny.cfg")
        s3.download_file(yolo_bucket, "yolov3-tiny.weights", "/tmp/yolov3-tiny.weights")
    
        decoded_data = base64.b64decode(image)
        np_data = np.fromstring(decoded_data,np.uint8)
        img = cv2.imdecode(np_data,cv2.IMREAD_UNCHANGED)
        
        npimg=np.array(img)
        image=npimg.copy()
        image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    
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

                objects = []
                if len(idxs) > 0:
                    # loop over the indexes we are keeping
                    for i in idxs.flatten():
                        objects.append(
                            {"label": LABELS[classIDs[i]], "accuracy": confidences[i], 
                            "rectangle": {"height": boxes[i][3], "left": boxes[i][0], "top": boxes[i][1], "width": boxes[i][2]}}
                            )
        
        tags = {}
        for obj in objects:
            if obj["accuracy"] >= 0.6:
                if obj["label"] not in tags:
                    tags[obj["label"]] = 1
                else:
                    tags[obj["label"]] += 1
        
        result = []
        for dbRecord in dbRecords:
            if all(tag in dbRecord["objects"].keys() for tag in tags.keys()):
                if all(dbRecord["objects"][tag] >= tags[tag] for tag in tags.keys()):
                    result.append(dbRecord["image_url"])
        
        return {
            'statusCode': 200,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({"links": result})
        }
    # Manual addition or removal of tags    
    elif str(event['resource']) == "/api/images/change/tags" and str(event['httpMethod']) == "POST":
        requestBody = json.loads(event['body'])
        tagBundles = requestBody['tags']
        
        tags = {}
    
        # Change how tags are structured from [{"tag": "sample1", "count": 1},{"tag": "sample2", "count": 2}] to {sample1: 1, sample2: 2}
        for tagBundle in tagBundles:
            tags[tagBundle['tag']] = tagBundle['count'] if "count" in tagBundle else 1
    
        # Identify which record needs to be modified
        record_to_modify = table.scan(
                FilterExpression='image_url = :value',
                ExpressionAttributeValues={':value': requestBody['url']}
                )
                
        # Record before modification
        unmodified_record = copy.deepcopy(record_to_modify["Items"])
        
        mode = requestBody["type"]
        # Removal of tags
        if mode == 0:
            for tag in tags.keys():
                if tag in record_to_modify["Items"][0]["objects"]:
                    # Subtract based on user input upto zero
                    record_to_modify["Items"][0]["objects"][tag] = max(record_to_modify["Items"][0]["objects"][tag] - tags[tag], 0)
                    # If zero counts of the tag exists, remove it
                    if record_to_modify["Items"][0]["objects"][tag] == 0:
                        record_to_modify["Items"][0]["objects"].pop(tag)
        # Addition of tags
        elif mode == 1:
            for tag in tags.keys():
                if tag in record_to_modify["Items"][0]["objects"]:
                    record_to_modify["Items"][0]["objects"][tag] += tags[tag]
                else:
                    record_to_modify["Items"][0]["objects"][tag] = tags[tag]
                    
        table.update_item(
        Key={'id': record_to_modify["Items"][0]['id']},
        UpdateExpression='SET objects = :objects',
        ExpressionAttributeValues={':objects': record_to_modify["Items"][0]['objects']}
        )
        
        
        # Record after modification
        modified_record = table.scan(
                FilterExpression='image_url = :value',
                ExpressionAttributeValues={':value': requestBody['url']}
                )["Items"]
                
        
        return {
            'statusCode': 200,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        }, 
            'body': json.dumps({"from": unmodified_record, "to": modified_record})
        }
    # Delete an image (Need to add error checking)
    elif str(event['resource']) == "/api/images" and str(event['httpMethod']) == "DELETE":
            image_url = event['queryStringParameters']['image_url']
            
            # Delete from table
            records_to_delete = table.scan(
                FilterExpression='image_url = :value',
                ExpressionAttributeValues={':value': image_url}
                )
            for item in records_to_delete['Items']:
                key = {'id': item['id']}
                table.delete_item(Key=key)
            
            s3 = boto3.client('s3')
            image_url_tokens = image_url.split("/")
            s3.delete_object(Bucket=image_url_tokens[-2].strip(".s3.amazonaws.com"), Key=image_url_tokens[-1])
            
            return {
                'statusCode': 204,
                'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Credentials': 'true',
                'Content-Type': 'application/json'
            }}