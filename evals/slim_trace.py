"""
Slim down a LangGraph trace before a deepeval judge reads it.

WHY THIS EXISTS
deepeval's LangChain CallbackHandler records every LangGraph step as a span,
and each span stores its full input and output. In a plan-and-execute graph
the same data is recorded many times over: the whole graph state goes into
every node, and the full message history goes into every LLM call. One run of
our agent can serialize to ~50k tokens, which can exceed a GROQ rate limit
in a single request (and costs more, and dilutes the judge's attention).

WHAT IT KEEPS (each fact once)
  - root span   : input (the user's task) + output (plan, step results, answer)
  - planner     : output (the plan)
  - executor    : output (the result of each step)
  - responder   : output (the final answer)
  - tool spans  : input (arguments) + output (what the tool returned)
  - llm spans   : output (the model's decision, e.g. which tool to call)
Everything else keeps its place in the tree but drops the repeated input and
output. The `more_steps` routing spans are removed entirely.

USAGE
    from evals.slim_trace import with_slim_trace
    SlimTaskCompletion = with_slim_trace(TaskCompletionMetric, save_dir="evals/results/traces")
    metric = SlimTaskCompletion(threshold=0.7, model="openai/gpt-oss-120b")

With save_dir set, you can open <save_dir>/<task>.judge.json to see exactly what
the judge was shown for each golden.

It works the same way for any trace-reading metric (Plan Quality, Plan
Adherence, Step Efficiency, ...).
"""

import copy
import re
from pathlib import Path

from deepeval.utils import serialize_to_json

ROUTER_SPANS = {"more_steps", "tools_condition"}   # pure routing, no information
OUTPUT_ONLY_NODES = {"planner", "executor", "responder"}


def slim_trace(node: dict, is_root: bool = True) -> dict:
    """Return a slimmed copy of a deepeval trace dict."""
    slim = {k: v for k, v in node.items() if k not in ("input", "output", "children")}
    span_type, name = node.get("type"), node.get("name")

    if is_root or span_type == "tool":
        keep = ("input", "output")
    elif span_type == "llm" or name in OUTPUT_ONLY_NODES:
        keep = ("output",)
    else:
        keep = ()
    for key in keep:
        if key in node:
            slim[key] = node[key]

    slim["children"] = [
        slim_trace(child, is_root=False)
        for child in node.get("children", [])
        if child.get("name") not in ROUTER_SPANS
    ]
    return slim


def _save(folder: Path, test_case, raw: dict, slim: dict) -> None:
    """Write the raw and slimmed trace to <folder>/<task-slug>.{raw,judge}.json."""
    folder.mkdir(parents=True, exist_ok=True)
    root_input = raw.get("input")
    task = root_input.get("task") if isinstance(root_input, dict) else None
    slug = re.sub(r"[^a-z0-9]+", "_", str(task or test_case.input).lower()).strip("_")[:60] or "trace"
    # Exactly the text deepeval puts into the judge's prompt:
    judge_text = serialize_to_json(slim, indent=2)
    (folder / f"{slug}.judge.json").write_text(judge_text)
    (folder / f"{slug}.raw.json").write_text(serialize_to_json(raw, indent=2))
    print(f"[trace saved] {folder / (slug + '.judge.json')}  (~{len(judge_text) // 4:,} tokens)")


# Ids of traces this module has already slimmed. When several metrics grade the
# same trace (e.g. Task Completion + Plan Quality), deepeval hands them the same
# test case: the first metric slims and saves it, the others use it as it is.
_ALREADY_SLIM: set[int] = set()


def _slim_test_case(test_case, save_dir=None):
    trace = getattr(test_case, "_trace_dict", None)
    if not isinstance(trace, dict) or id(trace) in _ALREADY_SLIM:
        return
    slim = slim_trace(copy.deepcopy(trace))
    if save_dir:
        _save(Path(save_dir), test_case, trace, slim)
    _ALREADY_SLIM.add(id(slim))
    test_case._trace_dict = slim


def with_slim_trace(metric_cls, save_dir=None):
    """Wrap a deepeval metric class so it judges the slimmed trace.

    save_dir: if given (e.g. "evals/results/traces"), every trace is also written there as
      <task>.judge.json – exactly what the judge LLM reads
      <task>.raw.json   – the full trace before slimming, for comparison
    """

    class SlimTraceMetric(metric_cls):
        def measure(self, test_case, *args, **kwargs):
            _slim_test_case(test_case, save_dir)
            return super().measure(test_case, *args, **kwargs)

        async def a_measure(self, test_case, *args, **kwargs):
            _slim_test_case(test_case, save_dir)
            return await super().a_measure(test_case, *args, **kwargs)

    # deepeval finds a metric's judge prompts by its class name, so the wrapper
    # must keep the original name (e.g. "TaskCompletionMetric").
    SlimTraceMetric.__name__ = metric_cls.__name__
    SlimTraceMetric.__qualname__ = metric_cls.__qualname__
    return SlimTraceMetric