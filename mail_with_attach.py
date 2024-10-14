import os.path
import base64
import mimetypes  
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticate and get Gmail API service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message_with_attachment(sender, to, subject, message_text, file):
    """Create a message with an attachment."""
    # Create a MIMEMultipart message object
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Attach the body text
    message.attach(MIMEText(message_text, 'plain'))

    # Process the attachment
    content_type, encoding = mimetypes.guess_type(file)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)

    with open(file, 'rb') as f:
        file_content = MIMEBase(main_type, sub_type)
        file_content.set_payload(f.read())
        encoders.encode_base64(file_content)
        file_content.add_header(
            'Content-Disposition', f'attachment; filename="{os.path.basename(file)}"')
        message.attach(file_content)

    # Encode the message as base64 and return as a dict
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

def send_message(service, to, subject, message_text, file):
    """Send an email with an attachment."""
    try:
        sender = "atiq786313@gmail.com"
        message = create_message_with_attachment(sender, to, subject, message_text, file)
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        print(f"Message with attachment sent successfully: {sent_message}")
    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    # Authenticate and get Gmail service
    service = authenticate_gmail()

    # Define email details
    sender_email = 'atiq786313@gmail.com'
    receiver_email = 'atiqsm24@gmail.com'
    subject = 'Hello with Attachment'
    body = 'This email contains an attachment.'
    attachment_file = 'ASM.png'  # Replace with the actual file path

    # Send the email with attachment
    send_message(service, receiver_email, subject, body, attachment_file)
