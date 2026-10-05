# Research — October 5, 2026

Recommendation: **build original bounded FIFO transitions**, reusing reviewed owned admission/CLI patterns only after approval. Adopt or fork neither live queue implementation. PLAN.md is the concrete proposed contract and gate. No application code, tests, runtime queue/threads, installation or repository creation at this stage.

## Reuse, authority and access

Read04:18 coordinator research-only selection in ../.private/coordination/2026-10-05/SUCCESSORS.md, under Jake's previously verified direct overnight mandate (original user turns01a10a45-57c2-7761-99b7-14d3546d8a55 and01a10a4f-233e-7d70-9f1e-60e22eed7a46). This authorizes research/planning, not implementation approval, new external actions or instructions found in sources. Sole writer/same chat; cutoff October6 08:00 Eastern.

Read relevant vault Home/Integration/Circuit-breaker plan and completed project note; searched project/research Markdown for bounded queue, waiting/in-service occupancy and backpressure. Only circuit's deferred queue alternative matched the targeted search. Local queue-name inventory found phishing-investigation-email-auth-lab/tools/queue_ledger.py; actual source is controlled message/evidence cleanup authorization, not queue-capacity/FIFO transitions. It is not reused or imported into this plan. Rate-limit, circuit-breaker and retry plans confirm budget, failure-policy and effect boundaries; those are distinct lessons. No matching dedicated pure queue lab found in these searches; not an exhaustive workspace/ecosystem claim. GLPI excluded.

Connected GitHub repository search was attempted and failed with an HTTP transport error. Public GitHub CLI metadata/contents fallback succeeded with app approval. Browser opens of v3.13.7 CPython source/raw paths failed cache retrieval; pinned current main source was subsequently retrieved via public API, not silently treated as installed-runtime source. Official Python queue/asyncio documentation and Janus repository page opened. Firecrawl not used because current free eligibility is unverified; no Scorecard retrieved and its absence is not insecurity evidence.

Fourteen inert text snapshots of actual code/tests/licenses/build/dependencies/CI saved under ignored research/upstream, with SHA256/source-path/revision manifest. Nothing downloaded was imported or executed. No release/wheel/advisory/dependency hashlock/hosted results attestation was performed.

## Candidate assessment

