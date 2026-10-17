"""Branded 1080x1350 post images in several rotating layouts, plus public image links from this GitHub repo.

Layouts:
  panel     - photo on top, green panel with headline
  overlay   - full-bleed photo, green gradient, big headline over the photo
  hook      - lime background, big question, photo in an arched frame
  checklist - cream background, headline + 3 numbered points, round photo  (great for "signs to look for")
  myth      - green background, MYTH (crossed out) vs FACT, photo strip
"""
import os, pathlib, random, shutil
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONTS = ROOT / "assets" / "fonts"
PHOTOS = ROOT / "photos"
LOGO = ROOT / "assets" / "logo.png"           # white logo (recoloured green on light backgrounds)

W, H = 1080, 1350
GREEN, DEEP, LIME = (44, 79, 38), (31, 58, 27), (222, 237, 106)   # Home Instead brand
CREAM, WHITE = (247, 243, 234), (255, 255, 255)

EYEBROWS = {"difference": "WHY HOME INSTEAD", "education": "CARE GUIDE", "live_in": "LIVE-IN CARE",
            "recruitment": "WE'RE HIRING", "choice": "HOME CARE IN LEEDS"}
LAYOUTS = {"difference": ["panel", "overlay", "myth"],
           "education": ["checklist", "overlay", "panel"],
           "live_in": ["overlay", "hook", "panel"],
           "recruitment": ["hook", "overlay", "panel"],
           "choice": ["myth", "hook", "overlay", "panel"]}


# ---------- helpers ----------
def serif(size, italic=False):
    return ImageFont.truetype(str(FONTS / ("InstrumentSerif-Italic.ttf" if italic else "InstrumentSerif-Regular.ttf")), size)


