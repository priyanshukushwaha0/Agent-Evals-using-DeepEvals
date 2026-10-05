"""
Task Completion eval for the LangGraph File Manager agent.

How the pieces connect:
  - deepeval's LangChain `CallbackHandler` is passed into the graph's config.
    It turns every LangGraph step (planner, executor steps, LLM calls, tool
    calls, responder) into a span, so deepeval gets the agent's full trace
    with no @observe decorators needed.
  - The metric is given to the CallbackHandler, which attaches it to that trace.
  - `evals_iterator` loops over the goldens and collects the results into one
    test run. deepeval's "Aggregate Metrics" table at the end shows the
    overall average score and pass rate across all goldens.

Goldens live in goldens/goldens.json: 15 tasks written against the workspace in
sandbox.py, each tagged with a difficulty in additional_metadata:
  easy       one action, the exact file is named in the request
  medium     the agent must look first (discover names/contents) or use a tool
             creatively (e.g. rename = move_file to a new name)
  difficult  many steps, reasoning over file contents, or requests that are
             partly impossible with the available tools — where the correct
             outcome includes honestly saying what could not be done

Run (from the project root):
    uv sync
    # put GROQ_API_KEY=sk-... in a .env file in the project root
    uv run deepeval set-eval-mode llm
    uv run python -m evals.eval_task_completion

After the run, open evals/results/reports/task_completion_<date>_<time>.md for a
task-by-task report (and the .csv for a spreadsheet).
"""

import os
from dotenv import load_dotenv

# Load GROQ_API_KEY (and JUDGE_MODEL, if set) from .env before anything
# reads them — the judge model needs the key just like the agent does.
load_dotenv()

from deepeval.dataset import EvaluationDataset
from deepeval.evaluate.configs import AsyncConfig
from deepeval.integrations.langchain import CallbackHandler
from deepeval.metrics import TaskCompletionMetric

from evals.report import write_report
from evals.slim_trace import with_slim_trace
from file_manager_agent.agent import build_agent, run_agent
from file_manager_agent.sandbox import PROJECT_ROOT, reset_sandbox

JUDGE_MODEL = "openai/gpt-oss-20b"

GOLDENS_PATH = PROJECT_ROOT / "goldens" / "goldens.json"
TRACES_DIR = PROJECT_ROOT / "evals" / "results" / "traces"

# Task Completion that judges a slimmed trace (see slim_trace.py): the raw
# LangGraph trace repeats the same state/messages at every level and can reach
# ~50k tokens — too big for one request on a 30k tokens/min rate limit.
# save_dir also writes what the judge sees to evals/results/traces/<task>.judge.json
SlimTaskCompletion = with_slim_trace(TaskCompletionMetric, save_dir=TRACES_DIR)

# ---------------------------------------------------------------------------
# 1. Goldens — loaded from goldens/goldens.json. Task Completion is referenceless: the
#    judge infers the task from the trace and checks whether the outcome
#    achieves it, so each golden only needs an `input`.
# ---------------------------------------------------------------------------
dataset = EvaluationDataset()
dataset.add_goldens_from_json_file(str(GOLDENS_PATH))


# ---------------------------------------------------------------------------
# 2. The metric
#    A metric object stores its extracted task/outcome/score on itself, so
#    each golden gets its OWN instance. Sharing one object across goldens
#    makes their results overwrite each other.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 3. Run the eval
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = build_agent()

    # Grade one golden at a time with a pause in between. By default deepeval
    # grades them all at once, and several full traces sent together can
    # exceed a low OpenAI rate limit (e.g. 30k tokens/min for gpt-4o).
    async_config = AsyncConfig(max_concurrent=1, throttle_value=15)

    rows = []   # (golden, metric) — scores are filled in by deepeval, read after the loop
    for golden in dataset.evals_iterator(async_config=async_config):
        reset_sandbox()   # every golden starts from the same files
        metric = SlimTaskCompletion( #ignore for now
            threshold=0.7,
            model=JUDGE_MODEL,
            include_reason=True,
            verbose_mode=True, 
        )
        rows.append((golden, metric)) # ignore for now
        run_agent(agent, golden.input, callbacks=[CallbackHandler(metrics=[metric])])

    # Task-by-task results in evals/results/reports/ (the terminal trims long output)
    write_report(rows, "task_completion") # ignore for now