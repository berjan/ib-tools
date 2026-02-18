---
description: Show a summary of your latest Slack messages across DMs, group DMs, and channels. Use when the user wants a quick overview of recent Slack activity, wants to catch up on messages, or asks for a Slack summary.
user_invocable: true
---

# Slack Summary

Show your latest Slack messages at a glance — DMs, group DMs, and all channels you're a member of.

## Prerequisites

A `SLACK_USER_TOKEN` environment variable must be set (starts with `xoxp-`).

## Usage

Run the summary script:

```bash
uv run scripts/summary.py
```

To limit the number of messages per conversation:

```bash
uv run scripts/summary.py --limit 5
```

## Workflow

1. Run `uv run scripts/summary.py --limit 20` to fetch the latest messages
2. Present the output to the user as a readable summary
3. If the user wants to dive deeper into a specific conversation, use `uv run scripts/read_messages.py CHANNEL_ID` for more messages or thread replies
