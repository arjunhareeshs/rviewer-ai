import inspect
from livekit.agents.cli.cli import run_app

print("run_app file:", inspect.getsourcefile(run_app))
lines, start_line = inspect.getsourcelines(run_app)
print("run_app start_line:", start_line)
print("run_app length:", len(lines))
