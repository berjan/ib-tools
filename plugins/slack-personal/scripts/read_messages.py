#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Formatted message reader — fetch and display Slack messages with resolved names.

Usage:
    uv run scripts/read_messages.py CHANNEL_ID [--limit 20] [--oldest TS] [--thread TS]
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slack_helpers import (
    get_token,
    slack_api,
    batch_resolve_users,
    extract_user_ids,
    format_messages,
)


def parse_args(args):
    """Parse CLI arguments into a dict."""
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0)

    result = {"channel": args[0], "limit": "20"}
    i = 1
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            result["limit"] = args[i + 1]
            i += 2
        elif args[i] == "--oldest" and i + 1 < len(args):
            result["oldest"] = args[i + 1]
            i += 2
        elif args[i] == "--thread" and i + 1 < len(args):
            result["thread_ts"] = args[i + 1]
            i += 2
        else:
            print(f"Unknown argument: {args[i]}", file=sys.stderr)
            sys.exit(1)
    return result


def main():
    opts = parse_args(sys.argv[1:])
    token = get_token()

    # Build API params
    if "thread_ts" in opts:
        method = "conversations.replies"
        params = {
            "channel": opts["channel"],
            "ts": opts["thread_ts"],
            "limit": opts["limit"],
        }
    else:
        method = "conversations.history"
        params = {
            "channel": opts["channel"],
            "limit": opts["limit"],
        }
        if "oldest" in opts:
            params["oldest"] = opts["oldest"]

    # Fetch messages
    data = slack_api(method, params, token=token)

    if not data.get("ok"):
        print(f"Error: {data.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    messages = data.get("messages", [])

    if not messages:
        print("No messages found.")
        return

    # Reverse to chronological order (Slack returns newest first for history)
    if method == "conversations.history":
        messages.reverse()

    # Resolve all user IDs
    user_ids = extract_user_ids(messages)
    user_map = batch_resolve_users(list(user_ids), token=token) if user_ids else {}

    # Print formatted output
    print(format_messages(messages, user_map))


if __name__ == "__main__":
    main()
