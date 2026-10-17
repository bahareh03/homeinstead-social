"""Decide today's post type, write the text, make the image.  Output: state/next_post.json"""
import datetime, json, os, pathlib, random, re
from zoneinfo import ZoneInfo
import requests, yaml
from image import make_card, host, pick_photo, pick_layout
from content_bank import BANK, EDUCATION_POINTS

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
B = CFG["business"]
STATE = ROOT / "state"
KW = json.loads((STATE / "keywords.json").read_text()) if (STATE / "keywords.json").exists() \
    else {"top": [], "gaps": [], "own_images": []}
HF = STATE / "history.json"
H = json.loads(HF.read_text()) if HF.exists() else {}
for k in ("keywords", "media", "published", "types", "franchisor", "layouts"):
    H.setdefault(k, [])

TODAY = datetime.datetime.now(ZoneInfo(B["timezone"])).date()
MONTH = TODAY.strftime("%Y-%m")


# ---------- what to post today ----------
def franchisor_item():
    folder = ROOT / CFG["franchisor"]["folder"] / MONTH
    used_this_month = [f for f in H["franchisor"] if f.startswith(MONTH)]
    if len(used_this_month) >= CFG["franchisor"]["per_month"] or not folder.exists():
        return None
    for img in sorted(folder.iterdir()):
        key = f"{MONTH}/{img.name}"
        if img.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp") and key not in H["franchisor"]:
            cap = img.with_suffix(".txt")
            return {"key": key, "image": img, "caption": cap.read_text().strip() if cap.exists() else ""}
    return None


def post_type():
    t = CFG["weekly_plan"][TODAY.weekday()]
    if t == "choice" and (TODAY.weekday() == 1 or TODAY.day >= 22):   # Tuesdays, or catch-up late in month
        item = franchisor_item()
        if item:
            return "franchisor", item
    return t, None


def rotate(name, items):
    return items[H["types"].count(name) % len(items)]


# ---------- writing ----------
BRIEFS = {
    "difference": "What makes us different from other Leeds home care companies: visits of at least an hour, "
                  "a consistent care professional matched to each client, relationship-led care.",
    "education": "An educational post about {topic}: the signs families should look out for and practical tips. "
                 "Accurate, reassuring, no medical claims; suggest speaking to a GP where relevant.",
    "live_in": "Live-in care at home as an alternative to a care home: what it is, who it suits, staying with "
               "pets, routines and neighbours, peace of mind for families.",
    "recruitment": "A recruitment post for care professionals in Leeds: no experience needed, full training, "
                   "flexible hours, visits of at least an hour so you never rush. Apply at {recruitment_url}.",
    "choice": "A post about: {topic}. It should make families choose us over other home care companies in Leeds.",
    "franchisor": "Rewrite this franchisor-supplied content for our local Leeds office, keeping its message: {caption}",
}


