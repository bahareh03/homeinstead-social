"""Decide today's post type, write the text, make the image.  Output: state/next_post.json"""
import datetime, json, os, pathlib, random, re
from zoneinfo import ZoneInfo
import requests, yaml
from image import make_card, host

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
B = CFG["business"]
STATE = ROOT / "state"
KW = json.loads((STATE / "keywords.json").read_text()) if (STATE / "keywords.json").exists() \
    else {"top": [], "gaps": [], "own_images": []}
HF = STATE / "history.json"
H = json.loads(HF.read_text()) if HF.exists() else {}
for k in ("keywords", "media", "published", "types", "franchisor"):
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
    "difference": "Explain what home care is and what makes us different from other Leeds home care companies "
                  "(minimum one-hour visits, consistent care professionals, CQC rated Good, relationship-led care).",
    "education": "An educational post about {topic}: signs families should look for, practical tips, and how "
                 "home care can help. Accurate, non-alarming, no medical claims; suggest seeing a GP where relevant.",
    "live_in": "A post about live-in care at home as an alternative to a care home: what it is, who it suits, "
               "peace of mind for families, staying with pets and routines.",
    "recruitment": "A recruitment post for care professionals in Leeds: no experience needed, full training, "
                   "flexible hours, meaningful work, minimum one-hour visits so you never rush. Invite people "
                   "to apply at {recruitment_url}.",
    "choice": "A post about: {topic}. Make it the kind of content that makes families choose us over other "
              "home care companies in Leeds.",
    "franchisor": "Rewrite this franchisor-supplied content for our local Leeds office, keeping its message: "
                  "{caption}",
}


def claude(prompt):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    r = requests.post("https://api.anthropic.com/v1/messages", timeout=90,
                      headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                      json={"model": "claude-sonnet-5-5", "max_tokens": 1500,
                            "messages": [{"role": "user", "content": prompt}]})
    if not r.ok:
        print("Claude API failed, using template:", r.text[:200])
        return None
    m = re.search(r"\{.*\}", r.json()["content"][0]["text"], re.S)
    return json.loads(m.group(0)) if m else None


def write(ptype, brief, keywords):
    prompt = (f"You write social posts for {B['name']}, a CQC-regulated home care provider in {B['area']} "
              f"(phone {B['phone']}).\nTask: {brief}\n"
              f"Work in these search phrases naturally, once each: {', '.join(keywords) or 'none'}.\n"
              "Rules: warm plain British English, no prices, no client names, no made-up reviews, "
              "statistics or quotes.\nReturn ONLY JSON with keys:\n"
              '"headline": max 7 words for an image,\n'
              f'"social": Facebook/Instagram text, max 900 characters, emojis sparingly, end with a call to action,\n'
              '"google": Google Business Profile version, max 1200 characters, no hashtags or emojis.')
    out = claude(prompt)
    if out:
        return out
    k = (keywords + ["home care in Leeds"] * 3)[:3]
    templates = {
        "recruitment": ("We're hiring care professionals",
                        f"Want a job that really matters? We're recruiting care professionals in {B['area']}. "
                        f"No experience needed: full training, flexible hours and never-rushed visits. "
                        f"Apply at {B['recruitment_url']}"),
        "live_in": ("Live-in care, at home",
                    f"Live-in care means your loved one stays in the home they love, with pets, routines and "
                    f"one-to-one support. Call {B['phone']} to talk about live-in care in {B['area']}."),
    }
    head, body = templates.get(ptype, ("Care that feels like family",
                 f"Looking for {k[0]}? Our care professionals help older people stay safe and independent "
                 f"at home across {B['area']}, with {k[1]} and {k[2]} built around each person. "
                 f"Call {B['phone']} for a friendly chat."))
    return {"headline": head, "social": body, "google": body}


# ---------- main ----------
def main():
    ptype, item = post_type()
    topic = rotate("education", CFG["education_topics"]) if ptype == "education" else \
        rotate("choice", CFG["choice_topics"]) if ptype == "choice" else ""
    brief = BRIEFS[ptype].format(topic=topic, recruitment_url=B["recruitment_url"],
                                 caption=item["caption"] if item else "")
    if ptype == "choice" and KW["gaps"]:
        brief += f" If natural, also cover something competitors mention that we rarely do: {KW['gaps'][0]}."
    recent = set(H["keywords"][-60:])
    keywords = ([k for k in KW["top"] if k not in recent] or KW["top"])[:CFG["keywords_per_post"]]
    if ptype == "recruitment":
        keywords = []          # job posts don't need care-service keywords
    text = write(ptype, brief, keywords)

    if item:                                         # franchisor image used as-is
        image_path = item["image"]
    else:
        unused = [u for u in KW["own_images"] if u not in H["media"]] or KW["own_images"]
        bg = random.choice(unused) if unused else None
        image_path = make_card(text["headline"], B["name"], bg, STATE / f"card-{TODAY}.jpg")
    image_url = host(image_path, f"{TODAY}-{ptype}.jpg")

    post = {"date": str(TODAY), "type": ptype, "topic": topic, "keywords": keywords,
            "headline": text["headline"],
            "social": text["social"].strip() + "\n\n" + CFG["hashtags"],
            "google": text["google"].strip()[:1450],
            "image_url": image_url, "franchisor_key": item["key"] if item else None,
            "gaps": KW["gaps"][:10]}
    (STATE / "next_post.json").write_text(json.dumps(post, indent=2))
    print(json.dumps(post, indent=2))


if __name__ == "__main__":
    main()
