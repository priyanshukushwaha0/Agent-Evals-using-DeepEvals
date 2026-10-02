# Agent-Evals-using-DeepEvals
# 🤖 Agent Evals using DeepEvals

A practical **AI Agent Evaluation Platform** for evaluating a LangGraph-based file-management agent using **DeepEval**.

The project provides a complete evaluation workflow for testing whether an AI agent can understand and execute file-management tasks correctly. It evaluates **task completion, plan quality, and plan adherence** while maintaining a controlled sandbox workspace.

The project also includes a **Streamlit UI** for interacting with the agent, viewing the workspace, running evaluations, and inspecting evaluation reports.

---

## 🚀 Project Overview

Modern AI agents can generate a response that looks correct while still failing to perform the requested task.

For example, if a user asks:

> "Create a folder called reports and move report.txt into it."

An agent should not only describe the correct operation — it should actually perform the operation correctly.

This project evaluates an agent's ability to:

* Understand the user's task
* Create an appropriate execution plan
* Select and use the correct tools
* Perform file operations correctly
* Complete the requested task
* Follow its generated plan
* Produce an appropriate final response

The agent operates inside an isolated sandbox so that evaluation tasks can be executed safely and repeatedly.

---

# 🎯 Key Features

## 🤖 AI File Manager Agent

The project contains a LangGraph-based file-management agent capable of performing tasks on a controlled workspace.

Example tasks:

```text
Create a file named notes.txt.

Create a folder called reports.

Move report.txt into the reports folder.

Rename old_notes.txt to notes.txt.

Delete temporary.txt.

Create a project folder and organize the files inside it.
```

---

## 🧪 DeepEval Evaluation

The project uses **DeepEval** to evaluate agent performance.

The evaluation framework measures areas such as:

* Task Completion
* Plan Quality
* Plan Adherence
* Agent execution behavior
* Final task outcome

---

## 🧠 Plan Evaluation

The agent generates a plan before executing a task.

The project evaluates whether the generated plan is:

* Relevant
* Complete
* Appropriate for the task
* Followed during execution

---

## 📂 Controlled Sandbox

The agent does not operate on arbitrary system files.

Instead, it works inside:

```text
data/workspace/
```

The sandbox can be reset before an evaluation so that every test starts from a known state.

The original starting state is maintained separately in:

```text
data/workspace_original/
```

This makes evaluations reproducible.

---

## 📋 Golden Evaluation Tasks

Evaluation tasks are stored in:

```text
goldens/goldens.json
```

The project contains test tasks categorized by difficulty, including:

* Easy
* Medium
* Difficult

These tasks provide consistent scenarios for evaluating agent performance.

---

# 🖥️ Streamlit UI

The project includes a Streamlit interface for interacting with the agent and running evaluations.

The UI provides:

### 🚀 Run Agent

Enter a file-management task and execute the existing LangGraph agent.

### 🔄 Reset Workspace

Restore the sandbox to its original state.

### 📂 Workspace Explorer

View files and folders currently available inside the agent workspace.

### 📄 File Viewer

Inspect text files created or modified by the agent.

### 🧪 Run Evaluations

Run:

* Full Agent Evaluation
* Task Completion Evaluation
* Plan Judge Check

### 📊 Evaluation Reports

View generated Markdown and CSV evaluation reports directly from the UI.

---

# 🏗️ Architecture

```text
                    ┌──────────────────────────┐
                    │       Streamlit UI       │
                    │          app.py          │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      LangGraph Agent     │
                    │        agent.py          │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │       Agent Tools        │
                    │     File Operations      │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      Sandbox Manager     │
                    │       sandbox.py         │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      data/workspace      │
                    │      Agent Workspace     │
                    └──────────────────────────┘


             Evaluation Flow
             ────────────────

                    goldens/goldens.json
                              │
                              ▼
                    ┌───────────────────┐
                    │   Agent Execution │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │     DeepEval      │
                    │    Evaluation     │
                    └─────────┬─────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
          Task Completion  Plan Quality  Plan Adherence
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                    evals/results/reports/
```

---

# 📁 Project Structure

