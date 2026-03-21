# gmail_service.py
import requests

def fetch_latest_emails(token):
    headers = {'Authorization': f'Bearer {token["access_token"]}'}
    # Get list of message IDs
    list_url = "https://www.googleapis.com/gmail/v1/users/me/messages?maxResults=10"
    list_res = requests.get(list_url, headers=headers).json()
    
    emails = []
    if 'messages' in list_res:
        for msg in list_res['messages']:
            # Fetch actual content for each ID
            detail_url = f"https://www.googleapis.com/gmail/v1/users/me/messages/{msg['id']}"
            detail_res = requests.get(detail_url, headers=headers).json()
            
            # Extract Subject and Snippet
            headers_list = detail_res.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers_list if h['name'] == 'Subject'), "No Subject")
            snippet = detail_res.get('snippet', "")
            
            emails.append({"subject": subject, "snippet": snippet})
    return emails