"""Read the franchisor's monthly social media plan (.docx table: Day | Content Idea | Copy | Image)
and turn it into ready-to-post items for Home Instead Leeds Central."""
import pathlib, re
import docx

SKIP = re.compile(r"\[(client name|insert name|name)\]|poll|testimonial", re.I)   # needs local input we don't have


def load(folder, business):
    items = []
    for f in sorted(pathlib.Path(folder).glob("*.docx")):
        for table in docx.Document(f).tables:
            for row in table.rows[1:]:
                cells = [c.text.strip() for c in row.cells]
                if len(cells) < 3 or not cells[2]:
                    continue
                day, idea, copy = cells[0], cells[1], cells[2]
                if SKIP.search(idea + " " + copy):
                    continue
                items.append({"key": f"{f.stem}/{day}", "day": day, "idea": idea,
                              "copy": fill(copy, business)})
    return items


def fill(text, b):
    text = re.sub(r"Home Instead \[office\]", b["name"], text)
    text = text.replace("[office]", "Leeds Central").replace("[location]", b["area"])
    text = text.replace("[insert number]", b["phone"])
    text = re.sub(r"\[insert link\]", b["website"], text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def day_number(day):
    m = re.match(r"(\d+)", day)
    return int(m.group(1)) if m else 0
