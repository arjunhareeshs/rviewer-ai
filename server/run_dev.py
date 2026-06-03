#!/usr/bin/env python
"""
Development server startup script.
Fixes the 'forrtl: error (200)' crash on Windows caused by the interaction
between watchfiles (used by uvicorn --reload) and the Intel Fortran runtime
(libifcoremd.dll) bundled inside TensorFlow.

Root cause: when watchfiles detects a file change it sends a Windows CTRL+C
event to the worker subprocess. TF's bundled Intel Fortran runtime intercepts
that signal and prints:
  "forrtl: error (200): program aborting due to control-C event"

Fix: FOR_DISABLE_CONSOLE_CTRL_HANDLER=1 tells the Intel Fortran runtime NOT
to register its own Ctrl+C handler, so the signal passes through normally
without the crash message.
"""
import os
import sys
import subprocess

# Build the environment for the child process, inheriting everything
env = os.environ.copy()

# Actual fix: prevent Intel Fortran runtime from hijacking Ctrl+C on Windows
env["FOR_DISABLE_CONSOLE_CTRL_HANDLER"] = "1"

# Suppress TF C++ level noise
env["TF_CPP_MIN_LOG_LEVEL"] = "3"
env["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Use polling watcher to avoid filesystem-event based signal kills
env["WATCHFILES_FORCE_POLLING"] = "1"

# Suppress Python-level TF deprecation warnings
env["PYTHONWARNINGS"] = "ignore::DeprecationWarning"

cmd = [
    sys.executable, "-m", "uvicorn",
    "app.main:app",
    "--reload",
    "--reload-dir", "app",
    "--reload-delay", "1",
    "--port", "8000",
    "--host", "127.0.0.1",
]

print(">> Starting RViewer AI backend with hot-reload...")
print("   forrtl fix: FOR_DISABLE_CONSOLE_CTRL_HANDLER=1")
print("   Server: http://127.0.0.1:8000\n")

subprocess.run(cmd, env=env)
