"""
Task Completion + Plan Quality + Plan Adherence eval for the LangGraph File Manager agent.

All metrics grade the SAME run: the agent runs once per golden, deepeval's
`CallbackHandler` records one trace, and the trace metrics read that trace.

    Task Completion  — did the task get done?   (judges the outcome)
    Plan Quality     — was the plan any good?    (deepeval: sees the task and a
                                                  paraphrase of the plan only)
    Plan Quality (sees workspace)                (evals/plan_judge.py: sees the task, the
                                                  exact plan, the workspace listing
                                                  and the tool list)
    Plan Adherence   — did the executor follow the plan? (deepeval: finds the plan
                                                  in the trace, then checks each step
                                                  was done, in order, nothing extra)

deepeval's metrics run on JUDGE_MODEL; your own plan judge runs on
PLAN_JUDGE_MODEL (gpt-4o), because gpt-4o-mini misreads the workspace listing.

Plan Adherence gives 1.0 automatically when its judge finds no plan in the
trace (reason: "There were no plans to evaluate..."). That 1.0 checked nothing.

Running them together shows WHERE a failure comes from:
    good plan  + task done     → working as intended
    bad plan   + task done     → the executor covered for the planner (lucky)
    good plan  + task failed   → execution problem
    bad plan   + task failed   → planning problem

Goldens live in goldens/goldens.json: 15 tasks written against the workspace in
sandbox.py, each tagged easy / medium / difficult in additional_metadata.

Run (from the project root):
    uv sync
    # put GROQ_API_KEY=sk-... in a .env file in the project root
    uv run python -m evals.eval_agent

After the run, open evals/results/reports/agent_eval_<date>_<time>.md for all
scores per task, and evals/results/traces/<task>.judge.json for exactly what
the judge read.
"""

from dotenv import load_dotenv

# Load GROQ_API_KEY from .env before anything reads it.
load_dotenv()

from deepeval.dataset import EvaluationDataset
from deepeval.evaluate.configs import AsyncConfig, DisplayConfig
from deepeval.integrations.langchain import CallbackHandler
from deepeval.metrics import PlanAdherenceMetric, PlanQualityMetric, TaskCompletionMetric

from evals.plan_judge import make_plan_judge, plan_test_case
from evals.report import write_report
from evals.slim_trace import with_slim_trace
from file_manager_agent.agent import build_agent, run_agent
from file_manager_agent.sandbox import PROJECT_ROOT, list_workspace, reset_sandbox

JUDGE_MODEL = "openai/gpt-oss-20b"        # Task Completion, Plan Quality, Plan Adherence
PLAN_JUDGE_MODEL = "openai/gpt-oss-120b"        # your own plan judge (gpt-4o-mini misreads the listing)
THRESHOLD = 0.7

GOLDENS_PATH = PROJECT_ROOT / "goldens" / "goldens.json"
TRACES_DIR = PROJECT_ROOT / "evals" / "results" / "traces"


# ---------------------------------------------------------------------------
# 1. Metrics — all three judge the slimmed trace (see slim_trace.py) and save what
#    the judge read to evals/results/traces/. The plan the agent wrote is in each trace's
#    `planner` span.
# ---------------------------------------------------------------------------
SlimTaskCompletion = with_slim_trace(TaskCompletionMetric, save_dir=TRACES_DIR)
SlimPlanQuality = with_slim_trace(PlanQualityMetric, save_dir=TRACES_DIR)
SlimPlanAdherence = with_slim_trace(PlanAdherenceMetric, save_dir=TRACES_DIR)


# ---------------------------------------------------------------------------
# 2. Goldens
# ---------------------------------------------------------------------------
dataset = EvaluationDataset()
dataset.add_goldens_from_json_file(str(GOLDENS_PATH))


# ---------------------------------------------------------------------------
# 3. Run the eval
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = build_agent()

    # One golden at a time, with a pause, to stay under OpenAI rate limits.
    async_config = AsyncConfig(max_concurrent=1, throttle_value=15)
    # Don't ask "Open run in deepeval inspect TUI? [Y/n]" — finish by itself.
    display_config = DisplayConfig(inspect_after_run=False)

    rows = []   # (golden, {name: metric}) — scores filled in by deepeval after the loop
    try:
        for golden in dataset.evals_iterator(
            async_config=async_config, display_config=display_config
        ):
            reset_sandbox()   # every golden starts from the same 20 files
            # Exactly the listing the planner is about to see (the workspace was just reset).
            listing = list_workspace()

            # Fresh metrics for every golden — a metric stores its own score and reason.
            # The first three grade the trace (deepeval); the last grades the plan with
            # the workspace and tools in view (plan_judge.py).
            trace_metrics = {
                "Task Completion": SlimTaskCompletion(
                    threshold=THRESHOLD, model=JUDGE_MODEL, include_reason=True, verbose_mode=True
                ),
                "Plan Quality": SlimPlanQuality(
                    threshold=THRESHOLD, model=JUDGE_MODEL, include_reason=True, verbose_mode=True
                ),
                # Did the executor do what the plan said? Keep it on gpt-4o-mini:
                # the slim trace goes to the judge 3 times per task.
                "Plan Adherence": SlimPlanAdherence(
                    threshold=THRESHOLD, model='openai/gpt-oss-120b', include_reason=True, verbose_mode=True
                ),
            }
            plan_judge = make_plan_judge(model=PLAN_JUDGE_MODEL, threshold=THRESHOLD)
            rows.append((golden, {**trace_metrics, "Plan Quality (sees workspace)": plan_judge}))

            state = run_agent(
                agent,
                golden.input,
                callbacks=[CallbackHandler(metrics=list(trace_metrics.values()))],
                full=True,
            )

            # Grade the plan now, while we have it and the listing.
            try:
                plan_judge.measure(plan_test_case(golden.input, state["plan"], listing))
            except Exception as e:           # show it in the report instead of crashing
                plan_judge.error = f"{type(e).__name__}: {e}"
    finally:
        # Always write the report, even if the run crashed or was stopped.
        if rows:
            write_report(rows, "agent_eval")