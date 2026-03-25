import requests
from dotenv import load_dotenv
import os

class SendReply:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("FRESHDESK_API_KEY")
        self.domain = os.getenv("FRESHDESK_DOMAIN")
        self.password = os.getenv("FRESHDESK_PASSWORD")

        missing = [name for name, value in {
            "FRESHDESK_API_KEY": self.api_key,
            "FRESHDESK_DOMAIN": self.domain,
        }.items() if not value]
        if missing:
            raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
        
    def reply_to_ticket(self, ticket_id, message, from_email=None, cc_emails=None, bcc_emails=None):
        url = f"https://{self.domain}.freshdesk.com/api/v2/tickets/{ticket_id}/reply"

        payload = {
            "body": f"<div>{message}</div>"
        }

        if from_email:
            payload["from_email"] = from_email
        if cc_emails:
            payload["cc_emails"] = cc_emails
        if bcc_emails:
            payload["bcc_emails"] = bcc_emails

        response = requests.post(
            url,
            auth=(str(self.api_key), str(self.password)),
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        if response.ok:
            print("Reply sent successfully")
            return response.json()
        else:
            print("Failed to send reply")
            print(response.status_code, response.text)
            return None