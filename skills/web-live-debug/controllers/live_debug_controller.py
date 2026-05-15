#!/usr/bin/env python3
"""
Generic Live Debug Controller for grok-live-web-debug skill.

This provides a reusable base for controlling a live Chrome browser
via remote debugging (CDP) + Playwright.

It is intentionally generic. Application-specific helpers should be added
by subclassing LiveDebugController in your own code or in examples/.

Usage as library:
    from controllers.live_debug_controller import LiveDebugController

    ctrl = LiveDebugController()
    ctrl.connect(target_url="http://localhost:5000")
    ctrl.goto("http://localhost:5000")
    ctrl.click("#some-button")
    state = ctrl.evaluate("window.myApp.getState()")

Usage as interactive REPL:
    python -m controllers.live_debug_controller

    # Then use ctrl. methods directly in the REPL
"""

from __future__ import annotations

import code
import sys
import time
from pathlib import Path
from typing import Any, Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout


class LiveDebugController:
    """High-level controller for a live Chrome debugging session.

    Connects to an existing Chrome instance launched with:
        --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0

    Provides convenient methods that wrap Playwright and are easy to extend.
    """

    def __init__(self, cdp_url: str = "http://127.0.0.1:9222"):
        self.cdp_url = cdp_url
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._connected = False

    def connect(self, target_url: Optional[str] = None) -> None:
        """Connect to the existing Chrome instance via CDP.

        Tries multiple common addresses (helpful for WSL + Windows setups).
        """
        print(f"[LiveDebug] Connecting to Chrome at {self.cdp_url}...")

        self.playwright = sync_playwright().start()

        # Try several addresses (very useful for WSL mirrored networking)
        candidates = [self.cdp_url]
        if "127.0.0.1" in self.cdp_url:
            candidates.append(self.cdp_url.replace("127.0.0.1", "localhost"))
        if "::1" not in self.cdp_url:
            candidates.append("http://[::1]:9222")

        last_error = None
        for url in candidates:
            try:
                self.browser = self.playwright.chromium.connect_over_cdp(url)
                self.cdp_url = url  # remember what worked
                print(f"[LiveDebug] Connected via {url}")
                break
            except Exception as e:
                last_error = e
                continue

        if not self.browser:
            print("Failed to connect to Chrome.")
            print("Make sure you launched Chrome with --remote-debugging-port=9222")
            print("Try: python launchers/launch_chrome_debug.py")
            raise last_error

        # Use existing context or create one
        if self.browser.contexts:
            self.context = self.browser.contexts[0]
        else:
            self.context = self.browser.new_context()

        # Try to reuse a suitable page (localhost or matching target)
        target_page = None
        for p in self.context.pages:
            if target_url and target_url in (p.url or ""):
                target_page = p
                break
            if any(h in (p.url or "") for h in ["localhost", "127.0.0.1", "0.0.0.0"]):
                target_page = p
                break

        if target_page:
            self.page = target_page
            print(f"[LiveDebug] Reusing existing page: {self.page.url}")
        else:
            self.page = self.context.new_page()
            if target_url:
                print(f"[LiveDebug] Navigating to {target_url}...")
                self.page.goto(target_url, wait_until="domcontentloaded", timeout=30000)

        self._connected = True
        print("[LiveDebug] Ready. You can now use ctrl.goto(), ctrl.click(), etc.\n")

    # ------------------------------------------------------------------
    # High-level actions (easy to call from REPL or autonomous code)
    # ------------------------------------------------------------------

    def goto(self, url: str, wait_until: str = "domcontentloaded", timeout: int = 30000) -> None:
        """Navigate the page to a URL."""
        if not self.page:
            raise RuntimeError("Not connected. Call connect() first.")
        print(f"[LiveDebug] goto {url}")
        self.page.goto(url, wait_until=wait_until, timeout=timeout)

    def click(self, selector: str, timeout: int = 10000) -> None:
        """Click an element by CSS selector."""
        print(f"[LiveDebug] click {selector}")
        self.page.click(selector, timeout=timeout)

    def fill(self, selector: str, value: str, timeout: int = 10000) -> None:
        """Fill an input or textarea."""
        print(f"[LiveDebug] fill {selector} -> {value}")
        self.page.fill(selector, value, timeout=timeout)

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 30000) -> None:
        """Wait for a selector to reach a state (visible, hidden, attached, detached)."""
        self.page.wait_for_selector(selector, state=state, timeout=timeout)

    def evaluate(self, expression: str) -> Any:
        """Evaluate JavaScript in the page and return the result."""
        return self.page.evaluate(expression)

    def screenshot(self, path: str = None, full_page: bool = False) -> str:
        """Take a screenshot. Returns the path used."""
        if path is None:
            path = f"/tmp/grok-debug-{int(time.time())}.png"
        self.page.screenshot(path=path, full_page=full_page)
        print(f"[LiveDebug] Screenshot saved: {path}")
        return path

    def get_text(self, selector: str) -> str:
        """Get innerText of an element."""
        return self.page.inner_text(selector)

    def is_visible(self, selector: str) -> bool:
        """Check if element is currently visible."""
        return self.page.is_visible(selector)

    def reload(self) -> None:
        """Reload the current page."""
        self.page.reload(wait_until="domcontentloaded")

    def close(self) -> None:
        """Close the Playwright connection (leaves the real Chrome running)."""
        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass
        self._connected = False
        print("[LiveDebug] Connection closed (browser left running).")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ---------------------------------------------------------------------------
# Interactive mode when run directly
# ---------------------------------------------------------------------------

class _InteractiveController(LiveDebugController):
    """Slightly friendlier subclass for the interactive REPL."""

    def help(self):
        print("""
Available methods on 'ctrl':
  ctrl.goto(url)
  ctrl.click(selector)
  ctrl.fill(selector, value)
  ctrl.wait_for_selector(selector)
  ctrl.evaluate(js_expression)
  ctrl.screenshot([path])
  ctrl.get_text(selector)
  ctrl.is_visible(selector)
  ctrl.reload()

  ctrl.help()        # show this message
  ctrl.close()       # disconnect (browser stays open)

Example:
  ctrl.goto("http://localhost:5000")
  ctrl.click("#create-lobby")
        """)


def main():
    print("=" * 60)
    print("GROK LIVE WEB DEBUG - INTERACTIVE CONTROLLER")
    print("=" * 60)
    print("Connecting to Chrome (port 9222)...")
    print("Make sure Chrome was launched with remote debugging enabled.")
    print("  Tip: python launchers/launch_chrome_debug.py")
    print("-" * 60)

    ctrl = _InteractiveController()
    try:
        ctrl.connect(target_url="http://localhost:5000")
        ctrl.help()
        print("\nDropping into interactive Python REPL...")
        print("Use 'ctrl' to control the browser. Type ctrl.help() for commands.\n")

        # Expose ctrl in the REPL namespace
        namespace = {"ctrl": ctrl, "help": ctrl.help}
        code.interact(local=namespace, banner="")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        ctrl.close()


if __name__ == "__main__":
    main()