```text
Agent-Evals-Using-DeepEvals/
│
├── app.py
│   └── Streamlit user interface
│
├── main.py
│   └── Run the agent from the command line
│
├── requirements.txt
│   └── Python dependencies
│
├── .env
│   └── Local API keys and environment variables
│
├── .env.example
│   └── Environment variable template
│
├── .gitignore
│   └── Git ignore rules
│
├── README.md
│   └── Project documentation
│
├── src/
│   └── file_manager_agent/
│       │
│       ├── __init__.py
│       │
│       ├── agent.py
│       │   └── LangGraph agent, prompts, tools and run_agent()
│       │
│       └── sandbox.py
│           └── Sandbox files, reset_sandbox() and safe paths
│
├── evals/
│   │
│   ├── __init__.py
│   │
│   ├── eval_agent.py
│   │   └── Main evaluation
│   │
│   ├── eval_task_completion.py
│   │   └── Task Completion evaluation
│   │
│   ├── plan_judge.py
│   │   └── Plan quality evaluation
│   │
│   ├── check_plan_judge.py
│   │   └── Plan judge sanity check
│   │
│   ├── slim_trace.py
│   │   └── Simplifies LangGraph traces
│   │
│   ├── report.py
│   │   └── Generates Markdown and CSV reports
│   │
│   └── results/
│       │
│       ├── reports/
│       │   └── Evaluation reports
│       │
│       └── traces/
│           └── Evaluation traces
│
├── goldens/
│   └── goldens.json
│       └── Evaluation tasks
│
└── data/
    │
    ├── workspace/
    │   └── Temporary agent workspace
    │
    └── workspace_original/
        └── Original sandbox state
```

---

# 🛠️ Technologies Used

| Technology    | Purpose                         |
| ------------- | ------------------------------- |
| Python        | Main programming language       |
| LangGraph     | Agent orchestration             |
| LangChain     | LLM/agent framework             |
| DeepEval      | AI agent evaluation             |
| OpenAI        | LLM provider                    |
| Streamlit     | Web interface                   |
| Pandas        | Evaluation report/data handling |
| python-dotenv | Environment variable management |
| Git/GitHub    | Version control                 |

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Agent-Evals-Using-DeepEvals.git
```

Move into the project:

```bash
cd Agent-Evals-Using-DeepEvals
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

---

# 📦 Install Dependencies

This project uses `requirements.txt` for dependency management.

Install all dependencies:

```bash
pip install -r requirements.txt
```

The project does **not require `uv`**.

You can therefore use standard:

```text
Python
   ↓
pip
   ↓
requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key

DEEPEVAL_API_KEY=your_deepeval_api_key

LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=agent-evals-using-deepevals
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

Not every environment variable is necessarily required for every execution mode.

### `.env.example`

For GitHub, commit `.env.example` instead of your real `.env`:

```env
OPENAI_API_KEY=
DEEPEVAL_API_KEY=

LANGCHAIN_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=agent-evals-using-deepevals
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### ⚠️ Never commit your real `.env`

Your `.gitignore` should contain:

```gitignore
.env
.env.*
!.env.example

.venv/
__pycache__/
*.pyc

data/workspace/*
data/workspace_original/*

evals/results/traces/*
```

---

# 🖥️ Run the Streamlit UI

After installing dependencies:

```bash
streamlit run app.py
```

Streamlit will start a local server.

Open:

```text
http://localhost:8501
```

The UI provides:

```text
Agent Task
     ↓
LangGraph Agent
     ↓
Sandbox Workspace
     ↓
Agent Result
     ↓
DeepEval
     ↓
Evaluation Report
```

---

# 💻 Run from Command Line

You can also use the project without Streamlit.

Run the agent:

```bash
python main.py
```

If your `main.py` accepts a task argument:

```bash
python main.py "Create a file named notes.txt"
```

---

# 🧪 Run Evaluations

## Full Agent Evaluation

Run:

```bash
python -m evals.eval_agent
```

This is the primary evaluation workflow.

It evaluates the agent across the project's golden tasks.

---

## Task Completion Evaluation

Run:

```bash
python -m evals.eval_task_completion
```

This focuses on whether the agent successfully completes the requested task.

---

## Plan Judge

Run:

```bash
python -m evals.plan_judge
```

This evaluates the quality of the agent's generated plans.

---

## Plan Judge Sanity Check

Run:

```bash
python -m evals.check_plan_judge
```

This checks whether the plan judge can distinguish appropriate plans from inappropriate plans.

---

# 📊 Evaluation Results

Evaluation results are stored in:

```text
evals/results/
```

Reports:

```text
evals/results/reports/
```

Typical report formats include:

```text
.md
.csv
```

Traces:

```text
evals/results/traces/
```

Traces contain detailed information about agent execution and are intended primarily for evaluation/debugging.

---

# 📂 Sandbox Data

The project does not require you to manually provide a large dataset.

The sandbox is generated and reset by:

```text
src/file_manager_agent/sandbox.py
```

The runtime workspace is:

```text
data/workspace/
```

The original workspace is:

```text
data/workspace_original/
```

The sandbox provides the files on which the agent performs its file-management tasks.

---

# 🔄 Sandbox Reset

Before running an evaluation, the workspace can be reset to its original state.

The existing code provides:

```python
reset_sandbox()
```

This ensures that different evaluation runs start from a controlled environment.

---

# 🧪 Example Evaluation Tasks

Example tasks can include:

### Easy

```text
Create a file named notes.txt.
```

```text
Rename notes.txt to important_notes.txt.
```

### Medium

```text
Create a folder named reports and move report.txt into it.
```

```text
Create a project folder and move all Python files into it.
```

### Difficult

```text
Organize the workspace into folders based on file type while preserving existing files and directory structure.
```

The actual evaluation tasks used by the project are defined in:

```text
goldens/goldens.json
```

---

# 🔍 Evaluation Workflow

The complete evaluation process is:

```text
1. Load Golden Task
        ↓
2. Reset Sandbox
        ↓
3. Run LangGraph Agent
        ↓
4. Agent Creates Plan
        ↓
5. Agent Executes Tools
        ↓
6. Workspace Changes
        ↓
7. Evaluate Task Completion
        ↓
8. Evaluate Plan Quality
        ↓
9. Evaluate Plan Adherence
        ↓
10. Generate Report
```

---

# 🎯 Why Use a Sandbox?

The sandbox provides a controlled environment for agent evaluation.

Without a sandbox, an agent performing file operations could potentially modify unintended files.

With the sandbox:

```text
Agent
  │
  ▼
data/workspace/
  │
  ├── create
  ├── read
  ├── rename
  ├── move
  └── delete
```

This makes evaluation safer and reproducible.

---

# 🔐 Security

Never place API keys directly inside Python source code.

Use:

```text
.env
```

instead.

Never commit:

```text
.env
```

to GitHub.

Use:

```text
.env.example
```

for documenting required environment variables.

---

# 📈 Example Workflow

Start the application:

```bash
streamlit run app.py
```

Enter:

```text
Create a folder named reports and create a file summary.txt inside it.
```

Click:

```text
Run Agent
```

The agent:

```text
Understand task
      ↓
Generate plan
      ↓
Execute tools
      ↓
Modify sandbox
      ↓
Return result
```

Then run:

```bash
python -m evals.eval_agent
```

DeepEval evaluates the agent's execution.

---

# 🧩 Project Components

## `app.py`

Streamlit frontend.

Provides:

* Agent execution
* Workspace explorer
* File viewer
* Sandbox reset
* Evaluation controls
* Evaluation reports
* Session history

---

## `main.py`

Command-line entry point for running the agent.

---

## `agent.py`

Main LangGraph agent implementation.

Contains:

* Agent graph
* Prompts
* Tools
* Agent execution logic
* `build_agent()`
* `run_agent()`

---

## `sandbox.py`

Controls the agent's workspace.

Contains functionality for:

* Creating starting files
* Resetting the workspace
* Safe file paths
* Sandbox management

---

## `eval_agent.py`

Main evaluation workflow.

Evaluates:

* Task Completion
* Plan Quality
* Plan Adherence

---

## `eval_task_completion.py`

Runs a simpler Task Completion evaluation.

---

## `plan_judge.py`

Contains the plan evaluation logic.

---

## `check_plan_judge.py`

Provides a sanity check for the plan judge.

---

## `slim_trace.py`

Reduces LangGraph execution traces before they are passed to evaluation/judging components.

---

## `report.py`

Generates evaluation reports in:

```text
Markdown
CSV
```