def claude(prompt):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    r = requests.post("https://api.anthropic.com/v1/messages", timeout=90,
                      headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                      json={"model": "claude-sonnet-5-5", "max_tokens": 1800,
                            "messages": [{"role": "user", "content": prompt}]})
    if not r.ok:
        print("Claude API failed, using fallback wording:", r.text[:200])
        return None
    m = re.search(r"\{.*\}", r.json()["content"][0]["text"], re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        return None


def write(ptype, brief, keywords, topic, area):
    prompt = (f"You write social posts for {B['name']}, a home care provider in {B['area']} (phone {B['phone']}).\n"
              f"Task: {brief}\n"
              f"Use these search phrases naturally, once each, only where they fit: {', '.join(keywords) or 'none'}.\n"
              f"Mention the Leeds area '{area}' once, naturally.\n"
              "What performs best for home care: open with a hook families recognise (a worry, a sign, a question); "
              "ease guilt; be warm and specific; one clear call to action.\n"
              "Rules: plain British English, no prices, no client names, no made-up reviews, quotes or statistics, "
              "no claims about ratings or awards.\n"
              "Return ONLY JSON with keys:\n"
              '"headline": max 7 words for the image,\n'
              '"hook": a question a worried family member might ask, max 9 words,\n'
              '"points": 3 short items, max 6 words each (signs, tips or benefits),\n'
              '"myth": a common misconception, max 9 words, "fact": the truth, max 14 words,\n'
              '"body": the post text, 400-700 characters, first line is the hook, emojis sparingly, '
              'ends with a call to action, no hashtags,\n'
              '"google": Google Business Profile version, 400-900 characters, no hashtags or emojis, '
              'focused on the service and why to choose us, ends with a call to action.')
    out = claude(prompt)
    if out and out.get("headline") and out.get("body"):
        return out
    variants = BANK.get(ptype) or BANK["choice"]
    c = dict(variants[H["types"].count(ptype) % len(variants)])
    if ptype == "education" and topic:
        c["headline"] = f"Understanding {topic}"[:60]
        c["points"] = next((v for k, v in EDUCATION_POINTS.items() if k in topic.lower()), c["points"])
        c["body"] = (f"{topic[:1].upper() + topic[1:]} can feel worrying for families. Spotting changes early "
                     f"makes a real difference: " + "; ".join(p.lower() for p in c["points"]) +
                     ". If you're concerned, speak to their GP.")
    k = keywords[0] if keywords else "home care in Leeds"
    tail = (f" Apply at {B['recruitment_url']}" if ptype == "recruitment"
            else f" Supporting families in {area} and across Leeds. Call {B['phone']} for a friendly chat.")
    c["google"] = c["body"] + ("" if ptype == "recruitment" else f" Looking for {k}?") + tail
    c["body"] = f"{c.get('hook', '')}\n\n{c['body']}{tail}".strip()
    return c


def hashtags(ptype, topic, n):
    tags = list(CFG["hashtags"].get(ptype, CFG["hashtags"]["choice"]))
    if ptype == "education":
        for key, tag in CFG.get("topic_hashtags", {}).items():
            if key in topic.lower():
                tags.insert(0, tag)
    return " ".join(list(dict.fromkeys(tags))[:n])


# ---------- main ----------
def main():
    ptype, item = post_type()
    topic = rotate("education", CFG["education_topics"]) if ptype == "education" else \
        rotate("choice", CFG["choice_topics"]) if ptype == "choice" else ""
    area = CFG["areas"][len(H["published"]) % len(CFG["areas"])]
    brief = BRIEFS[ptype].format(topic=topic, recruitment_url=B["recruitment_url"],
                                 caption=item["caption"] if item else "")
    if ptype == "choice" and KW["gaps"]:
        brief += f" If natural, also cover something competitors mention that we rarely do: {KW['gaps'][0]}."
    recent = set(H["keywords"][-60:])
    keywords = [] if ptype == "recruitment" else \
        ([k for k in KW["top"] if k not in recent] or KW["top"])[:CFG["keywords_per_post"]]
    text = write(ptype, brief, keywords, topic, area)

    photo, layout = None, "franchisor"
    if item:                                         # franchisor image used as-is
        image_path = item["image"]
    else:
        photo = pick_photo(ptype, H["media"])
        layout = pick_layout(ptype, H.get("layouts", []), text)
        image_path = make_card(text, ptype, photo, STATE / f"card-{TODAY}.jpg", phone=B["phone"], layout=layout)
    image_url = host(image_path, f"{TODAY}-{ptype}.jpg")

    body = text["body"].strip()
    post = {"date": str(TODAY), "type": ptype, "topic": topic, "keywords": keywords, "layout": layout,
            "headline": text["headline"],
            "instagram": body + "\n\n" + hashtags(ptype, topic, 5),       # Instagram allows max 5 hashtags
            "facebook": body + "\n\n" + hashtags(ptype, topic, 2),        # Facebook: 1-3 works best
            "google": text["google"].strip()[:1450],
            "google_ok": ptype in CFG["google_post_types"],
            "image_url": image_url, "photo": photo.name if photo else None,
            "franchisor_key": item["key"] if item else None, "gaps": KW["gaps"][:10]}
    post["social"] = post["instagram"]
    (STATE / "next_post.json").write_text(json.dumps(post, indent=2))
    print(json.dumps(post, indent=2))


if __name__ == "__main__":
    main()
