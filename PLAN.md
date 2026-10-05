# Bounded-queue Admission Lab — proposed plan

Research/plan only, October5,2026;04:18 coordinator assignment under Jake's previously verified overnight mandate. **Application code requires coordinator approval of this concrete plan.** No implementation or repository is authorized by the source research. Tier3 because bounded untrusted-input admission, ownership and report integrity are consequential security/learning functionality. Sole writer in existing chat; cutoff October6 08:00 Eastern.

## Approval recorded before code —04:39

Coordinator approved stages1–4 in ../.private/coordination/2026-10-05/SUCCESSORS.md under Jake's verified direct delegated mandate. Freeze>=18 full hand reports/closed errors and lifecycle/ordinal/slot oracle before application code. Preserve positive separate waiting/service capacities, explicit starts/no auto-start, busy-before-empty, submitted ID uniqueness including rejection, matching owned completions, ties, whole structural gate, failed-start neutrality, conservation/peaks and detached snapshots. Reject native exotic types with identity comparisons before equality/hashing/iteration/serialization; add metaclass/key/subclass no-hook regressions, cycles and alias visits. Measure genuinely admitted report growth; distinguish unreachable cap seams. Normal/-O actual help/usage/report/error closed/both-failed sink evidence, four meaningful isolated assertion mutants, current-hash restoration/SAST/ECC/docs/vault required. No new repository/install/live calls/jobs/threads/services/queues/transport/effects/fairness/durability/expanded external permissions. Sole writer; root pulls completion, no reply loop.

## Problem, success criteria and recommendation

Explain finite waiting occupancy versus in-service occupancy and why taking an item frees a waiting slot without completing it. Build an original deterministic offline `queue-fifo-waiting/1` model over invented submit/start/complete events. Success: full hand-calculated reports and a separate table/ledger oracle agree with transitions; queue/slot/ownership/count invariants hold; rejected or unfinished records never silently become completed work; late invalid input returns no successful prefix; limits and sinks are checked.

Adopt/fork comparison in RESEARCH.md: CPython Queue and Janus are useful source references but implement live locking/notification/time/shutdown/aggregate task_done behavior, not this owned serial trace. Original small stdlib transitions with reviewed owned parser/CLI reuse are preferred. No third-party runtime dependency or copied candidate implementation.

FIFO selected over priority/deadline variants. FIFO ties use accepted input order; no priority selection/starvation fairness theorem. Deadlines introduce expiry equality, cancellation/generation and waiting-versus-running rules; defer them. Compared to existing labs: rate budgets govern cost units, breakers govern observed-failure/recovery gating, retry labs govern declared attempts/effects. This lab governs where admitted records occupy finite waiting/service slots.

## Scope and non-goals

One queue, positive waiting capacity Q1–8 and service slots S1–4. Capacity means waiting records only, not total unfinished records. Waiting<=Q, in_service<=S, unfinished<=Q+S. All admitted submissions enter the waiting FIFO, even when service slots are idle; no automatic dispatch/direct-to-service shortcut. Start is an explicit dequeue-and-slot-assignment event, not a real worker. Completion explicitly releases the matched model slot, not a job success/effect assertion.

No real queues/jobs/workers/threads/coroutines, producers/consumers, blocking/wakeup/transport, network/services, clocks/sleeps, retries/redelivery/idempotency/effects, failures/recovery, deadlines/priority/cancellation/eviction/shutdown, persistence/durability, authorization/authenticity or production fairness/throughput claims. Invented identifiers and source-kind are declarations, not identity/provenance proof. No package install, new repository/CI, publication, merge, deployment, new chat/subagents/scheduler or external messages.

## Exact proposed input

Root fields exactly `schema_version` (actual integer1), `source_kind` (literal `synthetic`), `profile` (`queue-fifo-waiting/1`), `queue_id` (ASCII `lab-queue-NNNN`), `policy`, `events`. Policy exactly `waiting_capacity` actual int1–8 and `service_slots` actual int1–4; no defaults/unbounded sentinel. Booleans are not integers.

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

## Independent cases to freeze before application code

Notation U(job,t)=submit, D(slot,t)=start, C(slot,job,t)=complete. Event IDs distinct; all Q/S values supplied. These are proposed expectations, not executed checks. Stage1 must expand **full inputs and complete row/snapshot/count reports**, seal hashes and freeze SCHEMA/status/errors before production code.

