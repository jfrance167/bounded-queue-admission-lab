# Bounded-queue Admission Lab

An offline Python teaching model for finite FIFO waiting capacity and separately owned service slots. Invented submit/start/complete records produce admission decisions, before/after snapshots, occupancy peaks and reconciled counters. No real queues, jobs, workers, threads, clocks or services are executed.

The lesson: **removing an item frees waiting capacity without completing it**. Waiting records and in-service records both remain unfinished. FIFO chooses which job starts; separate slots may complete in a different order.

## Run

Run from this directory with Python3.11 or newer; verified here on Windows CPython3.13.7. The application uses only standard-library modules. Create a fresh demo directory:

```powershell
python scripts/make_demo.py demos
python -m queue_lab demos/dequeue-not-complete.json
```

The generator creates21 invented inputs and refuses existing destinations. It generates data; `queue_lab` performs the model replay. In this demo Q1/S1: submit1 waits, start1 assigns job1 to slot1, then submit2 can wait while job1 remains unfinished. Final waiting1/in_service1/unfinished2/completions0 is valid even though unfinished exceeds waiting capacity1.

Exit0 means a complete model, including valid rejected submissions, unsuccessful starts and unfinished records. Exit2 means an error; stderr contains a fixed JSON code. Late invalid structure or ownership produces no successful report prefix. Output delivery remains nontransactional and can fail/partially write.

## Selected profile

`queue-fifo-waiting/1` has one queue, positive waiting capacity1–8 and service slots1–4. All admitted submissions join waiting FIFO, even with idle slots. Starts and completions are explicit; no auto-start or direct dispatch. Nonpositive limits are invalid rather than Python Queue's unbounded sentinel.

| Event | Decision | Modeled occupancy |
| --- | --- | --- |
| Submit with waiting room | accepted | Append job/enqueue time |
| Submit to full waiting list | rejected | Preserve all occupancy |
| Start on occupied slot | not_started/service_slot_busy | Preserve head and slot; takes precedence over empty waiting |
| Start on free slot with empty FIFO | not_started/queue_empty | Create no work |
| Start on free slot with waiting job | started/fifo_head | Move oldest accepted job into requested slot |
| Complete matching in-service job/slot | completed/owned_completion | Release only that slot |
| Complete queued/rejected/unknown/wrong-slot/already completed job | trace.invalid | Discard whole provisional model |

Submission IDs are globally unique even when rejected or already completed. Times are nondecreasing exact integer milliseconds; ties follow array order. Time jumps cause no scheduling/expiry. Final pending records remain unfinished. Completion is a supplied model declaration, not proof of success or actual work. Reports label effects `unmodeled` and actual_execution `unverified`.

## Architecture/API

`admission.py`: bounded raw/lexical JSON and exact builtin native-tree gates. `core.py`: whole structural validation into frozen policy/event/job records, fresh bounded waiting/slot state, owned transitions, independent snapshots and checked report size. `__main__.py`: regular-file input and checked help/report/error sinks. [SCHEMA.md](SCHEMA.md) is the frozen field/status/error contract.

```python
from queue_lab import model, model_document, render
from queue_lab.admission import LabError

report = model(raw)  # raw: UTF-8 JSON bytes matching SCHEMA.md
text = render(report)
# model_document(document) admits exact builtin JSON trees instead.
```

Native checks use identity before class equality/hash/iteration/serialization. Custom metaclasses, key subclasses and conversion hooks are rejected without being called. Cycles reject and acyclic aliases count on every visit. Caller inputs and snapshots are independent; concurrent caller mutation is unsupported. `render` expects internal reports and is not an arbitrary-object admission API.

## Verification and reusable tools

```powershell
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
# Requires already installed Bandit; evidence destination must be fresh.
python scripts/verify.py docs/verification/my-run
# Write a fresh report-width record; no trace or real queue executes.
python scripts/report_bound.py docs/verification/my-width.json
```

Verified October5,2026:31 normal and optimized tests;21 full pre-code hand cases;1,024 independent lifecycle/rank/slot traces; four assertion-detected isolated mutants with original source unchanged;21 exact CLI demo reports/errors; zero Bandit findings/errors with seven narrow harness subprocess annotations. Actual help/usage/report/error closed/both-failed pipe paths run in each mode. [VERIFICATION.md](VERIFICATION.md) records precise evidence and limitations; [REVIEW.md](REVIEW.md) records ECC self-review.

Raw input<=65,536 bytes, depth8, encoded string body128 bytes, integer spelling16 characters, arrays128, total keys1,024, visits4,096; trace<=128 events and64 submissions/starts/completions; occupancy<=8 waiting+4 in-service. Report cap262,144 bytes. A genuine128-event full-occupancy report is235,925 bytes; a conservative frozen-field width envelope is250,007 bytes. That envelope combines impossible independent maxima, not an admitted trace or exact worst-case report. The fixed cap is defensive for this schema; reduced-cap/arbitrary-tree tests are explicitly injected seams.

Postdecode cardinality gates do not prevent decoder allocation. Limits do not guarantee CPU/RSS/I/O deadlines, file-race isolation or safe hostile evidence handling. No concurrency, live backpressure transport, fairness, authentication, durability, retry/idempotency/effect or actual completion guarantee. Linux/other runtimes/hosted CI/CodeQL/types/dedicated lint were not run. See [SECURITY.md](SECURITY.md).

## Attribution and learning

Original transitions, MIT licensed. Parser/CLI/verifier patterns adapted from Jake's reviewed structured-log/rate/circuit labs (MIT), with identity-only native checks and current profile adaptations. CPython/Janus were researched, not copied, installed or executed; actual pinned code/tests/licenses/dependencies/CI and source limits are in [RESEARCH.md](RESEARCH.md). Their live transport/task-counter contracts differ from explicit slot ownership. Research-stage wording is historical; current completion is in [STATE.md](STATE.md).

AI assistance: Codex researched, implemented, verified and self-reviewed. Local Ollama supplied short comparison/usage drafts; inaccurate completion/starvation/async and generator-execution language was corrected, exact usage commands supplied from actual code. Raw drafts are retained separately. No remote drafting inference/spending; narrow installed ECC skills used, full native ECC plugin uninstalled. Self-review is not independent review.

Exercise: with Q1/S1, compare submit1,submit2,start1 against submit1,start1,submit2 at the same timestamp. [LEARNING.md](LEARNING.md) explains the result. Local stages1–4 are complete; no repository/publication/deployment was created.

## Publication status

See [publication review](PUBLICATION.md) for the October 5 source snapshot, fresh local checks, evidence boundaries and current hosted-check distinction.
