"""Streamlit UI for Agent Evals using DeepEvals.

This UI is a thin layer over the existing agent/evaluation code. It does not
reimplement the agent: it imports build_agent/run_agent/reset_sandbox from the
existing package and runs the existing eval modules.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from file_manager_agent.agent import build_agent, run_agent
from file_manager_agent.sandbox import SANDBOX, reset_sandbox

import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

load_dotenv(ROOT / ".env")

from file_manager_agent.agent import build_agent, run_agent  # noqa: E402
from file_manager_agent.sandbox import SANDBOX, list_workspace, reset_sandbox  # noqa: E402

st.set_page_config(page_title="Agent Evals using DeepEvals", page_icon="🤖", layout="wide")

st.title("🤖 Agent Evals using DeepEvals")
st.caption("Streamlit UI connected directly to the existing LangGraph agent and DeepEval evaluation modules.")


def workspace_tree():
    if not SANDBOX.exists():
        return []
    items = []
    for p in sorted(SANDBOX.rglob("*")):
        rel = p.relative_to(SANDBOX)
        if p.is_dir():
            items.append(f"📁 {rel}/")
        else:
            items.append(f"📄 {rel}")
    return items


def latest_reports():
    report_dir = ROOT / "evals" / "results" / "reports"
    return sorted(report_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)


def run_evaluation(module_name: str):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", module_name],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=3600,
    )

with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Reset Workspace", use_container_width=True):
        reset_sandbox()
        st.success("Workspace reset to the original starting state.")
        st.rerun()

    st.divider()
    st.subheader("Evaluation")
    run_full = st.button("▶ Run Full Evaluation", use_container_width=True, type="primary")
    run_task = st.button("▶ Task Completion Only", use_container_width=True)
    run_plan = st.button("▶ Plan Judge Check", use_container_width=True)

    st.divider()
    st.info("The UI uses the same agent and evaluation code as the CLI commands.")

if run_full or run_task or run_plan:
    module = (
        "evals.eval_agent" if run_full else
        "evals.eval_task_completion" if run_task else
        "evals.check_plan_judge"
    )
    with st.status(f"Running `{module}`...", expanded=True) as status:
        result = run_evaluation(module)
        if result.stdout:
            st.code(result.stdout, language="text")
        if result.stderr:
            st.code(result.stderr, language="text")
        if result.returncode == 0:
            status.update(label="Evaluation completed", state="complete")
        else:
            status.update(label=f"Evaluation failed (exit code {result.returncode})", state="error")

# ---------------------------------------------------------------------------
# Run one agent task
# ---------------------------------------------------------------------------
st.subheader("Run Agent on One Task")

task = st.text_area(
    "Task",
    value="Create a file named shopping.txt with the content 'eggs, bread, milk'",
    height=90,
    help="This is passed directly to the existing run_agent() function.",
)

col1, col2 = st.columns([1, 1])
with col1:
    reset_before = st.checkbox("Reset workspace before task", value=True)
with col2:
    show_details = st.checkbox("Show execution details", value=True)

if st.button("🚀 Run Agent", type="primary"):
    if not task.strip():
        st.warning("Enter a task first.")
    else:
        with st.spinner("Agent is working..."):
            try:
                if reset_before:
                    reset_sandbox()
                state = run_agent(build_agent(), task.strip(), full=True)
                st.session_state["last_state"] = state
            except Exception as exc:
                st.error(f"Agent failed: {type(exc).__name__}: {exc}")

state = st.session_state.get("last_state")
if state:
    st.subheader("Agent Result")
    st.success(state.get("response", "No response returned."))

    if show_details:
        left, right = st.columns(2)
        with left:
            st.markdown("### Plan")
            for i, step in enumerate(state.get("plan", []), 1):
                st.write(f"**{i}.** {step}")
        with right:
            st.markdown("### Step Results")
            for step, result in state.get("past_steps", []):
                with st.expander(step):
                    st.write(result)

# ---------------------------------------------------------------------------
# Workspace viewer
# ---------------------------------------------------------------------------
st.subheader("📂 Current Agent Workspace")
files = workspace_tree()
if files:
    st.code("\n".join(files), language="text")
else:
    st.info("Workspace is empty. Reset it to restore the starting files.")

# ---------------------------------------------------------------------------
# Evaluation reports
# ---------------------------------------------------------------------------
st.subheader("📊 Evaluation Reports")
reports = latest_reports()
if not reports:
    st.info("No evaluation reports yet. Run the Full Evaluation from the sidebar.")
else:
    for report in reports[:10]:
        with st.expander(report.name):
            if report.suffix.lower() == ".md":
                st.markdown(report.read_text(encoding="utf-8"))
            elif report.suffix.lower() == ".csv":
                import pandas as pd
                st.dataframe(pd.read_csv(report), use_container_width=True)
            else:
                st.download_button(
                    "Download",
                    report.read_bytes(),
                    file_name=report.name,
                )

st.divider()
st.caption("CLI remains available: python main.py \"your task\" | python -m evals.eval_agent")
