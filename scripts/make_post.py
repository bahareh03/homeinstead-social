"""Decide today's post type, write the text, make the image.  Output: state/next_post.json"""
import datetime, json, os, pathlib, random, re
from zoneinfo import ZoneInfo
import requests, yaml
from image import make_card, host, pick_photo, pick_layout
from content_bank import BANK, EDUCATION_POINTS, STATS, SOURCE
import franchisor_plan

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
    """Up to N franchisor items a month: an uploaded image (+ .txt caption), or a row from the monthly plan (.docx)."""
    folder = ROOT / CFG["franchisor"]["folder"] / MONTH
    used_this_month = [f for f in H["franchisor"] if f.startswith(MONTH)]
    if len(used_this_month) >= CFG["franchisor"]["per_month"] or not folder.exists():
        return None
    for img in sorted(folder.iterdir()):
        key = f"{MONTH}/{img.name}"
        if img.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp") and key not in H["franchisor"]:
            cap = img.with_suffix(".txt")
            return {"key": key, "image": img, "caption": cap.read_text().strip() if cap.exists() else ""}
    plan = [i for i in franchisor_plan.load(folder, B) if f"{MONTH}/{i['key']}" not in H["franchisor"]]
    upcoming = [i for i in plan if franchisor_plan.day_number(i["day"]) >= TODAY.day] or plan
    if upcoming:
        i = upcoming[0]
        return {"key": f"{MONTH}/{i['key']}", "image": None, "caption": i["copy"], "idea": i["idea"]}
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
              "Home Instead brand rules: call carers 'Care Professionals' or 'Care Pros'; image text must be very short.\n"
              "Rules: plain British English, no prices, no client names, no made-up reviews, quotes or statistics, "
              "no claims about ratings or awards.\n"
              "Return ONLY JSON with keys:\n"
              '"headline": the image headline, 2-6 words,\n'
              '"sub": one supporting line for the image, max 12 words, wrap the 2-3 most important words in **double asterisks**,\n'
              '"points": 3-4 short items, max 5 words each (signs, tips or benefits),\n'
              '"body": the post text, 400-700 characters, first line is a hook question, emojis sparingly, '
              'ends with a call to action, no hashtags,\n'
              '"google": Google Business Profile version, 400-900 characters, no hashtags or emojis, '
              'focused on the service and why to choose us, ends with a call to action.')
    out = claude(prompt)
    if not (out and out.get("headline") and out.get("body")):
        variants = BANK.get(ptype) or BANK["choice"]
        out = dict(variants[H["types"].count(ptype) % len(variants)])
        if ptype == "education" and topic:
            out["headline"] = f"Understanding {topic}"[:60]
            out["points"] = next((v for k, v in EDUCATION_POINTS.items() if k in topic.lower()), out["points"])
            out["body"] = (f"{topic[:1].upper() + topic[1:]} can feel worrying for families. Spotting changes early "
                           "makes a real difference. If you're concerned, speak to their GP.")
        k = keywords[0] if keywords else "home care in Leeds"
        tail = (f" Looking for {k}? Apply at {B['recruitment_url']}" if ptype == "recruitment"
                else f" Looking for {k}? Our local team supports families in {area} and across Leeds. "
                     f"Call {B['phone']} for a friendly chat.")
        out["google"] = out["body"] + tail
        out["body"] = out["body"] + tail
    if ptype in ("difference", "choice"):                       # verified Home Instead/YouGov figure
        st = dict(STATS[H["types"].count(ptype) % len(STATS)], source=SOURCE)
        out["stat"] = st
    return out


def franchisor_text(item):
    """The franchisor's own (approved) copy; headline taken from the first short sentence or the idea title."""
    copy = item["caption"]
    first = re.split(r"(?<=[.!?])\s|\n", copy.strip())[0].strip()
    head = first if 2 <= len(first.split()) <= 7 else item.get("idea", "Weekends Well Spent")
    head = re.sub(r"[^\w\s'’,!?-]", "", head).strip()
    c = {"headline": head, "body": copy, "google": re.sub(r"#\w+", "", copy).strip()}
    for st in STATS:
        if st["number"] in copy:
            c["stat"] = dict(st, source=SOURCE)
    m = re.search(r"(\d+(?:\.\d+)? million hours)", copy)
    if m and "stat" not in c:
        c["stat"] = {"number": m.group(1).split()[0] + "m", "text": "hours of **weekend leisure time** lost every week "
                     "to family caring across Britain", "source": "Home Instead estimate from YouGov data, 2026"}
    return c


def hashtags(ptype, topic, n, existing=""):
    have = re.findall(r"#\w+", existing)
    campaign = CFG.get("campaign_hashtags", {}).get(MONTH, []) if ptype in ("difference", "choice", "live_in") else []
    tags = list(campaign) + list(CFG["hashtags"].get(ptype, CFG["hashtags"]["choice"]))
    if ptype == "education":
        for key, tag in CFG.get("topic_hashtags", {}).items():
            if key in topic.lower():
                tags.insert(0, tag)
    tags = [t for t in dict.fromkeys(tags) if t.lower() not in {h.lower() for h in have}]
    return " ".join(tags[:max(0, n - len(have))])


