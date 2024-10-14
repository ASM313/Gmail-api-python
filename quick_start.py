import os.path
import base64
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

# Define the scopes (Gmail API read/write access)
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticate and get Gmail API service."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    # If it exists, load it, else authenticate new user.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials, log in and get new tokens.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use.
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Create a Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to, subject, message_text):
    """Create a message for an email."""
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw}

def send_message(service, sender, to, subject, message_text):
    """Send an email message."""
    try:
        message = create_message(sender, to, subject, message_text)
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        print(f"Message sent successfully: {sent_message['id']}")
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    # Authenticate and get Gmail service
    service = authenticate_gmail()
    
    # Define email details
    sender_email = 'Atiq786313@gmail.com'
    receiver_email = 'atiqsm24@gmail.com'
    subject = 'Hello from Gmail API'
    body = 'This is a test email sent through Gmail API using Python.'

    # Send the email
    send_message(service, sender_email, receiver_email, subject, body)
