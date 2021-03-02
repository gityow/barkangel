import logging
import requests
from discord import File
from flask import current_app, Flask, render_template, request, Flask, request
import yaml
import base64
import json
import os

from google.auth.transport import requests
from google.cloud import pubsub_v1
from google.oauth2 import id_token

from discord_bot import get_discord_bot
from parser_email_pdf import (get_all_etfs, compare, pretty_print)
from gmail_client import (find_ark_email, parse_email, setup_watch)

import threading
import google.cloud.logging


################## GOOGLE LOGGING ##################
# Instantiates a client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
client.get_default_handler()
client.setup_logging()

# Imports Python standard library logging
import logging

logger = logging.getLogger(__name__)
##########################################################

with open("paths.yml", "r") as f:
    paths = yaml.load(f, Loader=yaml.FullLoader)

################## LOAD .ENV ##################
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
#  api = Api(app)

# This is used in the push request handler to verify that the request came from
# pubsub and originated from a trusted source.
app.config['PUBSUB_VERIFICATION_TOKEN'] = \
    os.environ['PUBSUB_VERIFICATION_TOKEN']
app.config['TOPIC_ID'] = os.environ['TOPIC_ID']
app.config['PROJECT_ID'] = os.environ['PROJECT_ID']

###################################################

# Global list to store messages, tokens, etc. received by this instance.
MESSAGES = []
TOKENS = []
CLAIMS = []


# [START index]
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', messages=MESSAGES, tokens=TOKENS,
                               claims=CLAIMS)
    
# [END index]

# [START send_message]
@app.route('/send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        data = request.form.get('payload', 'Example payload').encode('utf-8')

        # Consider initializing the publisher client outside this function
        # for better latency performance.
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(app.config['PROJECT_ID'],
                                        app.config['TOPIC_ID'])
        future = publisher.publish(topic_path, data)
        future.result()

        return 'OK', 200

# [END send_message]

# [START push]
@app.route('/push-handlers/receive_messages', methods=['POST'])
def receive_messages_handler():
    # Verify that the request originates from the application.
    if (request.args.get('token', '') !=
            current_app.config['PUBSUB_VERIFICATION_TOKEN']):
        return 'Invalid request', 400
    
    # Verify that the push request originates from Cloud Pub/Sub.
    # try:
    #     # Get the Cloud Pub/Sub-generated JWT in the "Authorization" header.
    #     bearer_token = request.headers.get('Authorization')
    #     token = bearer_token.split(' ')[1]
    #     TOKENS.append(token)
    #     claim = id_token.verify_oauth2_token(token, requests.Request(),audience='example.com')
    #     CLAIMS.append(claim)
    # except Exception as e:
    #     return 'Invalid token: {}\n'.format(e), 400

    # envelope = json.loads(request.data.decode('utf-8'))
    # payload = base64.b64decode(envelope['message']['data'])
    # MESSAGES.append(payload)
    
    threading.Thread(target=task_send_message, kwargs={'dev':False}).start()  # TODO consider calling this outside to improve latency
    #task()
    
    # Returning any 2xx status indicates successful receipt of the message.
    return 'OK', 200
# [END push]

# [START download]
@app.route('/download', methods=['POST'])
def download_etfs():
    if (request.args.get('token', '') !=
            current_app.config['PUBSUB_VERIFICATION_TOKEN']):
        return 'Invalid request', 400
    
    #threading.Thread(target=task_send_message).start()  # TODO consider calling this outside to improve latency

    return 'OK', 200
# [END download]

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

    
def task_send_message(dev):
    
    logger.info('Started task...')
    #print(threading.current_thread().name) 

    # START PROCESS
    bot = get_discord_bot(dev)
    bot.send(content="Hey there! New Ark Email Received. I'm taking a look at current ARK ETF Holdings... woof!")

    # GET PDFs # TODO read from blob
    all_etfs_df, update_dt = get_all_etfs(latest=True)
    logger.info('Parsing complete')

    # GET NEW EMAIL
    message_id, email_dt = find_ark_email()
    email_df = parse_email(message_id)
    logger.info('new email parsed')

    # COMPARE DFs
    exec_buy = compare(email_df, all_etfs_df)
    bot.send("Woof! Analysis Complete! ")

    # REPORT RESULTS
    if len(exec_buy) == 0:
        bot.send("ARK had no new buys")
    elif len(exec_buy) > 0:
        all_etfs_df
        bot.send("New companies were added:")
        bot.send(pretty_print(exec_buy, email_dt, update_dt))
    
    pdf_files = [File(f'/tmp/{name}_etf.pdf') for name in paths['etf_names']]
    bot.send("For full reports see attached", files=pdf_files)

    # RENEW GMAIL WATCH 
    setup_watch()

    bot.send("Bark going to sleep now...")

# TODO write to blob        
def task_make_tables():
    all_etfs_df, update_dt = get_all_etfs(latest=True)
    

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    #app.run(port=8080,debug=True)
    app.run(debug=True)
