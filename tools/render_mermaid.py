"""Validate and render figures/pipeline.mmd to SVG + PNG with the official Mermaid library (headless Edge/Chrome).

    python tools/render_mermaid.py
Needs internet (loads mermaid@10.9.1 from cdn.jsdelivr.net) and a Chromium browser (see tools/page_count.py).
Fails loudly if Mermaid reports a syntax error. GitHub renders the same diagram natively from the README.
"""
import html
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from page_count import browser as _browser  # noqa: E402

CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe", "google-chrome", "chromium"]


def browser() -> str:
    """Prefer Chrome: Edge's Windows launcher detaches and returns no --dump-dom output."""
    import shutil
    for c in CHROME:
        if Path(c).exists() or shutil.which(c):
            return c
    return _browser()

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / "figures/pipeline.mmd", ROOT / "figures/fig4_pipeline"

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script></head>
<body style="margin:0;background:#fff"><div id="out"></div><script>
mermaid.initialize({startOnLoad:false, theme:"neutral", securityLevel:"strict", flowchart:{htmlLabels:false}});
mermaid.render("fig", %s).then(r => {document.getElementById("out").innerHTML = r.svg;
  document.title = "OK";}).catch(e => {document.getElementById("out").textContent = "MERMAID_ERROR " + e;
  document.title = "ERR";});
</script></body></html>"""


def main() -> None:
    code = SRC.read_text(encoding="utf-8")
    import json
    with tempfile.TemporaryDirectory() as d:
        page = Path(d, "m.html")
        page.write_text(PAGE % json.dumps(code), encoding="utf-8")
        dom = subprocess.run([browser(), "--headless", "--disable-gpu", "--virtual-time-budget=15000", "--dump-dom",
                              page.as_uri()], capture_output=True, text=True, encoding="utf-8").stdout
        out = re.search(r'<div id="out">(.*?)</div><script>', dom, re.S)
        body = out.group(1) if out else ""
        if not body.startswith("<svg"):
            sys.exit("Mermaid render failed: " + (html.unescape(body)[:400] or "no SVG produced"))
        svg = re.search(r"<svg.*</svg>", body, re.S).group(0)
        OUT.with_suffix(".svg").write_text(svg, encoding="utf-8")
        shot = Path(d, "shot.png")
        wrap = Path(d, "s.html")
        wrap.write_text(f"<!doctype html><html><body style='margin:0;background:#fff'>{svg}</body></html>", encoding="utf-8")
        w = re.search(r'max-width:\s*([\d.]+)px', svg)
        width = int(float(w.group(1))) + 20 if w else 1000
        vb = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', svg)
        height = int(float(vb.group(2)) * (width - 20) / float(vb.group(1))) + 20 if vb else 1200
        subprocess.run([browser(), "--headless", "--disable-gpu", "--hide-scrollbars", f"--window-size={width},{height}",
                        "--force-device-scale-factor=2", f"--screenshot={shot}", wrap.as_uri()], capture_output=True)
        for _ in range(60):
            if shot.exists() and shot.stat().st_size > 0:
                break
            time.sleep(0.5)
        time.sleep(0.5)
        OUT.with_suffix(".png").write_bytes(shot.read_bytes())
    print("Mermaid syntax OK; wrote", OUT.with_suffix(".svg").name, "and", OUT.with_suffix(".png").name)


if __name__ == "__main__":
    main()
