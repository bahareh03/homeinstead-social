"""Run ONCE on your computer to get the Google refresh token and your account/location IDs.
   pip install google-auth-oauthlib requests
   python scripts/get_google_token.py client_secret.json"""
import sys
import requests
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    sys.argv[1], scopes=["https://www.googleapis.com/auth/business.manage"])
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
h = {"Authorization": f"Bearer {creds.token}"}

print("\nGBP_CLIENT_ID     =", creds.client_id)
print("GBP_CLIENT_SECRET =", creds.client_secret)
print("GBP_REFRESH_TOKEN =", creds.refresh_token)

accts = requests.get("https://mybusinessaccountmanagement.googleapis.com/v1/accounts", headers=h).json()
for a in accts.get("accounts", []):
    aid = a["name"].split("/")[1]
    locs = requests.get(f"https://mybusinessbusinessinformation.googleapis.com/v1/{a['name']}/locations",
                        params={"readMask": "name,title"}, headers=h).json()
    for l in locs.get("locations", []):
        print(f"\n{l['title']}\n  GBP_ACCOUNT_ID  = {aid}\n  GBP_LOCATION_ID = {l['name'].split('/')[1]}")
