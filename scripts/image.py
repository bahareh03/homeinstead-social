"""Make a 1080x1080 branded card, and give images a public link via this (public) GitHub repo."""
import io, os, pathlib, shutil, textwrap
from urllib.parse import quote
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NAVY, WHITE = (24, 40, 72), (255, 255, 255)


def _font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def make_card(headline, business, bg_url, out_path):
    size = (1080, 1080)
    img = Image.new("RGB", size, NAVY)
    if bg_url:
        try:
            bg = Image.open(io.BytesIO(requests.get(bg_url, timeout=20).content)).convert("RGB")
            img = ImageOps.fit(bg, size)
        except Exception as e:
            print("Background image failed, using plain card:", e)
    shade = Image.new("RGBA", (1080, 460), NAVY + (215,))
    img.paste(shade, (0, 620), shade)
    d = ImageDraw.Draw(img)
    y = 670
    for line in textwrap.wrap(headline, 20)[:3]:
        d.text((60, y), line, font=_font(76), fill=WHITE)
        y += 92
    d.text((60, 990), business, font=_font(38), fill=WHITE)
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
