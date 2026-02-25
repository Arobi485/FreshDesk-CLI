import requests
from dotenv import load_dotenv
import os

class GetTicketTimes:
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

    def getTime(self, id):
        ticket_url = f"https://{self.domain}.freshdesk.com/api/v2/tickets/{id}/time_entries"
        r_ticket = requests.get(
            ticket_url,
            auth=(str(self.api_key), str(self.password))
        )
        self._check(r_ticket)
        ticket = r_ticket.json()

        return ticket


# ADD A WAY FOR THIS TO ALSO TRACK MAINTANENCE TIMES
#
#
#
#
#
#
#
#
#
#
