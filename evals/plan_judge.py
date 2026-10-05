"""
A plan judge that sees what the planner saw.

deepeval's PlanQualityMetric grades a plan from the task and a paraphrase of
the plan only. It never sees the workspace or the tools, so it can't tell a
complete plan from an incomplete one in this agent: "delete these 3 .tmp
files" looks incomplete unless you know there are exactly 3.

This judge is a deepeval G-Eval metric with its own grading steps. It gets:
    input          the user's task
    actual_output  the plan, word for word, as the planner wrote it
    context        the workspace listing the planner was given, and the tool list

Use gpt-4o (or stronger) as the judge model: gpt-4o-mini misreads the listing.

Usage (see eval_agent.py):
    judge = make_plan_judge(model="gpt-4o")
    judge.measure(plan_test_case(task, plan_steps, listing))
    judge.score, judge.reason
"""

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from file_manager_agent.agent import TOOL_LIST

GRADING_STEPS = [
    # What the judge has to work with
    "The input is the user's task. The actual output is the agent's plan, one numbered "
    "step per line. The context holds (1) the workspace listing the planner was given: "
    "every file and folder that existed when the plan was written, folders ending in '/'; "
    "and (2) the tools the agent can use, with their arguments and what each one does. "
    "After the plan runs, a separate responder always writes the final answer to the user "
    "from the step results, so the plan does not need a step just to report results.",

    # Ambiguous words: don't punish a reasonable reading
    "Ambiguity: if a word in the task can reasonably mean more than one thing (for "
    "example 'text file' can mean only .txt files, or any file you can read as text such "
    "as .txt, .log or .tmp), accept any reasonable reading the plan uses and do not "
    "deduct for it. Judge the plan's completeness under the reading it chose.",

    # Completeness, checked against the listing, file by file
    "Completeness: the context has an exact, code-computed list of FILES THE PLAN NEVER "
    "MENTIONS. Go through that list one file at a time and decide whether this task "
    "needs it (for every / all / each, every matching file is needed, under the reading "
    "the plan chose). Any needed file on that list is SKIPPED: a serious flaw, worse than "
    "an extra file, and you must name it in your reason. Trust that list: never say the "
    "plan skips nothing if a needed file is on it. Also name files the plan uses that "
    "the task doesn't need. Do not assume files exist that are not in the listing.",

    # Real names only
    "Names: every file or folder the plan uses must appear in the listing, or be one the "
    "task asks to create. Using a name that does not exist is a serious flaw. If the task "
    "names something that is not in the listing, the correct plan tells the user it "
    "doesn't exist instead of calling a tool on it; that is not a missing step.",

    # Tools used for what they do
    "Tools: each tool call must use a tool for what its description says, with the "
    "argument names shown. Using a tool for something it cannot do (for example deleting "
    "a folder with a tool that deletes single files) is a serious flaw.",

    # Order and dependencies
    "Dependencies: a step that needs a file's contents must come after the step that "
    "reads it and must refer to that result. Writing file contents or choosing which "
    "files match before they have been read is a serious flaw.",

    # Efficiency
    "Efficiency: penalise steps that are not needed, such as reading files whose contents "
    "don't matter to the task or writing the same file twice. A short plan that is "
    "complete is ideal.",

    # Repeat steps: the flaw the judge kept missing (#3, #5 got 1.0)
    "Deduct for a step that only repeats an earlier result, such as 'Tell the user the "
    "text returned in step 1' or 'Tell the user the files returned in step 1'. It adds "
    "nothing, because the responder reports results anyway. Do NOT deduct for a 'Tell the "
    "user' step that gives new information no earlier step produced, such as saying a "
    "requested file does not exist or that something cannot be done.",

    # What NOT to penalise (the things judges keep asking for)
    "Do not deduct for missing existence checks or for not calling list_files: the "
    "planner already has the workspace listing, so checking again adds nothing. Also do "
    "not deduct for missing error handling, for not explaining why other files were left "
    "out, or for not having a separate step for small work the executor (an LLM) does "
    "naturally, such as counting names in a list, picking a date out of text it has read, "
    "or choosing which read files mention a word.",
]


def make_plan_judge(model: str, threshold: float = 0.7) -> GEval:
    """A fresh judge for one golden (a metric stores its own score and reason)."""
    return GEval(
        name="Plan Quality (sees workspace)",
        evaluation_steps=GRADING_STEPS,
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.CONTEXT,
        ],
        model=model,
        threshold=threshold,
        async_mode=False,   # we call measure() ourselves inside the eval loop
    )


def files_not_in_plan(plan: list[str], listing: list[str]) -> list[str]:
    """Files in the listing that the plan never touches, worked out in code.

    A judge model is bad at comparing a long listing with a long plan line by
    line (it kept saying "no files are skipped" when two were). Code does this
    exactly, so we hand the judge the answer and let it decide what matters.

    A file counts as touched if the plan names it ('notes/ideas.txt'), or names
    a folder it sits in ('logs' in delete_folder, 'reports' in list_files).
    """
    text = " ".join(plan)
    named = lambda p: f"'{p}'" in text or f'"{p}"' in text
    folders = [f.rstrip("/") for f in listing if f.endswith("/")]
    touched_folders = [f for f in folders if named(f) or named(f + "/")]
    return [
        p for p in listing
        if not p.endswith("/")
        and not named(p)
        and not any(p.startswith(f + "/") for f in touched_folders)
    ]


def plan_test_case(task: str, plan: list[str], listing: list[str]) -> LLMTestCase:
    """Package one run for the judge: the task, the exact plan, and what the planner saw."""
    untouched = files_not_in_plan(plan, listing)
    return LLMTestCase(
        input=task,
        actual_output="\n".join(f"{n}. {step}" for n, step in enumerate(plan, 1)),
        context=[
            "WORKSPACE LISTING (when the plan was written):\n" + "\n".join(listing),
            "FILES THE PLAN NEVER MENTIONS (worked out by code, exact; many of these are "
            "rightly left alone, so decide which ones this task needs):\n"
            + ("\n".join(untouched) if untouched else "(none)"),
            "TOOLS:\n" + TOOL_LIST,
        ],
    )