"""
Sanity check for the plan judge (evals/plan_judge.py).

A judge that says PASS to everything looks perfect on a run where every plan is
good. Before trusting its scores, show it plans we already KNOW are bad and
plans we already KNOW are good, and check that it tells them apart.

    BAD plans   real plans from earlier runs that were wrong, each with the flaw
                we found by reading its trace. The judge must FAIL them.
    GOOD plans  real plans from the 30 Sep 04:25 run that deepeval's Plan Quality
                failed but that are correct. The judge must PASS them.

No agent runs here. Only the judge is called: one call per plan, per repeat.

Run (from the project root):
    uv run python -m evals.check_plan_judge
"""

from dotenv import load_dotenv

load_dotenv()

from evals.plan_judge import make_plan_judge, plan_test_case
from file_manager_agent.sandbox import list_workspace, reset_sandbox

JUDGE_MODEL = "openai/gpt-oss-120b"   # the model you use for the plan judge in eval_agent.py
THRESHOLD = 0.7
REPEATS = 3              # set to 3 to see how much the judge's score moves between calls

# Note on the BAD plans from the 29 Sep 11:04 run: the old planner used wrong
# argument names (file=, filename=, source=). We changed them to today's names
# (path=, content=) so the judge has to catch the real mistake in the logic,
# not just a naming slip. Everything else is word for word from the trace.
CASES = [
    # ---------------- BAD: the judge must FAIL these ----------------
    {
        "name": "11:04 #12 made-up content",
        "expect": "FAIL",
        "flaw": "Writes invented text instead of the ERROR lines it read, and writes the file twice.",
        "task": "Create logs/errors_summary.txt containing every line from logs/error.log that starts with ERROR",
        "plan": [
            "Call read_file with path='logs/error.log'",
            "Call create_file with path='logs/errors_summary.txt' and content='ERROR lines from logs/error.log'",
            "Call create_file with path='logs/errors_summary.txt' and content='Filtered ERROR lines'",
        ],
    },
    {
        "name": "11:04 #13 wrong scope + guessed result",
        "expect": "FAIL",
        "flaw": "Only looks in notes/, and writes all three notes into people.txt before checking which mention Priya.",
        "task": "Find every text file in the workspace that mentions Priya and write their paths, one per line, into people.txt",
        "plan": [
            "Call list_files with folder='notes'",
            "Call read_file with path='notes/ideas.txt'",
            "Call read_file with path='notes/meeting_feb.txt'",
            "Call read_file with path='notes/meeting_jan.txt'",
            "Call create_file with path='people.txt' and content='notes/ideas.txt\\nnotes/meeting_feb.txt\\nnotes/meeting_jan.txt'",
        ],
    },
    {
        "name": "03:30 #13 reads the wrong files",
        "expect": "FAIL",
        "flaw": "Reads the three .tmp files but skips reports/summary.txt and todo.txt, so it misses a file that mentions Priya.",
        "task": "Find every text file in the workspace that mentions Priya and write their paths, one per line, into people.txt",
        "plan": [
            "Call read_file with path='cache.tmp'",
            "Call read_file with path='logs/app.log'",
            "Call read_file with path='logs/error.log'",
            "Call read_file with path='logs/old/debug.log'",
            "Call read_file with path='notes/ideas.txt'",
            "Call read_file with path='notes/meeting_feb.txt'",
            "Call read_file with path='notes/meeting_jan.txt'",
            "Call read_file with path='old_draft.tmp'",
            "Call read_file with path='reports/draft_q3_2024.tmp'",
            "Call create_file with path='people.txt' and content equal to the paths of the text files from steps 1-9 whose contents mention 'Priya', with one path per line",
        ],
    },
    {
        "name": "11:04 #15 delete_file on folders",
        "expect": "FAIL",
        "flaw": "Uses delete_file (single files only) on the folders logs/old/ and logs/, so the folders are never deleted.",
        "task": "Delete the logs folder completely",
        "plan": [
            "Call delete_file with path='logs/old/debug.log'",
            "Call delete_file with path='logs/old/'",
            "Call delete_file with path='logs/error.log'",
            "Call delete_file with path='logs/app.log'",
            "Call delete_file with path='logs/'",
        ],
    },
    {
        "name": "11:04 #6 needless reads",
        "expect": "FAIL",
        "flaw": "Reads all four PDFs just to count them; the listing in step 1 already answers the question. (The mildest flaw here.)",
        "task": "How many PDF files are in the reports folder?",
        "plan": [
            "Call list_files with folder='reports'",
            "Call read_file with path='reports/q1_2024.pdf'",
            "Call read_file with path='reports/q2_2024.pdf'",
            "Call read_file with path='reports/q3_2024.pdf'",
            "Call read_file with path='reports/q4_2023.pdf'",
        ],
    },
    # ---------------- GOOD: the judge must PASS these ----------------
    {
        "name": "04:25 #10 all .tmp files",
        "expect": "PASS",
        "flaw": "",
        "task": "Delete every .tmp file in the workspace, including those inside subfolders",
        "plan": [
            "Call delete_file with path='cache.tmp'",
            "Call delete_file with path='old_draft.tmp'",
            "Call delete_file with path='reports/draft_q3_2024.tmp'",
        ],
    },
    {
        "name": "04:25 #13 reads every text file",
        "expect": "PASS",
        "flaw": "",
        "task": "Find every text file in the workspace that mentions Priya and write their paths, one per line, into people.txt",
        "plan": [
            "Call read_file with path='logs/app.log'",
            "Call read_file with path='logs/error.log'",
            "Call read_file with path='logs/old/debug.log'",
            "Call read_file with path='notes/ideas.txt'",
            "Call read_file with path='notes/meeting_feb.txt'",
            "Call read_file with path='notes/meeting_jan.txt'",
            "Call read_file with path='reports/summary.txt'",
            "Call read_file with path='todo.txt'",
            "Call create_file with path='people.txt' and content set to the paths from steps 1-8 whose text mentions 'Priya', with one path per line",
        ],
    },
    {
        "name": "04:25 #14 honest about a missing file",
        "expect": "PASS",
        "flaw": "",
        "task": "Move q2_2024.pdf and q2_2025.pdf from reports into the archive folder",
        "plan": [
            "Call move_file with source='reports/q2_2024.pdf' and destination='archive'",
            "Tell the user: 'reports/q2_2025.pdf' is not present in the workspace listing, so it could not be moved to 'archive'.'",
        ],
    },
    {
        "name": "04:25 #15 one delete_folder call",
        "expect": "PASS",
        "flaw": "",
        "task": "Delete the logs folder completely",
        "plan": ["Call delete_folder with path='logs'"],
    },
]


