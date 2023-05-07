import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class Authentication:
    def __init__(self):
        self.users = {}

    def register_user(self, email: str):
        """
        Register a new user with the given email address
        """
        self.users[email] = {}

    def test(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            if not labels:
                print('No labels found.')
                return
            print('Labels:')
            for label in labels:
                print(label['name'])

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')

    def authenticate_user(self) -> str:
        """
        Authenticate the user using the Gmail API and return the user's email
        """
        # Load the user's credentials from the token.json file
        creds = None
        if os.path.exists('token.json'):
            with open('token.json', 'r') as token:
                creds = Credentials.from_authorized_user_info(info=json.load(token))
        # Check if the user is registered
        if creds:
            service = build('gmail', 'v1', credentials=creds)
            user_profile = service.users().getProfile(userId='me').execute()
            email = user_profile['emailAddress']
            if email in self.users:
                return email
        # Unregistered user or invalid credentials
        return None



#from Authentication import Authentication

# def main():
#     auth = Authentication()

#     while True:
#         print("1. Register user")
#         print("2. Authenticate user")
#         print("3. Exit")
#         choice = input("Enter your choice (1/2/3): ")

#         if choice == "1":
#             email = input("Enter user email: ")
#             auth.register_user(email)
#             print("User registered successfully!")
#         elif choice == "2":
#             #access_token = input("Enter ID token: ")
#             auth.test()
#             email = auth.authenticate_user()
#             if email:
#                 print(f"User {email} authenticated successfully!")
#             else:
#                 print("Invalid ID token or unregistered user!")
#         elif choice == "3":
#             break
#         else:
#             print("Invalid choice!")


# if __name__ == "__main__":
#     main()