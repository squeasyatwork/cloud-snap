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
    
        # Change how tags are structured from [{"tag": "sample1", "count": 1},{"tag": "sample2", "count": 2}] to {sample1: 1, sample2: 2}
        for tagBundle in tagBundles:
            tags[tagBundle['tag']] = tagBundle['count'] if "count" in tagBundle else 1

        for dbRecord in dbRecords:

            # Don't need this anymore, will be handled by db schema
            # image_tags = {}
            # for object in dbRecord['objects']:
            #     if object['label'] in image_tags:
            #         image_tags[object['label']] += 1
            #     else:
            #         image_tags[object['label']] = 1
    
            # Iterate through records in the database and find records which are a superset of the input and have a count >= to each tag in the input 
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
            records_to_delete = table.scan(
                FilterExpression='image_url = :value',
                ExpressionAttributeValues={':value': event['queryStringParameters']['image_url']}
                )
            for item in records_to_delete['Items']:
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