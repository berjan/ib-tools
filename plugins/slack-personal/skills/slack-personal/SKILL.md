---
description: Read personal Slack messages including DMs, group DMs, and channel conversations. Use when the user wants to read their DMs, check private messages, see group conversations, list their Slack channels, search messages, or catch up on Slack activity.
---

# Slack Personal

Read your own Slack messages — DMs, group DMs, private channels, and public channels — using `curl` and the Slack Web API. Uses a **user token** so you see everything you have access to, no bot invites needed. Read-only.

## Quick Setup

Create a Slack app with all the right scopes in one step using the bundled manifest:

1. Go to https://api.slack.com/apps → **Create New App** → **From a manifest**
2. Select your workspace
3. Paste the contents of `slack-app-manifest.json` (included in this plugin) as JSON
4. Click **Create** and then **Install to Workspace**
5. Copy the **User OAuth Token** (`xoxp-...`) from **OAuth & Permissions**
6. Set it as an environment variable: `export SLACK_USER_TOKEN=xoxp-...`

The manifest grants these read-only **user** scopes:

| Scope | Access |
|-------|--------|
| `channels:read` + `channels:history` | Public channels you're in |
| `groups:read` + `groups:history` | Private channels you're in |
| `im:read` + `im:history` | Your direct messages |
| `mpim:read` + `mpim:history` | Your group direct messages |
| `users:read` | Resolve user IDs to names |
| `search:read` | Search messages and files |

## Helper Scripts

This plugin includes Python helper scripts (stdlib-only, no dependencies) for common tasks:

### Check Scopes

Verify your token and see what capabilities are available:

```bash
uv run scripts/check_scopes.py                  # Full report: token info + capabilities
uv run scripts/check_scopes.py --check search:read  # Silent check: exit 0 if granted, 1 if not
```

### Resolve Users

Batch-resolve Slack user IDs to real names:

```bash
uv run scripts/resolve_users.py U12345 U67890                 # Resolve specific IDs
uv run scripts/resolve_users.py --from-channel C1Y6QA5M0 --limit 20  # Extract + resolve from messages
```

### Read Messages

Fetch and display messages with resolved usernames and readable timestamps:

```bash
uv run scripts/read_messages.py C1Y6QA5M0 --limit 20           # Channel messages
uv run scripts/read_messages.py C1Y6QA5M0 --thread 1234567890.123456  # Thread replies
uv run scripts/read_messages.py C1Y6QA5M0 --oldest 1700000000  # Messages since timestamp
```

## Prerequisites

A `SLACK_USER_TOKEN` environment variable must be set (starts with `xoxp-`).

## Workflow

1. Verify the token and check capabilities:
   ```bash
   uv run scripts/check_scopes.py
   ```
   This shows your token info, granted scopes, and which features are available. If you prefer a manual check:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
     "https://slack.com/api/auth.test" | jq '.'
   ```
   If `ok` is `false`, the token is invalid or revoked — ask the user to check their token.

2. List all conversations you have access to (channels, DMs, group DMs):
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
     "https://slack.com/api/conversations.list?types=public_channel,private_channel,im,mpim&limit=200" \
     | jq '.channels[] | {id: .id, name: (.name // "DM"), is_im: .is_im, is_mpim: .is_mpim, is_private: .is_private}'
   ```
   If `missing_scope` is returned, reduce the `types` parameter to only the scopes available. Use `check_scopes.py` to see which types your token supports.

3. List only your DMs:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
     "https://slack.com/api/conversations.list?types=im&limit=200" \
     | jq '.channels[] | {id: .id, user: .user}'
   ```

4. List only your group DMs:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
     "https://slack.com/api/conversations.list?types=mpim&limit=200" \
     | jq '.channels[] | {id: .id, name: .name, num_members: .num_members}'
   ```

5. Read messages from any conversation (channel, DM, or group DM):
   ```bash
   uv run scripts/read_messages.py CONVERSATION_ID --limit 20
   ```
   This auto-resolves user IDs to names and formats timestamps. For raw API output:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
     "https://slack.com/api/conversations.history?channel=CONVERSATION_ID&limit=20" \
     | jq '.messages[] | {user: .user, text: .text, ts: .ts}'
   ```

6. Read thread replies:
   ```bash
   uv run scripts/read_messages.py CONVERSATION_ID --thread THREAD_TS
   ```
   Or with curl:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
     "https://slack.com/api/conversations.replies?channel=CONVERSATION_ID&ts=THREAD_TS&limit=50" \
     | jq '.messages[] | {user: .user, text: .text, ts: .ts}'
   ```

