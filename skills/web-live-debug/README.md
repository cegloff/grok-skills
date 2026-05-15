```markdown
# Grok Live Web Debug

A powerful, reusable skill for **live browser debugging** of any local web application.

This skill lets you connect to a real, visible Chrome instance via remote debugging (CDP) and control it using Playwright from Python — while mixing autonomous test agents with interactive control.

## Why This Skill?

Traditional browser automation is either:
- Fully headless and hard to debug, or
- Fully manual in the browser with no automation.

This skill gives you the best of both worlds:
- You see everything happening in a real browser tab
- You can drive it programmatically or let subagents run test workflows
- You can jump in interactively at any moment

## Core Components

- **Live Debug Controller** — An interactive Python REPL with high-level helpers for your specific app.
- **Autonomous Web Tester** — A framework for writing repeatable, autonomous test workflows.
- **Chrome Launcher** — Cross-platform scripts to launch Chrome with remote debugging enabled.
- **Multi-Subagent Pattern** — Recommended way to combine server management + browser automation.

## Supported Platforms

- Windows + WSL (with mirrored networking — recommended)
- Native Linux
- macOS

## Quick Start

See the [docs](docs/) folder for detailed setup instructions for your operating system.

Basic flow:
1. Launch Chrome with remote debugging using the provided launcher.
2. Run the live debug controller.
3. Start automating or let an autonomous tester take over.

## Example Use Cases

- Debugging complex game state or UI issues in web games
- End-to-end testing with real browser visibility
- Reproducing hard-to-catch race conditions or timing bugs
- Interactive exploration while an agent handles repetitive setup

## Project Structure

```
skills/web-live-debug/
├── SKILL.md
├── README.md
├── launchers/               # Chrome launch scripts
├── controllers/             # Interactive live controller
├── testers/                 # Autonomous test framework
├── examples/                # Example apps and workflows
└── docs/                    # Detailed guides
```

## Contributing

This skill is part of the [grok-skills](https://github.com/cegloff/grok-skills) monorepo.

## License

TBD
```