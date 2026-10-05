# Frozen schema and report contract

Frozen after04:39 approval before application code. Proposed-wording headings below retain the reviewed plan text; this is the selected implementation contract.

## Exact proposed input

Root fields exactly `schema_version` (actual integer1), `source_kind` (literal `synthetic`), `profile` (`queue-fifo-waiting/1`), `queue_id` (ASCII `lab-queue-NNNN`), `policy`, `events`. Policy exactly `waiting_capacity` actual int1â€“8 and `service_slots` actual int1â€“4; no defaults/unbounded sentinel. Booleans are not integers.

Each event has unique ASCII `event_id:lab-event-NNNN`, actual integer `time_ms:0..3600000`, literal `kind` and exact kind-specific fields:

- `submit`: `job_id:lab-job-NNNN` required; unique across all submissions, including rejected ones. No slot/outcome field.
- `start`: actual integer `slot_id:1..S` required; no job_id/outcome supplied. The model chooses FIFO head only on a valid start.
- `complete`: `slot_id:1..S` and `job_id:lab-job-NNNN` required. They must match the currently assigned in-service record; no outcome field.

At most128 events and64 submissions,64 start requests,64 completions (shared event cap still applies). Times globally nondecreasing; array order resolves ties, no sorting or clock advancement. Empty events valid with all initial counts zero/null last time. Duplicate event IDs/submission IDs, extra/missing/null/type/version/profile/Unicode-label failures invalidate structure even behind a would-be rejected event.

All byte/tree/schema/time/ID/cardinality structure validates first into immutable admitted records. Then replay the entire trace and size-check the report. Wrong ownership errors are semantic; a later structural error is caught before an earlier semantic error. First failing gate determines closed error code, not exhaustive classification.

## Transition and ownership rules

Initial waiting FIFO empty; S service slots empty; no completed/rejected effect inference; last_event_time null.

| Event | Predicate in order | Decision/reason | Mutation of modeled occupancy |
| --- | --- | --- | --- |
| Submit | waiting count<Q | accepted / waiting_slot_available | Append owned immutable job/enqueued time; do not start it |
| Submit | waiting count>=Q | rejected / waiting_full | No waiting/service/completion change; submission ID remains globally used |
| Start | requested slot occupied | not_started / service_slot_busy | Preserve head and every slot; takes precedence over queue_empty |
| Start | requested slot free and FIFO empty | not_started / queue_empty | No record created; requested slot remains free |
| Start | requested slot free and FIFO nonempty | started / fifo_head | Remove oldest admitted waiting job; assign same record plus start time to requested slot |
| Complete | slot contains exactly the supplied job ID | completed / owned_completion | Release only that slot; no automatic next start |
| Complete | empty/wrong slot or queued/rejected/unknown/already completed job | whole-trace trace.invalid | Return no provisional model |

Service slots may complete out of FIFO order: FIFO governs start selection, not completion order. Slots may be reused after completion. Submissions never reuse a job ID, so old completions cannot match new generations. Rejected submissions cannot be started/completed; busy/empty starts do not reserve work. Time alone causes no occupancy changes. Final waiting and in-service records remain unfinished, never timed out/failed/succeeded by inference.

Same-time examples differ by order: dequeue then submit can free waiting capacity; submit then dequeue can reject that submission. Complete then start can reuse a service slot; start then complete yields busy not_started first. Filling waiting while service slots are idle is valid and can still reject because starts are explicit.

## Exact proposed report/status

Root: schema_version/source_kind/profile/queue_id/fresh policy, `status:modeled`, `effects:unmodeled`, `actual_execution:unverified`, `rows`, `summary`, `final_state`.

Each row exactly event_id/kind/time_ms, `result`, `before`, `after`. Result exactly decision/reason/job_id/slot_id. Submit result carries supplied ID and null slot, including rejection. Start result carries requested slot and selected job ID only when started; not_started has null job. Complete result carries matching job/slot. Decisions/reasons are the closed table above, no raw payload/outcome exception or universal safe verdict.

