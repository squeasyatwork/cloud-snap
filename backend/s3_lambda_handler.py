import json
import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus


s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('a2images')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        #imagefile = s3_client.get_object(Bucket=bucket, Key=key)
        
        imgoutput = {"id":"64a9dca7-966b-5900-ae28-f5841f7092cf",
        "objects":[
            {
                "accuracy":0.5288963913917542,"label":"sports ball",
                "rectangle":{"height":17,"left":327,"top":66,"width":15}
            },
            {
                "accuracy":0.8288963913917542,"label":"person",
                "rectangle":{"height":17,"left":327,"top":66,"width":15}
            },
            {
                "accuracy":0.7288963913917542,"label":"kite",
                "rectangle":{"height":17,"left":327,"top":66,"width":15}
            },
            {
                "accuracy":0.2288963913917542,"label":"bus",
                "rectangle":{"height":17,"left":327,"top":66,"width":15}
            },
            {
                "accuracy":0.9288963913917542,"label":"person",
                "rectangle":{"height":17,"left":327,"top":66,"width":15}
            }
            ]
        }
        
        outputstore = {}
        for obj in imgoutput["objects"]:
            if obj["accuracy"] > 0.6:
                if obj["label"] not in outputstore:
                    outputstore[obj["label"]] = 1
                else:
                    outputstore[obj["label"]] += 1
        
        
        table.put_item(
            Item={
                'id': imgoutput["id"],
                'image_url': "abc.jpg",
                'objects': outputstore
            }
        )
    return {
       'statusCode': 200,
       'body': json.dumps('Records successfully inserted into database...')
    }