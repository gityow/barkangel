import logging
import requests
from discord import File
from flask import Flask, request
import yaml

with open("paths.yml", "r") as f:
    paths = yaml.load(f, Loader=yaml.FullLoader)

app = Flask(__name__)

@app.route('/push-handlers/receive_messages', methods=['POST'])
def receive_messages_handler():
    # Verify that the request originates from the application.
    if (request.args.get('token', '') !=
            current_app.config['PUBSUB_VERIFICATION_TOKEN']):
        return 'Invalid request', 400

    # Verify that the push request originates from Cloud Pub/Sub.
    try:
        # Get the Cloud Pub/Sub-generated JWT in the "Authorization" header.
        bearer_token = request.headers.get('Authorization')
        token = bearer_token.split(' ')[1]
        TOKENS.append(token)

        # Verify and decode the JWT. `verify_oauth2_token` verifies
        # the JWT signature, the `aud` claim, and the `exp` claim.
        # Note: For high volume push requests, it would save some network
        # overhead if you verify the tokens offline by downloading Google's
        # Public Cert and decode them using the `google.auth.jwt` module;
        # caching already seen tokens works best when a large volume of
        # messages have prompted a single push server to handle them, in which
        # case they would all share the same token for a limited time window.
        claim = id_token.verify_oauth2_token(token, requests.Request(),
                                             audience='example.com')
        CLAIMS.append(claim)
    except Exception as e:
        return 'Invalid token: {}\n'.format(e), 400

    envelope = json.loads(request.data.decode('utf-8'))
    payload = base64.b64decode(envelope['message']['data'])
    MESSAGES.append(payload)
    
    main()
    # Returning any 2xx status indicates successful receipt of the message.
    return 'OK', 200

# @app.route('/new_email', methods=['GET'])
# def hello():
#     """ Wake up Bark """
    
#     if request.method == 'GET':
#         payload = request.args
#         print(user)

#         print('An email from ARK was received')

#         main()

        

#     return 200


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

    
def main():
    # START PROCESS
    bot = get_discord_bot()
    bot.send(content="Hey there! New Ark Email Received. I'm taking a look at current ARK ETF Holdings... woof!")

    # PARSE PDFs
    import parser_email_pdf
    all_etfs_df, update_dt = parse_email.get_all_etfs(latest=True)
    print('Parsing complete')

    # GET NEW EMAIL
    import gmail_client
    message_id, email_dt = gmail_client.find_ark_email()
    email_df = gmail_client.parse_email(message_id)
    print('new email parsed')

    # COMPARE DFs
    import parse_email
    exec_buy = parse_email.compare(email_df, all_etfs_df)
    
    bot.send("Woof! Analysis Complete! ")

    # REPORT RESULTS
    if len(exec_buy) == 0:
        bot.send("ARK had no new buys")
    elif len(exec_buy) > 0:
        all_etfs_df
        bot.send("New companies were added:")
        bot.send(pretty_print(exec_buy, email_dt, update_dt))
    
    from discord import File
    pdf_files = [File(f'./temp/{name}_etf.pdf') for name in paths['etf_names']]
    bot.send("For full reports see attached", files=pdf_files)
    bot.send("Bark going to sleep now...")
        

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
