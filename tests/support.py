"""Pre-application sealed hand reports and independent lifecycle/rank oracle."""

import copy
import hashlib
import json
from pathlib import Path

FIXTURE_SHA = "ccf24c69ba586f5e340667a4b7c41d4e27aaa758037d12a59e4f710ad5644787"
FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "cases.json"
FIELDS = ("events", "submissions", "admitted", "rejected", "start_requests", "started",
          "not_started", "busy_not_started", "empty_not_started", "completions", "waiting",
          "in_service", "unfinished", "peak_waiting", "peak_in_service", "peak_unfinished")


def cases():
    raw = FIXTURE_PATH.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SHA:
        raise ValueError("frozen fixture mismatch")
    return json.loads(raw)["cases"]


def document(events=(("submit", 1, 0, None),), policy=(1, 1)):
    doc = {"schema_version": 1, "source_kind": "synthetic", "profile": "queue-fifo-waiting/1",
           "queue_id": "lab-queue-0001", "policy": dict(zip(
               ("waiting_capacity", "service_slots"), policy, strict=True)), "events": []}
    for index, (kind, target, timestamp, completed_job) in enumerate(events):
        row = {"event_id": f"lab-event-{index:04d}", "kind": kind, "time_ms": timestamp}
        row["job_id" if kind == "submit" else "slot_id"] = (
            f"lab-job-{target:04d}" if kind == "submit" else target)
        if kind == "complete":
            row["job_id"] = f"lab-job-{completed_job:04d}"
        doc["events"].append(row)
    return doc


def encode(doc):
    return json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def ledger_oracle(doc):
    """Independent admitted-structure oracle; lifecycle ledger + ordinal min.

    No production imports or FIFO mutation helper. Structural checks belong to
    separate tests; this oracle returns full reports or a closed ownership error.
    """
    ledger, rows, last = {}, [], None
    count = dict.fromkeys(FIELDS, 0)
    policy = doc["policy"]

    def snapshot():
        queued = sorted((row for row in ledger.values() if row["phase"] == "waiting"),
                        key=lambda row: row["ordinal"])
        active = sorted((row for row in ledger.values() if row["phase"] == "service"),
                        key=lambda row: row["slot"])
        return {"waiting": [{"job_id": row["id"], "enqueued_at_ms": row["enqueue"]} for row in queued],
                "in_service": [{"slot_id": row["slot"], "job_id": row["id"],
                                "enqueued_at_ms": row["enqueue"], "started_at_ms": row["start"]}
                               for row in active],
                "waiting_count": len(queued), "in_service_count": len(active),
                "unfinished_count": len(queued) + len(active), "last_event_time_ms": last}

    for ordinal, event in enumerate(doc["events"]):
        before = snapshot()
        kind, timestamp = event["kind"], event["time_ms"]
        slot = event.get("slot_id")
        identifier = event.get("job_id")
        if kind == "submit":
            count["submissions"] += 1
            accepted = before["waiting_count"] != policy["waiting_capacity"]
            ledger[identifier] = {"phase": "waiting" if accepted else "rejected", "id": identifier,
                                  "ordinal": ordinal, "enqueue": timestamp, "slot": None, "start": None}
            count["admitted" if accepted else "rejected"] += 1
            decision, reason = (("accepted", "waiting_slot_available") if accepted
                                else ("rejected", "waiting_full"))
        elif kind == "start":
            count["start_requests"] += 1
            occupied = any(row["phase"] == "service" and row["slot"] == slot for row in ledger.values())
            waiting = [row for row in ledger.values() if row["phase"] == "waiting"]
            if occupied or not waiting:
                identifier = None
                count["not_started"] += 1
                count["busy_not_started" if occupied else "empty_not_started"] += 1
                decision, reason = "not_started", "service_slot_busy" if occupied else "queue_empty"
            else:
                chosen = min(waiting, key=lambda row: row["ordinal"])
                chosen.update(phase="service", slot=slot, start=timestamp)
                identifier = chosen["id"]
                count["started"] += 1
                decision, reason = "started", "fifo_head"
        else:
            owned = ledger.get(identifier)
            if owned is None or owned["phase"] != "service" or owned["slot"] != slot:
                return {"status": "error", "code": "trace.invalid"}
            owned["phase"] = "completed"
            count["completions"] += 1
            decision, reason = "completed", "owned_completion"
        count["events"] += 1
        last = timestamp
        after = snapshot()
        for name, value in (("waiting", after["waiting_count"]), ("in_service", after["in_service_count"]),
                            ("unfinished", after["unfinished_count"])):
            count[name] = value
            count["peak_" + name] = max(count["peak_" + name], value)
        rows.append({"event_id": event["event_id"], "kind": kind, "time_ms": timestamp,
                     "result": {"decision": decision, "reason": reason, "job_id": identifier, "slot_id": slot},
                     "before": before, "after": after})
    report = {key: copy.deepcopy(value) for key, value in doc.items() if key != "events"}
    report.update(status="modeled", effects="unmodeled", actual_execution="unverified",
                  rows=rows, summary=count, final_state=snapshot())
    return report
