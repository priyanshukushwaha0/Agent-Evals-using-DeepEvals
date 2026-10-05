"""
Run the File Manager agent on one task and print its plan and answer.

    uv run main.py "Rename todo.txt to tasks.txt"

The sandbox is reset first, so every run starts from the same 20 files in
data/workspace/. Open that folder to see what the agent changed.
"""

import sys

from file_manager_agent.agent import build_agent, run_agent
from file_manager_agent.sandbox import SANDBOX, reset_sandbox


def main():
    if len(sys.argv) < 2:
        print('Usage: uv run main.py "<task>"')
        sys.exit(1)
    task = " ".join(sys.argv[1:])   # quotes are optional

    reset_sandbox()   # start from the known 20 files, like every golden does
    state = run_agent(build_agent(), task, full=True)

    print(f"TASK: {task}\n\nPLAN:")
    for n, step in enumerate(state["plan"], 1):
        print(f"  {n}. {step}")
    print(f"\nRESPONSE: {state['response']}")
    print(f"\nWorkspace: {SANDBOX}")


if __name__ == "__main__":
    main()
