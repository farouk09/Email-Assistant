import base64
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# If modifying these SCOPES, delete the token.json file.
SCOPES = ["https://www.googleapis.com/auth/gmail.send",  "https://www.googleapis.com/auth/calendar"]


# Define the directory where token.json and credentials.json are stored
CREDENTIALS_DIR = os.path.join(os.path.dirname(__file__), "agent", "credentials")
TOKEN_PATH = "src/agent/credentials/token.json"
CREDENTIALS_PATH = "src/agent/credentials/credentials.json"


def get_gmail_service():
    
    creds = None 

    print("Token path:", TOKEN_PATH , "Credentials path:", CREDENTIALS_PATH)
    print(SCOPES)

    if os.path.exists(TOKEN_PATH):
        print("Token file exists")
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        print("Token file loaded")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    
    return build("gmail", "v1", credentials=creds)

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    
    return build("calendar", "v3", credentials=creds)

def create_message(to, subject, content):
    message = MIMEText(content)
    message["to"] = to
    message["subject"] = subject
    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}


#print(check_calendar_availability("2025-03-29"))

#write_email("faroukfobama@gmail.com", "Test Email", "This is a test email from Python!")