"""Branded 1080x1350 post card (photo + green panel, Instrument Serif headline, Plus Jakarta Sans labels),
and public image links served from this GitHub repo."""
import os, pathlib, random, shutil
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONTS = ROOT / "assets" / "fonts"
PHOTOS = ROOT / "photos"
LOGO = ROOT / "assets" / "logo.png"          # optional: drop a transparent PNG here and it replaces the text name

W, H, PANEL_Y = 1080, 1350, 800
GREEN, DEEP, LIME = (21, 77, 58), (14, 56, 42), (200, 214, 40)
CREAM, WHITE = (247, 243, 234), (255, 255, 255)

EYEBROWS = {"difference": "WHY HOME INSTEAD", "education": "CARE GUIDE", "live_in": "LIVE-IN CARE",
            "recruitment": "WE'RE HIRING", "choice": "HOME CARE IN LEEDS"}


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
    fresh = [p for p in tagged if p.name not in used[-len(tagged) + 1:]] if len(tagged) > 1 else tagged
    return random.choice(fresh or tagged)


def wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if draw.textlength(test, font=font) <= width:
            line = test
        else:
            lines.append(line)
            line = word
    return lines + [line] if line else lines


def tracked(draw, xy, text, font, fill, spacing=3):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing


def photo_area(photo):
    """Fill the top area with the photo (cover crop). Cut-out PNGs sit on a cream background with a lime arch."""
    area = Image.new("RGB", (W, PANEL_Y), CREAM)
    if not photo:
        return area
    im = Image.open(photo)
    if im.mode == "RGBA":
        im.thumbnail((int(W * 0.8), PANEL_Y - 40))
        area.paste(im, ((W - im.width) // 2, PANEL_Y - im.height), im)
    else:
        area = ImageOps.fit(im.convert("RGB"), (W, PANEL_Y), centering=(0.5, 0.35))
    return area


def make_card(headline, ptype, photo, out_path, phone="0113 518 3005", eyebrow=None):
    img = Image.new("RGB", (W, H), GREEN)
    img.paste(photo_area(photo), (0, 0))
    d = ImageDraw.Draw(img)

    # "CQC rated Good" pill on the photo
    pill = sans(26, 700)
    label = "CQC rated Good"
    pw = d.textlength(label, font=pill) + 56
    d.rounded_rectangle((48, 48, 48 + pw, 104), radius=28, fill=DEEP)
    d.ellipse((66, 68, 82, 84), fill=LIME)
    d.text((92, 60), label, font=pill, fill=WHITE)

    # green panel with lime accent
    d.rectangle((0, PANEL_Y, W, H), fill=GREEN)
    d.rectangle((72, PANEL_Y + 64, 72 + 56, PANEL_Y + 70), fill=LIME)
    tracked(d, (148, PANEL_Y + 50), (eyebrow or EYEBROWS.get(ptype, "HOME CARE IN LEEDS")).upper(), sans(26, 700), LIME)

    # headline: Instrument Serif, shrink to fit 3 lines
    for size in (92, 84, 76, 68, 60):
        font = serif(size)
        lines = wrap(d, headline, font, W - 144)
        if len(lines) <= 3:
            break
    y = PANEL_Y + 110
    for line in lines[:3]:
        d.text((72, y), line, font=font, fill=WHITE)
        y += int(size * 1.08)

    # footer: logo (or name) + phone
    d.line((72, H - 120, W - 72, H - 120), fill=(60, 110, 92), width=2)
    if LOGO.exists():
        logo = Image.open(LOGO).convert("RGBA")
        logo.thumbnail((360, 64))
        img.paste(logo, (72, H - 96 + (64 - logo.height) // 2), logo)
    else:
        d.text((72, H - 92), "Home Instead", font=sans(32, 800), fill=WHITE)
        d.text((72 + d.textlength("Home Instead ", font=sans(32, 800)), H - 92), "Leeds Central",
               font=sans(32, 400), fill=WHITE)
    pf = sans(32, 700)
    d.text((W - 72 - d.textlength(phone, font=pf), H - 92), phone, font=pf, fill=LIME)

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