def sans(size, weight=600):
    f = ImageFont.truetype(str(FONTS / "PlusJakartaSans-VariableFont_wght.ttf"), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def pick_photo(ptype, used):
    """Photos are named '<post types>__description.jpg'; prefer one tagged for this post type, least recently used."""
    photos = sorted(p for p in PHOTOS.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
    if not photos:
        return None
    tagged = [p for p in photos if ptype in p.name.split("__")[0].split("-")] or photos
    recent = set(used[-(len(tagged) - 1):]) if len(tagged) > 1 else set()
    return random.choice([p for p in tagged if p.name not in recent] or tagged)


def pick_layout(ptype, used, content):
    options = list(LAYOUTS.get(ptype, ["panel"]))
    if not content.get("points"):
        options = [o for o in options if o != "checklist"]
    if not (content.get("myth") and content.get("fact")):
        options = [o for o in options if o != "myth"]
    if not content.get("hook"):
        options = [o for o in options if o != "hook"]
    options = options or ["panel", "overlay"]
    last = used[-1] if used else None
    return random.choice([o for o in options if o != last] or options)


def wrap(d, text, font, width):
    lines, line = [], ""
    for word in str(text).split():
        test = f"{line} {word}".strip()
        if d.textlength(test, font=font) <= width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    return lines + [line] if line else lines


def fit_text(d, text, sizes, width, max_lines, font_fn):
    for size in sizes:
        font = font_fn(size)
        lines = wrap(d, text, font, width)
        if len(lines) <= max_lines:
            return font, size, lines
    return font, size, lines[:max_lines]


def draw_lines(d, xy, lines, font, size, fill, leading=1.08):
    x, y = xy
    for line in lines:
        d.text((x, y), line, font=font, fill=fill)
        y += int(size * leading)
    return y


def tracked(d, xy, text, font, fill, spacing=3):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + spacing


def eyebrow(d, xy, text, color):
    x, y = xy
    d.rectangle((x, y + 14, x + 56, y + 20), fill=color)
    tracked(d, (x + 76, y), text.upper(), sans(26, 700), color)


def load_photo(photo, size, centering=(0.5, 0.35)):
    if not photo:
        return Image.new("RGB", size, CREAM)
    im = Image.open(photo)
    if im.mode == "RGBA":                                  # cut-out: place on cream
        bg = Image.new("RGB", size, CREAM)
        im.thumbnail((int(size[0] * 0.85), size[1] - 20))
        bg.paste(im, ((size[0] - im.width) // 2, size[1] - im.height), im)
        return bg
    return ImageOps.fit(im.convert("RGB"), size, centering=centering)


def footer(img, phone, dark_bg=True, rule=True):
    """Logo + 'Leeds Central' + phone along the bottom."""
    d = ImageDraw.Draw(img)
    text_c = WHITE if dark_bg else DEEP
    accent = LIME if dark_bg else GREEN
    if rule:
        d.line((72, H - 124, W - 72, H - 124), fill=(80, 112, 72) if dark_bg else (200, 196, 180), width=2)
    x = 72
    if LOGO.exists():
        logo = Image.open(LOGO).convert("RGBA")
        logo.thumbnail((400, 66))
        if not dark_bg:                                   # recolour white logo to brand green
            solid = Image.new("RGBA", logo.size, GREEN + (255,))
            solid.putalpha(logo.getchannel("A"))
            logo = solid
        img.paste(logo, (x, H - 100 + (66 - logo.height) // 2), logo)
        x += logo.width + 24
    else:
        d.text((x, H - 92), "Home Instead", font=sans(32, 800), fill=text_c)
        x += int(d.textlength("Home Instead", font=sans(32, 800))) + 24
    d.line((x, H - 92, x, H - 46), fill=(110, 140, 100) if dark_bg else (170, 180, 140), width=2)
    d.text((x + 24, H - 86), "Leeds Central", font=sans(30, 500), fill=text_c)
    pf = sans(32, 700)
    d.text((W - 72 - d.textlength(phone, font=pf), H - 92), phone, font=pf, fill=accent)


# ---------- layouts ----------
def layout_panel(c, photo, phone):
    img = Image.new("RGB", (W, H), GREEN)
    img.paste(load_photo(photo, (W, 800)), (0, 0))
    d = ImageDraw.Draw(img)
    eyebrow(d, (72, 850), c["eyebrow"], LIME)
    font, size, lines = fit_text(d, c["headline"], (92, 84, 76, 68, 60), W - 144, 3, serif)
    draw_lines(d, (72, 910), lines, font, size, WHITE)
    footer(img, phone)
    return img


def layout_overlay(c, photo, phone):
    img = load_photo(photo, (W, H), centering=(0.5, 0.3))
    grad = Image.new("L", (1, H))
    for y in range(H):                                      # transparent top -> deep green bottom
        t = max(0.0, (y - H * 0.38) / (H * 0.45))
        grad.putpixel((0, y), int(min(1.0, t) * 242))
    img = Image.composite(Image.new("RGB", (W, H), DEEP), img, grad.resize((W, H)))
    d = ImageDraw.Draw(img)
    font, size, lines = fit_text(d, c["headline"], (112, 100, 90, 80, 70), W - 144, 3, serif)
    top = H - 160 - len(lines) * int(size * 1.04)
    eyebrow(d, (72, top - 64), c["eyebrow"], LIME)
    draw_lines(d, (72, top), lines, font, size, WHITE, 1.04)
    footer(img, phone, rule=False)
    return img


def layout_hook(c, photo, phone):
    img = Image.new("RGB", (W, H), LIME)
    d = ImageDraw.Draw(img)
    eyebrow(d, (72, 90), c["eyebrow"], DEEP)
    font, size, lines = fit_text(d, c["hook"], (104, 94, 84, 74, 66), W - 144, 3, lambda s: serif(s, italic=True))
    y = draw_lines(d, (72, 150), lines, font, size, DEEP, 1.04)
    top, bottom, x0, x1 = max(y + 40, 520), H - 150, 72, W - 72   # photo in an arched frame
    ph = load_photo(photo, (x1 - x0, bottom - top))
    mask = Image.new("L", ph.size, 0)
    md = ImageDraw.Draw(mask)
    r = (x1 - x0) // 2
    md.rectangle((0, r, ph.width, ph.height), fill=255)
    md.ellipse((0, 0, ph.width, 2 * r), fill=255)
    img.paste(ph, (x0, top), mask)
    footer(img, phone, dark_bg=False, rule=False)
    return img


def layout_checklist(c, photo, phone):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    size = 300                                              # round photo top-right
    ph = load_photo(photo, (size, size), centering=(0.5, 0.3))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    d.ellipse((W - 72 - size - 12, 60, W - 60, 72 + size), fill=LIME)
    img.paste(ph, (W - 72 - size, 72), mask)
    eyebrow(d, (72, 96), c["eyebrow"], GREEN)
    font, fsize, lines = fit_text(d, c["headline"], (84, 76, 68, 60), W - 144 - size - 40, 4, serif)
    y = draw_lines(d, (72, 156), lines, font, fsize, DEEP)
    y = max(y + 40, 72 + size + 50)
    for i, point in enumerate(c["points"][:3], 1):
        d.ellipse((72, y, 72 + 92, y + 92), fill=GREEN)
        n, nf = str(i), sans(44, 800)
        d.text((72 + 46 - d.textlength(n, font=nf) / 2, y + 18), n, font=nf, fill=LIME)
        pf, psize, plines = fit_text(d, point, (48, 44, 40, 36), W - 144 - 130, 2, lambda s: sans(s, 600))
        ty = y + 46 - (len(plines) * int(psize * 1.25)) / 2
        draw_lines(d, (72 + 130, ty), plines, pf, psize, DEEP, 1.25)
        y += 178
    d.rounded_rectangle((72, y + 10, W - 72, y + 110), radius=50, fill=LIME)
    note = c.get("note", "Noticed any of these? We're here to help.")
    nf2 = serif(46, italic=True)
    d.text(((W - d.textlength(note, font=nf2)) / 2, y + 32), note, font=nf2, fill=DEEP)
    footer(img, phone, dark_bg=False)
    return img


def layout_myth(c, photo, phone):
    img = Image.new("RGB", (W, H), GREEN)
    img.paste(load_photo(photo, (W, 500)), (0, 0))
    d = ImageDraw.Draw(img)
    y = 550
    tracked(d, (72, y), "MYTH", sans(30, 800), (255, 170, 160))
    font, size, lines = fit_text(d, c["myth"], (60, 54, 48), W - 144, 2, serif)
    y2 = draw_lines(d, (72, y + 50), lines, font, size, (205, 215, 200))
    for i, line in enumerate(lines):                       # strike-through
        ly = y + 50 + i * int(size * 1.08) + int(size * 0.55)
        d.line((72, ly, 72 + d.textlength(line, font=font), ly), fill=(255, 170, 160), width=4)
    y = y2 + 40
    font, size, lines = fit_text(d, c["fact"], (88, 80, 72, 64, 56), W - 192, 3, serif)
    box_end = min(H - 150, y + 96 + len(lines) * int(size * 1.08) + 40)
    d.rounded_rectangle((60, y - 10, W - 60, box_end), radius=28, fill=DEEP)
    tracked(d, (96, y + 24), "FACT", sans(30, 800), LIME)
    draw_lines(d, (96, y + 80), lines, font, size, WHITE)
    footer(img, phone, rule=False)
    return img


RENDER = {"panel": layout_panel, "overlay": layout_overlay, "hook": layout_hook,
          "checklist": layout_checklist, "myth": layout_myth}


def make_card(content, ptype, photo, out_path, phone="0113 518 3005", layout="panel"):
    c = {"headline": content} if isinstance(content, str) else dict(content)
    c.setdefault("eyebrow", EYEBROWS.get(ptype, "HOME CARE IN LEEDS"))
    img = RENDER.get(layout, layout_panel)(c, photo, phone)
    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG", quality=90)
    return out_path


def host(path, name):
    """Place the image in images/ (committed by the workflow) and return its public raw GitHub URL.
    Franchisor images already live in the repo, so they are linked where they are."""
    path = pathlib.Path(path).resolve()
    if ROOT / "images" not in path.parents and ROOT / "franchisor" not in path.parents:
        dest = ROOT / "images" / name
        dest.parent.mkdir(exist_ok=True)
        shutil.copy(path, dest)
        path = dest
    rel = path.relative_to(ROOT).as_posix()
    repo = os.getenv("GITHUB_REPOSITORY", "bahareh03/homeinstead-social")
    branch = os.getenv("GITHUB_REF_NAME", "main")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{quote(rel)}"