| Case | Script | Expected key outcome |
| --- | --- | --- |
| Empty | Q1,S1; no events | All counts0, empty occupancy, null time |
| Finite waiting/no auto-start | Q1,S1; U1@0,U2@0 | Admit1/reject2 despite idle slot; waiting1/in_service0/completions0 |
| Dequeue frees waiting, not unfinished | Q1,S1; U1,D1,U2 at0 | Two admitted; waiting2's ID/in_service1's ID; unfinished2>Q; completed0 |
| FIFO differs from sorted IDs | Q3,S1; U3,U1,U2,D1 at0 | Start3, waiting[1,2] |
| Busy start preserves head | Q2,S1; U1,D1,U2,D1 at0 | Last busy no_start; waiting[2], slot1 owns1, started1 |
| Empty start | Q1,S1; D1@0 | queue_empty, null result job, empty slot |
| Busy precedes empty | Q1,S1; U1,D1,D1 at0 | service_slot_busy, not queue_empty |
| No auto-start on complete | Q1,S1; U1,D1,U2,C(1,1) at0 | waiting[2], empty slot, completions1; must explicitly D1 to start2 |
| Two slots/out-of-order complete | Q2,S2; U1,U2,D2,D1,C(1,2) at0 | Start1 in slot2 then2 in slot1; completing2 legal; slot2 still owns1 |
| Same-time capacity tie | Q1,S1; U1,U2,D1 versus U1,D1,U2 | First rejects2/unfinished1; second admits2/unfinished2 |
| Same-time slot tie | Q1,S1; U1,D1,U2,D1,C(1,1) versus U1,D1,U2,C(1,1),D1 | First busy preserves2 waiting; second starts2 |
| Rejected completion | Q1,S1; U1,U2,D1,C(1,2) | trace.invalid, no report |
| Queued completion | Q1,S1; U1,C(1,1) | trace.invalid |
| Wrong/empty-slot completion | Q1,S2; U1,D1,C(2,1) | trace.invalid |
| Duplicate/unknown completion | U1,D1,C(1,1),C(1,1); standalone unknown C | trace.invalid |
| Slot reuse | Q1,S1; U1,D1,C(1,1),U2,D1,C(1,2) | Two legal starts/completions; unfinished0; old C(1,1) would fail |
| Pending with large time jump | Q1,S1; U1@0,D1@0,D1@3600000 | Busy no_start; job remains in-service, no inferred outcome |
| Structural precedence | early unknown completion plus late extra field | schema.invalid before replay; no partial rows |

Also test every bound at/over, max Q/S occupancy simultaneously,64th/65th submission/start/completion,128th/129th event, empty/missing/null/extras/duplicate IDs/decoded keys, bool/float/nonfinite/numeric/string/depth/node/Unicode gates, invalid slot range, backwards time, input immutability/frozen records/snapshot independence, repeated deterministic model, exact large-fit labels and failed/closed/help/error channels. Job IDs used by denied submits remain unavailable for resubmission.

Separate oracle after contract seal: declarative job lifecycle ledger (absent->waiting->service(slot)->completed), enqueue ordinal ranks and slot ownership; next job chosen by minimum admitted waiting ordinal, not production FIFO/container helpers. Enumerate short traces over submit/start/complete patterns at Q1/2,S1/2 with legal/illegal ownership and compare full states/decisions/counts. No production imports; hand fixtures remain an additional independent representation. Finite evidence, not formal proof.

Target four isolated semantic mutants: use waiting+in_service for waiting-capacity denial; take newest rather than oldest FIFO record; treat start as completion/clear unfinished; allow mismatched completion slot/job. Each must have a meaningful assertion against frozen exact reports, not crash-only detection; preserve original hashes and report any additional mutant errors honestly. Failed-start-preserves-head and no-auto-start invariants must be checked even if not selected as a fifth mutant.

## Stages and definitions of done

1. **Approval/contract freeze:** record coordinator addendum in STATE/PLAN; freeze SCHEMA/status/error precedence and at least the18 full hand cases/hashes before production code. Explain waiting versus unfinished lesson; no approval means no code.
2. **Pure model:** bounded native/byte gate, immutable owned records and FIFO/service transitions; hand/table oracles, ownership/invariants/ties/neutral rejected states, no caller mutation. No live queue package.
3. **CLI/verification:** checked file/sinks/demos and reusable fresh evidence script. Run normal/-O, actual/simulated failed sinks, late-error/no-prefix, bounds/max-cardinality-fit and four restored isolated assertion mutants. Use installed Python3.13.7/Bandit only, no installs; preserve first failures.
4. **Review/handoff:** ECC actual-source self-review/SAST, fixes/affected checks, exact receipts/hygiene; README/MIT/owned attribution/AI disclosure/security/limitations/learning/STATE/DECISIONS/vault. No repository/CI/hosted external action. Linux/other runtimes/formal proof/actual workload effects remain unverified unless separately executed/authorized.

Worker plan: local Ollama supplied one bounded draft, reviewed/corrected, raw preserved. Remaining contract/source/security judgment stays Codex. Free OpenRouter public drafts considered but unnecessary; no remote call/price probe or fallback. Laya schemas unsuitable. No application/tests/bounds-fit/CodeQL/ECC implementation verdict exists during research. Next: coordinator reviews this concrete proposal; continue only approved stages afterward.
