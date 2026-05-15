```markdown
# Grok Live Web Debug

**Live browser debugging and autonomous testing for any local web application using remote debugging (CDP) + Playwright.**

This skill lets you control a *real, visible Chrome instance* from Python while freely mixing long-running autonomous agents with hands-on interactive debugging — all while you watch everything happen live in your normal browser tab.

## Why This Skill Exists

Traditional browser automation forces an unpleasant tradeoff:
- Headless = fast but you can't see what's happening and debugging is painful
- Manual browser = you see everything but you get no automation power

`grok-live-web-debug` removes the tradeoff. You get:
- Full visual feedback in a real browser
- Powerful Python + Playwright automation
- The ability for subagents to run long test loops autonomously
- Instant ability to take interactive control when something looks wrong

It has been battle-tested on a complex real-time strategy game and repeatedly found deep, subtle bugs (lobby state machines, fog-of-war, camera/HUD scaling, AI propagation, etc.) that would have been extremely difficult to catch otherwise.

## Quick Start

```bash
# 1. Launch Chrome with remote debugging
python launchers/launch_chrome_debug.py

# 2. Connect interactively (drops you into a Python REPL)
python -m controllers.live_debug_controller

# 3. Run autonomous tests
python -m testers.autonomous_web_tester --cycles 3
```

## Core Components

### Live Debug Controller (`controllers/`)
An interactive `LiveDebugController` with high-level helpers (`goto`, `click`, `fill`, `evaluate`, `screenshot`, etc.). Run it as a module to get a powerful REPL connected to your browser.

Easily subclassed with application-specific methods.

### Autonomous Web Tester (`testers/`)
`AutonomousWebTester` base class for repeatable test workflows. Handles looping, error reporting, and failure screenshots. Subclass it for your app.

### Chrome Launchers (`launchers/`)
The recommended cross-platform way to launch Chrome with remote debugging:
- `launch_chrome_debug.py` (primary — works on Windows, macOS, Linux)
- `launch-chrome-debug.sh` and `.ps1` (convenience wrappers)

## Multi-Subagent Pattern
This skill shines when combined with Grok subagents:

- One subagent manages your web server (persistent, auto-restart, log monitoring)
- One subagent drives the browser (autonomous tester or interactive controller)
- You stay in control and can take over the REPL instantly when needed

See `docs/multi-subagent-pattern.md` for the full recommended workflow.

## Example Applications

- `examples/simple-web-app/` — Tiny, clean FastAPI + HTMX demo perfect for learning the skill
- `examples/rts-game/` — Full reference implementation for a complex Phaser 3 RTS game (the original use case). Includes `RTSLiveController` and `RTSAutonomousTester` that can play complete matches autonomously.

## Documentation

- `docs/remote-debugging.md` — Detailed cross-platform setup instructions (especially important for Windows + WSL mirrored networking)
- `docs/multi-subagent-pattern.md` — How to get the most out of this skill with subagents
- `docs/extending.md` — How to build your own high-level controller and tester for your application

## Platform Support

- **Windows + WSL** (primary — enable mirrored networking in `.wslconfig` for best results)
- **macOS**
- **Native Linux**

## Extending
See `docs/extending.md` and the `examples/` folder. The pattern is deliberately simple: subclass `LiveDebugController`, add your app-specific high-level methods, and write autonomous workflows on top.

## Contributing
This skill is part of the [grok-skills](https://github.com/cegloff/grok-skills) monorepo.

Contributions, new examples, and improvements are very welcome.
```