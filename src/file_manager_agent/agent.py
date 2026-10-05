"""
File Manager agent built with LangGraph + LangChain — PLAN-AND-EXECUTE style.

Graph:

    START ──► planner ──► executor ──(steps left?)──► executor ...
                              │
                              └──(all steps done)──► responder ──► END

- planner   : one LLM call that writes an explicit, numbered plan. It is shown
              a listing of the workspace first, so it plans with real file
              names instead of guessing them (structured output -> list of
              steps). It uses a stronger model than the other two nodes,
              because planning is the hardest part. This makes the agent's
              planning visible in the trace, which the Plan Quality and
              Plan Adherence metrics need.
- executor  : carries out ONE plan step per visit, using a small tool-calling
              sub-agent (LangChain `create_agent`). It sees only the current
              step and the results of the steps before it, not the rest of the
              plan, so it can't run ahead and do later steps early.
- responder : writes the final answer from the step results.

Everything happens inside the `data/workspace/` folder, which is defined and
reset in sandbox.py. The tools below can only touch files inside it.

Setup — create a file named .env in the project root containing:
    GROQ_API_KEY=sk-...
"""

import json
import operator
import shutil
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from file_manager_agent.sandbox import SANDBOX, list_workspace, safe_path

# Read GROQ_API_KEY (and any other settings) from the .env file in the project root.
load_dotenv()

# Models: a stronger model plans; a small, cheap one executes and answers.
PLANNER_MODEL = "openai/gpt-oss-120b"
WORKER_MODEL = "openai/gpt-oss-20b"


# ===========================================================================
# 1. Tools — the @tool docstring is what the models read to pick a tool,
#    so each one says what it does AND what it doesn't do.
# ===========================================================================
@tool
def list_files(folder: str = ".") -> str:
    """List what is directly inside one workspace folder (use '.' for the root).
    Names ending in '/' are folders. Does not look inside subfolders: list each
    subfolder separately."""
    p = safe_path(folder)
    if not p.is_dir():
        return f"Error: folder '{folder}' not found"
    return json.dumps([f"{c.name}/" if c.is_dir() else c.name for c in sorted(p.iterdir())])


@tool
def read_file(path: str) -> str:
    """Return the full text content of one file. Only needed when the task depends
    on what is inside the file; file names alone are visible with list_files."""
    p = safe_path(path)
    return p.read_text() if p.is_file() else f"Error: file '{path}' not found"


@tool
def create_file(path: str, content: str) -> str:
    """Create a file with the given text, or overwrite it if it already exists.
    Missing parent folders are created. Write the complete final text in one call."""
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Created {path}"


@tool
def create_folder(path: str) -> str:
    """Create a folder, including any missing parent folders. Does nothing if it
    already exists."""
    safe_path(path).mkdir(parents=True, exist_ok=True)
    return f"Created folder {path}/"


@tool
def move_file(source: str, destination: str) -> str:
    """Move one file. If destination is an existing folder, the file keeps its name
    inside it; otherwise destination is the new path, so this also renames files.
    The source is removed."""
    src, dst = safe_path(source), safe_path(destination)
    if not src.exists():
        return f"Error: '{source}' not found"
    if dst.is_dir():
        dst = dst / src.name
    shutil.move(str(src), str(dst))
    return f"Moved {source} -> {dst.relative_to(SANDBOX)}"


@tool
def delete_file(path: str) -> str:
    """Permanently delete one file. Cannot delete folders: use delete_folder."""
    p = safe_path(path)
    if not p.is_file():
        return f"Error: file '{path}' not found"
    p.unlink()
    return f"Deleted {path}"


@tool
def delete_folder(path: str) -> str:
    """Permanently delete a folder and everything inside it (files and subfolders)
    in one call. There is no need to delete its contents first."""
    p = safe_path(path)
    if p == SANDBOX:
        return "Error: the workspace root cannot be deleted"
    if not p.is_dir():
        return f"Error: folder '{path}' not found"
    shutil.rmtree(p)
    return f"Deleted folder {path}/ and everything in it"


