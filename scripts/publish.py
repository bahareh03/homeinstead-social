"""Publish state/next_post.json to Facebook + Instagram + Google Business Profile via Metricool."""
import datetime, json, os, pathlib
from zoneinfo import ZoneInfo
import requests, yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
STATE = ROOT / "state"
API = "https://app.metricool.com/api/v2/scheduler/posts"


def send(text, networks, image_url, when):
    body = {"publicationDate": {"dateTime": when, "timezone": CFG["business"]["timezone"]},
            "text": text, "providers": [{"network": n} for n in networks],
            "autoPublish": True, "draft": False, "shortener": False,
            "saveExternalMediaFiles": True, "media": [image_url] if image_url else []}
    if "facebook" in networks:
        body["facebookData"] = {"type": "POST"}
    if "instagram" in networks:
        body["instagramData"] = {}
    if "gmb" in networks:
        body["gmbData"] = {}
    r = requests.post(API, timeout=60, json=body,
                      params={"blogId": CFG["metricool"]["blog_id"], "userId": os.environ["METRICOOL_USER_ID"]},
                      headers={"X-Mc-Auth": os.environ["METRICOOL_TOKEN"]})
    print(networks, r.status_code, r.text[:300])
    r.raise_for_status()


def main():
    post = json.loads((STATE / "next_post.json").read_text())
    if not post.get("image_url"):
        raise SystemExit("No hosted image: Instagram needs one. Set up the Cloudflare R2 secrets.")
    when = (datetime.datetime.now(ZoneInfo(CFG["business"]["timezone"])) +
            datetime.timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    send(post["social"], CFG["metricool"]["networks_social"], post["image_url"], when)
    send(post["google"], CFG["metricool"]["networks_google"], post["image_url"], when)

    hf = STATE / "history.json"
    h = json.loads(hf.read_text()) if hf.exists() else {}
    for k in ("keywords", "media", "published", "types", "franchisor"):
        h.setdefault(k, [])
    h["published"].append(f"{post['date']} {post['type']}")
    h["types"].append(post["type"])
    h["keywords"] += post["keywords"]
    if post.get("franchisor_key"):
        h["franchisor"].append(post["franchisor_key"])
    hf.write_text(json.dumps(h, indent=2))


if __name__ == "__main__":
    main()
