"""Repeatable conservative report-width calculation for the frozen schema.

Usage: python scripts/report_bound.py FRESH_JSON. No input trace is executed.
The impossible envelope widens each field independently, not joint state laws.
See VERIFICATION.md; changing schema/enums/caps requires reviewing this bound.
"""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from queue_lab import render  # noqa: E402
from queue_lab.admission import MAX_OUTPUT  # noqa: E402
from queue_lab.core import FIELDS  # noqa: E402


def bound_record():
    """Return byte envelope for exact owned report fields; not arbitrary trees."""
    snapshot = {"waiting": [{"job_id": "lab-job-9999", "enqueued_at_ms": 3600000} for _ in range(8)],
                "in_service": [{"slot_id": 4, "job_id": "lab-job-9999", "enqueued_at_ms": 3600000,
                                "started_at_ms": 3600000} for _ in range(4)],
                "waiting_count": 8, "in_service_count": 4, "unfinished_count": 12, "last_event_time_ms": 3600000}
    row = {"event_id": "lab-event-9999", "kind": "complete", "time_ms": 3600000,
           "result": {"decision": "not_started", "reason": "waiting_slot_available",
                      "job_id": "lab-job-9999", "slot_id": None}, "before": snapshot, "after": snapshot}
    report = {"schema_version": 1, "source_kind": "synthetic", "profile": "queue-fifo-waiting/1",
              "queue_id": "lab-queue-9999", "policy": {"waiting_capacity": 8, "service_slots": 4},
              "status": "modeled", "effects": "unmodeled", "actual_execution": "unverified",
              "rows": [row] * 128, "summary": dict.fromkeys(FIELDS, 128), "final_state": snapshot}
    size = len(render(report).encode("utf-8"))
    return {"overapproximation_report_bytes": size, "output_cap": MAX_OUTPUT,
            "schema_reachable_cap": size > MAX_OUTPUT, "admitted_trace": False,
            "assumptions": "Frozen exact fields;128 rows;8 waiting/4 service;7-digit times;fixed ASCII labels;"
                           "longest enums independently;null slot spelling;all counters3 digits."
                           "Joint state/result is deliberately impossible;not an arbitrary-render-tree bound."}


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        return 2
    try:
        record = bound_record()
        with Path(args[0]).open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(record, indent=2) + "\n")
    except (OSError, ValueError):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
