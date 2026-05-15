# Convenience wrapper for launch_chrome_debug.py

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$ScriptDir\launch_chrome_debug.py" $args