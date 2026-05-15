#!/usr/bin/env python3
"""
Cross-platform Chrome launcher with remote debugging enabled.

This is the recommended launcher for the grok-live-web-debug skill.
It works on Windows, macOS, and Linux.

Usage:
    python launch_chrome_debug.py

It will launch Chrome with the correct flags for remote debugging
and open it to http://localhost:5000 by default (customizable).
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def find_chrome() -> str:
    system = platform.system()

    candidates = []

    if system == "Windows":
        candidates = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
    elif system == "Darwin":  # macOS
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
        ]
    else:  # Linux
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]

    for path in candidates:
        if Path(path).exists():
            return path

    print("ERROR: Could not find Google Chrome or Chromium.")
    print("Please install Chrome or set CHROME_PATH environment variable.")
    sys.exit(1)


def main():
    chrome_path = os.environ.get("CHROME_PATH") or find_chrome()

    debug_dir = Path.home() / ".grok-chrome-debug-profile"
    debug_dir.mkdir(parents=True, exist_ok=True)

    target_url = os.environ.get("DEBUG_TARGET_URL", "http://localhost:5000")

    cmd = [
        chrome_path,
        "--remote-debugging-port=9222",
        "--remote-debugging-address=0.0.0.0",
        f"--user-data-dir={debug_dir}",
        "--start-maximized",
        target_url,
    ]

    print("Launching Chrome with remote debugging...")
    print(f"  Profile: {debug_dir}")
    print(f"  Target : {target_url}")
    print(f"  Port   : 9222")

    subprocess.run(cmd)


if __name__ == "__main__":
    main()
