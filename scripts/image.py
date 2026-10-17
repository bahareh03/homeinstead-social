"""Post images built to the Home Instead UK Social Media Toolkit (HI25):
  - 1080x1350 (4:5), Instrument Serif headlines, Plus Jakarta Sans body with **bold** highlights
  - the 'domus' house mark in a corner triangle (500x330), accent element in the opposing corner
  - text kept inside the 850px content area, ideally 25 words or fewer
  - photos fill the frame, or sit behind a translucent house overlay (750x790 centred / 1080x1138 bottom)

Layouts: text, stat, tips, photo_house, photo_house_big, photo_corner, cutout
"""
import os, pathlib, random, re, shutil
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONTS, ASSETS, PHOTOS = ROOT / "assets" / "fonts", ROOT / "assets", ROOT / "photos"

W, H = 1080, 1350
# Official Home Instead UK palette
GREEN = (0x2C, 0x4F, 0x26)      # Primary Green "New beginning"
LIME = (0xDE, 0xED, 0x6A)       # Lime Green "Friendly"
PALE = (0xFA, 0xFF, 0xEE)       # Pale Green "Support"
SKY = (0xA6, 0xD9, 0xFF)        # Sky Blue "Clear Sky"
LILAC = (0xB7, 0xB4, 0xEE)      # Lilac "Serenity"
MIDNIGHT = (0x21, 0x3C, 0x56)   # Midnight Blue "Night Sky"
ORANGE = (0xFA, 0xAC, 0x6E)     # Orange "Bright Future"
WHITE = (255, 255, 255)

EYEBROWS = {"difference": "Why Home Instead", "education": "Care guide", "live_in": "Live-in care",
            "recruitment": "We're hiring", "choice": "Home care in Leeds", "franchisor": "Home Instead"}
LAYOUTS = {"difference": ["photo_house", "photo_corner", "stat", "text"],
           "education": ["tips", "photo_house_big", "text"],
           "live_in": ["photo_house_big", "photo_corner", "photo_house"],
           "recruitment": ["photo_house", "tips", "photo_house_big"],
           "choice": ["stat", "photo_corner", "photo_house", "text"],
           "franchisor": ["photo_house_big", "stat", "photo_corner"]}


# ---------- fonts & text ----------
def serif(size, italic=False):
    return ImageFont.truetype(str(FONTS / ("InstrumentSerif-Italic.ttf" if italic else "InstrumentSerif-Regular.ttf")), size)


def sans(size, weight=300):
    f = ImageFont.truetype(str(FONTS / "PlusJakartaSans-VariableFont_wght.ttf"), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def wrap(d, text, font, width):
    lines, line = [], ""
    for word in str(text).split():
        test = f"{line} {word}".strip()
        if d.textlength(test, font=font) <= width or not line:
            line = test
        else:
            lines.append(line)
            line = word
    return lines + ([line] if line else [])


def headline(d, text, cx, top, width, color, sizes=(130, 116, 104, 92, 80, 70), max_lines=3, leading=0.98):
    """Centred Instrument Serif headline. Returns bottom y."""
    for size in sizes:
        f = serif(size)
        lines = wrap(d, text, f, width)
        if len(lines) <= max_lines:
            break
    y = top
    for line in lines[:max_lines]:
        d.text((cx - d.textlength(line, font=f) / 2, y), line, font=f, fill=color)
        y += int(size * leading)
    return y


def rich(d, text, cx, top, width, color, bold_color, size=44, max_lines=4):
    """Centred Jakarta Sans Light text; **words** become Bold in the highlight colour. Returns bottom y."""
    tokens = []
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", str(text))):
        for w in part.split():
            tokens.append((w, i % 2 == 1))
    for s in (size, size - 4, size - 8, size - 12):
        light, bold = sans(s, 300), sans(s, 700)
        space = d.textlength(" ", font=light)
        lines, line, lw = [], [], 0
        for w, b in tokens:
            ww = d.textlength(w, font=bold if b else light)
            if line and lw + space + ww > width:
                lines.append((line, lw)); line, lw = [], 0
            lw += (space if line else 0) + ww
            line.append((w, b, ww))
        if line:
            lines.append((line, lw))
        if len(lines) <= max_lines:
            break
    y = top
    for line, lw in lines[:max_lines]:
        x = cx - lw / 2
        for k, (w, b, ww) in enumerate(line):
            if k and w[0] in ",.;:!?)":
                x -= space
            d.text((x, y), w, font=bold if b else light, fill=bold_color if b else color)
            x += ww + space
        y += int(s * 1.35)
    return y


# ---------- brand elements ----------
def house_mark(colour):
    name = {GREEN: "house-green.png", LIME: "house-lime.png"}.get(colour, "house-white.png")
    im = Image.open(ASSETS / name).convert("RGBA")
    im.thumbnail((132, 140))
    return im


def corner(img, where, fill, mark=None):
    """500x330 triangle in a corner; optional house mark inside (toolkit spec)."""
    d = ImageDraw.Draw(img)
    pts = {"bl": [(0, H), (0, H - 330), (500, H)], "br": [(W, H), (W, H - 330), (W - 500, H)],
           "tl": [(0, 0), (500, 0), (0, 330)], "tr": [(W, 0), (W - 500, 0), (W, 330)]}[where]
    d.polygon(pts, fill=fill)
    if mark:
        m = house_mark(mark)
        x = 35 if where in ("bl", "tl") else W - 35 - m.width
        y = H - 35 - m.height if where in ("bl", "br") else 35
        img.paste(m, (x, y), m)


def arrow(img, colour, where="tl"):
    """The toolkit's corner arrow motif (120px)."""
    d = ImageDraw.Draw(img)
    x, y, s, t = (35, 45, 120, 22) if where == "tl" else (W - 155, 45, 120, 22)
    d.rectangle((x, y, x + s, y + t), fill=colour)                      # top bar
    d.rectangle((x, y, x + t, y + s - 30), fill=colour)                 # down bar
    d.polygon([(x - 14, y + s - 34), (x + t + 14, y + s - 34), (x + t / 2, y + s)], fill=colour)  # arrow head


def house_shape(w, h, roof=0.3):
    """Mask of the Home Instead house overlay shape."""
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(0, int(h * roof)), (w // 2, 0), (w, int(h * roof)), (w, h), (0, h)], fill=255)
    return m


def load_photo(photo, size, centering=(0.5, 0.3)):
    if not photo:
        return Image.new("RGB", size, PALE)
    im = Image.open(photo)
    if im.mode == "RGBA":
        bg = Image.new("RGB", size, PALE)
        im.thumbnail((int(size[0] * 0.9), size[1]))
        bg.paste(im, ((size[0] - im.width) // 2, size[1] - im.height), im)
        return bg
    return ImageOps.fit(im.convert("RGB"), size, centering=centering)


def darken(img, top_alpha=0, bottom_alpha=170, start=0.35):
    grad = Image.new("L", (1, H))
    for y in range(H):
        t = max(0.0, min(1.0, (y / H - start) / (1 - start)))
        grad.putpixel((0, y), int(top_alpha + (bottom_alpha - top_alpha) * t))
    return Image.composite(Image.new("RGB", (W, H), (20, 35, 18)), img, grad.resize((W, H)))


# ---------- layouts ----------
def lay_text(c, photo):
    bg, ink, accent = random.choice([(WHITE, GREEN, LILAC), (PALE, GREEN, SKY), (GREEN, WHITE, LILAC)])
    img = Image.new("RGB", (W, H), bg)
    corner(img, "tr", accent)
    corner(img, "bl", LIME, mark=GREEN)
    arrow(img, LIME if bg != WHITE else SKY)
    d = ImageDraw.Draw(img)
    hl = LILAC if bg == GREEN else (SKY if accent == SKY else GREEN)
    y = headline(d, c["headline"], W / 2, 470, 850, hl, sizes=(120, 104, 92, 80))
    rich(d, c.get("sub", ""), W / 2, y + 40, 820, ink, LIME if bg == GREEN else LILAC)
    return img


def lay_stat(c, photo):
    s = c["stat"]
    bg = random.choice([WHITE, PALE, GREEN])
    img = Image.new("RGB", (W, H), bg)
    corner(img, "tr", random.choice([LILAC, SKY]))
    corner(img, "bl", LIME, mark=GREEN)
    arrow(img, LIME)
    d = ImageDraw.Draw(img)
    num_c = LIME if bg == GREEN else random.choice([SKY, LILAC])
    f = serif(300)
    d.text((W / 2 - d.textlength(s["number"], font=f) / 2, 400), s["number"], font=f, fill=num_c)
    y = rich(d, s["text"], W / 2, 760, 820, WHITE if bg == GREEN else GREEN, LIME if bg == GREEN else LILAC, size=48)
    src = s.get("source", "")
    if src:
        sf = sans(24, 400)
        d.text((W / 2 - d.textlength(src, font=sf) / 2, y + 36), src, font=sf,
               fill=(190, 205, 185) if bg == GREEN else (120, 130, 115))
    return img


def lay_tips(c, photo):
    img = Image.new("RGB", (W, H), random.choice([WHITE, PALE]))
    corner(img, "tr", GREEN)
    corner(img, "bl", LIME, mark=GREEN)
    d = ImageDraw.Draw(img)
    num_c = random.choice([SKY, LILAC])
    top = 420 - 30 * max(0, len(c.get("points", [])) - 3)
    y = headline(d, c["headline"], W / 2, top, 850, num_c, sizes=(110, 96, 84, 74))
    f, fb = sans(44, 400), sans(44, 700)
    items = c.get("points", [])[:5]
    widths = [d.textlength(f"{i}.  ", font=fb) + d.textlength(p, font=f) for i, p in enumerate(items, 1)]
    x = W / 2 - min(850, max(widths or [0])) / 2
    y += 50
    for i, p in enumerate(items, 1):
        n = f"{i}."
        d.text((x, y), n, font=fb, fill=num_c)
        for j, line in enumerate(wrap(d, p, f, 850 - 70)):
            d.text((x + 70, y + j * 58), line, font=f, fill=GREEN)
        y += 58 * len(wrap(d, p, f, 850 - 70)) + 30
    return img


def lay_photo_house(c, photo):
    img = load_photo(photo, (W, H))
    ow, oh = 750, 790
    ox, oy = (W - ow) // 2, 250 + (850 - oh) // 2
    overlay = Image.new("RGB", (ow, oh), GREEN)
    region = img.crop((ox, oy, ox + ow, oy + oh))
    blended = Image.blend(region, overlay, 0.85)
    img.paste(blended, (ox, oy), house_shape(ow, oh, 0.28))
    corner(img, "bl", LIME, mark=GREEN)
    arrow(img, random.choice([SKY, LIME]))
    d = ImageDraw.Draw(img)
    y = headline(d, c["headline"], W / 2, oy + 260, 620, random.choice([LILAC, LIME]), sizes=(116, 100, 88, 76), max_lines=3)
    if c.get("sub"):
        rich(d, c["sub"], W / 2, y + 24, 600, WHITE, LIME, size=38, max_lines=3)
    return img


def lay_photo_house_big(c, photo):
    img = load_photo(photo, (W, H), centering=(0.5, 0.2))
    ow, oh = 1080, 820                                      # big house overlay aligned to bottom edge
    oy = H - oh
    shade = Image.blend(img.crop((0, oy, W, H)), Image.new("RGB", (ow, oh), GREEN), 0.82)
    img.paste(shade, (0, oy), house_shape(ow, oh, 0.34))
    d = ImageDraw.Draw(img)
    top = oy + int(oh * 0.30)
    y = headline(d, c["headline"], W / 2, top, 860, random.choice([SKY, LIME, LILAC]), sizes=(116, 100, 88, 78), max_lines=2)
    if c.get("sub"):
        rich(d, c["sub"], W / 2, y + 18, 820, WHITE, LIME, size=40, max_lines=2)
    m = house_mark(LIME)
    img.paste(m, (35, H - 35 - m.height), m)
    return img


def lay_photo_corner(c, photo):
    img = darken(load_photo(photo, (W, H)), 0, 235, 0.3)
    corner(img, "tl", random.choice([SKY, LILAC, LIME]))
    corner(img, "br", GREEN, mark=LIME)
    d = ImageDraw.Draw(img)
    top = 820 if not c.get("sub") else 760
    y = headline(d, c["headline"], W / 2, top, 860, LIME, sizes=(112, 100, 88, 78), max_lines=3)
    if c.get("sub"):
        rich(d, c["sub"], W / 2, y + 16, 760, WHITE, LIME, size=36, max_lines=2)
    return img


def lay_cutout(c, photo):
    img = Image.new("RGB", (W, H), PALE)
    d = ImageDraw.Draw(img)
    hx, hy, hw, hh = 140, 380, 800, 640                     # lilac hexagon/house behind the person
    d.polygon([(hx, hy + 160), (hx + hw // 2, hy), (hx + hw, hy + 160), (hx + hw, hy + hh), (hx, hy + hh)], fill=LILAC)
    if photo:
        im = Image.open(photo).convert("RGBA")
        im.thumbnail((900, hh + 20))
        img.paste(im, ((W - im.width) // 2, hy + hh - im.height), im)
    corner(img, "br", GREEN, mark=LIME)
    headline(d, c["headline"], W / 2, 110, 850, GREEN, sizes=(96, 84, 74), max_lines=2)
    return img


CONTACT = {"phone": "0113 518 3005", "email": "central.leeds@homeinstead.co.uk",
           "web": "homeinstead.co.uk/leedscentral"}
# which bottom corner holds the house triangle in each layout (contact details go on the other side)
MARK_SIDE = {"text": "left", "stat": "left", "tips": "left", "photo_house": "left",
             "photo_house_big": "left", "photo_corner": "right", "cutout": "right"}
ON_PHOTO = {"photo_house", "photo_house_big", "photo_corner"}


def contact(img, mark_side, on_photo):
    """Phone, email and website stacked in the bottom corner opposite the house triangle."""
    d = ImageDraw.Draw(img)
    lines = [(CONTACT["phone"], sans(34, 700)), (CONTACT["email"], sans(26, 500)), (CONTACT["web"], sans(26, 500))]
    if on_photo:                                           # soft shade so text stays legible on photos
        shade = Image.new("L", (W, 260), 0)
        sd = ImageDraw.Draw(shade)
        for y in range(260):
            sd.line((0, y, W, y), fill=int(150 * y / 260))
        img.paste(Image.new("RGB", (W, 260), (20, 35, 18)), (0, H - 260), shade)
        d = ImageDraw.Draw(img)
    bg = img.getpixel((W - 60 if mark_side == "left" else 60, H - 60))
    light_bg = sum(bg) / 3 > 150
    ink = GREEN if light_bg else WHITE
    accent = GREEN if light_bg else LIME
    y = H - 40 - sum(int(f.size * 1.35) for _, f in lines)
    for i, (t, f) in enumerate(lines):
        x = W - 40 - d.textlength(t, font=f) if mark_side == "left" else 40
        d.text((x, y), t, font=f, fill=accent if i == 0 else ink)
        y += int(f.size * 1.35)


RENDER = {"text": lay_text, "stat": lay_stat, "tips": lay_tips, "photo_house": lay_photo_house,
          "photo_house_big": lay_photo_house_big, "photo_corner": lay_photo_corner, "cutout": lay_cutout}


# ---------- choosing ----------
def pick_photo(ptype, used):
    """Photos are named '<post types>__description.jpg'; prefer one tagged for this post type, least recently used."""
    photos = sorted(p for p in PHOTOS.glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
    if not photos:
        return None
    tagged = [p for p in photos if ptype in p.name.split("__")[0].split("-")] or photos
    recent = set(used[-(len(tagged) - 1):]) if len(tagged) > 1 else set()
    return random.choice([p for p in tagged if p.name not in recent] or tagged)


def pick_layout(ptype, used, content, photo=None):
    if photo and str(photo).lower().endswith(".png"):
        return "cutout"
    options = list(LAYOUTS.get(ptype, ["photo_house"]))
    if not content.get("points"):
        options = [o for o in options if o != "tips"]
    if not content.get("stat"):
        options = [o for o in options if o != "stat"]
    options = options or ["photo_house", "photo_corner"]
    last = used[-1] if used else None
    return random.choice([o for o in options if o != last] or options)


def make_card(content, ptype, photo, out_path, phone=None, layout="photo_house", details=None):
    c = {"headline": content} if isinstance(content, str) else dict(content)
    if details:
        CONTACT.update({k: v for k, v in details.items() if v})
    img = RENDER.get(layout, lay_photo_house)(c, photo)
    contact(img, MARK_SIDE.get(layout, "left"), layout in ON_PHOTO)
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
