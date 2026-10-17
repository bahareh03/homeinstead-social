"""Crawl own site + competitor sites, rank home-care keyword phrases.
Output: state/keywords.json  {"top": [...], "gaps": [...], "own_images": [...]}"""
import json, re, collections, pathlib
from urllib.parse import urljoin
import requests, yaml
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
UA = {"User-Agent": "Mozilla/5.0 (GBP keyword research)"}
STOP = set("""a an and are as at be by for from has have in is it its of on or our that the
this to we with you your can will us who what when how more all any into their they them""".split())


def fetch(url):
    try:
        r = requests.get(url, headers=UA, timeout=20)
        if r.ok and "text/html" in r.headers.get("content-type", ""):
            return BeautifulSoup(r.text, "html.parser")
    except requests.RequestException:
        pass
    return None


def page_text(soup):
    for t in soup(["script", "style", "nav", "footer", "header"]):
        t.decompose()
    return soup.get_text(" ", strip=True).lower()


def phrases(text):
    words = [w for w in re.findall(r"[a-z][a-z\-]+", text)]
    seeds = set(CFG["seed_terms"])
    out = collections.Counter()
    for n in (2, 3):
        for i in range(len(words) - n + 1):
            g = words[i:i + n]
            if g[0] in STOP or g[-1] in STOP:
                continue
            if any(any(s in w for s in seeds) for w in g):
                out[" ".join(g)] += 1
    return out


def crawl_own():
    cfg = CFG["own_site"]
    queue, seen = list(cfg["start_urls"]), set()
    counts, images = collections.Counter(), []
    while queue and len(seen) < cfg["max_pages"]:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        soup = fetch(url)
        if not soup:
            continue
        for img in soup.find_all("img", src=True):
            src = urljoin(url, img["src"])
            if src.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) and "logo" not in src.lower():
                images.append(src)
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"]).split("#")[0]
            if link.startswith(cfg["allowed_prefix"]) and link not in seen:
                queue.append(link)
        counts += phrases(page_text(soup))
    return counts, list(dict.fromkeys(images))


def crawl_competitors():
    counts, sites = collections.Counter(), collections.Counter()
    for url in CFG["competitors"]:
        soup = fetch(url)
        if not soup:
            continue
        c = phrases(page_text(soup))
        counts += c
        sites.update(c.keys())          # how many competitor sites use each phrase
    return counts, sites


def main():
    own, own_images = crawl_own()
    comp, comp_sites = crawl_competitors()
    area = CFG["business"]["area"].lower()

    def score(p):
        s = own[p] + 2 * comp[p] + 5 * comp_sites[p]
        return s * (1.5 if area in p else 1)

    candidates = set(own) | set(comp)
    ranked = sorted(candidates, key=score, reverse=True)
    top = [p for p in ranked if own[p] > 0][:40]                       # things we really offer
    gaps = [p for p in ranked if own[p] == 0 and comp_sites[p] >= 2][:20]  # competitors use, we don't

    out = ROOT / "state" / "keywords.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"top": top, "gaps": gaps, "own_images": own_images[:50]}, indent=2))
    print(f"{len(top)} keywords, {len(gaps)} gaps, {len(own_images)} site images")


if __name__ == "__main__":
    main()
