"""Print the GitHub approval issue body for state/next_post.json."""
import json, pathlib

p = json.loads((pathlib.Path(__file__).resolve().parents[1] / "state" / "next_post.json").read_text())
print(f"**{p['type'].replace('_', ' ').title()}**" + (f": {p['topic']}" if p["topic"] else ""))
if p["image_url"]:
    print(f"\n![image]({p['image_url']})")
print("\n### Facebook & Instagram\n\n" + p["social"])
print("\n### Google Business Profile\n\n" + p["google"])
print("\n**Keywords:** " + (", ".join(p["keywords"]) or "none"))
if p["gaps"]:
    print("\n**Keywords Leeds competitors use that you don't:** " + ", ".join(p["gaps"]))
print("\n---\nAdd the **approved** label to publish to all three. Close the issue to skip. "
      "To change the wording, edit the JSON at the bottom of this issue before approving.")
print("\n<!--POST\n" + json.dumps(p) + "\nPOST-->")