def pick_keywords(ptype):
    """Rotate through the curated search phrases for this post type (main phrase + 1 related)."""
    pri = CFG.get("priority_keywords", {}).get(ptype) or CFG["priority_keywords"]["difference"]
    i = H["types"].count(ptype)
    picks = [pri[i % len(pri)]]
    if len(pri) > 1 and ptype != "recruitment":
        picks.append(pri[(i + 1) % len(pri)])
    return picks


def clean_for_google(text):
    """Google posts: no phone numbers, emails, links or hashtags in the text (content policy)."""
    t = re.sub(r"#\w+", "", text)
    bad = re.compile(r"https?://|www\.|\S+@\S+|\b(?:\+44\s?|0)\d[\d\s]{8,12}\d\b|link in (?:our )?bio|\bcall\b|\bemail\b|apply at", re.I)
    parts = re.split(r"(?<=[.!?])\s+|\n+", t)
    keep = [p.strip() for p in parts if p.strip() and not bad.search(p) and not re.match(r"^[📞✉️🌐]", p.strip())]
    return re.sub(r"\s{2,}", " ", " ".join(keep)).strip()[:1400]


def strip_links_for_instagram(text):
    """Instagram captions can't hold clickable links (franchisor plan note)."""
    return re.sub(r"https?://\S+", "the link in our bio", text)


def limit_hashtags(text, n):
    tags = re.findall(r"#\w+", text)
    for t in tags[n:]:
        text = text.replace(t, "", 1)
    return re.sub(r"[ \t]+\n", "\n", text).strip()


# ---------- main ----------
def main():
    ptype, item = post_type()
    topic = rotate("education", CFG["education_topics"]) if ptype == "education" else \
        rotate("choice", CFG["choice_topics"]) if ptype == "choice" else ""
    area = CFG["areas"][len(H["published"]) % len(CFG["areas"])]
    keywords = []
    if item:
        text = franchisor_text(item) if item.get("image") is None else \
            {"headline": item.get("idea", ""), "body": item["caption"], "google": item["caption"]}
    else:
        brief = BRIEFS[ptype].format(topic=topic, recruitment_url=B["recruitment_url"], caption="")
        if ptype == "choice" and KW["gaps"]:
            brief += f" If natural, also cover something competitors mention that we rarely do: {KW['gaps'][0]}."
        keywords = pick_keywords(ptype)
        text = write(ptype, brief, keywords, topic, area)

    photo, layout = None, "franchisor image"
    if item and item.get("image"):                   # franchisor's own image used as-is
        image_path = item["image"]
    else:
        photo = pick_photo(ptype if ptype != "franchisor" else "choice", H["media"])
        layout = pick_layout(ptype, H.get("layouts", []), text, photo)
        if layout in ("text", "stat", "tips"):
            photo = None
        image_path = make_card(text, ptype, photo, STATE / f"card-{TODAY}.jpg", layout=layout,
                               details={"phone": B["phone"], "email": B.get("email"), "web": B.get("website_short")})
    image_url = host(image_path, f"{TODAY}-{ptype}.jpg")
    g_path = pathlib.Path(image_path).with_name(pathlib.Path(image_path).stem + "-google.jpg")
    google_image_url = host(g_path, f"{TODAY}-{ptype}-google.jpg") if g_path.exists() else image_url

    body = text["body"].strip()
    if text.get("stat") and layout == "stat" and SOURCE not in body and ptype != "franchisor":
        body += f"\n\n*Source: {text['stat']['source']}."
    body += f"\n\n📞 {B['phone']}\n✉️ {B['email']}\n🌐 {B['website_short']}"
    ig = limit_hashtags(strip_links_for_instagram(body), 5)
    fb = limit_hashtags(body, 3)
    post = {"date": str(TODAY), "type": ptype, "topic": topic, "keywords": keywords, "layout": layout,
            "headline": text["headline"],
            "instagram": (ig + "\n\n" + hashtags(ptype, topic, 5, ig)).strip(),   # Instagram max 5 hashtags
            "facebook": (fb + "\n\n" + hashtags(ptype, topic, 2, fb)).strip(),    # Facebook: 1-3 works best
            # Google posts must NOT contain phone numbers, emails or links in the text (content policy);
            # the CALL button carries the number instead.
            "google": clean_for_google(text["google"]),
            "google_ok": ptype in CFG["google_post_types"],
            "image_url": image_url, "google_image_url": google_image_url, "photo": photo.name if photo else None,
            "franchisor_key": item["key"] if item else None, "gaps": KW["gaps"][:10]}
    post["social"] = post["instagram"]
    (STATE / "next_post.json").write_text(json.dumps(post, indent=2))
    print(json.dumps(post, indent=2))


if __name__ == "__main__":
    main()
