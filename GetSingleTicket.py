import requests
from dotenv import load_dotenv
import os

class GetSingleTicket:
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

    def _check(self, r):
        if r.status_code != 200:
            raise RuntimeError(
                "Error code other than 200 was given, code: ",
                r.status_code, "message: ", r.text
            )

    def getTicket(self, id):
        ticket_url = f"https://{self.domain}.freshdesk.com/api/v2/tickets/{id}"
        r_ticket = requests.get(
            ticket_url,
            params={"include": "requester"},
            auth=(str(self.api_key), str(self.password))
        )
        self._check(r_ticket)
        ticket = r_ticket.json()

        conv_url = f"https://{self.domain}.freshdesk.com/api/v2/tickets/{id}/conversations"
        r_conv = requests.get(conv_url, auth=(str(self.api_key), str(self.password)))
        self._check(r_conv)
        conversations = r_conv.json()

        return {
            "id": ticket.get("id"),
            "subject": ticket.get("subject"),
            "description_text": ticket.get("description_text"),
            "status": ticket.get("status"),
            "requester": ticket.get("requester"),
            "created_at": ticket.get("created_at"),
            "updated_at": ticket.get("updated_at"),
            "conversations": conversations,
        }