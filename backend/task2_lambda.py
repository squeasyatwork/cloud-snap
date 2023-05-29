import simplejson as json
import boto3
import base64
import numpy as np
import sys
import time
import cv2
import os

# Lambda function
def lambda_handler(event, context):
    # Connecting to images table and retrieving records
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('images')
    body = table.scan()
    dbRecords = body['Items']
    
    # Find images based on the tags by handling API requests
    if str(event['resource']) == "/api/images/search/tags" and str(event['httpMethod']) == "POST":
        requestBody = json.loads(event['body'])
        tagBundles = requestBody['tags']
        
        result = []
        tags = {}
        
        # Creating a dictionary of tags and their counts
        for tagBundle in tagBundles:
            tags[tagBundle['tag']] = tagBundle['count'] if "count" in tagBundle else 1
        
        # Filtering images based on the provided tags
        for dbRecord in dbRecords:
            if all(tag in dbRecord["objects"].keys() for tag in tags.keys()):
                if all(dbRecord["objects"][tag] >= tags[tag] for tag in tags.keys()):
                    result.append(dbRecord["image_url"])
        
        # Returning the search results as a JSON response
        return {
            'statusCode': 201,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({"links": result})
        }
    # Find images based on the tags of an image by handling API requests
    elif str(event['resource']) == "/api/images/search/image" and str(event['httpMethod']) == "POST":
        
        # Get image tags
        requestBody = json.loads(event['body'])
        id = requestBody["id"]
        image = requestBody["image"]
        
        
        # Copy code from previous if statement
        
        # Returning the image tags as a JSON response
        return {
            'statusCode': 201,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
        'body': str(image)
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
        
        return {
            'statusCode': 201,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        }}
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
            s3.delete_object(Bucket=image_url_tokens[-2], Key=image_url_tokens[-1]) 
            
            
            
            return {
                'statusCode': 204,
                'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Credentials': 'true',
                'Content-Type': 'application/json'
            }}
