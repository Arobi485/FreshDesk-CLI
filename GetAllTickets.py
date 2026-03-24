import requests
import datetime

from dotenv import load_dotenv
import os

class GetAllTickets:
    def __init__(self):
        self.daysBack = 2
        self.perPage = 100

        load_dotenv()

        self.api_key = os.getenv("FRESHDESK_API_KEY")
        self.password = os.getenv("FRESHDESK_PASSWORD")
        self.domain = os.getenv("FRESHDESK_DOMAIN")

        
        missing = [name for name, value in {
            "FRESHDESK_API_KEY": self.api_key,
            "FRESHDESK_PASSWORD": self.password,
            "FRESHDESK_DOMAIN": self.domain,
        }.items() if not value]

        if missing:
            raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

        self.url = f"https://{self.domain}.freshdesk.com/api/v2/tickets?include=requester"

    def addToTicket(self, ticket, extracted_tickets):
        extracted_tickets.append({
            "id": ticket.get("id"),
            "subject": ticket.get("subject"),
            "status": ticket.get("status"),
            "requester": ticket.get("requester"),
            "created_at": ticket.get("created_at"),
            "updated_at": ticket.get("updated_at"),
            "emailConfigID": ticket.get("email_config_id"),
            "install": "False"
        })


    def getOpenTickets(self, installs):
        today = datetime.date.today()
        last_week = today - datetime.timedelta(days=2)
        formatted_date = last_week.strftime('%Y-%m-%d') + "T00:00:00Z"

        page = 1
        extracted_tickets = []

        while True:
            params = {
                "updated_since": formatted_date,
                "page": page,
                "per_page": self.perPage
            }

            r = requests.get(self.url, params=params, auth=(str(self.api_key), str(self.password)))

            if r.status_code != 200:
                raise RuntimeError(f"Error code other than 200 was given, code: ", r.status_code, "message: ", r.text)

            tickets = r.json()
                
            if not tickets:
                break
            
            for ticket in tickets:
                if installs == False:
                    if ticket.get("status") == 2:
                        self.addToTicket(ticket, extracted_tickets)
                else:
                    self.addToTicket(ticket, extracted_tickets)

            page += 1

        extracted_tickets.sort(key=lambda t: t["updated_at"], reverse=True)

        return extracted_tickets
        