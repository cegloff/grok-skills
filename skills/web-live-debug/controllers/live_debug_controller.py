#!/usr/bin/env python3
"""
Generic Live Debug Controller for grok-live-web-debug skill.

This provides a reusable base for controlling a live Chrome browser
via remote debugging (CDP) + Playwright.

Key improvements:
- Robust CDP URL discovery with probing and multiple fallbacks
- Built-in support for Playwright Tracing (highly recommended)
- Video recording support (best with fresh context)

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
"""

from __future__ import annotations

import code
import os
import socket
import time
from pathlib import Path
from typing import Any, Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout


class LiveDebugController:
    """High-level controller for a live Chrome debugging session via CDP.

    Connects to an existing Chrome instance launched with:
        --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0

    Features:
    - Aggressive CDP endpoint discovery (127.0.0.1, localhost, IPv6, WSL host IP)
    - Playwright Tracing support (start_tracing / stop_tracing)
    - Video recording (best effort, works best with fresh_context=True)
    - Easy to subclass for application-specific high-level methods
    """

    def __init__(
        self,
        cdp_url: str = "http://127.0.0.1:9222",
        fresh_context: bool = False,
        record_video: bool = False,
        video_dir: str = "recordings",
    ):
        self.cdp_url = cdp_url
        self.fresh_context = fresh_context
        self.record_video = record_video
        self.video_dir = Path(video_dir)
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._connected = False
        self._tracing_active = False
        self._video_recording_path: Optional[Path] = None

    # ------------------------------------------------------------------
    # Robust CDP Discovery
    # ------------------------------------------------------------------

    @classmethod
    def discover_available_chrome_instances(cls, ports: list[int] | None = None) -> list[str]:
        """Probe common CDP endpoints and return those that respond.

        This is the most reliable way to find a running Chrome with remote debugging.
        """
        if ports is None:
            ports = [9222, 9223, 9224]

        candidates: list[str] = []

        # Standard local addresses
        for port in ports:
            candidates.extend([
                f"http://127.0.0.1:{port}",
                f"http://localhost:{port}",
                f"http://[::1]:{port}",
            ])

        # WSL-friendly: try to reach Windows host
        try:
            # Common ways to reach Windows host from WSL
            candidates.append(f"http://host.docker.internal:{ports[0]}")
            # Try to get the Windows host IP via resolv.conf (common in WSL2)
            with open("/etc/resolv.conf") as f:
                for line in f:
                    if line.startswith("nameserver"):
                        ip = line.split()[1].strip()
                        if ip and not ip.startswith("127."):
                            for port in ports:
                                candidates.append(f"http://{ip}:{port}")
                            break
        except Exception:
            pass

        # Deduplicate while preserving order
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                unique_candidates.append(c)

        working: list[str] = []
        import urllib.request
        import urllib.error

        for url in unique_candidates:
            try:
                # Lightweight probe - Chrome remote debugging exposes /json/version
                req = urllib.request.Request(f"{url}/json/version", headers={"User-Agent": "grok-live-debug"})
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    if resp.status == 200:
                        working.append(url)
                        print(f"[LiveDebug] Discovered Chrome at {url}")
            except (urllib.error.URLError, socket.timeout, Exception):
                continue

        return working

    def _get_cdp_candidates(self) -> list[str]:
        """Build a smart list of CDP URLs to try, based on user input + discovery."""
        candidates: list[str] = []

        # 1. Explicitly provided URL (highest priority)
        if self.cdp_url:
            candidates.append(self.cdp_url)

        # 2. Environment variable override
        env_url = os.environ.get("CDP_URL") or os.environ.get("GROK_DEBUG_CDP_URL")
        if env_url and env_url not in candidates:
            candidates.append(env_url)

        # 3. Common variants of the provided URL
        base = self.cdp_url or "http://127.0.0.1:9222"
        if "127.0.0.1" in base:
            candidates.append(base.replace("127.0.0.1", "localhost"))
        if "localhost" in base:
            candidates.append(base.replace("localhost", "127.0.0.1"))

        # 4. IPv6
        if "::1" not in base:
            candidates.append("http://[::1]:9222")

        # 5. WSL host.docker.internal
        candidates.append("http://host.docker.internal:9222")

        # 6. Run full discovery (probes /json/version)
        discovered = self.discover_available_chrome_instances()
        for url in discovered:
            if url not in candidates:
                candidates.append(url)

        # Deduplicate
        seen = set()
        final = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                final.append(c)
        return final

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self, target_url: Optional[str] = None) -> None:
        """Connect to Chrome via CDP with robust discovery."""
        print("[LiveDebug] Starting CDP discovery...")

        self.playwright = sync_playwright().start()

        candidates = self._get_cdp_candidates()
        last_error: Optional[Exception] = None

        for url in candidates:
            try:
                print(f"[LiveDebug] Trying {url}...")
                self.browser = self.playwright.chromium.connect_over_cdp(url)
                self.cdp_url = url
                print(f"[LiveDebug] ✓ Successfully connected via {url}")
                break
            except Exception as e:
                last_error = e
                continue

        if not self.browser:
            print("\n[LiveDebug] ERROR: Could not connect to any Chrome instance.")
            print("Make sure Chrome was launched with:")
            print("  --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0")
            print("\nTip: python launchers/launch_chrome_debug.py")
            print("\nDiscovered candidates tried:")
            for c in candidates:
                print(f"  - {c}")
            if last_error:
                raise last_error
            raise ConnectionError("No Chrome remote debugging endpoint found.")

        # Context selection
        if self.fresh_context or not self.browser.contexts:
            context_options: dict[str, Any] = {}
            if self.record_video:
                self.video_dir.mkdir(parents=True, exist_ok=True)
                context_options["record_video_dir"] = str(self.video_dir)
                print(f"[LiveDebug] Video recording enabled → {self.video_dir}")
            self.context = self.browser.new_context(**context_options)
            print("[LiveDebug] Created fresh browser context")
        else:
            self.context = self.browser.contexts[0]
            print("[LiveDebug] Reusing existing browser context")

        # Page selection / creation
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
        print("[LiveDebug] Ready.\n")

    # ------------------------------------------------------------------
    # Tracing (excellent for debugging complex interactions)
    # ------------------------------------------------------------------

    def start_tracing(
        self,
        name: str = "debug-session",
        screenshots: bool = True,
        snapshots: bool = True,
        sources: bool = True,
    ) -> None:
        """Start Playwright tracing on the current context.

        Traces are extremely powerful for post-mortem debugging.
        Open them later with: `playwright show-trace path/to/trace.zip`
        """
        if not self.context:
            raise RuntimeError("Not connected.")

        trace_path = Path(f"traces/{name}-{int(time.time())}.zip")
        trace_path.parent.mkdir(parents=True, exist_ok=True)

        self.context.tracing.start(
            screenshots=screenshots,
            snapshots=snapshots,
            sources=sources,
        )
        self._tracing_active = True
        self._current_trace_path = trace_path
        print(f"[LiveDebug] Tracing started → {trace_path}")

    def stop_tracing(self, path: Optional[str] = None) -> Optional[str]:
        """Stop tracing and save the trace file."""
        if not self.context or not self._tracing_active:
            return None

        if path:
            final_path = Path(path)
        else:
            final_path = getattr(self, "_current_trace_path", Path("traces/session.zip"))

        final_path.parent.mkdir(parents=True, exist_ok=True)

        self.context.tracing.stop(path=str(final_path))
        self._tracing_active = False
        print(f"[LiveDebug] Trace saved → {final_path}")
        return str(final_path)

    # ------------------------------------------------------------------
    # Video Recording
    # ------------------------------------------------------------------

    def start_video_recording(self, output_dir: str | None = None) -> None:
        """Start video recording.

        Note: Video recording works best when using fresh_context=True at initialization.
        When connected to an existing user Chrome context, video may not be available.
        """
        if output_dir:
            self.video_dir = Path(output_dir)

        self.video_dir.mkdir(parents=True, exist_ok=True)

        # If we already have a context that supports video, great.
        # Otherwise we warn the user.
        if self.context and hasattr(self.context, "_impl_obj"):
            # Best effort - many CDP contexts don't support starting video after creation
            print("[LiveDebug] Warning: Video recording on an existing CDP context is limited.")
            print("[LiveDebug] For reliable video, use LiveDebugController(fresh_context=True, record_video=True)")

        print(f"[LiveDebug] Video recording directory ready: {self.video_dir}")

    def stop_video_recording(self) -> Optional[str]:
        """Stop video recording and return the path to the last video (if any)."""
        if not self.page:
            return None

        try:
            # Playwright records video per page when record_video_dir was set at context creation
            video_path = self.page.video.path() if self.page.video else None
            if video_path:
                print(f"[LiveDebug] Video saved → {video_path}")
                return str(video_path)
        except Exception as e:
            print(f"[LiveDebug] Could not retrieve video path: {e}")
        return None

    # ------------------------------------------------------------------
    # High-level browser actions
    # ------------------------------------------------------------------

    def goto(self, url: str, wait_until: str = "domcontentloaded", timeout: int = 30000) -> None:
        if not self.page:
            raise RuntimeError("Not connected. Call connect() first.")
        print(f"[LiveDebug] goto {url}")
        self.page.goto(url, wait_until=wait_until, timeout=timeout)

    def click(self, selector: str, timeout: int = 10000) -> None:
        print(f"[LiveDebug] click {selector}")
        self.page.click(selector, timeout=timeout)

    def fill(self, selector: str, value: str, timeout: int = 10000) -> None:
        print(f"[LiveDebug] fill {selector} → {value}")
        self.page.fill(selector, value, timeout=timeout)

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 30000) -> None:
        self.page.wait_for_selector(selector, state=state, timeout=timeout)

    def evaluate(self, expression: str) -> Any:
        return self.page.evaluate(expression)

    def screenshot(self, path: str = None, full_page: bool = False) -> str:
        if path is None:
            path = f"/tmp/grok-debug-{int(time.time())}.png"
        self.page.screenshot(path=path, full_page=full_page)
        print(f"[LiveDebug] Screenshot saved: {path}")
        return path

    def get_text(self, selector: str) -> str:
        return self.page.inner_text(selector)

    def is_visible(self, selector: str) -> bool:
        return self.page.is_visible(selector)

    def reload(self) -> None:
        self.page.reload(wait_until="domcontentloaded")

    def close(self) -> None:
        """Close connection (leaves the real Chrome browser running)."""
        # Auto-stop tracing if active
        if self._tracing_active:
            try:
                self.stop_tracing()
            except Exception:
                pass

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
# Interactive REPL
# ---------------------------------------------------------------------------

