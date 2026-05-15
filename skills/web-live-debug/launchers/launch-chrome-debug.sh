#!/usr/bin/env bash
# Convenience wrapper - launches Chrome with remote debugging
# Works on Linux and macOS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/launch_chrome_debug.py" "$@"
