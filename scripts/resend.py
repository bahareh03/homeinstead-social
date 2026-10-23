"""Resend one day's post to chosen platforms only (e.g. when Instagram failed but the others worked).
Usage (GitHub > Actions > Daily social post > Run workflow): date=YYYY-MM-DD, only=instagram"""
import os, re, sys, json, pathlib, requests
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import publish

date, only = os.environ["RESEND_DATE"], [p.strip() for p in os.environ["RESEND_ONLY"].split(",")]
issues = requests.get(f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues",
                      params={"labels": "report", "state": "all", "per_page": 30},
                      headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}"}, timeout=30).json()
body = next(i["body"] for i in issues if date in i["title"])
image = re.search(r"\]\((https://raw\.githubusercontent\.com\S+?\.jpg)\)", body).group(1)
caption = re.search(r"### Caption \(Facebook\)\n\n(.*?)\n\n---", body, re.S).group(1).strip()
ptype = re.search(r"\(([^)]+)\)\s*$", next(i["title"] for i in issues if date in i["title"])).group(1).replace(" ", "_")
post = {"date": date, "type": ptype, "image_url": image, "google_image_url": image.replace(".jpg", "-google.jpg"),
        "google": "", "facebook": caption, "instagram": caption, "social": caption, "google_ok": "google" in only}
publish.CFG["platforms"] = only
publish.CFG["make_platforms"] = only
print("Resent to:", publish.via_make(post), image)
