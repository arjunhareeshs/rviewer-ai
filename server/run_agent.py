import os
# Prevent Intel Fortran runtime from hijacking Ctrl+C on Windows (causes silent crashes during hot-reload)
os.environ["FOR_DISABLE_CONSOLE_CTRL_HANDLER"] = "1"

import sys
import logging
from dotenv import load_dotenv

load_dotenv("server/.env")
load_dotenv(".env")

from livekit.agents import cli, WorkerOptions
from app.core.interview.agent_entrypoint import entrypoint, prewarm

if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
    ))
