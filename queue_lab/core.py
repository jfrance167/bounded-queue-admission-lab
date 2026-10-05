"""Pure bounded FIFO/slot occupancy; completion is a declared model event."""

from dataclasses import dataclass
import json
import re

from .admission import LabError, MAX_OUTPUT, check_tree, parse

PROFILE = "queue-fifo-waiting/1"
FIELDS = ("events", "submissions", "admitted", "rejected", "start_requests", "started",
          "not_started", "busy_not_started", "empty_not_started", "completions", "waiting",
          "in_service", "unfinished", "peak_waiting", "peak_in_service", "peak_unfinished")
LABELS = {kind: re.compile("lab-" + kind + r"-[0-9]{4}", re.ASCII)
          for kind in ("queue", "event", "job")}


@dataclass(frozen=True)
class Policy:
    waiting_capacity: int
    service_slots: int


@dataclass(frozen=True)
class Event:
    event_id: str
    kind: str
    time_ms: int
    job_id: str | None
    slot_id: int | None


@dataclass(frozen=True)
class Trace:
    queue_id: str
    policy: Policy
    events: tuple[Event, ...]


@dataclass(frozen=True)
class Job:
    job_id: str
    enqueued_at_ms: int


@dataclass(frozen=True)
class Active:
    job: Job
    started_at_ms: int


def _shape(value, names):
    if type(value) is not dict or set(value) != set(names):
        raise LabError("schema.invalid")


def _integer(value, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise LabError("schema.invalid")
    return value


def _enum(value, values):
    if type(value) is not str or value not in values:
        raise LabError("schema.invalid")
    return value


def _label(value, kind):
    if type(value) is not str or LABELS[kind].fullmatch(value) is None:
        raise LabError("schema.invalid")
    return value


def _validate(document):
    """Internal: exact bounded tree gate precedes all structural checks."""
    _shape(document, ("schema_version", "source_kind", "profile", "queue_id", "policy", "events"))
    _integer(document["schema_version"], 1, 1)
    _enum(document["source_kind"], {"synthetic"})
    _enum(document["profile"], {PROFILE})
    identifier = _label(document["queue_id"], "queue")
    settings = document["policy"]
    _shape(settings, ("waiting_capacity", "service_slots"))
    policy = Policy(_integer(settings["waiting_capacity"], 1, 8),
                    _integer(settings["service_slots"], 1, 4))
    events = document["events"]
    if type(events) is not list:
        raise LabError("schema.invalid")
    if len(events) > 128:
        raise LabError("input.limit")
    seen_events, seen_jobs, records = set(), set(), []
    totals, previous = dict.fromkeys(("submit", "start", "complete"), 0), 0
    for row in events:
        if type(row) is not dict:
            raise LabError("schema.invalid")
        kind = _enum(row.get("kind"), totals)
        names = ("event_id", "kind", "time_ms")
        _shape(row, names + (("job_id",) if kind == "submit" else
                            (("slot_id",) if kind == "start" else ("slot_id", "job_id"))))
        event_id = _label(row["event_id"], "event")
        timestamp = _integer(row["time_ms"], 0, 3_600_000)
        if event_id in seen_events or timestamp < previous:
            raise LabError("schema.invalid")
        seen_events.add(event_id)
        previous = timestamp
        totals[kind] += 1
        if totals[kind] > 64:
            raise LabError("input.limit")
        job = _label(row["job_id"], "job") if kind != "start" else None
        slot = _integer(row["slot_id"], 1, policy.service_slots) if kind != "submit" else None
        if kind == "submit":
            if job in seen_jobs:
                raise LabError("schema.invalid")
            seen_jobs.add(job)
        records.append(Event(event_id, kind, timestamp, job, slot))
    return Trace(identifier, policy, tuple(records))


def _snapshot(waiting, slots, last):
    return {"waiting": [{"job_id": job.job_id, "enqueued_at_ms": job.enqueued_at_ms} for job in waiting],
            "in_service": [{"slot_id": slot, "job_id": active.job.job_id,
                            "enqueued_at_ms": active.job.enqueued_at_ms,
                            "started_at_ms": active.started_at_ms} for slot, active in sorted(slots.items())],
            "waiting_count": len(waiting), "in_service_count": len(slots),
            "unfinished_count": len(waiting) + len(slots), "last_event_time_ms": last}


def _apply(event, policy, waiting, slots, count):
    if event.kind == "submit":
        count["submissions"] += 1
        if len(waiting) >= policy.waiting_capacity:
            count["rejected"] += 1
            return "rejected", "waiting_full", event.job_id
        waiting.append(Job(event.job_id, event.time_ms))
        count["admitted"] += 1
        return "accepted", "waiting_slot_available", event.job_id
    if event.kind == "start":
        count["start_requests"] += 1
        if event.slot_id in slots:
            count["not_started"] += 1
            count["busy_not_started"] += 1
            return "not_started", "service_slot_busy", None
        if not waiting:
            count["not_started"] += 1
            count["empty_not_started"] += 1
            return "not_started", "queue_empty", None
        job = waiting.pop(0)
        slots[event.slot_id] = Active(job, event.time_ms)
        count["started"] += 1
        return "started", "fifo_head", job.job_id
    owned = slots.get(event.slot_id)
    if owned is None or owned.job.job_id != event.job_id:
        raise LabError("trace.invalid")
    del slots[event.slot_id]
    count["completions"] += 1
    return "completed", "owned_completion", event.job_id


def _simulate(trace):
    waiting, slots, rows, last = [], {}, [], None
    count = dict.fromkeys(FIELDS, 0)
    for event in trace.events:
        before = _snapshot(waiting, slots, last)
        decision, reason, job = _apply(event, trace.policy, waiting, slots, count)
        last = event.time_ms
        count["events"] += 1
        after = _snapshot(waiting, slots, last)
        for name, value in (("waiting", len(waiting)), ("in_service", len(slots)),
                            ("unfinished", len(waiting) + len(slots))):
            count[name] = value
            count["peak_" + name] = max(count["peak_" + name], value)
        rows.append({"event_id": event.event_id, "kind": event.kind, "time_ms": event.time_ms,
                     "result": {"decision": decision, "reason": reason, "job_id": job, "slot_id": event.slot_id},
                     "before": before, "after": after})
    report = {"schema_version": 1, "source_kind": "synthetic", "profile": PROFILE, "queue_id": trace.queue_id,
              "policy": {"waiting_capacity": trace.policy.waiting_capacity, "service_slots": trace.policy.service_slots},
              "status": "modeled", "effects": "unmodeled", "actual_execution": "unverified",
              "rows": rows, "summary": count, "final_state": _snapshot(waiting, slots, last)}
    render(report)  # Size bound covers native/bytes callers before returning.
    return report


def model(raw: bytes) -> dict:
    """Admit bytes and validate the whole trace before returning a full model."""
    return _simulate(_validate(parse(raw)))


def model_document(document) -> dict:
    """Bound exact builtin trees before serialization; do not mutate callers.

    No custom class/key hooks. Cycles reject; aliases count per visit. Native
    allocations and concurrent mutation are not isolated.
    """
    check_tree(document)
    raw = json.dumps(document, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return model(raw)


def render(report: dict) -> str:
    """Serialize internally produced reports with a defensive fixed byte cap."""
    output = json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    if len(output.encode("utf-8")) > MAX_OUTPUT:
        raise LabError("output.error")
    return output
