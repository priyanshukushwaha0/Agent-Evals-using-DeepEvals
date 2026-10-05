"""Evaluation code for the File Manager agent. Run each script as a module from
the project root, e.g. `python3 -m evals.eval_agent` (or `uv run python -m ...`)."""

import sys
from pathlib import Path

# The agent lives in src/file_manager_agent/. `uv sync` installs it into .venv,
# but a plain `python3` doesn't know about that, so put src/ on the import path
# here. Python runs this file before any evals/ module, so the
# `from file_manager_agent... import` lines work with either interpreter.
SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
