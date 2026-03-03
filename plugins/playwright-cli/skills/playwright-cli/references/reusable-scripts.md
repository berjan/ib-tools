# Reusable Scripts

Save a completed interactive playwright-cli flow as a re-runnable bash script so it can be repeated without manual intervention.

## Script format

```bash
#!/bin/bash
set -e

# Load environment variables (Cloudflare Access tokens, etc.)
if [ -f .env ]; then
  source .env
fi

# Disable Chrome sandbox when running as root / in a container
export PLAYWRIGHT_MCP_SANDBOX=false

# --- Flow starts here ---
playwright-cli open

# Set Cloudflare Access headers if needed
playwright-cli run-code "async page => { await page.context().setExtraHTTPHeaders({'CF-Access-Client-Id': '$CF_ACCESS_CLIENT_ID', 'CF-Access-Client-Secret': '$CF_ACCESS_CLIENT_SECRET'}); }"

playwright-cli goto https://app.example.com/login
playwright-cli fill e1 "user@example.com"
playwright-cli fill e2 "s3cret"
playwright-cli click e3          # Submit button

playwright-cli goto https://app.example.com/dashboard
playwright-cli click e7          # "Export" button
playwright-cli screenshot --filename=export-result.png

playwright-cli close
```

## Key points

- Always start with `set -e` so the script stops on the first error.
- Source `.env` at the top for any secrets (CF tokens, credentials).
- Export `PLAYWRIGHT_MCP_SANDBOX=false` when running headless / as root.
- End with `playwright-cli close` to clean up the browser.
- Element refs (`e1`, `e3`, …) are snapshot-dependent. If the page structure changes, re-run the flow interactively and update the refs.

## Where to store scripts

Place scripts in a `scripts/` directory relative to your project root:

```
scripts/
  login-and-export.sh
  create-invoice.sh
```

Make them executable:

```bash
chmod +x scripts/login-and-export.sh
```

## Running a saved script

```bash
bash scripts/login-and-export.sh
```

Or, if marked executable:

```bash
./scripts/login-and-export.sh
```

## Creating a script from an interactive session

After completing a successful interactive flow, ask Claude to turn the session into a reusable script. Claude will:

1. Collect the sequence of `playwright-cli` commands from the session.
2. Wrap them in the format above (shebang, `set -e`, env loading, close).
3. Write the script to `scripts/<descriptive-name>.sh`.
