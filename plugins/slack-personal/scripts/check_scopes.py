#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Scope detection CLI — check what your Slack token can do.

Usage:
    uv run scripts/check_scopes.py              # Print token info + capabilities
    uv run scripts/check_scopes.py --check SCOPE # Exit 0 if scope granted, 1 if not
"""

import sys
import os

# Allow importing slack_helpers from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slack_helpers import get_scopes, available_types


CAPABILITY_MAP = {
    "channels:read": "List public channels",
    "channels:history": "Read public channel messages",
    "groups:read": "List private channels",
    "groups:history": "Read private channel messages",
    "im:read": "List direct messages",
    "im:history": "Read direct messages",
    "mpim:read": "List group direct messages",
    "mpim:history": "Read group direct messages",
    "users:read": "Resolve user IDs to names",
    "search:read": "Search messages and files",
}


def main():
    args = sys.argv[1:]

    # --check mode: silent boolean check
    if len(args) >= 2 and args[0] == "--check":
        scope_to_check = args[1]
        _, scopes = get_scopes()
        sys.exit(0 if scope_to_check in scopes else 1)

    # Default mode: print full report
    auth_info, scopes = get_scopes()

    print("=== Token Info ===")
    print(f"  User:      {auth_info.get('user', '?')}")
    print(f"  User ID:   {auth_info.get('user_id', '?')}")
    print(f"  Team:      {auth_info.get('team', '?')}")
    print(f"  Team ID:   {auth_info.get('team_id', '?')}")
    print()

    print(f"=== Granted Scopes ({len(scopes)}) ===")
    for scope in sorted(scopes):
        print(f"  {scope}")
    print()

    print("=== Capabilities ===")
    for scope, desc in CAPABILITY_MAP.items():
        status = "YES" if scope in scopes else " NO"
        print(f"  [{status}] {desc} ({scope})")
    print()

    types = available_types(scopes)
    if types:
        print(f"=== Available Conversation Types ===")
        print(f"  types={types}")
    else:
        print("WARNING: No conversation read scopes granted — cannot list any conversations.")
    print()

    # Summarize what's missing
    missing = [s for s in CAPABILITY_MAP if s not in scopes]
    if missing:
        print(f"=== Missing Scopes ({len(missing)}) ===")
        for scope in missing:
            print(f"  {scope} — {CAPABILITY_MAP[scope]}")
        print()
        print("To add scopes: go to https://api.slack.com/apps → your app → OAuth & Permissions")
        print("Add the scopes under 'User Token Scopes', then reinstall to workspace.")
    else:
        print("All scopes granted — full access available.")


if __name__ == "__main__":
    main()
