```markdown
# grok-live-web-debug

A powerful, reusable pattern for **live browser debugging** of any local web application using remote debugging (CDP), Playwright, and multi-subagent automation.

Works great with:
- Web games (Phaser, Unity WebGL, etc.)
- Modern SPAs (React, Vue, Svelte, Next.js, etc.)
- Admin panels and internal tools
- Any localhost web app you want to debug or test with real browser visibility

## Key Features

- Connect to your **real, visible Chrome** instance via remote debugging
- Mix **autonomous test agents** with **interactive control**
- Watch everything happen live in your normal browser
- Strong support for Windows + WSL (mirrored networking), macOS, and Linux

## Requirements

- Google Chrome (or Chromium)
- Python 3.10+
- Playwright for Python

## Usage

See the [README](./README.md) for detailed setup and usage instructions.

## Available Commands

This skill provides two main entrypoints:

- `live_debug_controller.py` — Interactive REPL with high-level helpers
- `autonomous_web_tester.py` — Run automated test workflows

Example interactive usage:
```bash
python -m skills.web_live_debug.controllers.live_debug_controller
```

Once connected, you can run commands like:
- `create_lobby("My Game", 2)` (example app-specific helper)
- `goto("/some/page")`
- `click("#submit")`
- `evaluate_js("window.myApp.getState()")`
- `take_screenshot("before_test")`

## Related Patterns

This skill demonstrates powerful multi-subagent workflows:
- One subagent manages your web server
- Another drives the browser
- You stay in control via an interactive REPL when needed

## Platform Support

- Windows + WSL (recommended setup with mirrored networking)
- macOS
- Native Linux

## Contributing

See the main [grok-skills](https://github.com/cegloff/grok-skills) repository.
```
