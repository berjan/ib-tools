---
description: Convert PDF files to Markdown using Microsoft's markitdown. Use when the user wants to convert a PDF to markdown, extract text from a PDF, or make a PDF readable as markdown. Also supports DOCX, PPTX, XLSX, HTML, images, and audio files.
---

# PDF to Markdown

Convert PDF (and other document formats) to Markdown using Microsoft's `markitdown` via `uvx`.

## Prerequisites

Install `uv` (includes `uvx`) if not already available:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

No other dependencies required.

## Usage

```bash
# PDF to Markdown
uvx --from 'markitdown[pdf]' markitdown input.pdf -o output.md

# All formats (DOCX, PPTX, XLSX, HTML, images, audio)
uvx --from 'markitdown[all]' markitdown input.docx -o output.md
```

Supported extras: `[pdf]`, `[docx]`, `[pptx]`, `[xlsx]`, `[all]`.

## Options

| Flag | Description |
|------|-------------|
| `-o` | Output file path (otherwise prints to stdout) |
| `-d` | Use Azure Document Intelligence for OCR |
| `-e` | Document Intelligence endpoint (requires `-d`) |

## Examples

```bash
# Convert PDF and save to file
uvx --from 'markitdown[pdf]' markitdown report.pdf -o report.md

# Convert DOCX
uvx --from 'markitdown[docx]' markitdown contract.docx -o contract.md

# Convert and print to stdout
uvx --from 'markitdown[pdf]' markitdown invoice.pdf

# Pipe from stdin
cat document.pdf | uvx --from 'markitdown[pdf]' markitdown
```

## Workflow

1. Identify the input file format to choose the correct extra (`[pdf]`, `[docx]`, or `[all]`).
2. Run `uvx --from 'markitdown[<extra>]' markitdown <input> -o <output>`.
3. Read the output markdown to verify conversion quality.
