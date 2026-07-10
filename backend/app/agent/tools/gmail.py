import os
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
# gmail.readonly allows us to look at emails without accidental deletion risks
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def fetch_gmail_job_updates() -> List[Dict[str, Any]]:
    """
    Authenticates with the Gmail API and searches the user's inbox 
    for relevant recruitment and application emails from the past 7 days.
    """
    creds = None
    token_path = 'token.json'
    creds_path = 'credentials.json' # Downloaded from Google Developer Console

    # 1. Handle Local Token Authentication
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                print("[GMAIL TOOL] Token refresh failed. Re-authenticating...")
                creds = None
        
        if not creds:
            if not os.path.exists(creds_path):
                print("[WARNING] credentials.json not found! Skipping Gmail scan and returning empty list.")
                return get_mock_gmail_jobs()
                
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    # 2. Query the Live Gmail Inbox
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Calculate date threshold (7 days ago)
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')
        
        # Construct a sharp Gmail search query string
        search_query = f'after:{seven_days_ago} "recruiter" OR "job application" OR "interview offer"'
        
        # Fetch matching message ID lists
        response = service.users().messages().list(userId='me', q=search_query, maxResults=5).execute()
        messages = response.get('messages', [])
        
        normalized_emails = []
        
        for msg in messages:
            # Fetch individual email payload records
            msg_details = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            payload = msg_details.get('payload', {})
            headers = payload.get('headers', [])
            
            # Extract basic metadata headers
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
            snippet = msg_details.get('snippet', '')
            
            normalized_emails.append({
                "source": "User Gmail Inbox Scan",
                "id": msg['id'],
                "company": sender.split('<')[0].strip(), # Basic regex cleanup for display names
                "title": f"Email: {subject}",
                "location": "Inferred Remote / Direct Outreach",
                "description": f"Sender: {sender}\nSubject: {subject}\nSnippet: {snippet}",
                "url": f"https://mail.google.com/mail/u/0/#inbox/{msg['id']}",
                "posted_at": datetime.now().isoformat() # Timestamp marker
            })
            
        print(f"[GMAIL TOOL] Successfully synchronized {len(normalized_emails)} direct inbox leads.")
        return normalized_emails

    except HttpError as error:
        print(f"[ERROR] Gmail API Connectivity failure: {error}")
        return []

def get_mock_gmail_jobs() -> List[Dict[str, Any]]:
    """Simulated inbox ingestion baseline data for sandboxed local testing."""
    return [
        {
            "source": "Mock Gmail Ingestion Stream",
            "id": "gmail-mock-101",
            "company": "TalentAcquisition Global",
            "title": "Email: Inbound Recruiter Outreach - AI Infrastructure",
            "location": "Remote",
            "description": "Sender: recruiter@talentglobal.com\nSubject: Opportunities at Apex Solutions\nSnippet: Hi Conrad, I stumbled across your profile on GitHub while looking into LangGraph pipeline builds. We are expanding our LLMOps divisions and looking for core infrastructural developers...",
            "url": "https://mail.google.com",
            "posted_at": datetime.now().isoformat()
        }
    ]