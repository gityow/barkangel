import json
import pickle
import os.path
from googleapiclient.discovery import build
from concurrent.futures import TimeoutError
from google.cloud import pubsub
from google.auth import jwt

# Documentation of pubsub here
# https://googleapis.dev/python/pubsub/latest/index.html

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

    print(f"Listening for messages on {subscription_path}..\n")
    
    # Pull Messages Synchronously
    response = subscriber.pull(request={
        "subscription": subscription_path,
        "max_messages": MAX_MESSAGE,
    })

    for msg in response.received_messages:
        print("Received message:", msg.message.data)
    
    ack_ids = [msg.ack_id for msg in response.received_messages]
    subscriber.acknowledge(
    request={
        "subscription": subscription_path,
        "ack_ids": ack_ids,
    })




