import nltk
#nltk.download()
from textblob import TextBlob
nltk.data.path.append(".")
import boto3


# Setup aws credentials
aws_access_id = "" #accesskey
aws_secret_access_key = ""#secretkey

sqs = boto3.client("sqs", region_name='ap-south-1', aws_access_key_id=aws_access_id, 
                   aws_secret_access_key=aws_secret_access_key)
queue_url="" #textqueueurl

def process_message(sentence):
    output_list=[]
    output_dict={}
    output= TextBlob(sentence)
    o_tags=output.tags
    output_dict['body']=sentence
    for tag in o_tags:
        if(tag[1]== "NN"):
            output_dict["Noun"]=tag[0]
        elif(tag[1]== "JJ"):
            output_dict["Adjective"]=tag[0]
        elif(tag[1]== "RB"):
            output_dict["Adverb"]=tag[0]
        elif(tag[1]== "DT"):
            output_dict["Determiner"]=tag[0]
    output_dict["Sentiment"]=output.polarity
    output_list.append(output_dict)
    print(output_list)

if __name__ == "__main__":
    while True:
        print("waiting for next message..")
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5
        )
        if 'Messages' in response:
            message = response['Messages'][0]
            print(f"new messsage received: {message['Body']}")
            process_message(message['Body'])
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )