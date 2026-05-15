#!/usr/bin/env python3
"""
Generic Live Debug Controller

This provides a reusable base for controlling a live Chrome browser
via remote debugging (CDP) + Playwright.

It is intentionally generic. Application-specific helpers (e.g. create_lobby,
add_ai, etc.) should live in an examples/ folder or in your own project.

Example usage:
    from controllers.live_debug_controller import LiveDebugController

    ctrl = LiveDebugController()
    ctrl.goto("http://localhost:5000")
    ctrl.click("#create-lobby")
    ctrl.fill("#name", "My Game")
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout


class LiveDebugController:
    """High-level controller for a live Chrome debugging session."""

    def __init__(self, cdp_url: str = "http://127.0.0.1:9222"):
        self.cdp_url = cdp_url
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def connect(self, target_url: Optional[str] = None) -> None:
        """Connect to the existing Chrome instance and find or open the target."""
        print(f"[LiveDebug] Connecting to Chrome at {self.cdp_url}...")
        self.playwright = sync_playwright().start()

        try:
            self.browser = self.playwright.chromium.connect_over_cdp(self.cdp_url)
        except Exception as e:
            print(f"Failed to connect to Chrome at {self.cdp_url}")
            print("Make sure Chrome was launched with --remote-debugging-port=9222")
            raise e

        if not self.browser.contexts:
            self.context = self.browser.new_context()
        else:
            self.context = self.browser.contexts[0]

        # Try to find an existing page with the target URL
        target_page = None
        for p in self.context.pages:
            if target_url and target_url in p.url:
                target_page = p
                break
            if "localhost" in p.url or "127.0.0.1" in p.url:
                target_page = p
                break

        if target_page:
            self.page = target_page
            print(f"Reusing existing page: {self.page.url}")
        else:
            self.page = self.context.new_page()
            if target_url:
                print(f"Navigating to {target_url}...")
                self.page.goto(target_url, wait_until="domcontentloaded", timeout=30000)

        print("[LiveDebug] Connected to browser.\n")

    def goto(self, url: str, wait_until: str = "domcontentloaded", timeout: int = 30000) -> None:
        """Navigate to a URL."""
        print(f"[LiveDebug] goto {url}")
        self.page.goto(url, wait_until=wait_until, timeout=timeout)

    def click(self, selector: str, timeout: int = 10000) -> None:
        """Click an element."""
        print(f"[LiveDebug] click {selector}")
        self.page.click(selector, timeout=timeout)

    def fill(self, selector: str, value: str, timeout: int = 10000) -> None:
        """Fill an input field."""
        print(f"[LiveDebug] fill {selector} -> {value}")
        self.page.fill(selector, value, timeout=timeout)

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 30000) -> None:
        """Wait for a selector to reach a certain state."""
        self.page.wait_for_selector(selector, state=state, timeout=timeout)

    def evaluate(self, expression: str) -> Any:
        """Evaluate JavaScript in the page context."""
        return self.page.evaluate(expression)

    def screenshot(self, path: str, full_page: bool = False) -> None:
        """Take a screenshot."""
        self.page.screenshot(path=path, full_page=full_page)
        print(f"[LiveDebug] Screenshot saved: {path}")

    def close(self) -> None:
        """Close the browser connection (the browser itself stays open)."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("[LiveDebug] Connection closed (browser left running).")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Example of how to extend for a specific application
class ExampleAppController(LiveDebugController):
    """Example of an app-specific controller (see examples/ for real ones)."""

    def create_something(self, name: str):
        self.goto("http://localhost:5000")
        self.click("#create-button")
        self.fill("#name-input", name)
        self.click("#submit-button")
        self.wait_for_selector("#success-message")
        print(f"Created item: {name}")


if __name__ == "__main__":
    print("This is a library. Import it or run one of the example controllers.")
    print("See examples/ for real-world usage (e.g. rts-game).")
