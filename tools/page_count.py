"""Render markdown files to A4 PDF (pandoc -> HTML -> headless Edge/Chrome) and report page counts.

Usage: python tools/page_count.py reports/memo.md reports/personas/P1_adults_65plus.md ...
Needs pandoc and a Chromium browser (Edge on Windows, or set BROWSER=/path/to/chrome). 11pt Calibri/Arial, 2 cm margins.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CSS = ("body{font-family:Calibri,Arial,sans-serif;font-size:11pt;margin:0} table{border-collapse:collapse;font-size:9.5pt}"
       " td,th{border:1px solid #999;padding:2px 4px} @page{size:A4;margin:2cm} h1{font-size:16pt} h2{font-size:13pt}")
CANDIDATES = [os.environ.get("BROWSER", ""), r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe", "google-chrome", "chromium", "msedge"]


def browser() -> str:
    for c in CANDIDATES:
        if c and (Path(c).exists() or shutil.which(c)):
            return c
    sys.exit("no Chromium-based browser found; set BROWSER")


def pages(md: Path) -> int:
    with tempfile.TemporaryDirectory() as d:
        css, html, pdf = Path(d, "s.css"), Path(d, "x.html"), Path(d, "x.pdf")
        css.write_text(CSS)
        subprocess.run(["pandoc", str(md), "-o", str(html), "--standalone", "--metadata", "title= ", "-c", str(css)], check=True)
        subprocess.run([browser(), "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                        html.as_uri()], check=True, capture_output=True)
        for _ in range(60):  # Edge may hand off to a background process and return before the PDF is written
            if pdf.exists() and pdf.stat().st_size > 0:
                break
            __import__("time").sleep(0.5)
        __import__("time").sleep(0.5)
        return len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))


if __name__ == "__main__":
    for f in sys.argv[1:]:
        print(f"{pages(Path(f))}\t{f}")
