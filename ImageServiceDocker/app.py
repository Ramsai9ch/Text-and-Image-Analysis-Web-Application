#from email import message
#from traceback import print_tb
#from urllib import response
import boto3
import json
import io
from keras.applications.resnet import ResNet50, preprocess_input, decode_predictions
from keras.preprocessing import image
import numpy as np
from PIL import Image

print("Loading..")

# Setup aws credentials
aws_access_id = ""
aws_secret_access_key = ""

# Setup queue
sqs = boto3.client("sqs", region_name='ap-south-1', aws_access_key_id=aws_access_id, 
                   aws_secret_access_key=aws_secret_access_key)
queue_url = ''#queueurl

# Setup model
model = ResNet50(weights='weights.h5')
bucket="image-ramsai"

def load_image_from_s3(bucket, key, region_name='ap-southeast-1'):
    s3=boto3.resource("s3", region_name='ap-south-1', aws_access_key_id=aws_access_id, 
                   aws_secret_access_key=aws_secret_access_key)
    bucket = s3.Bucket(bucket)
    object = bucket.Object(key)
    response = object.get() 
    file_stream = response['Body']
    im = Image.open(file_stream)
    newsize = (224, 224)
    im = im.resize(newsize)
    return np.array(im)

def process_message(message):
    # convert json string to object
    message = json.loads(message)

    print(f"processing message: {message}")
    labels = predict_resetnet(message["image_path"])
    
    # do what you want with the message here
    save_output(message["image_id"], labels)
    pass

def predict_resetnet(image_path):
    print("Loading image from %s bucket... "%bucket)
    img = load_image_from_s3(bucket,image_path)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0) 
    x = preprocess_input(x)
    preds = model.predict(x)

    labels = decode_predictions(preds, top=3)[0]
    print(labels)
    return labels

def save_output(image_id, labels):
    print("saving output of image_id %s in txt file " % image_id)
    # TODO: Do something with the labels
    name=image_id
    output_file_name="%s.txt" % name
    f = open(output_file_name,"w+")
    f.write(str(labels))
    f.close()
    s3 = boto3.client("s3", region_name='ap-south-1', aws_access_key_id=aws_access_id, 
                   aws_secret_access_key=aws_secret_access_key)
    s3.upload_file(output_file_name, bucket, output_file_name)
    print("output file {} created in {} bucket".format(output_file_name,bucket))

if __name__ == "__main__":
    while True:
        print("waiting for next message..")
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=2
        )

        if 'Messages' in response:
                message = response['Messages'][0]
                print(f"new messsage received: {message['Body']}")
                process_message(message['Body'])
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