7. Resolve user IDs to names:
   ```bash
   uv run scripts/resolve_users.py USER_ID1 USER_ID2
   ```
   Or with curl:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
     "https://slack.com/api/users.info?user=USER_ID" \
     | jq '{id: .user.id, name: .user.real_name, display_name: .user.profile.display_name}'
   ```

8. Get conversation details:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
     "https://slack.com/api/conversations.info?channel=CONVERSATION_ID" \
     | jq '.channel | {name: .name, is_im: .is_im, is_mpim: .is_mpim, topic: .topic.value, purpose: .purpose.value}'
   ```

## Search Messages

Search across all messages you have access to (requires `search:read` scope):

```bash
curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
  "https://slack.com/api/search.messages?query=SEARCH_QUERY&count=20" \
  | jq '.messages.matches[] | {channel: .channel.name, user: .username, text: .text, ts: .ts, permalink: .permalink}'
```

Search modifiers:

| Modifier | Example | Description |
|----------|---------|-------------|
| `in:#channel` | `in:#general bug report` | Search within a specific channel |
| `from:@user` | `from:@berjan deploy` | Messages from a specific user |
| `before:` / `after:` | `after:2024-01-01` | Date range filter |
| `has:link` | `has:link documentation` | Messages containing links |
| `has:reaction` | `has:reaction :+1:` | Messages with specific reactions |

Check if search is available before using:
```bash
uv run scripts/check_scopes.py --check search:read && echo "Search available" || echo "search:read scope not granted"
```

## List Channel Members

List members of a channel or conversation:

```bash
curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
  "https://slack.com/api/conversations.members?channel=CONVERSATION_ID&limit=200" \
  | jq '.members[]'
```

Resolve the member IDs to names:
```bash
uv run scripts/resolve_users.py $(curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
  "https://slack.com/api/conversations.members?channel=CONVERSATION_ID&limit=200" \
  | jq -r '.members[]')
```

## Reading Messages by Date

Use Unix timestamps with `oldest` and `latest` parameters:

```bash
# Messages from the last 24 hours
OLDEST=$(date -v-1d +%s 2>/dev/null || date -d '1 day ago' +%s)
curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
  "https://slack.com/api/conversations.history?channel=CONVERSATION_ID&oldest=$OLDEST&limit=100" \
  | jq '.messages[] | {user: .user, text: .text, ts: .ts}'
```

## Pagination

For conversations with many messages, use cursor-based pagination:

```bash
RESPONSE=$(curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
  "https://slack.com/api/conversations.history?channel=CONVERSATION_ID&limit=100")

CURSOR=$(echo "$RESPONSE" | jq -r '.response_metadata.next_cursor')

# Next page (if cursor is not empty)
curl -s -H "Authorization: Bearer $SLACK_USER_TOKEN" \
  "https://slack.com/api/conversations.history?channel=CONVERSATION_ID&limit=100&cursor=$CURSOR"
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `not_authed` | Token is invalid, revoked, or app was uninstalled | Generate a new token and reinstall to workspace |
| `missing_scope` | Token lacks a required OAuth scope | Run `check_scopes.py` to see what's missing, add scopes and reinstall |
| `channel_not_found` | Invalid conversation ID | Verify the ID with `conversations.list` |
| `account_inactive` | Token belongs to a deactivated user | Reinstall the app to the workspace |

## Tips

- Run `check_scopes.py` first to verify your token and see available capabilities before making API calls
- Always check the `ok` field in responses — if `false`, check `.error` for details
- With a user token you see everything you can see in Slack — no need to invite a bot
- DMs show a `user` field instead of `name` — resolve it with `resolve_users.py` or `users.info`
- For group DMs (`mpim`), the name is auto-generated from member names
- Message timestamps (`ts`) serve as unique message IDs and are used for threading
- Use `read_messages.py` for formatted output with resolved names, or curl for raw JSON
