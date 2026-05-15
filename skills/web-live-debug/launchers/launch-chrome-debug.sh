#!/usr/bin/env bash
# Convenience wrapper for launch_chrome_debug.py

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/launch_chrome_debug.py" "$@"