#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
Shared helpers for Slack API interactions.

Stdlib-only (urllib, json, os, sys, time) — no external dependencies.
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import urllib.parse

SLACK_BASE_URL = "https://slack.com/api"

# In-memory cache for resolved users (user_id -> profile dict)
_user_cache = {}


def get_token():
    """Read SLACK_USER_TOKEN from env. Exit with clear error if missing."""
    token = os.environ.get("SLACK_USER_TOKEN", "").strip()
    if not token:
        print("Error: SLACK_USER_TOKEN environment variable is not set.", file=sys.stderr)
        print("Set it with: export SLACK_USER_TOKEN=xoxp-...", file=sys.stderr)
        sys.exit(1)
    if not token.startswith("xoxp-"):
        print("Warning: token does not start with 'xoxp-' — are you sure this is a user token?", file=sys.stderr)
    return token


def slack_api(method, params=None, token=None, return_headers=False):
    """
    Call a Slack Web API method with Bearer auth.

    Returns parsed JSON response. If return_headers=True, returns (json, headers).
    """
    if token is None:
        token = get_token()

    url = f"{SLACK_BASE_URL}/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req) as resp:
            headers = dict(resp.headers)
            data = json.loads(resp.read().decode("utf-8"))
            if return_headers:
                return data, headers
            return data
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} from {method}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error calling {method}: {e.reason}", file=sys.stderr)
        sys.exit(1)


def get_scopes(token=None):
    """
    Call auth.test and extract granted scopes from x-oauth-scopes header.

    Returns (auth_info_dict, scopes_set).
    """
    if token is None:
        token = get_token()

    data, headers = slack_api("auth.test", token=token, return_headers=True)

    if not data.get("ok"):
        print(f"auth.test failed: {data.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    scopes_header = headers.get("x-oauth-scopes", headers.get("X-OAuth-Scopes", ""))
    scopes = {s.strip() for s in scopes_header.split(",") if s.strip()}

    return data, scopes


def available_types(scopes):
    """
    Map granted scopes to valid conversation types for conversations.list.

    Returns a comma-separated string of types the token can access.
    """
    type_map = {
        "channels:read": "public_channel",
        "groups:read": "private_channel",
        "im:read": "im",
        "mpim:read": "mpim",
    }
    types = [v for k, v in type_map.items() if k in scopes]
    return ",".join(types) if types else ""


def batch_resolve_users(user_ids, token=None):
    """
    Resolve a list of user IDs to profile dicts via users.info.

    Uses in-memory cache and rate limiting (Tier 4: ~100/min).
    Returns dict of {user_id: {id, name, display_name, real_name}}.
    """
    if token is None:
        token = get_token()

    result = {}
    to_resolve = []

    # Deduplicate and check cache
    for uid in set(user_ids):
        if uid in _user_cache:
            result[uid] = _user_cache[uid]
        else:
            to_resolve.append(uid)

    for i, uid in enumerate(to_resolve):
        if i > 0 and i % 40 == 0:
            # Basic rate limiting — pause every 40 requests
            time.sleep(1)

        data = slack_api("users.info", {"user": uid}, token=token)
        if data.get("ok") and "user" in data:
            user = data["user"]
            profile = {
                "id": user["id"],
                "name": user.get("name", ""),
                "real_name": user.get("real_name", ""),
                "display_name": user.get("profile", {}).get("display_name", ""),
            }
        else:
            profile = {
                "id": uid,
                "name": uid,
                "real_name": uid,
                "display_name": "",
            }

        _user_cache[uid] = profile
        result[uid] = profile

    return result


def _best_name(profile):
    """Pick the best display name from a user profile."""
    return profile.get("display_name") or profile.get("real_name") or profile.get("name") or profile.get("id", "?")


def _ts_to_human(ts):
    """Convert Slack timestamp to human-readable datetime."""
    try:
        epoch = float(ts.split(".")[0])
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch))
    except (ValueError, AttributeError):
        return ts


def format_messages(messages, user_map=None):
    """
    Render messages with resolved names, human-readable timestamps,
    and inline <@U...> replacement.

    messages: list of Slack message dicts
    user_map: dict of {user_id: profile_dict} from batch_resolve_users
    """
    if user_map is None:
        user_map = {}

    lines = []
    for msg in messages:
        user_id = msg.get("user", msg.get("bot_id", "system"))
        profile = user_map.get(user_id)
        name = _best_name(profile) if profile else user_id

        ts = _ts_to_human(msg.get("ts", ""))
        text = msg.get("text", "")

        # Replace inline <@U...> mentions with resolved names
        def replace_mention(match):
            uid = match.group(1)
            p = user_map.get(uid)
            return f"@{_best_name(p)}" if p else f"@{uid}"

        text = re.sub(r"<@(U[A-Z0-9]+)>", replace_mention, text)

        lines.append(f"[{ts}] {name}: {text}")

        # Show reactions if present
        if msg.get("reactions"):
            rxns = ", ".join(
                f":{r['name']}: ({r.get('count', 1)})" for r in msg["reactions"]
            )
            lines.append(f"  reactions: {rxns}")

    return "\n".join(lines)


def extract_user_ids(messages):
    """Extract all user IDs from messages (author + <@U...> mentions)."""
    ids = set()
    for msg in messages:
        if "user" in msg:
            ids.add(msg["user"])
        # Find <@U...> mentions in text
        text = msg.get("text", "")
        ids.update(re.findall(r"<@(U[A-Z0-9]+)>", text))
    return ids
