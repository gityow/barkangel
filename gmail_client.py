# https://developers.google.com/gmail/api/guides/push#protocol
request = {"labelIds": ["INBOX"], "topicName": "projects/myproject/topics/mytopic"}
gmail.users().watch(userId="me", body=request).execute()
