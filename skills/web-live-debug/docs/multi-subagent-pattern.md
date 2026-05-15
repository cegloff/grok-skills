```markdown
# Multi-Subagent Pattern

This skill was designed from the beginning to work beautifully with Grok's subagent system.

## Recommended Architecture

When working on a complex web application:

1. **Server Subagent** (persistent)
   - Runs `python -m server.main` or your web server
   - Monitors logs
   - Auto-restarts on crash
   - You can ask it to make code changes

2. **Browser Automation Subagent**
   - Runs the autonomous tester or the interactive controller
   - Can be long-running
   - Reports findings back to you

3. **You (Human + Main Agent)**
   - Stay in control
   - Use the live debug controller REPL when you want to explore
   - Watch the real browser tab the whole time
   - Jump in and take manual control instantly

## Why This Is So Powerful

- You get **visibility** (real browser, not headless)
- You get **autonomy** (long-running test loops while you do other things)
- You get **interactivity** (the moment something looks wrong, you can pause the agent and take the REPL)
- You get **fast iteration** (fix a bug in the server subagent, restart, and immediately re-run the browser tester)

## Example Session Flow

1. Start your game server in one subagent.
2. Launch Chrome with remote debugging.
3. Start an autonomous tester in another subagent: "Run 5 full games and report any errors or strange behavior."
4. While it runs, watch the live tab.
5. When the agent reports something suspicious (or you see it), take over with the interactive controller and investigate deeply using `evaluate()`, screenshots, etc.
6. Fix the bug, restart the tester, repeat.

This workflow found and fixed many subtle issues (fog of war, lobby state machine, camera zoom compensation, race propagation, etc.) extremely quickly.

## Tips

- Give the browser subagent clear success/failure criteria.
- Ask it to take screenshots on interesting events.
- Use `get_game_state_summary()` style methods liberally — they turn the browser into a powerful state inspector.
```