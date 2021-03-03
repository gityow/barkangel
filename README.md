Setup Instructions

1. pip install -r requirements.txt
2. Create .env file
3. mkdir creds folder
4. Make a `credentials.json` file, this is login for the gmail api.
5. Get google app crednetials and save in creds folder. For more information, see https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys . Set the path of this in the `.env` file under `GOOGLE_APPLICATION_CREDENTIALS`

Deploy locally
1. `$ export FLASK_APP=hello.py`
   `$ export FLASK_ENV=development`
   `$ flask run`
2. Make a curl request
`curl --header "Content-Type: application/json" -d @sample_message.json http://localhost:8080/push-handlers/receive_messages?token=test`

Live app in app engine:
https://barkangelinvest-1613342810822.nn.r.appspot.com
Make a curl request
`curl --header "Content-Type: application/json" -d @sample_message.json https://barkangelinvest-1613342810822.nn.r.appspot.com/push-handlers/receive_messages?token=test`

References:  
- setting up pub/sub push notifications https://cloud.google.com/run/docs/tutorials/pubsub#looking_at_the_code
- pubsub app engine code sample https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/appengine/standard_python3/pubsub
- app.yaml file configuration for app engine https://cloud.google.com/appengine/docs/standard/python3/config/appref#handlers_element
- deploying flask app python37 on GCP https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab
- https://cloud.google.com/appengine/docs/standard/python3/using-temp-files
- pdf reader without java https://towardsdatascience.com/how-to-extract-text-from-pdf-245482a96de7
- good read on authentication but not using these credentials https://realpython.com/flask-google-login/
- these were my vibes https://medium.com/analytics-vidhya/deployment-blues-why-wont-my-flask-web-app-just-deploy-2ac9092a1b40#c18b
- all files deployed on GAE https://stackoverflow.com/questions/40805182/see-the-files-that-will-be-deploy-to-google-appengine
- absolute and relative paths on GAE https://stackoverflow.com/questions/5050615/how-to-get-application-root-path-in-gae
- implicit application credentials https://cloud.google.com/docs/authentication/production#auth-cloud-implicit-python
- timezone on GAE is UTC (http://timezones.appspot.com/), bark times would be 5 hours ahead of EST.  
- Installing Java SDK in GAE https://stackoverflow.com/questions/59925185/installing-java-in-google-app-engine-with-python-runtime
- Dockerfile with both python and java https://stackoverflow.com/questions/51121875/how-to-run-docker-with-python-and-java
- Flask Deployment https://stackoverflow.com/questions/54028169/flask-app-deployment-on-google-app-engine-flex-using-docker

Feature Roadmap:
- [ ] refine push notification criteria (currently pushes upon new draft, read email, moved to bin)
- [ ] use content of push notification to parse email
- [ ] persisting data and loading to a database (ensure pdfs holdings before email, track changes over time) - https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-code-sample
- [ ] using java sdk in python runtime
- [x] setting up logging https://cloud.google.com/logging/docs/setup/python