def main():
    reset_sandbox()
    listing = list_workspace()   # the same starting workspace every planner saw

    results = []
    for case in CASES:
        for n in range(REPEATS):
            judge = make_plan_judge(model=JUDGE_MODEL, threshold=THRESHOLD)
            judge.measure(plan_test_case(case["task"], case["plan"], listing))
            got = "PASS" if judge.score >= THRESHOLD else "FAIL"
            ok = got == case["expect"]
            results.append((case, judge.score, got, ok, judge.reason))

            print(f"\n{'OK   ' if ok else 'WRONG'}  {case['name']}"
                  + (f"  (repeat {n + 1})" if REPEATS > 1 else ""))
            print(f"       expected {case['expect']}, judge gave {judge.score:.2f} {got}")
            if case["flaw"]:
                print(f"       known flaw: {case['flaw']}")
            print(f"       judge said: {judge.reason}")

    bad = [r for r in results if r[0]["expect"] == "FAIL"]
    good = [r for r in results if r[0]["expect"] == "PASS"]
    caught = sum(r[3] for r in bad)
    kept = sum(r[3] for r in good)

    print("\n" + "=" * 70)
    print(f"Judge model: {JUDGE_MODEL}   threshold: {THRESHOLD}   repeats: {REPEATS}")
    print(f"Bad plans failed  (should be all): {caught}/{len(bad)}")
    print(f"Good plans passed (should be all): {kept}/{len(good)}")
    worst_bad = max(r[1] for r in bad)
    best_good = min(r[1] for r in good)
    print(f"Highest score given to a BAD plan:  {worst_bad:.2f}")
    print(f"Lowest score given to a GOOD plan: {best_good:.2f}")
    if worst_bad < best_good:
        print("Every bad plan scored below every good plan: the judge separates them.")
    else:
        print("Some bad plan scored as high as a good one: don't trust close scores yet.")
    print("=" * 70)


if __name__ == "__main__":
    main()