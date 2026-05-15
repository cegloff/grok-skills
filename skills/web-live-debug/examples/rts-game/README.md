```markdown
# RTS Game Example (Reference Implementation)

This folder contains a real-world, production-quality reference implementation of the `grok-live-web-debug` skill applied to a complex Phaser 3 real-time strategy game (Neon Dominion).

It demonstrates how to extend the generic skill for a non-trivial application with:
- Lobby creation + AI opponents
- Race selection
- Starting and playing full matches
- Reading game state via JavaScript evaluation
- Autonomous full-game test loops

## Why This Example Matters

The original development of this skill happened while building and debugging a full 4-race RTS. The patterns here (especially the multi-subagent + live browser approach) were extremely effective at finding and fixing bugs that would have been nearly impossible to catch with headless testing or manual play.

## Files

- `rts_controller.py` — `RTSLiveController` subclass with high-level game actions
- `rts_autonomous_tester.py` — Autonomous tester that can play complete games
- This README

## How to Use

1. Run your RTS game server + open the client in Chrome (launched with remote debugging)
2. From this directory or the skill root:

```bash
# Interactive debugging
python -m examples.rts_game.rts_controller

# Full autonomous game playing (multiple cycles)
python -m examples.rts_game.rts_autonomous_tester --cycles 2
```

## Key Methods in RTSLiveController

- `create_lobby(name, max_players)`
- `add_ai_players(count, race)`
- `select_race(race)`
- `start_match()`
- `get_game_state_summary()` — evaluates Phaser scene state
- `leave_match()` / `return_to_lobby()`
- `take_screenshot(name)`

These high-level methods hide all the DOM/JS details and make autonomous testing and debugging dramatically more powerful.

## Recommended Workflow

Use the multi-subagent pattern:
- One subagent runs `python -m server.main` (your game server)
- One subagent runs the autonomous tester
- You watch in the live Chrome tab and can take over the `RTSLiveController` REPL at any time

This combination has repeatedly found deep bugs (lobby lifecycle, fog-of-war, camera zoom + HUD scaling, AI propagation, etc.) in a fraction of the time traditional methods would require.
```