TOOLS = [list_files, read_file, create_file, create_folder, move_file, delete_file,
         delete_folder]
# Show each tool with its argument names, e.g. "- delete_file(path): Permanently ...",
# so the planner uses the real names (path, content) instead of guessing (source, text).
TOOL_LIST = "\n".join(
    f"- {t.name}({', '.join(t.args)}): {' '.join(t.description.split())}" for t in TOOLS
)


# ===========================================================================
# 2. Prompts
# ===========================================================================
PLANNER_PROMPT = f"""\
You are the PLANNER of a file-manager agent that works in a sandboxed workspace.
Break the user's task into the smallest set of steps that completes it (at most 10).
Paths are relative to the workspace root.

You are given a listing of every file and folder currently in the workspace
(folders end with '/'). Use only names from that listing, or names the task asks
you to create. Never invent a name.

What a step can be:
- A tool call, naming the tool and its arguments exactly as listed below, e.g.
  "Call move_file with source='a.txt' and destination='backup'".
- A step that needs no tool: working something out from earlier results
  (e.g. "Count the names from step 1 that end in .csv"), or telling the user
  something (e.g. "Tell the user: ...").

Rules:
1. Don't guess what a later step depends on. If a step needs something an earlier
   step will find out (a file's contents, which files match), refer to that step
   instead of writing the answer in advance. Never make up file contents.
2. When the task says every / all / each, check the whole listing: every matching
   item, in every folder, including the root and nested folders.
3. Read a file only when the task depends on what is inside it. Counting, moving,
   renaming and deleting files only need their names, which the listing shows.
4. Use each tool only for what its description says. If a name in the task is not
   in the listing, or no tool can do part of the task, don't call a tool for that
   part: add a step that tells the user what can't be done and why.

Examples (a different workspace from the user's; the plan is what matters):

Workspace: data/, data/sales.csv, data/costs.csv, data/notes.md, old/, old/q1.csv
Task: How many CSV files are in the data folder?
Plan:
  1. Call list_files with folder='data'
  2. Count the names from step 1 that end in .csv and report the number

Workspace: mail/, mail/mon.txt, mail/tue.txt, archive/, archive/2023/, archive/2023/dec.txt, readme.txt
Task: Write the path of every .txt file that mentions "refund" into refunds.txt, one per line.
Plan:
  1. Call read_file with path='mail/mon.txt'
  2. Call read_file with path='mail/tue.txt'
  3. Call read_file with path='archive/2023/dec.txt'
  4. Call read_file with path='readme.txt'
  5. Call create_file with path='refunds.txt' and content = the paths from steps 1-4
     whose text mentions "refund", one per line

Workspace: build/, build/app.bin, build/tmp/, build/tmp/cache.dat, src/, src/main.py
Task: Remove the build folder and send the cleanup log to Sam.
Plan:
  1. Call delete_folder with path='build'
  2. Tell the user: the build folder was deleted, but there is no tool for sending
     messages and no cleanup log in the workspace, so nothing was sent to Sam

Available tools:
{TOOL_LIST}
"""

EXECUTOR_PROMPT = (
    "You are the EXECUTOR of a file-manager agent working in a sandboxed workspace. "
    "You are given the results of the steps already done and ONE current step. "
    "Do exactly that step and nothing more:\n"
    "- If the step says 'Call <tool>', make that one tool call, with those arguments.\n"
    "- If it doesn't name a tool, don't call any tool. Work it out from the step text "
    "and COMPLETED STEPS (e.g. the exact lines or paths they found).\n"
    "- Don't do any other step's work, and don't mention what comes next.\n"
    "Then reply with a short factual result of this step only, including any "
    "information found and any error a tool returned. Paths are relative to the "
    "workspace root."
)

