import json
import boto3
import os
import time
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from botocore.vendored import requests

service = 'es'
credentials = boto3.Session().get_credentials()
region = 'us-east-1'
host = 'https://search-myphoto-5ixouyqjs5g4jcffg7qppsrtsu.us-east-1.es.amazonaws.com'
index = 'myphoto'

url = host + '/' + index + '/_search'
headers = { "Content-Type": "application/json" }

def lambda_handler(event, context):
    # TODO implement
    # logger.info("event:{}".format(event))
    userId = "wl2655"
    # text = event
    text = event['queryStringParameters']['q'] #get text input from lex
    logger.info("raw text:{}".format(text))
    if text in ["use_voice"]:
        logger.info("using voice!!!!!!!!!!!!!!!!!!!!11")
        text = use_voice()
    logger.info("text:{}".format(text))


    client = boto3.client('lex-runtime')
    response = client.post_text(
        botName='SmartPhotoBot',
        botAlias='bota',
        userId=userId,
        inputText=text
    )
    print(response)
    logger.info("response:{}".format(response))
    # responseText = response['message']

    # responseMessages = dict()
    # responseMessages["messages"] = [{
    #     'type': 'string',
    #     'unstructured': {
    #         'id': 'string',
    #         'text': responseText,
    #         'timestamp': 'string'}}]


    response_slots = response['slots'] #gives labels from lex

    logger.info("slots:{}".format(response_slots))
    word_list = list()
    for key, value in response_slots.items():
        if value:
            word_list.append(value)
    word_list = set(word_list) #INPUT VAR for ES
    logger.info("word_list:{}".format(word_list))

    for word in word_list:
    # response_es = requests.get("https://vpc-photos-7a4y7c7ob2k6xmufkzaxmhofdy.us-east-1.es.amazonaws.com/predictions/_search?q=%s" % response_slots["ObjectOne"], auth=auth)
        query = {
            "size": 5,
            "query": {
                "multi_match": {
                    "query": word,
                    "fields": ["labels"]
                }
            }
        }

    r = requests.get(url, headers=headers, data=json.dumps(query)).json()
    logger.info("r:{}".format(r))
    result = r['hits']['hits']
    logger.info("result form elasticsearch:{}".format(result))
    res = {}
    for each_res in result:
            res[each_res['_source']['objectKey'].split('/')[-1]] = 'https://' +each_res['_source']['bucket']+  '.s3.amazonaws.com/' + each_res['_source']['objectKey'].replace(' ', "+")

    logger.info("res:{}".format(res))

    return {
        'statusCode': 200,
        'body': json.dumps(res),
        'headers': {
            "Access-Control-Allow-Origin" : "*",
            "Access-Control-Allow-Credentials" : True
            }
    }

def use_voice():


    transcribe = boto3.client('transcribe')
    job_name = "voice-test"
    job_uri = "https://hw3-voice.s3.amazonaws.com/undefined.mp3"
    logger.info("voice uploaded")
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        # print("Not ready yet...")
    logger.info("status:{}".format(status))
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['FAILED']:
            response = transcribe.delete_transcription_job(TranscriptionJobName=job_name)
            raise Exception("failed")
    else:
        url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        logger.info("transcribe url:{}".format(url))
        r = requests.get(url)
        res = r.json()
        logger.info("json file:{}".format(res))
        txt = res['results']['transcripts'][0]['transcript']
        txt  = 'give me ' + txt
        logger.info("translated txt:{}".format(txt))
        time.sleep(5)
        # if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED']:
        #     response = transcribe.delete_transcription_job(TranscriptionJobName=job_name)
        #     logger.info("cleaned up")
        return txt
