```markdown
# Extending the Skill for Your Own Application

The power of `grok-live-web-debug` comes from how easy it is to extend for your specific web app.

## Recommended Pattern

1. **Create a subclass** of `LiveDebugController` in your project or in `examples/your-app/`.
2. Add high-level, intent-revealing methods (`create_project()`, `login_as_admin()`, `start_simulation()`).
3. Create a tester subclass of `AutonomousWebTester` that uses your controller.
4. Document the high-level API in a README for that example.

## Example: Minimal Custom Controller

```python
# my_app_controller.py

from controllers.live_debug_controller import LiveDebugController

class MyAppController(LiveDebugController):
    def login(self, username: str, password: str):
        self.goto("http://localhost:3000/login")
        self.fill("#username", username)
        self.fill("#password", password)
        self.click("#login-btn")
        self.wait_for_selector(".dashboard")

    def create_project(self, name: str):
        self.click("#new-project")
        self.fill("#project-name", name)
        self.click("#create")
        self.wait_for_selector(".project-row")
```

## New Powerful Capabilities (Tracing + Video)

Your custom controller automatically inherits:

- `start_tracing()` / `stop_tracing()` — Record full interaction traces
- `start_video_recording()` / `stop_video_recording()`
- `record_full_game()` style helpers (see `examples/rts-game/rts_controller.py`)

You can also pass these at construction time:

```python
ctrl = MyAppController(
    fresh_context=True,
    record_video=True,
    video_dir="recordings/my-app"
)
ctrl.connect()
ctrl.start_tracing("checkout-flow")
```

## Making State Inspection Powerful

The single most valuable thing you can add is a `get_state_summary()` method that evaluates JavaScript and returns structured data from your app's runtime (Redux store, Phaser scene, React context, etc.).

This turns the browser into a live, queryable database for your autonomous agents.

## Robust CDP Discovery

The base controller now includes aggressive auto-discovery:
- Probes `/json/version` on many common addresses
- Handles WSL2 host IP detection via `/etc/resolv.conf`
- Tries `host.docker.internal`, IPv6, localhost variants, etc.

You rarely need to specify the exact CDP URL anymore.

## File Organization

```
your-project/
├── tools/
│   ├── my_app_controller.py
│   └── my_autonomous_tester.py
└── (the rest of your app)
```

Then copy the generic `live_debug_controller.py` and `autonomous_web_tester.py` from this skill as a starting point (or import them if you install the skill as a package later).
```