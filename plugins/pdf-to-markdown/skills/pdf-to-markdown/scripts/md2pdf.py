#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "markdown",
#     "weasyprint",
# ]
# ///
"""Convert a markdown file to a styled PDF.

Usage:
    uv run md2pdf.py <input.md>

Output: saves <input.pdf> in the same directory.
"""

import sys
from pathlib import Path

import markdown
import weasyprint

CSS = """
body {
    font-family: Helvetica, Arial, sans-serif;
    max-width: 800px;
    margin: 40px auto;
    padding: 0 20px;
    font-size: 11pt;
    line-height: 1.5;
    color: #222;
}
h1 {
    font-size: 18pt;
    border-bottom: 2px solid #333;
    padding-bottom: 8px;
    margin-top: 32px;
}
h2 {
    font-size: 14pt;
    color: #333;
    margin-top: 24px;
}
h3 {
    font-size: 12pt;
    color: #444;
    margin-top: 20px;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 10pt;
}
th, td {
    border: 1px solid #ccc;
    padding: 6px 10px;
    text-align: left;
}
th {
    background: #f5f5f5;
    font-weight: bold;
}
hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 24px 0;
}
strong {
    color: #111;
}
code {
    background: #f4f4f4;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 10pt;
}
pre {
    background: #f4f4f4;
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 10pt;
    line-height: 1.4;
}
pre code {
    background: none;
    padding: 0;
}
blockquote {
    border-left: 3px solid #ccc;
    margin: 16px 0;
    padding: 8px 16px;
    color: #555;
}
ul, ol {
    margin: 8px 0;
    padding-left: 24px;
}
li {
    margin: 4px 0;
}
"""


def convert(input_path: str) -> str:
    """Convert a markdown file to PDF. Returns the output path."""
    src = Path(input_path)
    if not src.exists():
        print(f"Error: {src} not found", file=sys.stderr)
        sys.exit(1)

    md_text = src.read_text(encoding="utf-8")
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>{CSS}</style>
</head><body>{html_body}</body></html>"""

    dst = src.with_suffix(".pdf")
    weasyprint.HTML(string=html).write_pdf(str(dst))
    return str(dst)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run md2pdf.py <input.md>", file=sys.stderr)
        sys.exit(1)

    output = convert(sys.argv[1])
    print(f"Created: {output}")
