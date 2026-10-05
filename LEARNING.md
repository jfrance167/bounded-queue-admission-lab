# Research learning goals

Implementation verified on Windows CPython3.13.7;31 normal and optimized tests,21 full hand cases and1,024 independent ledger traces. This is finite synthetic evidence.

- A dequeue frees waiting capacity while an in-service record can remain unfinished. Therefore unfinished can exceed the waiting limit without violating it.
- FIFO governs selection order, not completion order across multiple service slots.
- A bounded admission denial is a modeled capacity decision, not proof of actual blocking/wakeup/backpressure transport or fairness.
- Explicit owned completion prevents a rejected/queued/other-slot ID from laundering itself into processed work.
- Equal timestamps still need ordering; serial trace snapshots do not establish real concurrency semantics.

Optional exercise after implementation approval: for Q1/S1, compare submit1,submit2,start1 with submit1,start1,submit2 at the same timestamp. Which record is rejected, and what is the unfinished count?

Verified lessons:

- First ordering rejects job2 before start frees waiting room, leaving job1 in-service/unfinished1. Second ordering starts job1 before submitting job2, leaving one waiting plus one in-service/unfinished2. Waiting limit1 is respected in both.
- FIFO dequeue and slot completion are distinct ownership transitions. Multi-slot completion can be out of start order without changing the FIFO rule. Failed starts preserve head/service records and completing a slot does not auto-start waiting work.
- Even testing `type(value) in (dict,list)` can call exotic metaclass equality. Identity comparisons reject unsupported classes before these hooks; benign metaclass/key/subclass regressions record zero calls during admission.
- An optimized test parent does not automatically make a newly launched Python process optimized. The harness passes-O explicitly, and real help/usage/report/error closed-pipe children preserve frozen exits.
- Crash-only mutation detection is weak evidence. Every mutant here produces meaningful frozen-report assertion failures;1/5 additional errors for two mutants are reported separately, not hidden.
- Measure actual report growth before exercising caps. The full-occupancy trace fits235,925 bytes; a conservative independent-width envelope fits250,007. Reduced-cap seams are not actual schema-reachable cap failures.
