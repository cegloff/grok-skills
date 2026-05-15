```markdown
# grok-live-web-debug

**Live browser debugging using remote debugging (CDP), Playwright, and multi-subagent automation.**

A reusable Grok skill that lets you control a real, visible Chrome browser from Python while combining autonomous agents with interactive control. Perfect for debugging and testing complex local web applications (games, SPAs, admin tools, etc.).

## Overview

This skill solves a common pain point: traditional browser automation is either fully headless (hard to debug visually) or fully manual (no automation power). 

`grok-live-web-debug` gives you the best of both:
- You see everything happening live in your normal Chrome window
- Subagents or scripts can drive the browser programmatically
- You can jump in interactively at any moment via a Python REPL

## Key Features

- Connect to an existing Chrome instance via Chrome DevTools Protocol (CDP)
- High-level Playwright controller with easy extension points
- Base class for autonomous test workflows
- Cross-platform Chrome launcher (Python primary + shell wrappers)
- Strong Windows + WSL support (mirrored networking recommended)
- Multi-subagent friendly architecture

## Requirements

- Google Chrome or Chromium
- Python 3.10+
- `playwright` Python package (`pip install playwright && playwright install chromium`)

## Quick Start

### 1. Launch Chrome with Remote Debugging

```bash
python launchers/launch_chrome_debug.py
```

Chrome opens with remote debugging on port 9222 (and navigates to your target URL).

### 2. Connect Interactively

```bash
python -m controllers.live_debug_controller
```

This drops you into an interactive Python session connected to your browser.

### 3. Run Autonomous Tests

```bash
python -m testers.autonomous_web_tester --cycles 3
```

## Core Components

### Live Debug Controller

`controllers/live_debug_controller.py` — A reusable `LiveDebugController` class with common actions (`goto`, `click`, `fill`, `evaluate`, `screenshot`, etc.). Designed to be subclassed with application-specific helpers.

### Autonomous Web Tester

`testers/autonomous_web_tester.py` — `AutonomousWebTester` base class for repeatable test cycles. Includes example workflow.

### Launchers

`launchers/` contains the recommended cross-platform launcher:
- `launch_chrome_debug.py` (primary, works on Windows/macOS/Linux)
- Convenience wrappers: `launch-chrome-debug.sh` and `.ps1`

## Multi-Subagent Pattern

This skill is designed for powerful workflows:

- One subagent keeps your web server running (with auto-restart + log tailing)
- One subagent drives the browser autonomously or via the live controller
- You stay in the main session and can take interactive control whenever needed

See `docs/` for the recommended pattern.

## Extending for Your Application

1. Copy or subclass `LiveDebugController`
2. Add high-level methods specific to your app (e.g. `create_lobby()`, `login()`, `start_match()`)
3. Create a tester subclass with your test scenarios
4. Put the code in `examples/your-app/`

See `examples/rts-game/` for a real-world reference implementation (complex Phaser RTS game).

## Example Applications

- `examples/simple-web-app/` — Tiny FastAPI + HTMX demo app + tester
- `examples/rts-game/` — Full controller and autonomous tester for a real-time strategy game

## Documentation

- `docs/remote-debugging.md` — Detailed cross-platform setup (especially Windows + WSL mirrored networking)
- More guides coming (multi-subagent patterns, extending the controller, troubleshooting)

## Platform Support

- **Windows + WSL** (primary target — use mirrored networking for best results)
- **macOS**
- **Native Linux**

## Contributing

This skill lives in the [grok-skills](https://github.com/cegloff/grok-skills) monorepo.

Bug reports, improvements, and new example applications are welcome.
```
