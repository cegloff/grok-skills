# Convenience wrapper for the Python Chrome launcher
# Run this from Windows (especially useful with WSL)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$ScriptDir\launch_chrome_debug.py" $args
