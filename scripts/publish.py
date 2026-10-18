"""Publish state/next_post.json directly to Facebook, Instagram and Google Business Profile (all free APIs).
Each platform is tried separately, so one failing doesn't stop the others."""
import json, os, pathlib, time
import requests, yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
STATE = ROOT / "state"
GRAPH = "https://graph.facebook.com/v21.0"


def wait_until_live(url, tries=12):
    """The image was just pushed to GitHub; wait until its public link works."""
    for _ in range(tries):
        if requests.head(url, timeout=15).status_code == 200:
            return
        time.sleep(10)
    raise RuntimeError(f"Image not reachable: {url}")


def facebook(post):
    r = requests.post(f"{GRAPH}/{os.environ['FB_PAGE_ID']}/photos", timeout=60, data={
        "url": post["image_url"], "caption": post.get("facebook", post["social"]), "access_token": os.environ["META_PAGE_TOKEN"]})
    r.raise_for_status()
    return r.json().get("post_id")


def instagram(post):
    ig, tok = os.environ["IG_USER_ID"], os.environ["META_PAGE_TOKEN"]
    r = requests.post(f"{GRAPH}/{ig}/media", timeout=60,
                      data={"image_url": post["image_url"], "caption": post.get("instagram", post["social"])[:2200], "access_token": tok})
    r.raise_for_status()
    cid = r.json()["id"]
    for _ in range(12):                              # wait for Instagram to process the image
        s = requests.get(f"{GRAPH}/{cid}", params={"fields": "status_code", "access_token": tok}, timeout=30)
        if s.json().get("status_code") == "FINISHED":
            break
        time.sleep(5)
    r = requests.post(f"{GRAPH}/{ig}/media_publish", timeout=60, data={"creation_id": cid, "access_token": tok})
    r.raise_for_status()
    return r.json()["id"]


def google(post):
    if os.getenv("MAKE_WEBHOOK_URL"):            # free route: Make.com publishes to Google for us
        cta_url = CFG["business"]["recruitment_url"] if post["type"] == "recruitment" else CFG["business"]["website"]
        r = requests.post(os.environ["MAKE_WEBHOOK_URL"], timeout=60, json={
            "summary": post["google"], "image_url": post["image_url"],
            "cta_type": "LEARN_MORE", "cta_url": cta_url, "phone": CFG["business"]["phone"],
            "type": post["type"], "date": post["date"]})
        r.raise_for_status()
        return "sent to Make.com"
    t = requests.post("https://oauth2.googleapis.com/token", timeout=20, data={
        "client_id": os.environ["GBP_CLIENT_ID"], "client_secret": os.environ["GBP_CLIENT_SECRET"],
        "refresh_token": os.environ["GBP_REFRESH_TOKEN"], "grant_type": "refresh_token"})
    t.raise_for_status()
    url = (f"https://mybusiness.googleapis.com/v4/accounts/{os.environ['GBP_ACCOUNT_ID']}"
           f"/locations/{os.environ['GBP_LOCATION_ID']}/localPosts")
    cta = {"actionType": "CALL"}
    if post["type"] == "recruitment":
        cta = {"actionType": "LEARN_MORE", "url": CFG["business"]["recruitment_url"]}
    body = {"languageCode": "en-GB", "topicType": "STANDARD", "summary": post["google"], "callToAction": cta,
            "media": [{"mediaFormat": "PHOTO", "sourceUrl": post.get("google_image_url", post["image_url"])}]}
    r = requests.post(url, json=body, timeout=60, headers={"Authorization": f"Bearer {t.json()['access_token']}"})
    r.raise_for_status()
    return r.json().get("name")


PLATFORMS = {"facebook": (facebook, "META_PAGE_TOKEN"),
             "instagram": (instagram, "IG_USER_ID"),
             "google": (google, "GOOGLE_READY")}


def via_make(post):
    """One call to the Make.com scenario; its router posts to Google, Facebook and Instagram
    (each route has a filter on the matching yes/no field below)."""
    b = CFG["business"]
    cta_url = b["recruitment_url"] if post["type"] == "recruitment" else b["website"]
    to = {"google": post.get("google_ok", True), "facebook": True, "instagram": True}
    to = {k: v and k in CFG["platforms"] and k in CFG.get("make_platforms", ["google"]) for k, v in to.items()}
    r = requests.post(os.environ["MAKE_WEBHOOK_URL"], timeout=60, json={
        "summary": post["google"], "image_url": post["image_url"],
        "google_image_url": post.get("google_image_url", post["image_url"]),
        "cta_type": "LEARN_MORE", "cta_url": cta_url, "phone": b["phone"],
        "facebook_caption": post.get("facebook", post["social"]),
        "instagram_caption": post.get("instagram", post["social"])[:2200],
        "post_google": "yes" if to["google"] else "no",
        "post_facebook": "yes" if to["facebook"] else "no",
        "post_instagram": "yes" if to["instagram"] else "no",
        "type": post["type"], "date": post["date"]})
    r.raise_for_status()
    return [k for k, v in to.items() if v]


def main():
    post = json.loads((STATE / "next_post.json").read_text())
    if not post.get("image_url"):
        raise SystemExit("No image link: Instagram needs one.")
    wait_until_live(post["image_url"])

    done, failed = [], []
    if os.getenv("MAKE_WEBHOOK_URL"):
        try:
            done = via_make(post)
            print("Sent to Make.com for:", ", ".join(done) or "nothing")
        except Exception as e:
            print("Make.com FAILED", e, getattr(getattr(e, "response", None), "text", "")[:300])
            failed.append("make")
    handled = set(CFG.get("make_platforms", ["google"])) if os.getenv("MAKE_WEBHOOK_URL") else set()
    if os.getenv("GBP_REFRESH_TOKEN"):
        os.environ["GOOGLE_READY"] = "1"
    for name in CFG["platforms"]:
        if name in handled:
            continue
        fn, needed_secret = PLATFORMS[name]
        if name == "google" and not post.get("google_ok", True):
            print("google: skipped (this post type isn't shown on Google)")
            continue
        if not os.getenv(needed_secret):
            print(f"{name}: skipped (not set up yet)")
            continue
        try:
            print(f"{name}: published", fn(post))
            done.append(name)
        except Exception as e:
            detail = getattr(getattr(e, "response", None), "text", "")[:300]
            print(f"{name}: FAILED {e} {detail}")
            failed.append(name)

    if done:
        hf = STATE / "history.json"
        h = json.loads(hf.read_text()) if hf.exists() else {}
        for k in ("keywords", "media", "published", "types", "franchisor"):
            h.setdefault(k, [])
        h["published"].append(f"{post['date']} {post['type']} -> {', '.join(done)}")
        h["types"].append(post["type"])
        h["keywords"] += post["keywords"]
        h.setdefault("layouts", []).append(post.get("layout", ""))
        if post.get("photo"):
            h["media"].append(post["photo"])
        if post.get("franchisor_key"):
            h["franchisor"].append(post["franchisor_key"])
        hf.write_text(json.dumps(h, indent=2))
    (STATE / "publish_result.json").write_text(json.dumps({"done": done, "failed": failed}))
    if failed:
        raise SystemExit(f"Failed: {failed}")
    if not done:
        print("Nothing published: no platform set up yet for this post type.")   # shows red in GitHub + emails you


if __name__ == "__main__":
    main()
