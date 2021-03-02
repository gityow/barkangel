import discord
from discord import Webhook, RequestsWebhookAdapter, File
import os

################## LOAD .ENV ##################
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

WEBHOOK_ID = os.environ.get('WEBHOOK_ID')
WEBHOOK_TOKEN = os.environ.get('WEBHOOK_TOKEN')

WEBHOOK_ID_DEBUG = os.environ.get('WEBHOOK_ID_DEBUG')
WEBHOOK_TOKEN_DEBUG = os.environ.get('WEBHOOK_TOKEN_DEBUG')
###################################################

def get_discord_bot(dev=False):

    # Create webhook
    if dev:
        webhook = Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter())
    else:
        webhook = Webhook.partial(WEBHOOK_ID_DEBUG, WEBHOOK_TOKEN_DEBUG, adapter=RequestsWebhookAdapter())
    
    return webhook