"""Reproduce fixed local checks and four isolated semantic mutations.

Runs only reviewed owned Python/tests and installed Bandit, never upstream code.
Evidence must use a fresh folder. Failed checks remain recorded; no auto retries.
Seven narrow subprocess scanner exceptions are documented in VERIFICATION.md.
"""

import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess  # nosec B404: fixed owned Python/tests and installed scanner commands.
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from queue_lab import model, render  # noqa: E402
from tests.support import FIXTURE_SHA, cases, document, encode  # noqa: E402
from scripts.report_bound import bound_record  # noqa: E402

MUTATIONS = {
    "waiting-vs-unfinished": ('if len(waiting) >= policy.waiting_capacity:',
                              'if len(waiting) + len(slots) >= policy.waiting_capacity:', 1),
    "newest-vs-oldest": ('job = waiting.pop(0)', 'job = waiting.pop()', 1),
    "start-as-completion": ('count["started"] += 1\n        return "started", "fifo_head", job.job_id',
                            'count["started"] += 1\n        count["completions"] += 1\n        del slots[event.slot_id]\n        return "started", "fifo_head", job.job_id', 1),
    "mismatched-completion": ('if owned is None or owned.job.job_id != event.job_id:',
                              'if owned is None:', 1),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args, cwd, destination):
    # Caller constructs argv from fixed modules/flags and owned artifact paths.
    child = subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True,  # nosec B603
                           text=True, encoding="utf-8", errors="replace", timeout=40, check=False)
    text = child.stdout + child.stderr
    normalized = text.replace(str(ROOT), "<workspace>")
    destination.write_text(normalized, encoding="utf-8", newline="\n")
    return child.returncode, text


def check_mutations(evidence):
    source = ROOT / "queue_lab" / "core.py"
    original = source.read_bytes()
    text = original.decode("utf-8").replace("\r\n", "\n")
    results = []
    base = ROOT / ".test-tmp"
    base.mkdir(exist_ok=True)
    for name, (old, new, count) in MUTATIONS.items():
        if text.count(old) != count:
            raise ValueError("mutation target mismatch")
        with tempfile.TemporaryDirectory(dir=base) as folder:
            copy = Path(folder)
            for directory in ("queue_lab", "tests"):
                (copy / directory).mkdir()
                for file in (ROOT / directory).glob("*.py"):
                    shutil.copyfile(file, copy / directory / file.name)
            (copy / "fixtures").mkdir()
            shutil.copyfile(ROOT / "fixtures" / "cases.json", copy / "fixtures" / "cases.json")
            mutated = copy / "queue_lab" / "core.py"
            mutated.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
            try:
                code, output = run(["-B", "-m", "unittest", "tests.test_model.ModelTests.test_full_frozen_hand_reports", "-v"],
                                   copy, evidence / (name + ".log"))
                detected = code == 1 and "FAIL:" in output and "AssertionError" in output
            finally:
                mutated.write_bytes(original)
            restored = mutated.read_bytes() == original and source.read_bytes() == original
            results.append({"mutation": name, "exit": code, "assertion_detected": detected,
                            "assertion_failure_count": output.count("FAIL:"),
                            "additional_error_count": output.count("ERROR:"),
                            "copy_restored_original_unchanged": restored})
    return results


def check_demos(evidence):
    base = ROOT / ".test-tmp"
    base.mkdir(exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(dir=base) as folder:
        target = Path(folder) / "demos"
        code, _ = run(["scripts/make_demo.py", str(target)], ROOT, evidence / "demo-create.log")
        if code != 0:
            raise ValueError("demo creation failed")
        before = {path.name: digest(path) for path in target.glob("*.json")}
        for case in cases():
            name = case["name"]
            code, output = run(["-m", "queue_lab", str(target / (name + ".json"))], ROOT,
                               evidence / ("demo-" + name + ".json"))
            report = json.loads(output) if code in (0, 2) else {}
            expected_exit = 2 if case["expected"]["status"] == "error" else 0
            passed = code == expected_exit and report == case["expected"]
            results.append({"name": name, "exit": code, "full_expected_report_match": passed})
        code, _ = run(["scripts/make_demo.py", str(target)], ROOT, evidence / "demo-existing-refused.log")
        after = {path.name: digest(path) for path in target.glob("*.json")}
        results.append({"name": "refuse-existing-directory", "exit": code,
                        "full_expected_report_match": code == 2 and before == after})
    return results


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        return 2
    evidence = Path(args[0])
    evidence.mkdir(parents=False, exist_ok=False)
    records = {"python": sys.version.split()[0], "platform": sys.platform, "fixture_sha256": FIXTURE_SHA}
    files = sorted(path for folder in ("queue_lab", "tests", "scripts")
                   for path in (ROOT / folder).glob("*.py"))
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path.relative_to(ROOT)))
    records["syntax_files"] = len(files)
    frozen = json.loads((ROOT / "research" / "contract-freeze.json").read_text(encoding="utf-8"))
    records["contract_freeze_matches"] = all(digest(ROOT / path) == sha for path, sha in frozen["sha256"].items())
    for name, flags in (("normal", []), ("optimized", ["-O"])):
        code, _ = run([*flags, "-m", "unittest", "discover", "-s", "tests", "-v"], ROOT,
                      evidence / (name + ".log"))
        records[name + "_exit"] = code
    code, _ = run(["-m", "bandit", "-r", "queue_lab", "tests", "scripts", "-f", "json",
                   "-o", str(evidence / "bandit.json")], ROOT, evidence / "bandit-command.log")
    records["bandit_exit"] = code
    scanner = json.loads((evidence / "bandit.json").read_text(encoding="utf-8"))
    records["bandit_findings"] = len(scanner["results"])
    records["bandit_analysis_errors"] = len(scanner["errors"])
    records["bandit_narrow_skips"] = scanner["metrics"]["_totals"]["skipped_tests"]
    records["mutations"] = check_mutations(evidence)
    records["demos"] = check_demos(evidence)
    events = [("submit",i,3600000,None) for i in range(1,9)]
    events += [("start",i,3600000,None) for i in range(1,5)]
    events += [("submit",i,3600000,None) for i in range(9,65)]
    events += [("start",1,3600000,None)] * 60
    max_doc = document(events, (8,4))
    max_report = model(encode(max_doc))
    records["max_trace"] = {"events": len(events), "waiting": max_report["summary"]["waiting"],
                            "in_service": max_report["summary"]["in_service"],
                            "input_bytes": len(encode(max_doc)),
                            "report_bytes": len(render(max_report).encode()),
                            "largest_possible_report_proven": False}
    records["report_width_bound"] = bound_record()
    records["source_sha256"] = {str(path.relative_to(ROOT)).replace("\\", "/"): digest(path) for path in files}
    passed = (records["normal_exit"] == records["optimized_exit"] == records["bandit_exit"] == 0
              and records["contract_freeze_matches"] and not records["report_width_bound"]["schema_reachable_cap"]
              and records["bandit_findings"] == records["bandit_analysis_errors"] == 0
              and all(item["assertion_detected"] and item["copy_restored_original_unchanged"]
                      for item in records["mutations"])
              and all(item["full_expected_report_match"] for item in records["demos"]))
    records["status"] = "pass" if passed else "fail"
    (evidence / "results.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": records["status"], "normal_exit": records["normal_exit"],
                      "optimized_exit": records["optimized_exit"], "bandit_exit": records["bandit_exit"]}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
