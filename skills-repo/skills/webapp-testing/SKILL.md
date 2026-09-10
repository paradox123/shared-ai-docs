---
name: webapp-testing
description: Toolkit for verifying and debugging local web applications, generated HTML previews (including email templates), and static pages with an available Browser tool or Playwright. Supports functional checks, rendered visual QA, screenshots, and browser-console inspection.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

Start with the smallest route that produces rendered evidence:

- Use a callable Browser tool first for a one-off navigation, DOM inspection,
  interaction, or screenshot.
- Use a native Playwright script when the Browser tool is unavailable or the
  task needs repeatable assertions, console capture, multiple pages, or a
  server-and-test command that should run as one process.
- For a Playwright script, prefer Python only after the import preflight below
  succeeds; otherwise switch directly to the Node fallback. Once one route is
  viable, do not probe other runtimes or install packages ad hoc.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

Use the helper scripts as black boxes. Start with the stable invocation patterns below and only fall back to `--help` when the known-good shape does not fit the task. Do not read the source unless the helper cannot express the workflow you need.

For Codex Desktop sessions where a Playwright script is the right route, prefer
the bundled runtimes:

```bash
~/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  <skill-dir>/scripts/with_server.py \
  --server "<dev-server-command>" \
  --port <port> \
  -- python /tmp/your_playwright_script.py
```

Before choosing the Python form, verify the module is actually present:

```bash
~/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -c "import playwright"
```

If that import fails, do not run `find ~/...`, `npm ls -g`, or
`npm install` just to rediscover Playwright. Use one of these fallbacks:

- If a Browser tool became available and the task does not require a reusable
  script, use it for the rendered check.
- If you need Node packages inside the Node REPL Playwright fallback, add the bundled module root once:

```text
js_add_node_module_dir path=~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules
```

- If you need a shell `node` script under `with_server.py`, set `NODE_PATH` to
  the bundled module root and import CommonJS packages through the default export:

```javascript
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright-core");
```

If Playwright reports that its bundled browser executable is missing, first try
launching an installed system browser such as Google Chrome with
`executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`.
Only ask to install browsers or npm packages when no local browser path works.

## Decision Tree: Choosing Your Approach

```
User task → Is it static or generated HTML?
    ├─ Yes → Read the HTML file directly to identify selectors
    │         ├─ Self-contained → Open file:// with the chosen Browser/Playwright route
    │         └─ Needs HTTP/assets → Serve it with the smallest existing repo command
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Use the known-good `with_server.py` pattern below
        │        Then write the smallest Playwright script that verifies the task
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

For generated HTML such as an email preview, use the application's production
renderer or an existing repo fixture when practical, verify that it emitted a
non-empty artifact, and then inspect that artifact through the static branch
above. Do not recreate production markup solely to obtain a screenshot. This
skill owns rendered verification; project-specific fixture generation and
local-stack provisioning belong to the repository's helpers or playbook.

## Example: Using with_server.py

Use a direct known-good invocation first:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

If you are in Codex Desktop and want the fully qualified bundled runtime form:

```bash
~/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  ~/Documents/DanielsVault/_shared/shared-ai-docs/skills-repo/skills/webapp-testing/scripts/with_server.py \
  --server "npm run dev -- --host 127.0.0.1 --port 4173" \
  --port 4173 \
  -- python /tmp/your_automation.py
```

Only run `python scripts/with_server.py --help` when you already know you need a variant that the stable examples above do not cover.

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Start from the stable examples in this skill and use `--help` only when those examples clearly do not fit.
- For Codex Desktop local-app checks, use a callable Browser tool for one-off
  rendered inspection; otherwise use `with_server.py` plus the smallest
  Playwright script that proves the task.
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation
