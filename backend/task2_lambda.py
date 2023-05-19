import simplejson as json
import boto3

def lambda_handler(event, context):
    # Connecting to images table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('images')
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
            image_tags = {}
            for object in dbRecord['objects']:
                if object['label'] in image_tags:
                    image_tags[object['label']] += 1
                else:
                    image_tags[object['label']] = 1
    
            if all(tag in image_tags.keys() for tag in tags.keys()):
                if all(image_tags[tag] >= tags[tag] for tag in tags.keys()):
                    result.append(dbRecord["image"])
        
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
        
        # Copy code from previous if statement
        
        return {
            'statusCode': 200,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
        'body': "Find images based on the tags of an image"
        }
    # Manual addition or removal of tags
    elif str(event['resource']) == "/api/images/change/tags" and str(event['httpMethod']) == "POST":
        return {
            'statusCode': 200,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Credentials': 'true',
            'Content-Type': 'application/json'
        },
        'body': "Manual addition or removal of tags"
        }
    # Delete an image (Need to add error checking)
    elif str(event['resource']) == "/api/images" and str(event['httpMethod']) == "DELETE":
            # Delete from table
            response = table.scan(
                FilterExpression='image = :value',
                ExpressionAttributeValues={':value': event['queryStringParameters']['image_url']}
                )
            for item in response['Items']:
                key = {'id': item['id']}
                table.delete_item(Key=key)
            return {
                'statusCode': 200,
                'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Credentials': 'true',
                'Content-Type': 'application/json'
            }}