```markdown
# Simple Web App Example

A minimal FastAPI + HTMX application designed specifically as a learning target for the `grok-live-web-debug` skill.

## Purpose

This tiny app demonstrates:
- Connecting the live debug controller to a real running web app
- Performing clicks, fills, and waits
- Running autonomous test cycles
- Taking screenshots on success or failure

It is intentionally simple so you can focus on the debugging/automation skill itself rather than application complexity.

## Run the Example

```bash
cd skills/web-live-debug/examples/simple-web-app
python app.py
```

Then in another terminal:

```bash
# Interactive control
python -m controllers.live_debug_controller

# Or autonomous testing
python -m testers.autonomous_web_tester --cycles 3 --url http://localhost:5000
```

## What You Can Try in the REPL

```python
ctrl.goto("http://localhost:5000")
ctrl.fill("#item-input", "First test item")
ctrl.click("button")
ctrl.wait_for_selector(".item")
ctrl.screenshot("/tmp/demo.png")
```

## Extending the Example

This is a great starting point for learning how to build your own `MyAppController(LiveDebugController)` subclass.
```