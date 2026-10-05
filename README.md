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

### 🧪 Run Evaluations

Run:

* Full Agent Evaluation
* Task Completion Evaluation
* Plan Judge Check

---

# 🏗️ Architecture

```text
                    ┌──────────────────────────┐
                    │       Streamlit UI       │
                    │       frontend.py        │
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
├── frontend.py
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
| Groq          | LLM provider                    |
| Streamlit     | Web interface                   |
| Pandas        | Evaluation report/data handling |
| python-dotenv | Environment variable management |
| Git/GitHub    | Version control                 |

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/priyanshukushwaha0/Agent-Evals-Using-DeepEvals.git
```

Move into the project:

```bash
cd Agent-Evals-Using-DeepEvals
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv myenv
```

Activate it:

```bash
myenv\Scripts\activate
```


# 📦 Install Dependencies

This project uses `requirements.txt` for dependency management.

Install all dependencies:

```bash
pip install -r requirements.txt
```

# 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=""
GROQ_MODEL=openai/gpt-oss-120b

DEEPEVAL_API_KEY=your_deepeval_api_key

LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=agent-evals-using-deepevals
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

---

# 🖥️ Run the Streamlit UI

After installing dependencies:

```bash
streamlit run frontend.py
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

# ⭐ Project Summary

**Agent Evals using DeepEvals** is an evaluation-focused AI agent project that combines **LangGraph, DeepEval, and a controlled file-system sandbox** to measure whether an AI agent can correctly plan and execute real-world file-management tasks.

The project includes both a **command-line interface** and a **Streamlit evaluation dashboard**, making it possible to interact with the agent, inspect its workspace, run evaluation suites, and review generated evaluation reports.
