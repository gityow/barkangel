import json
import pickle
import os.path
from googleapiclient.discovery import build
from concurrent.futures import TimeoutError
from google.cloud import pubsub
from google.auth import jwt

# Documentation of pubsub here
# https://googleapis.dev/python/pubsub/latest/index.html

####################### LOGGING ###########################
# Imports Python standard library logging
import logging

logger = logging.getLogger(__name__)
##########################################################

############################# LOAD .ENV #############################
from os.path import join, dirname
from dotenv import load_dotenv, find_dotenv
import os

CURR_PATH = os.getcwd()
dotenv_path = join(CURR_PATH, '.env')
load_dotenv(dotenv_path)

GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
#########################################################################


def get_gcloud_creds():

    service_account_info = json.load(open(GOOGLE_APPLICATION_CREDENTIALS))
    audience = "https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"

    credentials = jwt.Credentials.from_service_account_info(
        service_account_info, audience=audience
    )
    return credentials

def sub_listen():
    creds = get_gcloud_creds()

    subscriber = pubsub.SubscriberClient(credentials=creds)
    subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

    logger.info(f"Listening for messages on {subscription_path}..\n")
    
    # Pull Messages Synchronously
    response = subscriber.pull(request={
        "subscription": subscription_path,
        "max_messages": MAX_MESSAGE,
    })

    for msg in response.received_messages:
        logger.info("Received message:", msg.message.data)
    
    ack_ids = [msg.ack_id for msg in response.received_messages]
    subscriber.acknowledge(
    request={
        "subscription": subscription_path,
        "ack_ids": ack_ids,
    })




