#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Slack summary — show latest messages from DMs, group DMs, and channels at a glance.

Usage:
    uv run scripts/summary.py              # Last 20 messages per conversation
    uv run scripts/summary.py --limit 5    # Last 5 messages per conversation
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


def get_conversations(token, conv_type):
    """Fetch conversations of a given type, sorted by latest activity."""
    data = slack_api(
        "conversations.list",
        {"types": conv_type, "limit": "200", "exclude_archived": "true"},
        token=token,
    )
    if not data.get("ok"):
        print(f"Error listing {conv_type}: {data.get('error', 'unknown')}", file=sys.stderr)
        return []
    channels = data.get("channels", [])
    # Sort by latest activity (most recent first)
    channels.sort(key=lambda c: float(c.get("updated", 0) or 0), reverse=True)
    return channels


def get_dm_name(channel, user_map):
    """Get a readable name for a DM conversation."""
    user_id = channel.get("user", "")
    profile = user_map.get(user_id)
    if profile:
        return profile.get("display_name") or profile.get("real_name") or profile.get("name") or user_id
    return user_id


def main():
    args = sys.argv[1:]
    limit = 20

    if "--limit" in args:
        idx = args.index("--limit")
        if idx + 1 < len(args):
            limit = int(args[idx + 1])

    token = get_token()

    # Fetch all conversation types
    dms = get_conversations(token, "im")
    group_dms = get_conversations(token, "mpim")
    channels = get_conversations(token, "public_channel,private_channel")

    # Collect all user IDs we need to resolve (DM partners)
    dm_user_ids = [ch.get("user") for ch in dms if ch.get("user")]
    all_user_ids = set(dm_user_ids)

    # Pre-resolve DM partner names
    user_map = batch_resolve_users(list(all_user_ids), token=token) if all_user_ids else {}

    # Filter to only conversations with recent messages
    active_dms = [ch for ch in dms if float(ch.get("updated", 0) or 0) > 0]
    active_groups = [ch for ch in group_dms if float(ch.get("updated", 0) or 0) > 0]
    active_channels = [ch for ch in channels if ch.get("is_member")]

    if not active_dms and not active_groups and not active_channels:
        print("No recent activity found.")
        return

    # Print DM summaries
    if active_dms:
        print("=" * 60)
        print("DIRECT MESSAGES")
        print("=" * 60)

        for ch in active_dms:
            name = get_dm_name(ch, user_map)
            channel_id = ch["id"]

            data = slack_api(
                "conversations.history",
                {"channel": channel_id, "limit": str(limit)},
                token=token,
            )
            if not data.get("ok"):
                continue

            messages = data.get("messages", [])
            if not messages:
                continue

            # Resolve any new user IDs from messages
            msg_user_ids = extract_user_ids(messages)
            new_ids = msg_user_ids - set(user_map.keys())
            if new_ids:
                user_map.update(batch_resolve_users(list(new_ids), token=token))

            messages.reverse()

            print(f"\n--- {name} ---")
            print(format_messages(messages, user_map))

    # Print group DM summaries
    if active_groups:
        print()
        print("=" * 60)
        print("GROUP DIRECT MESSAGES")
        print("=" * 60)

        for ch in active_groups:
            name = ch.get("name", ch["id"])
            # Clean up auto-generated mpim names
            if name.startswith("mpdm-"):
                name = name.replace("mpdm-", "").replace("--", ", ").rstrip("-")
            channel_id = ch["id"]

            data = slack_api(
                "conversations.history",
                {"channel": channel_id, "limit": str(limit)},
                token=token,
            )
            if not data.get("ok"):
                continue

            messages = data.get("messages", [])
            if not messages:
                continue

            # Resolve any new user IDs from messages
            msg_user_ids = extract_user_ids(messages)
            new_ids = msg_user_ids - set(user_map.keys())
            if new_ids:
                user_map.update(batch_resolve_users(list(new_ids), token=token))

            messages.reverse()

            print(f"\n--- {name} ---")
            print(format_messages(messages, user_map))

    # Print channel summaries
    if active_channels:
        print()
        print("=" * 60)
        print("CHANNELS")
        print("=" * 60)

        for ch in active_channels:
            name = ch.get("name", ch["id"])
            private = " (private)" if ch.get("is_private") else ""
            channel_id = ch["id"]

            data = slack_api(
                "conversations.history",
                {"channel": channel_id, "limit": str(limit)},
                token=token,
            )
            if not data.get("ok"):
                continue

            messages = data.get("messages", [])
            if not messages:
                continue

            # Resolve any new user IDs from messages
            msg_user_ids = extract_user_ids(messages)
            new_ids = msg_user_ids - set(user_map.keys())
            if new_ids:
                user_map.update(batch_resolve_users(list(new_ids), token=token))

            messages.reverse()

            print(f"\n--- #{name}{private} ---")
            print(format_messages(messages, user_map))

    print()


if __name__ == "__main__":
    main()
