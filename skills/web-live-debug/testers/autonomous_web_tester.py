#!/usr/bin/env python3
"""
Autonomous Web Tester (Generic Base)

Base class and example workflows for running fully autonomous
browser-driven tests against any local web application using the
grok-live-web-debug skill.

Designed to be subclassed. See examples/ for real implementations
(rts-game is a particularly complete reference).

Usage:
    python -m testers.autonomous_web_tester --cycles 5

Or subclass for your own application:
    class MyAppTester(AutonomousWebTester):
        def run_test_cycle(self):
            self.controller.goto("http://localhost:5000")
            ...
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Optional

from controllers.live_debug_controller import LiveDebugController


class AutonomousWebTester:
    """Base class for autonomous browser testing workflows.

    Subclass this and implement `run_test_cycle()`.
    The base class handles connection, looping, error reporting,
    and optional screenshot-on-failure.
    """

    def __init__(self, controller: Optional[LiveDebugController] = None, target_url: str = "http://localhost:5000"):
        self.controller = controller or LiveDebugController()
        self.target_url = target_url
        self.cycle_count = 0

    def setup(self):
        """Override to perform setup before the first test cycle."""
        self.controller.connect(target_url=self.target_url)

    def run_test_cycle(self):
        """**Must be overridden** by subclasses with actual test logic."""
        raise NotImplementedError("Subclasses must implement run_test_cycle()")

    def teardown(self):
        """Override to perform cleanup. Default leaves browser running."""
        # Intentionally does nothing so the browser stays open for inspection
        pass

    def on_cycle_failed(self, cycle: int, error: Exception):
        """Called when a cycle fails. Override to add custom logging/screenshots."""
        print(f"[Tester] Cycle {cycle} failed: {error}")
        try:
            path = f"/tmp/grok-test-failure-cycle{cycle}.png"
            self.controller.screenshot(path)
            print(f"[Tester] Failure screenshot saved to {path}")
        except Exception:
            pass

    def run(self, cycles: int = 1, continuous: bool = False):
        """Run one or more test cycles."""
        self.setup()
        try:
            cycle = 1
            while True:
                self.cycle_count = cycle
                print(f"\n{'='*60}")
                print(f"Starting test cycle {cycle}")
                print(f"{'='*60}")

                start = time.time()
                try:
                    self.run_test_cycle()
                    duration = time.time() - start
                    print(f"Cycle {cycle} completed successfully in {duration:.1f}s")
                except Exception as e:
                    self.on_cycle_failed(cycle, e)

                cycle += 1
                if not continuous and cycle > cycles:
                    break
                time.sleep(1.5)
        finally:
            self.teardown()


# ---------------------------------------------------------------------------
# Concrete example workflows
# ---------------------------------------------------------------------------

class SimpleWebAppTester(AutonomousWebTester):
    """Example tester for the simple-web-app in examples/simple-web-app."""

    def run_test_cycle(self):
        ctrl = self.controller
        ctrl.goto(self.target_url)
        ctrl.wait_for_selector("#item-input", timeout=10000)

        # Add a new item
        item_name = f"Test Item {int(time.time())}"
        ctrl.fill("#item-input", item_name)

        # Trigger the add (the button uses HTMX)
        if ctrl.is_visible("button"):
            ctrl.click("button")

        time.sleep(0.8)

        # Verify it appeared
        try:
            ctrl.wait_for_selector("li.item", timeout=5000)
            print(f"  Successfully added and saw item: {item_name}")
        except Exception:
            print("  Item list did not update as expected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run autonomous web tests")
    parser.add_argument("--cycles", type=int, default=3, help="Number of test cycles")
    parser.add_argument("--continuous", action="store_true", help="Run forever")
    parser.add_argument("--url", default="http://localhost:5000", help="Target URL")
    args = parser.parse_args()

    tester = SimpleWebAppTester(target_url=args.url)
    tester.run(cycles=args.cycles, continuous=args.continuous)