RESPONDER_PROMPT = (
    "You are the RESPONDER of a file-manager agent. Given the user's task and the results "
    "of each executed step, reply to the user in one or two sentences with what was done "
    "or the answer they asked for. Only report what the step results show. If any part "
    "of the task could not be done, say so plainly and why."
)


# ===========================================================================
# 3. Graph state
# ===========================================================================
class Plan(BaseModel):
    """The planner's structured output."""
    steps: list[str] = Field(description="Ordered, concrete steps to complete the task")


class PlanExecuteState(TypedDict):
    task: str                                                   # the user's request
    plan: list[str]                                             # written by the planner
    past_steps: Annotated[list[tuple[str, str]], operator.add]  # (step, result), appended
    response: str                                               # final answer


# ===========================================================================
# 4. The graph
# ===========================================================================
def build_agent(llm=None, planner_llm=None):
    """Build and compile the plan-and-execute agent.

    llm         : model for the executor and responder (default: WORKER_MODEL)
    planner_llm : model for the planner (default: PLANNER_MODEL)
    """
    llm = llm or ChatOpenAI(model=WORKER_MODEL, temperature=0)
    # GPT-5.x models are reasoning models: they take reasoning_effort, not temperature.
    planner_llm = planner_llm or ChatOpenAI(model=PLANNER_MODEL, reasoning_effort="low")
    structured_planner = planner_llm.with_structured_output(Plan)
    step_executor = create_agent(llm, tools=TOOLS, system_prompt=EXECUTOR_PROMPT,
                                 name="step_executor")

    # --- planner: writes the plan once --------------------------------------
    def planner(state: PlanExecuteState):
        # Look at the workspace NOW, so the plan uses real names instead of guesses.
        listing = "\n".join(list_workspace())
        plan = structured_planner.invoke([
            SystemMessage(PLANNER_PROMPT),
            HumanMessage(f"TASK: {state['task']}\n\nCURRENT WORKSPACE:\n{listing}"),
        ])
        return {"plan": plan.steps}

    # --- executor: one plan step per visit ----------------------------------
    def executor(state: PlanExecuteState):
        plan, done = state["plan"], state["past_steps"]
        i = len(done)
        step = plan[i]
        # Show ONLY what this step needs: earlier results + the current step.
        # Not the task and not the rest of the plan: when the executor could see
        # later steps, it kept doing them early (e.g. writing people.txt during a
        # read step, or answering the question before the step that asks for it).
        done_text = "\n".join(f"{n}. {s} -> {r}" for n, (s, r) in enumerate(done, 1)) or "(none yet)"
        prompt = (
            f"COMPLETED STEPS:\n{done_text}\n\n"
            f"CURRENT STEP ({i + 1}): {step}"
        )
        result = step_executor.invoke({"messages": [HumanMessage(prompt)]})
        return {"past_steps": [(step, result["messages"][-1].content)]}

    def more_steps(state: PlanExecuteState) -> str:
        return "executor" if len(state["past_steps"]) < len(state["plan"]) else "responder"

    # --- responder: final answer --------------------------------------------
    def responder(state: PlanExecuteState):
        results = "\n".join(f"- {s}: {r}" for s, r in state["past_steps"])
        msg = llm.invoke([
            SystemMessage(RESPONDER_PROMPT),
            HumanMessage(f"TASK: {state['task']}\n\nSTEP RESULTS:\n{results}"),
        ])
        return {"response": msg.content}

    graph = StateGraph(PlanExecuteState)
    graph.add_node("planner", planner)
    graph.add_node("executor", executor)
    graph.add_node("responder", responder)
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges("executor", more_steps, ["executor", "responder"])
    graph.add_edge("responder", END)
    return graph.compile(name="file_manager_agent")


def run_agent(agent, task: str, callbacks=None, full: bool = False):
    """Run one task. Returns the final answer, or with full=True the whole final
    state (task, plan, past_steps, response)."""
    result = agent.invoke(
        {"task": task, "past_steps": []},
        config={"callbacks": callbacks or [], "recursion_limit": 40},
    )
    return result if full else result["response"]