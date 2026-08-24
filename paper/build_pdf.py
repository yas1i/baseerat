#!/usr/bin/env python3
"""Render the HTML paper to a PDF using headless Chromium.

There is no LaTeX compiler on this machine, so this produces a shareable,
deposit-ready PDF from paper/baseerat.html (the readable version). The LaTeX
source (paper/baseerat.tex) remains the canonical arXiv-format source for a
later, properly typeset build.

Usage:
    python paper/build_pdf.py
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
HTML = HERE / "baseerat.html"
PDF = HERE / "baseerat.pdf"


def main() -> None:
    url = HTML.as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Render in the light theme with screen media so the styled backgrounds
        # (abstract panel, the dark figure box, table rules) are preserved.
        page.emulate_media(media="screen", color_scheme="light")
        page.goto(url, wait_until="networkidle")
        page.pdf(
            path=str(PDF),
            format="A4",
            print_background=True,
            margin={"top": "18mm", "bottom": "18mm",
                    "left": "16mm", "right": "16mm"},
        )
        browser.close()
    print(f"wrote {PDF}  ({PDF.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
