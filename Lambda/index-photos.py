import json
import boto3
import logging
import os
import sys
import uuid
# import requests
from botocore.vendored import requests
# from PIL import Image
# import PIL.Image
from datetime import *
#from requests_aws4auth import AWS4Auth

ES_HOST = 'https://search-myphoto-5ixouyqjs5g4jcffg7qppsrtsu.us-east-1.es.amazonaws.com'
REGION = 'us-east-1'
#credentials = boto3.Session().get_credentials()
#region = 'us-east-1'
#awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_url(index, type):
    url = ES_HOST + '/' + index + '/' + type
    return url

# def resize_image(image_path, resized_path):
#     with Image.open(image_path) as image:
#         image.thumbnail(tuple(x / 2 for x in image.size))
#         image.save(resized_path)

def lambda_handler(event, context):

    print(os.environ['AWS_SECRET_ACCESS_KEY'])
    print(os.environ['AWS_ACCESS_KEY_ID'])
    #logger.info(event)
    # print("EVENT --- {}".format(json.dumps(event)))

    headers = { "Content-Type": "application/json" }
    # rek = boto3.client('rekognition')
    rek = boto3.client('rekognition', aws_access_key_id='AKIA4RE4HWGIJSGLSTM5',
    aws_secret_access_key='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',
    region_name='us-east-1')

    # print(os.environ['AWS_SECRET_ACCESS_KEY'])
    # print(os.environ['AWS_ACCESS_KEY_ID'])
    # logger.info("rekkkkkkkkkk")

    # get the image information from S3
    record = event['Records'][-1]

    bucket = record['s3']['bucket']['name']

    key = record['s3']['object']['key']
    size = record['s3']['object']['size'] # up to 5MB
    # logger.info("detect begin")
    # logger.info(bucket)
    print(key)
    # detect the labels of current image
    labels = rek.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        }
    )

    logger.info("get lable")
    print("IMAGE LABELS --- {}".format(labels['Labels']))

    # prepare JSON object
    obj = {}
    obj['objectKey'] = key
    obj["bucket"] = bucket
    obj["createdTimestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    obj["labels"] = []

    for label in labels['Labels']:
        obj["labels"].append(label['Name'])

    print("JSON OBJECT --- {}".format(obj))
    logger.info("begin post")
    # post the JSON object into ElasticSearch, _id is automaticlly increased
    url = get_url('myphoto', 'Photo')
    print("ES URL --- {}".format(url))
    obj = json.dumps(obj)
    logger.info("json:{}".format(obj))

    req = requests.post(url, data=obj, headers=headers)
    print(req)
    logger.info('Successfully uploaded to ES')

    print("Success: ", req)
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            'Content-Type': 'application/json'
        },
        'body': json.dumps("Image labels have been successfully detected!")
    }
