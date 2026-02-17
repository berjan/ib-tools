---
description: Convert Mermaid diagram files (.mmd) to PNG, SVG, or PDF images. Use when the user wants to render, export, or convert a Mermaid diagram to an image format. Triggers on requests like "convert this mermaid to png", "render diagram as svg", "export mermaid chart", or "generate image from .mmd file".
---

# Mermaid to Image

Convert Mermaid diagram files to PNG, SVG, or PDF using the `mmdc` Python package via `uvx`.

## Prerequisites

Install `uv` (includes `uvx`) if not already available:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

No other dependencies required. No Node.js, Docker, or browser needed.

## Usage

Convert a `.mmd` file to an image:

```bash
uvx mmdc -i input.mmd -o output.png
uvx mmdc -i input.mmd -o output.svg
uvx mmdc -i input.mmd -o output.pdf
```

The output format is determined by the file extension.

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-i` | Input mermaid file (required) | — |
| `-o` | Output file: `.png`, `.svg`, `.pdf` (required) | — |
| `-t` | Theme: `default`, `forest`, `dark`, `neutral` | `default` |
| `-b` | Background color | `white` |
| `-s` | Scale factor | `1.0` |
| `-w` | Width in pixels | auto |
| `-H` | Height in pixels | auto |

## Examples

```bash
# Basic PNG conversion
uvx mmdc -i diagram.mmd -o diagram.png

# Dark theme with transparent background at 2x resolution
uvx mmdc -i diagram.mmd -o diagram.png -t dark -b transparent -s 2

# SVG with forest theme
uvx mmdc -i diagram.mmd -o diagram.svg -t forest
```

## Workflow

1. Read the `.mmd` source file to verify it contains valid Mermaid syntax.
2. Run `uvx mmdc -i <input> -o <output>` with desired options.
3. Verify the output file was created successfully.
