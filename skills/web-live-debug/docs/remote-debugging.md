```markdown
# Remote Debugging Setup Guide

This guide explains how to launch Chrome with remote debugging enabled on different operating systems so that the `grok-live-web-debug` skill can connect to it.

## Why Remote Debugging?

Remote debugging lets external tools (like Playwright) connect to a real, visible Chrome instance. This is extremely powerful for debugging because:
- You see everything happening live in your normal browser
- You can use all your normal extensions, logins, and devtools
- Subagents can drive the browser while you watch

## Recommended Launch Method

Use the Python launcher included in this skill:

```bash
python launchers/launch_chrome_debug.py
```

It works on Windows, macOS, and Linux.

## Platform-Specific Notes

### Windows + WSL (Most Common for Desktop Users)

1. On Windows, launch Chrome using the Python script or the `.ps1` wrapper.
2. From WSL, connect using `http://127.0.0.1:9222` or the Windows host IP.
3. **Strongly recommended**: Enable WSL mirrored networking for the best experience:

   In your `.wslconfig` file (usually `C:\Users\<you>\.wslconfig`):

   ```ini
   [wsl2]
   networkingMode=mirrored
   ```

   Then run `wsl --shutdown` and restart your WSL distro.

### macOS

```bash
python launchers/launch_chrome_debug.py
```

Chrome will open with remote debugging on port 9222.

From the same machine, connect using:

```python
browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
```

### Native Linux

Same as macOS. The Python launcher will find Chrome or Chromium.

If you use Chrome from a snap or flatpak, you may need to set the `CHROME_PATH` environment variable.

## Verifying the Connection

After launching Chrome with remote debugging, open another browser and visit:

```
http://localhost:9222/json/version
```

You should see a JSON response with Chrome version information.

## Tips

- Always use a dedicated `--user-data-dir` for debugging sessions so it doesn't interfere with your normal browsing.
- You can keep multiple Chrome instances open (one normal, one for debugging).
- The debug Chrome instance will show a banner "Chrome is being controlled by automated test software" — this is normal and harmless.
```
