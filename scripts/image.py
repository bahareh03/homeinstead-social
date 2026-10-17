"""Make a 1080x1080 branded card and host images on Cloudflare R2 (public URL needed by Instagram/Google)."""
import io, os, pathlib, textwrap
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

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
    out_path.parent.mkdir(exist_ok=True)
    img.save(out_path, "JPEG", quality=90)
    return out_path


def host(path, key):
    """Upload to Cloudflare R2; return the public URL (None if R2 isn't set up)."""
    if not os.getenv("R2_ACCESS_KEY_ID"):
        print("R2 not configured: image saved locally only:", path)
        return None
    import boto3
    s3 = boto3.client("s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
                      aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"], region_name="auto")
    ctype = "image/png" if str(path).lower().endswith(".png") else "image/jpeg"
    s3.upload_file(str(path), os.environ["R2_BUCKET"], key, ExtraArgs={"ContentType": ctype})
    return f"{os.environ['R2_PUBLIC_URL'].rstrip('/')}/{key}"