class _InteractiveController(LiveDebugController):
    """Friendlier subclass for the interactive REPL."""

    def help(self):
        print("""
Available methods on 'ctrl':

  Navigation & Interaction
    ctrl.goto(url)
    ctrl.click(selector)
    ctrl.fill(selector, value)
    ctrl.wait_for_selector(selector)
    ctrl.reload()

  Inspection
    ctrl.evaluate(js)
    ctrl.screenshot([path])
    ctrl.get_text(selector)
    ctrl.is_visible(selector)

  Powerful Debugging Tools
    ctrl.start_tracing(name="my-test")
    ctrl.stop_tracing("my-trace.zip")
    ctrl.start_video_recording()
    ctrl.stop_video_recording()

  Utilities
    ctrl.help()
    ctrl.close()

Example:
  ctrl.goto("http://localhost:5000")
  ctrl.start_tracing("lobby-flow")
  ctrl.click("#create-lobby")
  ctrl.stop_tracing()
        """)


def main():
    print("=" * 62)
    print("GROK LIVE WEB DEBUG - INTERACTIVE CONTROLLER")
    print("=" * 62)
    print("Connecting to Chrome with remote debugging (robust discovery)...")
    print("Tip: Launch Chrome first with: python launchers/launch_chrome_debug.py")
    print("-" * 62)

    ctrl = _InteractiveController()
    try:
        ctrl.connect(target_url="http://localhost:5000")
        ctrl.help()
        print("\nDropping into interactive Python REPL...")
        print("Type ctrl.help() anytime for available commands.\n")

        namespace = {"ctrl": ctrl, "help": ctrl.help}
        code.interact(local=namespace, banner="")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        ctrl.close()


if __name__ == "__main__":
    main()
