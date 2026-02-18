---
description: Read messages from Slack channels using the Slack Web API. Use when the user wants to read slack messages, list slack channels, check what was said in slack, search slack conversations, or look up slack users.
---

# Slack Bot

Read messages from Slack channels using `curl` and the Slack Web API. Read-only — no posting.

## Prerequisites

A `SLACK_BOT_TOKEN` environment variable must be set (starts with `xoxb-`).

To create a Slack App and get a bot token:

1. Go to https://api.slack.com/apps and click **Create New App** > **From scratch**
2. Name the app and select your workspace
3. Go to **OAuth & Permissions** and add these **Bot Token Scopes**:
   - `channels:history` — read messages in public channels
   - `channels:read` — list public channels
   - `groups:history` — read messages in private channels (optional)
   - `groups:read` — list private channels (optional)
   - `im:history` — read direct messages (optional)
   - `im:read` — list direct messages (optional)
   - `mpim:history` — read group direct messages (optional)
   - `mpim:read` — list group direct messages (optional)
   - `users:read` — resolve user IDs to names
4. Click **Install to Workspace** and authorize
5. Copy the **Bot User OAuth Token** (`xoxb-...`)
6. Invite the bot to channels it should read: `/invite @YourBotName`

## Workflow

1. Verify the token is valid by calling `auth.test`:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
     "https://slack.com/api/auth.test" | jq '.'
   ```
   If `ok` is `false`, the token is invalid or revoked — ask the user to check their token.

2. List public channels the bot can see:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
     "https://slack.com/api/conversations.list?types=public_channel&limit=200" \
     | jq '.channels[] | {id: .id, name: .name, topic: .topic.value}'
   ```
   Only add `private_channel` to the `types` parameter if the bot has the `groups:read` scope.

3. Fetch recent messages from a channel:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
     "https://slack.com/api/conversations.history?channel=CHANNEL_ID&limit=20" \
     | jq '.messages[] | {user: .user, text: .text, ts: .ts}'
   ```
   If this returns `not_in_channel`, the bot must be invited first: `/invite @YourBotName` in that channel.

4. Resolve a user ID to a display name:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
     "https://slack.com/api/users.info?user=USER_ID" \
     | jq '{name: .user.real_name, display_name: .user.profile.display_name}'
   ```

5. Get channel details:
   ```bash
   curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
     "https://slack.com/api/conversations.info?channel=CHANNEL_ID" \
     | jq '.channel | {name: .name, topic: .topic.value, purpose: .purpose.value, members: .num_members}'
   ```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `not_authed` | Token is invalid, revoked, or the app was uninstalled | Generate a new token from the Slack App settings and reinstall to workspace |
| `not_in_channel` | Bot hasn't been invited to the channel | Run `/invite @YourBotName` in the channel |
| `missing_scope` | Token lacks a required OAuth scope | Add the scope in the app's OAuth & Permissions settings and reinstall |
| `channel_not_found` | Invalid channel ID or bot cannot see the channel | Double-check the channel ID with `conversations.list` |
| `account_inactive` | Token belongs to a deleted or deactivated user/bot | Reinstall the app to the workspace |

## API Reference

| Endpoint | Description | Key Parameters |
|----------|-------------|----------------|
| `auth.test` | Verify token and get bot identity | — |
| `conversations.list` | List channels | `types`, `limit`, `cursor` |
| `conversations.history` | Channel messages | `channel`, `limit`, `oldest`, `latest`, `cursor` |
| `conversations.info` | Channel details | `channel` |
| `users.info` | User profile | `user` |

## Pagination

For endpoints returning many results, use cursor-based pagination:

```bash
# First request
RESPONSE=$(curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/conversations.list?limit=100")

# Get next cursor
CURSOR=$(echo "$RESPONSE" | jq -r '.response_metadata.next_cursor')

# Next page (if cursor is not empty)
curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/conversations.list?limit=100&cursor=$CURSOR"
```

## Filtering Messages by Date

Use Unix timestamps with `oldest` and `latest` parameters:

```bash
# Messages from the last 24 hours
OLDEST=$(date -v-1d +%s 2>/dev/null || date -d '1 day ago' +%s)
curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/conversations.history?channel=CHANNEL_ID&oldest=$OLDEST&limit=100" \
  | jq '.messages[] | {user: .user, text: .text, ts: .ts}'
```

## Rate Limits

Slack API tier limits apply. For `conversations.history`, the rate limit is roughly 50 requests per minute for most apps. If you receive a `429` response, wait the number of seconds specified in the `Retry-After` header before retrying.

## Tips

- Always call `auth.test` first to verify the token before making other API calls
- Always check the `ok` field in responses: `jq '.ok'` — if `false`, check `.error` for details
- The bot must be invited to a channel before it can read messages from it
- Message timestamps (`ts`) serve as unique message IDs and can be used for threading
- To read thread replies, use `conversations.replies` with `channel` and `ts` parameters
