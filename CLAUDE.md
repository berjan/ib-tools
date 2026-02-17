# ib-tools — Claude Code Plugin Marketplace

This repository is a **plugin marketplace** for Claude Code. It provides a collection of reusable plugins that can be installed by anyone using Claude Code.

## How it works

A marketplace is a git repository with a `.claude-plugin/marketplace.json` that lists available plugins. Each plugin lives in `plugins/<name>/` and contains:

- `.claude-plugin/plugin.json` — plugin manifest (name, description, version)
- `skills/<name>/SKILL.md` — the skill definition that Claude loads when triggered
- Optional: `scripts/`, `references/`, `assets/` for bundled resources

## Available plugins

| Plugin | Description | Usage |
|--------|-------------|-------|
| `mermaid-to-image` | Convert `.mmd` files to PNG/SVG/PDF | `uvx mmdc -i input.mmd -o output.png` |
| `pdf-to-markdown` | Convert PDF/DOCX/PPTX to Markdown | `uvx --from 'markitdown[pdf]' markitdown input.pdf -o output.md` |
| `skill-creator` | Guide for creating new skills and plugins | Follow the workflow to scaffold and package skills |

## Install for users

```bash
# Add the marketplace
/plugin marketplace add berjanbruens/ib-tools

# Install individual plugins
/plugin install mermaid-to-image@ib-tools
/plugin install pdf-to-markdown@ib-tools
/plugin install skill-creator@ib-tools
```

## Update

Users refresh their local copy with:

```bash
/plugin marketplace update
```

## Adding a new plugin

1. Create `plugins/<name>/.claude-plugin/plugin.json` with name, description, and version.
2. Create `plugins/<name>/skills/<name>/SKILL.md` with a `description` in the YAML frontmatter and instructions in the body.
3. Add the plugin entry to `.claude-plugin/marketplace.json` in the `plugins` array.
4. Use the `skill-creator` plugin for guidance on writing effective skills.

## Project requirements

All plugins in this marketplace use `uvx` (from [uv](https://docs.astral.sh/uv/)) to run Python CLI tools without installation. This keeps plugins zero-dependency and cross-platform (Linux, macOS, Windows).
