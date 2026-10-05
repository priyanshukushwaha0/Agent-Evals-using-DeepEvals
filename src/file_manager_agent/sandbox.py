"""
The sandbox: the `data/workspace/` folder the File Manager agent works in.

Everything about the workspace lives here:
  - SANDBOX          where the folder is (data/workspace/)
  - REFERENCE        data/workspace_original/ — an untouched copy of the starting
                     files, for you to look at. The agent can never reach it.
  - WORKSPACE_FILES  the 20 starting files and their contents
  - reset_sandbox()  wipe workspace/ and recreate the starting files
                     (and refresh workspace_original/)
  - safe_path()      turn a relative path into a real path, refusing anything
                     outside workspace/ — every tool goes through this

The goldens in goldens/goldens.json are written against exactly this layout,
so if you change WORKSPACE_FILES, check the goldens still make sense.

Keep data/workspace/ open in Finder / VS Code to watch the agent work, but don't
store anything of your own there: reset_sandbox() deletes its contents.
Open data/workspace_original/ next to it to compare with the starting state.

Run this module on its own (from the project root) to reset the workspace and
print its layout:
    uv run python -m file_manager_agent.sandbox
"""

import os
import shutil
import stat
from pathlib import Path

# The project root: this file is <root>/src/file_manager_agent/sandbox.py.
# .resolve() gives the real, absolute path (important on macOS, where some
# folders are symlinks). Every other path in the project is built from this,
# so nothing depends on which folder you run a command from.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

# A fixed `workspace/` folder inside data/.
SANDBOX = DATA_DIR / "workspace"

# A read-only copy of the starting state, for reference only. It sits NEXT TO
# workspace/, not inside it, so safe_path() blocks the agent from touching it.
REFERENCE = DATA_DIR / "workspace_original"

# The starting workspace: 20 files across nested folders (paths relative to workspace/).
WORKSPACE_FILES = {
    # root
    "budget.xlsx": "Budget 2024: rent 1200, salaries 8000, tools 450",
    "todo.txt": "1. Renew passport\n2. Book dentist appointment\n3. Pay electricity bill\n",
    "old_draft.tmp": "temporary draft",
    "cache.tmp": "cache data",
    # reports/
    "reports/q1_2024.pdf": "Q1 2024 quarterly report",
    "reports/q2_2024.pdf": "Q2 2024 quarterly report",
    "reports/q3_2024.pdf": "Q3 2024 quarterly report",
    "reports/q4_2023.pdf": "Q4 2023 quarterly report",
    "reports/summary.txt": "Revenue grew 12% in Q3 2024. Prepared by Priya.\n",
    "reports/draft_q3_2024.tmp": "unfinished Q3 draft",
    # invoices/
    "invoices/invoice_2023_11.pdf": "Invoice November 2023: 1,200 USD",
    "invoices/invoice_2023_12.pdf": "Invoice December 2023: 950 USD",
    "invoices/invoice_2024_01.pdf": "Invoice January 2024: 1,100 USD",
    "invoices/invoice_2024_02.pdf": "Invoice February 2024: 1,300 USD",
    # notes/
    "notes/meeting_jan.txt": "Discussed hiring plans for Q2. No launch date yet.\n",
    "notes/meeting_feb.txt": "Launch date fixed: 15 March. Owner: Priya.\n",
    "notes/ideas.txt": "Dark mode\nOffline sync\nExport to CSV\n",
    # logs/
    "logs/app.log": "INFO server started\nINFO request ok\nWARN slow response\n",
    "logs/error.log": (
        "INFO boot complete\n"
        "ERROR disk full\n"
        "INFO retrying\n"
        "ERROR timeout on /api/sync\n"
        "WARN low memory\n"
        "ERROR payment service unavailable\n"
    ),
    "logs/old/debug.log": "DEBUG cache warmed\nDEBUG config loaded\n",
}
EMPTY_FOLDERS = ["archive"]


def _make_writable_and_retry(func, path, _exc_info):
    """rmtree helper: read-only files (in workspace_original/) need unlocking first."""
    os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
    func(path)


def _build(folder: Path, read_only: bool = False) -> None:
    """Delete `folder` and recreate the starting files inside it."""
    if folder.exists():
        shutil.rmtree(folder, onerror=_make_writable_and_retry)
    folder.mkdir(parents=True)
    for rel_path, content in WORKSPACE_FILES.items():
        path = folder / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        if read_only:
            path.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)   # read-only for humans too
    for sub in EMPTY_FOLDERS:
        (folder / sub).mkdir(parents=True, exist_ok=True)


def reset_sandbox() -> None:
    """Wipe workspace/ and put back the same starting files.

    Also refreshes workspace_original/, so the reference copy always matches
    WORKSPACE_FILES (even if you edited that list, or a file there by accident).
    """
    _build(SANDBOX)
    _build(REFERENCE, read_only=True)


def safe_path(path: str) -> Path:
    """Resolve a path inside the sandbox and refuse anything outside it."""
    p = (SANDBOX / path).resolve()
    if not p.is_relative_to(SANDBOX):
        raise ValueError(f"Path '{path}' is outside the workspace")
    return p


def list_workspace() -> list[str]:
    """All paths currently in the workspace (folders end with '/')."""
    return sorted(
        str(p.relative_to(SANDBOX)) + ("/" if p.is_dir() else "")
        for p in SANDBOX.rglob("*")
    )


if __name__ == "__main__":
    reset_sandbox()
    print(f"Workspace reset: {SANDBOX}")
    print(f"Reference copy:  {REFERENCE}  (read-only, never touched by the agent)\n")
    for entry in list_workspace():
        print(" ", entry)
    print(f"\n{len(WORKSPACE_FILES)} files")