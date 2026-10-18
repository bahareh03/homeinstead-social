"""Write the daily report (state/report.md) after a publish attempt. The workflow posts it as a GitHub issue,
which GitHub emails to the repository owner."""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATE = ROOT / "state"
NAMES = {"facebook": "Facebook", "instagram": "Instagram", "google": "Google Business Profile", "make": "Make.com"}


def main():
    post = json.loads((STATE / "next_post.json").read_text()) if (STATE / "next_post.json").exists() else {}
    res = json.loads((STATE / "publish_result.json").read_text()) if (STATE / "publish_result.json").exists() \
        else {"done": [], "failed": ["the publishing step (it stopped before sending)"]}
    ok = not res["failed"] and res["done"]
    title = f"{'✅' if ok else '⚠️'} Daily post report: {post.get('date', '')} ({post.get('type', '').replace('_', ' ')})"
    lines = [f"**Status:** {'Published' if ok else 'Needs attention'}", ""]
    for p in res["done"]:
        lines.append(f"- ✅ Sent to **{NAMES.get(p, p)}**")
    for p in res["failed"]:
        lines.append(f"- ❌ **{NAMES.get(p, p)}** failed. Open the Actions log or Make.com History for the reason.")
    skipped = [p for p in ("facebook", "instagram", "google") if p not in res["done"]]
    if skipped:
        lines.append(f"- ⏸️ Not posted to: {', '.join(NAMES[p] for p in skipped)}")
    lines += ["", f"**Topic:** {post.get('topic') or post.get('headline', '')}",
              f"**Layout:** {post.get('layout', '')}", ""]
    if post.get("image_url"):
        lines.append(f"![post]({post['image_url']})")
    lines += ["", "### Caption (Facebook)", "", post.get("facebook", post.get("social", "")),
              "", "---", "_Check the final result in Make.com → History (green ticks = live on each platform)._"]
    (STATE / "report_title.txt").write_text(title)
    (STATE / "report.md").write_text("\n".join(lines))
    print(title)


if __name__ == "__main__":
    main()
