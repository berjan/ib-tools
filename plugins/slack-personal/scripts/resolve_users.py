#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Batch user resolution CLI — resolve Slack user IDs to names.

Usage:
    uv run scripts/resolve_users.py U12345 U67890
    uv run scripts/resolve_users.py --from-channel CHANNEL_ID [--limit 20]
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slack_helpers import (
    get_token,
    slack_api,
    batch_resolve_users,
    extract_user_ids,
)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0)

    token = get_token()

    if args[0] == "--from-channel":
        if len(args) < 2:
            print("Error: --from-channel requires a CHANNEL_ID", file=sys.stderr)
            sys.exit(1)

        channel_id = args[1]
        limit = 20

        # Parse --limit
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                limit = int(args[idx + 1])

        # Fetch messages
        data = slack_api(
            "conversations.history",
            {"channel": channel_id, "limit": str(limit)},
            token=token,
        )

        if not data.get("ok"):
            print(f"Error: {data.get('error', 'unknown')}", file=sys.stderr)
            sys.exit(1)

        messages = data.get("messages", [])
        user_ids = extract_user_ids(messages)

        if not user_ids:
            print("{}")
            return

        user_map = batch_resolve_users(list(user_ids), token=token)

    else:
        # Direct mode: resolve given user IDs
        user_ids = [a for a in args if a.startswith("U")]

        if not user_ids:
            print("Error: no user IDs provided (should start with 'U')", file=sys.stderr)
            sys.exit(1)

        user_map = batch_resolve_users(user_ids, token=token)

    # Output as JSON
    print(json.dumps(user_map, indent=2))


if __name__ == "__main__":
    main()
