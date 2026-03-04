---
name: md2pdf
description: Convert a markdown file to a professionally styled PDF. Use this skill whenever the user asks to convert markdown to PDF, export a .md file as PDF, generate a PDF from markdown, or wants a printable version of a markdown document. Also trigger when the user says "make a PDF of this", "export as PDF", or "convert to PDF" in the context of markdown files.
---

# Markdown to PDF Converter

Converts a markdown file to a clean, professionally styled PDF using the bundled script.

## Usage

Run the conversion script, passing the markdown file path as argument:

```bash
uv run .claude/skills/md2pdf/scripts/md2pdf.py <path-to-markdown-file>
```

The PDF will be saved in the same directory as the input file, with the same name but `.pdf` extension.

## What the script handles

- Markdown rendering including tables, code blocks, headings, bold/italic, links, lists, and horizontal rules
- Professional styling: Helvetica font, readable line spacing, proper heading hierarchy
- Clean table formatting with borders and alternating header background
- Automatic filename: `input.md` becomes `input.pdf`

## Example

User says: "Convert meetings/2026-03-04_summary.md to PDF"

```bash
uv run .claude/skills/md2pdf/scripts/md2pdf.py meetings/2026-03-04_summary.md
```

Output: `meetings/2026-03-04_summary.pdf`

## Notes

- Requires Python 3.9+. Dependencies (`markdown`, `weasyprint`) are auto-installed by `uv run`.
- If the user provides a relative path, use it as-is — the script handles it.
- For multiple files, run the script once per file.
