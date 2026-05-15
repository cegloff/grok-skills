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

## Making State Inspection Powerful

The single most valuable thing you can add is a `get_state_summary()` method that evaluates JavaScript and returns structured data from your app's runtime (Redux store, Phaser scene, React context, etc.).

This turns the browser into a live, queryable database for your autonomous agents.

## File Organization

```
your-project/
├── tools/
│   ├── my_app_controller.py
│   └── my_autonomous_tester.py
└── (the rest of your app)
```

Then copy the generic `live_debug_controller.py` and `autonomous_web_tester.py` from this skill as a starting point (or import them if you install the skill as a package later).

## Next Steps for This Skill

- Turn the core into an installable Python package
- Add more example applications
- Add video recording support
- Add better CDP connection discovery
```