---

# 🗂️ Data vs Evaluation Tasks

The project separates runtime workspace data from evaluation tasks.

### Runtime workspace

```text
data/
├── workspace/
└── workspace_original/
```

### Evaluation tasks

```text
goldens/
└── goldens.json
```

This separation makes it easier to add new evaluation scenarios without modifying the agent implementation.

---

# 🚀 Future Improvements

Possible future improvements include:

* More agent evaluation metrics
* More golden tasks
* Advanced trajectory evaluation
* Human evaluation
* Evaluation score dashboard
* Agent comparison
* Multiple LLM providers
* Automated regression testing
* Historical evaluation tracking
* Advanced trace visualization
* CI/CD evaluation pipelines

---

# 📌 Important Commands

| Purpose                      | Command                                |
| ---------------------------- | -------------------------------------- |
| Create environment           | `python -m venv .venv`                 |
| Activate Windows environment | `.venv\Scripts\activate`               |
| Install dependencies         | `pip install -r requirements.txt`      |
| Start Streamlit              | `streamlit run app.py`                 |
| Run CLI agent                | `python main.py`                       |
| Full evaluation              | `python -m evals.eval_agent`           |
| Task completion              | `python -m evals.eval_task_completion` |
| Plan judge                   | `python -m evals.plan_judge`           |
| Plan judge check             | `python -m evals.check_plan_judge`     |

---

# 🛠️ Troubleshooting

## `ModuleNotFoundError: No module named 'file_manager_agent'`

Make sure you run the command from the project root:

```bash
cd Agent-Evals-Using-DeepEvals
```

For Streamlit, use:

```bash
streamlit run app.py
```

The UI adds the `src` directory to Python's import path.

---

## `ModuleNotFoundError`

Reinstall dependencies:

```bash
pip install -r requirements.txt
```

Make sure your virtual environment is activated.

---

## API Key Error

Check your `.env` file:

```env
OPENAI_API_KEY=your_key
```

Then restart Streamlit:

```bash
streamlit run app.py
```

---

## Workspace Problems

Reset the sandbox from the Streamlit sidebar or use the existing sandbox reset functionality.

The workspace is:

```text
data/workspace/
```

---

# 📜 License

Add the license that you want to use for this repository.

For example:

```text
MIT License
```

If you use an MIT License, add a `LICENSE` file containing the standard MIT license text.

---

# 👨‍💻 Author

**Priyanshu Kushwaha**

Aspiring AI / GenAI Engineer focused on:

* Artificial Intelligence
* Machine Learning
* Generative AI
* LLM Applications
* AI Agents
* RAG
* Agent Evaluation

---

# ⭐ Project Summary

**Agent Evals using DeepEvals** is an evaluation-focused AI agent project that combines **LangGraph, DeepEval, and a controlled file-system sandbox** to measure whether an AI agent can correctly plan and execute real-world file-management tasks.

The project includes both a **command-line interface** and a **Streamlit evaluation dashboard**, making it possible to interact with the agent, inspect its workspace, run evaluation suites, and review generated evaluation reports.












# 🤖 Agent Evals using DeepEvals

