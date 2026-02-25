import requests
from dotenv import load_dotenv
import os

class SendOutEmail:
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
        
        self.url = f"https://{self.domain}.freshdesk.com/api/v2/tickets/outbound_email"
        

    def sendEmail(
        self,
        *,
        to_email: str, # required
        subject: str, # required
        body_html: str, # required
        email_config_id: int | None = None,
        cc_emails: list[str] | None = None,
        bcc_emails: list[str] | None = None,
        status: int = 5, # status to closed
        priority: int = 1, # low prio
        tags: list[str] | None = None,
        custom_fields: dict | None = None,
        attachments: list[str] | None = None,
        timeout: int = 30,
        ) -> dict:
        
        if not to_email or not subject or body_html is None:
            raise ValueError("to_email, subject, and body_html are required.")
        
        payload = {
            "description": body_html,
            "subject": subject,
            "email": to_email,
            "status": status,
            "priority": priority,
        }

        if email_config_id is not None:
            payload["email_config_id"] = int(email_config_id)
        if cc_emails:
            payload["cc_emails"] = cc_emails
        if bcc_emails:
            payload["bcc_emails"] = bcc_emails
        if tags:
            payload["tags"] = tags
        if custom_fields:
            payload["custom_fields"] = custom_fields

        auth = str((self.api_key, self.password))

        r = requests.post(self.url, auth=(str(self.api_key), str(self.password)), json=payload, timeout=timeout)

        if r.status_code != 201:
            raise RuntimeError(
                "Error code other than 201 was given, code: ",
                r.status_code, "message: ", r.text
            )

        ticket = r.json()

        return {
            "id": ticket.get("id"),
            "subject": ticket.get("subject"),
            "status": ticket.get("status"),
            "priority": ticket.get("priority"),
            "to": to_email,
            "email_config_id": ticket.get("email_config_id"),
            "created_at": ticket.get("created_at"),
            "updated_at": ticket.get("updated_at"),
        }


        