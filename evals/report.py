"""
Write a task-by-task report of an eval run to files, so nothing depends on the
terminal (which trims long output and squeezes deepeval's tables).

After a run you get, in evals/results/reports/:
  <name>_<date>_<time>.md   readable report: a summary per metric, one line per
                            task with every metric's score, then each task's
                            full judge reasoning (tasks with a failure first)
  <name>_<date>_<time>.csv  the same per-task data, for Excel / Google Sheets

Usage (in an eval script):
    rows = []      # (golden, {"Task Completion": metric, "Plan Quality": metric})
    for golden in dataset.evals_iterator(...):
        metrics = {"Task Completion": make_tc(), "Plan Quality": make_pq()}
        rows.append((golden, metrics))
        run_agent(..., callbacks=[CallbackHandler(metrics=list(metrics.values()))])
    write_report(rows, "agent_eval")     # after the loop: scores are filled in

A single metric per golden also works: rows.append((golden, metric)).
"""

import csv
from datetime import datetime
from pathlib import Path

from file_manager_agent.sandbox import PROJECT_ROOT

REPORT_DIR = PROJECT_ROOT / "evals" / "results" / "reports"

# Extra things a metric may hold after grading, shown under its reason.
#   attribute on the metric         label in the report
EXTRAS = [
    ("task", "Task (as the judge understood it)"),
    ("outcome", "Outcome (as the judge summarised it)"),
    ("extracted_plan", "Plan (as the judge extracted it)"),   # Plan Adherence
]


def _as_dict(metrics):
    """Accept one metric or a {name: metric} dict."""
    if isinstance(metrics, dict):
        return metrics
    return {getattr(metrics, "__name__", "Metric"): metrics}


def _result(metric):
    score = metric.score
    error = getattr(metric, "error", None)
    if score is None:
        status = "ERROR" if error else "NOT SCORED"
    else:
        status = "PASS" if score >= metric.threshold else "FAIL"
    reason = error or metric.reason or (
        "The run stopped before this task was graded." if score is None else ""
    )
    extras = []
    for attr, label in EXTRAS:
        value = getattr(metric, attr, None)
        if value:
            if isinstance(value, list):
                value = " → ".join(f"({i}) {s}" for i, s in enumerate(value, 1))
            extras.append((label, str(value)))
    return {
        "score": "" if score is None else round(score, 2),
        "status": status,
        "reason": reason,
        "extras": extras,
    }


def _slug(name):
    return name.lower().replace(" ", "_")


def write_report(rows, report_name: str) -> Path:
    """rows: list of (golden, metric-or-{name: metric}) after the eval loop."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)   # parents: results/ may not exist yet
    stamp = datetime.now().strftime("%Y%m%d_%H%M")

    tasks = []
    for i, (golden, metrics) in enumerate(rows, 1):
        meta = golden.additional_metadata or {}
        tasks.append({
            "#": i,
            "difficulty": meta.get("difficulty", ""),
            "task": golden.input,
            "results": {name: _result(m) for name, m in _as_dict(metrics).items()},
            "thresholds": {name: m.threshold for name, m in _as_dict(metrics).items()},
        })
    metric_names = list(tasks[0]["results"]) if tasks else []

    # ---- CSV ---------------------------------------------------------------
    csv_path = REPORT_DIR / f"{report_name}_{stamp}.csv"
    fields = ["#", "difficulty", "task"]
    for name in metric_names:
        fields += [f"{_slug(name)}_score", f"{_slug(name)}_status", f"{_slug(name)}_reason"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for t in tasks:
            row = {"#": t["#"], "difficulty": t["difficulty"], "task": t["task"]}
            for name in metric_names:
                r = t["results"][name]
                row[f"{_slug(name)}_score"] = r["score"]
                row[f"{_slug(name)}_status"] = r["status"]
                row[f"{_slug(name)}_reason"] = r["reason"]
            writer.writerow(row)

    # ---- Markdown ------------------------------------------------------------
    md_path = REPORT_DIR / f"{report_name}_{stamp}.md"
    title = report_name.replace("_", " ").title()
    lines = [f"# {title} report — {datetime.now():%d %b %Y, %H:%M}", ""]

    # Summary: one line per metric
    lines += ["| Metric | Average score | Passed | Threshold |", "|---|---|---|---|"]
    for name in metric_names:
        scores = [t["results"][name]["score"] for t in tasks if t["results"][name]["score"] != ""]
        passed = sum(t["results"][name]["status"] == "PASS" for t in tasks)
        avg = f"{sum(scores) / len(scores):.2f}" if scores else "n/a"
        lines.append(f"| {name} | {avg} | {passed}/{len(tasks)} | {tasks[0]['thresholds'][name]} |")

    # One line per task, every metric side by side
    lines += ["", "| # | Difficulty | Task | " + " | ".join(metric_names) + " |",
              "|---|---|---|" + "---|" * len(metric_names)]
    for t in tasks:
        cells = [f"{t['results'][n]['score']} {t['results'][n]['status']}" for n in metric_names]
        lines.append(f"| {t['#']} | {t['difficulty']} | {t['task']} | " + " | ".join(cells) + " |")

    # Details: tasks with any non-PASS first
    lines += ["", "## Details (tasks with a failure first)", ""]
    all_pass = lambda t: all(r["status"] == "PASS" for r in t["results"].values())
    for t in sorted(tasks, key=lambda t: (all_pass(t), t["#"])):
        lines += [f"### {t['#']}. {t['task']}", "", f"*Difficulty: {t['difficulty']}*", ""]
        for name in metric_names:
            r = t["results"][name]
            lines.append(f"**{name}: {r['status']} ({r['score']})**")
            lines.append("")
            for label, value in r["extras"]:
                lines.append(f"- {label}: {value}")
            lines.append(f"- Reason: {r['reason']}")
            lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"\nReport written:\n  {md_path}\n  {csv_path}")
    return md_path