Snapshots exactly `waiting` (FIFO list of fresh `{job_id,enqueued_at_ms}`), `in_service` (list sorted by slot_id of fresh `{slot_id,job_id,enqueued_at_ms,started_at_ms}`), `waiting_count`, `in_service_count`, `unfinished_count`, `last_event_time_ms`. Before uses preceding event time/null initially; after uses current time including rejected/not_started events. No object sharing with caller inputs or across snapshots/model runs.

Summary exactly events/submissions/admitted/rejected/start_requests/started/not_started/busy_not_started/empty_not_started/completions/waiting/in_service/unfinished/peak_waiting/peak_in_service/peak_unfinished. Peaks observed after every event, initial0, and do not count rejected submissions or busy/empty starts. Reconcile:

- events=submissions+start_requests+completions;
- submissions=admitted+rejected;
- start_requests=started+not_started; not_started=busy_not_started+empty_not_started;
- admitted=started+waiting; started=completions+in_service;
- admitted=completions+unfinished; unfinished=waiting+in_service.

Proposed CLI `python -m queue_lab FILE`:0 for valid full model (rejections/not-started/unfinished included);2 for errors. Successful JSON stdout; closed stderr JSON `{status:error,code:...}`. No successful prefix for late structure/semantic errors. Codes arguments.invalid, input.io/encoding/invalid_json/number/duplicate/limit, schema.invalid, trace.invalid, output.error, internal.error. Help uses checked emission/flush. Fixed diagnostics reflect no raw source/path/argv/exception. Error sink can fail; both dirty failed streams must retain exit2 at shutdown. Output is nontransactional.

## Architecture, boundaries and threat model

After approval reuse/adapt the reviewed owned circuit/rate/structured gate patterns with MIT attribution: fixed byte/lexical gates and strict stdlib JSON syntax; exact bounded native-tree gate; full structural validation into frozen policy/event/job records; fresh waiting FIFO and bounded slot map; pure transitions and independent snapshots; full report render cap; small regular-file CLI. A bounded list/deque is an internal representation, not a live queue service. Public proposed model(bytes)/model_document(exact builtin JSON tree)/render(internal report).

Raw input<=65536 bytes; depth8; encoded string body128 bytes; integer spelling16 characters preconversion; arrays128; total keys1024; tree visits4096 including keys/repeated acyclic aliases. Native gate accepts only exact dict/list/str/int/bool/None with exact string keys; rejects cycles/custom types/hooks/floats/nonfinite/surrogates before canonical serialization. Bound huge ints before text conversion; aliases count per visit. Caller input unchanged; concurrent caller mutation unsupported. Postdecode cardinality gates are not preallocation guarantees.

Trace cardinality above bounds seen-ID/history/report work; retained occupancy<=12 records and no elapsed-time loop. Output<=262144 UTF-8 bytes, reject rather than truncate. Checked regular descriptor/file read cap+1; path races/blocking/allocation/CPU/RSS/native caller/same-user/OS containment and transactional output are not guaranteed. Report-fit/max-cardinality and defensive unreachable render guards must be labeled accurately after testing.

Threats: resource amplification/custom native hooks, bool-int confusion, completion laundering to rejected/waiting/other-slot IDs, FIFO corruption on failed starts, accidental direct dispatch/auto-start, conflating waiting with unfinished capacity, same-time reorder, late-invalid partial success, reflected diagnostics and false effect/throughput claims. Mitigate explicit schema, bounded tree/owned records, exact predicates/ties/identity, all-or-nothing model construction, independent expected reports/ledger/mutations, checked sinks and truthful labels. Trust supplied synthetic observations only as model declarations; no authentication or actual completion truth.


## Frozen hand expectations

21 complete input/report-or-error cases, SHA256 ccf24c69ba586f5e340667a4b7c41d4e27aaa758037d12a59e4f710ad5644787. Expanded only from manually declared rows/states/counts in .drafts/hand-cases.json; formatter projects labels/fields and derives occupancy lengths, not admission or transition decisions. No application code was present. Tests and demos must verify fixture bytes.