> **An AI Agent Evaluation Platform for testing task completion, planning quality, and execution adherence in a LangGraph-based file-management agent.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Orchestration-orange.svg)](https://www.langchain.com/langgraph)
[![DeepEval](https://img.shields.io/badge/DeepEval-Agent%20Evaluation-purple.svg)](https://deepeval.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io/)

---

## 📌 Overview

**Agent Evals using DeepEvals** is a practical AI agent evaluation project designed to measure how reliably an AI agent can **understand, plan, and execute file-management tasks**.

The project combines **LangGraph** for agent orchestration with **DeepEval** for evaluation and a controlled **sandbox environment** for reproducible testing.

A **Streamlit dashboard** provides an interactive interface to run the agent, inspect its workspace, execute evaluation suites, and view generated reports.

The system is designed around a simple principle:

> **Don't evaluate an agent only by what it says — evaluate what it actually does.**

---

## 🎯 What This Project Evaluates

The agent is evaluated across multiple dimensions:

| Evaluation          | What it measures                                             |
| ------------------- | ------------------------------------------------------------ |
| **Task Completion** | Whether the requested task was actually completed            |
| **Plan Quality**    | Whether the generated plan is appropriate for the task       |
| **Plan Adherence**  | Whether the agent follows its planned steps                  |
| **Execution Trace** | How the agent reached the final result                       |
| **Final Response**  | Whether the final response accurately reflects the execution |

---

## ✨ Key Features

### 🤖 LangGraph File-Management Agent

A tool-using agent capable of performing operations such as:

* Create files
* Read files
* Edit files
* Rename files
* Move files
* Delete files
* Create directories
* Organize workspace content

Example:

```text
Create a folder named reports and move report.txt into it.
```

The agent creates a plan, executes the required operations, and returns the result.

---

### 🧪 DeepEval-Based Evaluation

DeepEval is used to evaluate the agent rather than relying only on the final text response.

The evaluation pipeline examines:

```text
User Task
    ↓
Agent Planning
    ↓
Tool Execution
    ↓
Workspace Changes
    ↓
Final Response
    ↓
DeepEval
    ↓
Evaluation Results
```

---

### 📂 Controlled Sandbox

All file operations are performed inside an isolated workspace:

```text
data/workspace/
```

The initial state is maintained separately:

```text
data/workspace_original/
```

The workspace can be reset before each evaluation, ensuring that tests start from a consistent state.

---

### 📋 Golden Test Cases

Evaluation scenarios are stored in:

```text
goldens/goldens.json
```

The test set contains tasks categorized by difficulty:

* Easy
* Medium
* Difficult

This allows the same agent to be evaluated consistently across multiple scenarios.

---

### 🖥️ Streamlit Dashboard

The project includes an interactive Streamlit UI.

The dashboard allows you to:

* Run the AI agent
* Enter custom tasks
* Reset the sandbox
* Explore workspace files
* View file contents
* Inspect agent plans
* Inspect execution steps
* Run DeepEval evaluations
* View evaluation reports
* Download CSV/Markdown reports
* Review session history

Launch it with:

```bash
streamlit run app.py
```

---

## 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │    Streamlit UI      │
                         │       app.py         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   LangGraph Agent    │
                         │      agent.py        │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │      Agent Tools      │
                         │  File Operations      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Sandbox Manager    │
                         │     sandbox.py       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    data/workspace    │
                         │   Controlled Files   │
                         └──────────────────────┘


                         Evaluation Pipeline
                         ───────────────────

                         goldens/goldens.json
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Agent Execution    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      DeepEval        │
                         │     Evaluation       │
                         └──────────┬───────────┘
                                    │
                   ┌────────────────┼────────────────┐
                   ▼                ▼                ▼
             Task Completion   Plan Quality   Plan Adherence
                   │                │                │
                   └────────────────┼────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   Evaluation Reports │
                         └──────────────────────┘
```

---

## 📁 Project Structure

```text
Agent-Evals-Using-DeepEvals/
│
├── app.py
│   └── Streamlit dashboard
│
├── main.py
│   └── CLI entry point
│
├── requirements.txt
│   └── Python dependencies
│
├── .env.example
│   └── Environment variable template
│
├── .gitignore
│
├── README.md
│
├── src/
│   └── file_manager_agent/
│       ├── __init__.py
│       ├── agent.py
│       └── sandbox.py
│
├── evals/
│   ├── __init__.py
│   ├── eval_agent.py
│   ├── eval_task_completion.py
│   ├── plan_judge.py
│   ├── check_plan_judge.py
│   ├── slim_trace.py
│   ├── report.py
│   │
│   └── results/
│       ├── reports/
│       └── traces/
│
├── goldens/
│   └── goldens.json
│
└── data/
    ├── workspace/
    └── workspace_original/
```

---

## 🛠️ Tech Stack

### AI & Agent

* **Python**
* **LangGraph**
* **LangChain**
* **OpenAI**

### Evaluation

* **DeepEval**
* Custom plan judge
* Execution trace analysis

### Interface

* **Streamlit**

### Data & Utilities

* **Pandas**
* **python-dotenv**

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Agent-Evals-Using-DeepEvals.git
```

```bash
cd Agent-Evals-Using-DeepEvals
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

This project uses standard `pip` and `requirements.txt`.

```bash
pip install -r requirements.txt
```

No `uv` or `uv.lock` is required.

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

```env
OPENAI_API_KEY=your_openai_api_key

DEEPEVAL_API_KEY=your_deepeval_api_key

LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=agent-evals-using-deepevals
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### `.env.example`

Commit only the template:

```env
OPENAI_API_KEY=
DEEPEVAL_API_KEY=

LANGCHAIN_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=agent-evals-using-deepevals
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

> ⚠️ **Never commit your actual `.env` file or API keys to GitHub.**

---

# 🖥️ Run the Streamlit Application

Start the dashboard:

```bash
streamlit run app.py
```

Open the URL shown by Streamlit, normally:

```text
http://localhost:8501
```

### Streamlit workflow

```text
Open Dashboard
      ↓
Enter Agent Task
      ↓
Run Agent
      ↓
View Plan
      ↓
View Execution Steps
      ↓
Inspect Workspace
      ↓
Run DeepEval
      ↓
View Evaluation Report
```

---

# 💻 Run the Agent from CLI

The project also supports command-line execution.

```bash
python main.py
```

If the CLI accepts a task argument:

```bash
python main.py "Create a file named notes.txt"
```

---

# 🧪 Run Evaluations

### Full Evaluation

```bash
python -m evals.eval_agent
```

The main evaluation includes:

* Task Completion
* Plan Quality
* Plan Adherence

---

### Task Completion Only

```bash
python -m evals.eval_task_completion
```

---

### Plan Judge

```bash
python -m evals.plan_judge
```

---

### Plan Judge Sanity Check

```bash
python -m evals.check_plan_judge
```

---

# 📊 Evaluation Reports

Reports are generated in:

```text
evals/results/reports/
```

The project supports:

```text
Markdown (.md)
CSV (.csv)
```

Execution traces are stored in:

```text
evals/results/traces/
```

These traces can be used to inspect the agent's execution behavior.

---

# 📂 Sandbox Design

The sandbox is automatically managed by:

```text
src/file_manager_agent/sandbox.py
```

### Original State

```text
data/workspace_original/
```

Contains the starting workspace.

### Runtime State

```text
data/workspace/
```

Contains the workspace currently being modified by the agent.

### Reset

The workspace can be restored using:

```python
reset_sandbox()
```

This ensures that evaluation runs remain reproducible.

---

# 📋 Example Tasks

### Easy

```text
Create a file named notes.txt.
```

```text
Rename notes.txt to important_notes.txt.
```

---

### Medium

```text
Create a reports folder and move report.txt into it.
```

```text
Create a Python folder and move all Python files into it.
```

---

### Difficult

```text
Organize the workspace into appropriate folders while preserving the existing files and directory structure.
```

The actual benchmark tasks are stored in:

```text
goldens/goldens.json
```

---

# 🔄 Evaluation Workflow

Each evaluation follows a controlled process:

```text
              Golden Task
                   │
                   ▼
            Reset Sandbox
                   │
                   ▼
            LangGraph Agent
                   │
                   ▼
              Generate Plan
                   │
                   ▼
             Execute Tools
                   │
                   ▼
            Modify Workspace
                   │
                   ▼
             Final Response
                   │
                   ▼
               DeepEval
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       Task      Plan     Plan
    Completion  Quality  Adherence
          │        │        │
          └────────┼────────┘
                   ▼
              Final Report
```

---

# 🔒 Security & Best Practices

* Keep API keys in `.env`.
* Never commit `.env`.
* Use `.env.example` for documentation.
* Keep agent operations inside the sandbox.
* Reset the workspace before benchmark runs.
* Avoid putting sensitive or personal files in the sandbox.

---

# 📌 Useful Commands

| Action               | Command                                |
| -------------------- | -------------------------------------- |
| Create environment   | `python -m venv .venv`                 |
| Activate Windows     | `.venv\Scripts\activate`               |
| Install dependencies | `pip install -r requirements.txt`      |
| Start UI             | `streamlit run app.py`                 |
| Run CLI              | `python main.py`                       |
| Full evaluation      | `python -m evals.eval_agent`           |
| Task evaluation      | `python -m evals.eval_task_completion` |
| Plan judge           | `python -m evals.plan_judge`           |
| Plan judge check     | `python -m evals.check_plan_judge`     |

---

