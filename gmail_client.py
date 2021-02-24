from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import json
import pickle
import os.path
import pandas as pd
from pandas import DataFrame
from datetime import datetime
import base64

################## LOAD .ENV ##################
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
WEBHOOK_ID = os.environ.get('WEBHOOK_ID')
WEBHOOK_TOKEN = os.environ.get('WEBHOOK_TOKEN')
PROJECT_ID = os.environ.get('PROJECT_ID')

###################################################


def get_gmail_creds():
    """returns credentials to build gmail api service

    Returns
    -------
    google.oauth2.credentials.Credentials
        credentials to access gmail api
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'creds', 'token.pickle')
    creds_json_path = os.path.join(os.path.dirname(__file__), '..', 'creds', 'credentials.json')

    if os.path.exists(creds_path):
        with open(creds_path, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_json_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("/tmp/token.pickle", 'wb') as token:
            pickle.dump(creds, token)

    return creds

def setup_watch():
    """
    Call watch everyday to make sure gmail inbox is watched by pub/sub topic

    """
    creds = get_gmail_creds()

    request = {
    'labelIds': ['INBOX'],
    'topicName': f'projects/{PROJECT_ID}/topics/gmail_trigger'
    }

    service = build('gmail', 'v1', credentials=creds)
    resp = service.users().watch(userId='me', body=request).execute()
    print(resp)

    return resp

def get_gmail_labels():
    """ return of gmail labels
    """
    creds = get_gmail_creds()
    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

def get_mail_list(history_id):
    creds = get_gmail_creds()
    service = build('gmail', 'v1', credentials=creds)

    message_ids = service.users().messages().list(userId='me').execute()['messages']
        
    for i in message_ids:
        mes_id = i['id']
        print(f'----- looking at: {mes_id} -----', )

        mes = service.users().messages().get(userId='me', id=mes_id).execute()

        print('history id is :', mes['historyId'])
        print('mimetype is :', mes['payload']['mimeType'])
        print(f"{mes['payload']['headers'][-6]['name']} is : {mes['payload']['headers'][-6]['value']}" ) # from
        print(f"{mes['payload']['headers'][-3]['name']} is : {mes['payload']['headers'][-3]['value']}" ) # subject
        if mes['historyId'] == history_id: 
            print(mes)

def find_ark_email():
    """ Return id of email

    Returns
    -------
    str
        message id of email
    """
    creds = get_gmail_creds()
    service = build('gmail', 'v1', credentials=creds)
    print('getting all emails')
    message_ids = service.users().messages().list(userId='me',labelIds=['Label_4122650900776215210'],includeSpamTrash=False).execute()['messages']
    
    max_id = 0
    max_epoch_ms = 0

    for i in message_ids:
        mes_id = i['id']
        print(f'looking at {mes_id}')
        mes = service.users().messages().get(userId='me', id=mes_id).execute()
        # find most recent email
        if int(mes['internalDate'])/1000.0 > max_epoch_ms :
            max_id = mes_id 
            max_epoch_ms = int(mes['internalDate'])/1000.0
        
    
    email_date_time = datetime.fromtimestamp(max_epoch_ms).strftime('%Y-%m-%d %H:%M:%S')
    print(f'found most recent ark email id {max_id} sent on :', email_date_time)

    return (max_id, email_date_time)


def parse_email(message_id: str) -> DataFrame:
    """ parses message payload returns all etf holding updates within email body

    Parameters
    ----------
    message_id : str
        id of most recent email

    Returns
    -------
    DataFrame
        Updates within email body
    """
    # https://stackoverflow.com/questions/46352216/python-gmail-api-base64-decode-strange-chars-in-email-body

    # message_id = "177a725558a62689" # test ARK email
    # message_id = "177a73785855e8fa" # simple email

    print(f'Parsing Email Body of {message_id}')
    creds = get_gmail_creds()
    service = build('gmail', 'v1', credentials=creds)
    message = service.users().messages().get(userId='me', id=message_id).execute()

    email_content = ''

    if 'data' in message['payload']['body'].keys():
            email_content+= message['payload']['body']['data']
    else:

        for part in message['payload']['parts']:
            email_content = part['body']['data'] + email_content
    
    mes_bytes = bytes(str(email_content),encoding='utf-8')
    html_string = base64.urlsafe_b64decode(mes_bytes)
    print(f'Found the following html body \n {html_string}')
    
    results = pd.read_html(html_string)[0]
    results = results[1:]
    columns = ['Num', 'Fund', 'Date', 'Direction', 'Ticker', 'CUSIP', 'Company', 'Shares', '% of ETF']
    results.columns = columns

    print(results)

    return results
    


