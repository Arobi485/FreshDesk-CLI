from dotenv import load_dotenv
import os
import requests

load_dotenv()

api_key = os.getenv("FRESHDESK_API_KEY")
password = os.getenv("FRESHDESK_PASSWORD")
domain = os.getenv("FRESHDESK_DOMAIN")


missing = [name for name, value in {
    "FRESHDESK_API_KEY": api_key,
    "FRESHDESK_PASSWORD": password,
    "FRESHDESK_DOMAIN": domain,
}.items() if not value]

if missing:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

url = f"https://{domain}.freshdesk.com/api/v2/email_configs"

r = requests.get(url, auth=(str(api_key), str(password)))
print(r.json())
