Setup Instructions

1. pip install -r requirements.txt
2. Create .env file
3. mkdir creds folder
4. Make a `credentials.json` file, this is login for the gmail api.
5. Get google app crednetials and save in creds folder. For more information, see https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys . Set the path of this in the `.env` file under `GOOGLE_APPLICATION_CREDENTIALS`
6. Grant 


References:  
- setting up pub/sub push notifications https://cloud.google.com/run/docs/tutorials/pubsub#looking_at_the_code
