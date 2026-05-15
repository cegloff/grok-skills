#!/usr/bin/env python3
"""
Autonomous Web Tester (Generic)

This provides a base class and example workflows for running
fully autonomous browser tests against any local web application.

It is designed to be subclassed for specific applications.

Example usage (see examples/ for real implementations):
    from testers.autonomous_web_tester import AutonomousWebTester

    class MyAppTester(AutonomousWebTester):
        def run_test_cycle(self):
            self.controller.goto("http://localhost:5000")
            # ... your test steps
"""

from __future__ import annotations

import argparse
import time
from typing import Optional

from controllers.live_debug_controller import LiveDebugController


class AutonomousWebTester:
    """Base class for autonomous browser testing workflows."""

    def __init__(self, controller: Optional[LiveDebugController] = None):
        self.controller = controller or LiveDebugController()

    def setup(self):
        """Override this method to perform any setup before tests."""
        self.controller.connect()

    def run_test_cycle(self):
        """Override this method with your actual test logic."""
        raise NotImplementedError("Subclasses must implement run_test_cycle()")

    def teardown(self):
        """Override this method to perform cleanup."""
        # Default: just leave the browser running
        pass

    def run(self, cycles: int = 1, continuous: bool = False):
        """Run one or more test cycles."""
        self.setup()
        try:
            cycle = 1
            while True:
                print(f"\n=== Starting test cycle {cycle} ===")
                start = time.time()
                try:
                    self.run_test_cycle()
                    duration = time.time() - start
                    print(f"Cycle {cycle} completed successfully in {duration:.1f}s")
                except Exception as e:
                    print(f"Cycle {cycle} failed: {e}")

                cycle += 1
                if not continuous and cycle > cycles:
                    break
                time.sleep(2)
        finally:
            self.teardown()


# ---------------------------------------------------------------------------
# Example workflow (very simple - for demonstration only)
# ---------------------------------------------------------------------------
class SimpleWebAppTester(AutonomousWebTester):
    """Example tester for a hypothetical simple web app."""

    def run_test_cycle(self):
        ctrl = self.controller
        ctrl.goto("http://localhost:5000")
        ctrl.wait_for_selector("#app", timeout=10000)

        # Example interaction
        if ctrl.page.is_visible("#create-item"):
            ctrl.click("#create-item")
            ctrl.fill("#item-name", f"Test Item {int(time.time())}")
            ctrl.click("#submit")
            ctrl.wait_for_selector(".success-message", timeout=5000)

        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--continuous", action="store_true")
    args = parser.parse_args()

    tester = SimpleWebAppTester()
    tester.run(cycles=args.cycles, continuous=args.continuous)
