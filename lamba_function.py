import json
import urllib.parse
import boto3
import random
import time

def lambda_handler(event, context):
    # TODO implement
    Bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    if key.endswith('.txt'):
        print(text_analysis(key,Bucket))
    else:
        print(image_analysis(key,Bucket))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def text_analysis(file_name,bucket):
    queue_url=''#textsevicequeue
    sqs = boto3.client("sqs", region_name='ap-south-1')
    client = boto3.client('s3')
    obj = client.get_object(Bucket=bucket, Key=file_name)
    data=obj['Body'].read().decode('utf-8')
    list_data=list(data.split('.'))
    for i in range(len(list_data)):
        response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(list_data[i]),
        MessageGroupId="01"
        )
    return "text analysis done"
    
    
def image_analysis(file_name,bucket):
    session = boto3.Session()
    s3 = session.resource('s3')
    copy_source = {
    'Bucket': bucket,
    'Key': file_name
    }
    time.sleep(5)
    bucket_image = "image-ramsai"
    bucket_target = s3.Bucket(bucket_image)
    bucket_target.copy(copy_source,file_name)
    sqs = boto3.client("sqs", region_name='ap-south-1')
    queue_url=''#imageservicequeueurl
    image_id=[random.randint(0,8000000)]
    image_path=[file_name]
    for i in range(len(image_id)):
        response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({"image_id":image_id[i], "image_path":image_path[i]}),
        MessageGroupId="01"
        )
    return "Image analysis done"
    