# Proposed decisions

- Select FIFO with separate finite waiting/service limits to teach removal versus completion; priority/deadline ordering/expiry policies require a future plan.
- Explicit starts even with idle slots; no direct dispatch/auto-start shortcut. Slot selection is supplied; FIFO job selection is modeled.
- Completion binds a job to its currently assigned slot; generic task_done counters do not supply that identity contract.
- Reject nonpositive capacity instead of the unbounded sentinel of Python queue APIs. Reject duplicate job submissions even after denial/completion; bounded total seen IDs prevent reuse ambiguity.
- Build original inert transitions and reuse reviewed owned MIT gates after approval. CPython/Janus live synchronization remains source context, not a dependency or source copy.
- Separate declared model completion from execution/effects and real service guarantees. Preserve research/worker raw evidence; no code/repository before concrete approval.

## Implemented after04:39 approval

- Seal21 full cases and independent lifecycle/ordinal/slot oracle before app code; the20 structurally valid oracle outputs match then, with late-schema failure separately frozen. Keep all three contract hashes unchanged through final verification.
- Adapt owned parser/CLI/verifier rather than live CPython/Janus queues. Identity-only native checks reject metaclass/key/subclass hooks before behavior. Frozen records/independent snapshots retain ownership semantics without caller mutation.
- Explicitly propagate optimization to actual child CLI tests; normal and-O suites each run21 physical children, including12 route/closed-pipe combinations. Fake dirty streams remain labeled seams.
- Use isolated mutations with assertion/error counts and byte restoration receipts. Normalize CRLF for exact source matching, never change original files for mutation tests.
- Measure a genuine128-event report235,925 bytes, then separately calculate a conservative250,007-byte frozen-field envelope below262,144 cap. The envelope is impossible as a joint trace; reduced cap and oversized render tests are defensive seams.
- Complete local stages1–4 with12 source receipts/docs/security/MIT/ECC/self-review/knowledge. No repository/hosted baseline/publish or live backpressure infrastructure created.
