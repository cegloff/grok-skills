```markdown
# grok-skills

A monorepo for high-quality, reusable Grok skills.

These skills capture powerful, practical patterns that combine **real browsers**, **subagent autonomy**, and **interactive control**.

## Skills

| Skill | Description |
|-------|-------------|
| **[web-live-debug](./skills/web-live-debug/)** | Live browser debugging using remote debugging (CDP) + Playwright. Mix autonomous agents with interactive REPL control while watching everything in a real Chrome window. Excellent for complex web apps and games. Strong Windows + WSL support. |

## Philosophy

- **Visibility first**: Headed browser > headless for debugging hard problems.
- **Autonomy + Control**: Long-running agents that you can take over instantly.
- **High-leverage patterns**: Things that dramatically speed up real development work.
- **Cross-platform**: Especially great on Windows + WSL (mirrored networking).

## Getting Started

Each skill lives under `skills/<skill-name>/` and follows the official Grok skill format (`SKILL.md`).

Clone the repo and start with the README and SKILL.md inside the skill you're interested in.

## Platform Support

Skills in this repository aim to support the environments the author actually uses:
- Windows + WSL (with mirrored networking — strongly recommended)
- Native Linux
- macOS

## Contributing

New skills or major improvements are welcome. Please open an issue first to discuss scope.
```