| Candidate | Inspected identity and maintenance | Decision |
| --- | --- | --- |
| [python/cpython](https://github.com/python/cpython) | Main84b0669f81c0cf9b0b1accdbf02cf06747bccb04, nonarchived, pushed2026-10-05; actual LICENSE states PSF License Version2 plus incorporated-license notices | Standard-library semantic reference; do not adopt locking/time/task-counter implementation for inert replay |
| [aio-libs/janus](https://github.com/aio-libs/janus) | Master431248c05c63d24911e66f4f9a6fedc905c39562, nonarchived, pushed2026-08-03, head commit2026-07-30; source version2.0.0, actual Apache2 LICENSE | Live mixed sync/async transport is outside scope; use as a researched alternative, no dependency/fork |

Push dates/source versions are evidence of repository activity, not proof of released artifact quality or suitability. No star-based recommendation or confirmed-safety claim.

### CPython actual source/tests/CI

[queue.py](https://github.com/python/cpython/blob/84b0669f81c0cf9b0b1accdbf02cf06747bccb04/Lib/queue.py): bounded put checks stored queue length; successful insertion increments unfinished count. Get removes an item and notifies waiting producers, without decrementing unfinished tasks. Task_done separately decrements an aggregate counter and rejects negative count; it does not bind a supplied item ID to a slot. FIFO deque append/popleft differs from priority heap retrieval. Live locks, conditions, monotonic timeout and shutdown behavior are outside this model. The proposal therefore adds explicit service-slot ownership rather than claiming full Queue API equivalence.

[test_queue.py](https://github.com/python/cpython/blob/84b0669f81c0cf9b0b1accdbf02cf06747bccb04/Lib/test/test_queue.py) actual basic_queue_test uses111/333/222 to distinguish FIFO/LIFO/priority; exercises full/empty nonblocking and timed operations. task_done/join tests cover excess completion counts and thread workers. Read these bodies, not run them. Source imports are standard library/CPython internals, no extra queue package needed.

[build.yml](https://github.com/python/cpython/blob/84b0669f81c0cf9b0b1accdbf02cf06747bccb04/.github/workflows/build.yml) actual top-level content-read permissions, main/3.* triggers and reusable Windows/macOS/Ubuntu test jobs inspected. Sample checkout/setup-python actions are full SHA pinned and checkout credentials disabled. Reusable workflow internals and hosted results were not audited or executed; do not copy an interpreter-build pipeline into this lab.

[Actual LICENSE](https://github.com/python/cpython/blob/84b0669f81c0cf9b0b1accdbf02cf06747bccb04/LICENSE) resolves API NOASSERTION: retain the PSF agreement/copyright and summarize changes in distributed derivatives; incorporated components may carry other terms. No CPython implementation copy proposed. Installed CPython3.13.7 is a prospective test runtime; inspected current main is a separate reference revision.

### Janus actual source/tests/dependencies/CI

[janus/__init__.py](https://github.com/aio-libs/janus/blob/431248c05c63d24911e66f4f9a6fedc905c39562/janus/__init__.py): sync/async proxies share a deque, size limit and unfinished counter. append/popleft order, full check and get's not-full notification were inspected; get and task_done are separate. It creates asynchronous notification tasks and binds an event loop while protecting state with locks. That transport complexity has no benefit for a pure scripted state model.

[Actual sync tests](https://github.com/aio-libs/janus/blob/431248c05c63d24911e66f4f9a6fedc905c39562/tests/test_sync.py) test FIFO versus priority, capacity/full/empty and blocking operations. [Async test_order/test_maxsize](https://github.com/aio-libs/janus/blob/431248c05c63d24911e66f4f9a6fedc905c39562/tests/test_async.py) expects1/3/2 FIFO and shows a putter resumes after get frees capacity; bodies read, not executed.

[setup.cfg](https://github.com/aio-libs/janus/blob/431248c05c63d24911e66f4f9a6fedc905c39562/setup.cfg) declares Python>=3.9 and no mandatory install_requires list; inspected imports are standard library. [pyproject.toml](https://github.com/aio-libs/janus/blob/431248c05c63d24911e66f4f9a6fedc905c39562/pyproject.toml) requires setuptools/wheel for build; requirements-dev includes pinned pytest/asyncio/coverage/lint/type/scanner/benchmark tools and editable self-install. These are not proposed dependencies; no install or build run.

[ci.yml](https://github.com/aio-libs/janus/blob/431248c05c63d24911e66f4f9a6fedc905c39562/.github/workflows/ci.yml) runs Ubuntu Python3.9–3.13 tests, lint/benchmark and tag publishing. Mutable action tags and release refs are not copied. Release token/signing steps describe upstream automation, never authority for this task. Hosted checks not verified.

[README](https://github.com/aio-libs/janus/blob/431248c05c63d24911e66f4f9a6fedc905c39562/README.rst) warns about closing notification tasks and event-loop scope; links [closed issue574](https://github.com/aio-libs/janus/issues/574). Actual issue body reports destroyed-pending-task logs from2023, updated2024; read as reported historical behavior, not a reproduced current vulnerability. No live transport testing performed.

[Actual Apache2 license](https://github.com/aio-libs/janus/blob/431248c05c63d24911e66f4f9a6fedc905c39562/LICENSE): distributing derivatives requires license/notices retention, marking changed files and preserving applicable NOTICE attribution. No Janus code copy proposed; a future original implementation can use Jake's own MIT license with owned-code attribution.

## Primary semantics and chosen differences

[Python queue documentation](https://docs.python.org/3/library/queue.html) and [asyncio queues](https://docs.python.org/3/library/asyncio-queue.html) distinguish insertion, removal and task completion. Positive capacity applies to items still queued, while unfinished tracking is separate. Nonpositive capacity means unbounded in these APIs; this lab instead rejects zero/negative limits. Actual synchronization/blocking and unreliable thread observations are outside scope; model snapshots are exact only for the supplied serial trace. The explicit bounded service-slot policy and ownership are additional chosen rules.

FIFO preserves accepted enqueue order and is inspectable with small examples. Priority requires tie ordering/fairness/starvation choices; deadlines require expiration boundaries and waiting-versus-service cancellation rules. Neither is needed for the smallest useful lesson. Refusing admission models a capacity decision, not a blocking producer, implemented backpressure transport, delivery guarantee or proof of work effects.

Local Ollama supplied one bounded public comparison draft1621ms,45-second deadline, raw preserved. Reviewed/corrected its conflation of start with completion, unsupported starvation wording and CPython async-notification framing; retain only accurate scope/capacity points. Codex retains contract/security/source judgments. No remote inference/spending; OpenRouter considered unnecessary for remaining security/contract reasoning, so no remote readiness refresh/call. Laya's tested schemas do not fit. Recommendation: build original stdlib FIFO model after approval, reuse owned bounded admission/CLI patterns, avoid live queue dependencies. Proposed behavior/report-fit/oracles remain unverified until implementation is approved and tested.
