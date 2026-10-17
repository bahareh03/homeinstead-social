"""Print 'draft' or 'auto' depending on mode and how many posts have been published."""
import json, pathlib, yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
hf = ROOT / "state" / "history.json"
published = len(json.loads(hf.read_text()).get("published", [])) if hf.exists() else 0

mode = cfg.get("mode", "draft")
if mode == "approve_first":
    mode = "draft" if published < cfg.get("approvals_required", 5) else "auto"
print(mode)
