---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

Use the helper scripts as black boxes. Start with the stable invocation patterns below and only fall back to `--help` when the known-good shape does not fit the task. Do not read the source unless the helper cannot express the workflow you need.

For Codex Desktop sessions, prefer the bundled runtimes when you need Playwright quickly:

```bash
~/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  <skill-dir>/scripts/with_server.py \
  --server "<dev-server-command>" \
  --port <port> \
  -- python /tmp/your_playwright_script.py
```

If you need Node packages inside the Node REPL Playwright fallback, add the bundled module root once:

```text
js_add_node_module_dir path=~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules
```

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
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
- For Codex Desktop local-app checks, assume `with_server.py` plus a minimal Playwright script is the default path when the Browser plugin does not expose a callable browser tool in the turn.
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation
