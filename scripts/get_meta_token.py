"""Run ONCE on your computer to get a permanent Facebook Page token + your Instagram account ID.
   python scripts/get_meta_token.py APP_ID APP_SECRET SHORT_LIVED_USER_TOKEN
Get the short-lived user token from developers.facebook.com/tools/explorer with permissions:
pages_show_list, pages_manage_posts, pages_read_engagement, instagram_basic, instagram_content_publish"""
import sys
import requests

G = "https://graph.facebook.com/v21.0"
app_id, app_secret, short = sys.argv[1:4]

long_user = requests.get(f"{G}/oauth/access_token", params={
    "grant_type": "fb_exchange_token", "client_id": app_id,
    "client_secret": app_secret, "fb_exchange_token": short}).json()["access_token"]

pages = requests.get(f"{G}/me/accounts", params={"access_token": long_user}).json()["data"]
for p in pages:                      # page tokens from a long-lived user token never expire
    ig = requests.get(f"{G}/{p['id']}", params={"fields": "instagram_business_account",
                                               "access_token": p["access_token"]}).json()
    print(f"\nPage: {p['name']}")
    print("  FB_PAGE_ID      =", p["id"])
    print("  META_PAGE_TOKEN =", p["access_token"])
    print("  IG_USER_ID      =", ig.get("instagram_business_account", {}).get("id", "(no Instagram linked)"))
