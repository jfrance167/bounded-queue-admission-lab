# Verification — October5,2026

Selected Windows CPython3.13.7; installed Bandit1.9.4. No install/upstream execution. `python scripts/verify.py docs/verification/final` exited0; results.json/logs in that directory bind the final12 Python source hashes to actual checks. Prior successful stage3 evidence remains preserved.

| Check | Result | Evidence |
| --- | --- | --- |
| Syntax AST | PASS12 files | final/results.json |
| Normal unittest | PASS31, exit0 | final/normal.log |
| Optimized unittest | PASS31, exit0 | final/optimized.log |
| Full sealed hand reports | PASS21 cases | fixtures/cases.json, research/contract-freeze.json |
| Independent lifecycle/rank/slot oracle | PASS1,024 traces | tests/support.py and test_model.py |
| Four isolated mutants | PASS meaningful assertions/restored originals | final/results.json and four logs |
| CLI demos | PASS21 complete report/error matches plus overwrite refusal/hash preservation | final/demo-* |
| Physical-process closed pipes | PASS21 children per suite, including12 help/usage/report/error closure matrix cases | test_cli.py; optimized children explicitly receive-O |
| Bandit | PASS0 findings/errors,7 narrow skips | final/bandit.json |
| Unsuppressed scanner control | Expected exit1,7 B404/B603 harness findings,0 errors/no application findings | bandit-control-final.json |
| Report growth | PASS128 events,8 waiting/4 service,10,600 input/235,925 output bytes | final/results.json |
| Conservative width envelope | PASS250,007 bytes<262,144 cap | final/report_width_bound, scripts/report_bound.py |
| ECC self-review | PASS0 unresolved actionable defects | REVIEW.md |
| Type checker/dedicated lint | NOT RUN; no configured checker executed | AST/Bandit are separate checks |
| Linux/other runtimes/hosted CI/CodeQL | NOT RUN | Windows selected interpreter only |
| Git baseline/history/protections | NOT APPLICABLE | No repository authorized or created |
| Real queues/threads/services/effects/fairness/durability | NOT APPLICABLE | Outside approved model |

## Pre-application freeze and independent controls

research/contract-freeze.json records21 full input/report-or-error cases, SCHEMA.md and independent tests/support.py hashes while queue_lab was absent. Fixture SHA256 `ccf24c69ba586f5e340667a4b7c41d4e27aaa758037d12a59e4f710ad5644787`. Manually declared decisions/after states/counts were expanded by a field formatter, not a transition algorithm. Before application code the lifecycle/rank oracle matched20 structurally valid cases; the21st independently freezes a late structural error before early ownership failure. Final verifier confirms all three freeze hashes remain unchanged.

Oracle uses job phases/ordinal minimum/owned slots rather than production FIFO pop helpers, and imports no application code. Tests cover full reports, finite short legal/illegal traces, conservation/peaks, no-auto-start/failed-start neutrality, tie order/out-of-order owned completions, submitted-ID reuse, input/snapshot independence/frozen records, cycles/aliases/huge integers/exact resource bounds and benign metaclass/key/subclass hooks never called. This is finite evidence, not formal verification.

## Mutants and sinks

Waiting-versus-unfinished mutant:5 assertion failures/0 errors. Newest-versus-oldest:1 assertion/1 additional error. Start-as-completion:7 assertions/5 additional errors. Mismatched-completion:1 assertion/0 errors. Every mutant has meaningful frozen-report assertions, not crash-only detection; mutated suites are not claimed error-free. Copies restored byte-for-byte and original source verified unchanged. Harness normalizes source CRLF before exact multiline target matching, restoring original bytes afterward.

CLI actual child tests propagate-O when the parent is optimized. The12-case matrix spans help/usage/report/error with stdout closed, stderr closed and both closed. Other children exercise valid rejected exit0, fixed no-prefix late error, argument/help/regular-file errors and individual sink closures. Simulated dirty/short/boolean/raising/closed/flush-failing streams are labeled seams; they are distinct from physical process pipes. Output is not transactional, error delivery may fail, and tests do not prove all races/blocking behavior.

## Report-cap reachability

The genuine128-event trace fills8 waiting/4 service at7-digit times, then records rejection/busy-start rows; report235,925 bytes. It is not the exact largest report. The repeatable report_bound.py widens each frozen field independently:128 rows, full waiting/service snapshots on both sides,7-digit times, fixed ASCII labels, longest enum strings, longer null slot spelling, all summary counters3 digits. An impossible joint result/state is intentionally used as a conservative envelope,250,007 bytes. Under current exact schema/caps this remains below262,144, so a normal report cannot hit that fixed guard. Review this reasoning if fields/enums/caps change.

Reduced MAX_OUTPUT=measured_size-1 verifies the library cap-before-return path; arbitrary oversized render input exercises a defensive guard. Neither is a naturally admitted fixed-cap trace. Renderer precondition remains internally produced reports, not untrusted arbitrary Python trees.

## Scanner and review limits

Seven narrow nosec annotations:2 B404 imports in test_cli.py/verify.py;4 B603 owned fixed CLI-child launches and1 fixed verifier runner. No application exclusions. They invoke selected local Python/module/tests/installed scanner with fixed argv construction and no shell or input-selected command. Unsuppressed control confirms those7 warnings and no app finding; it does not certify all subprocess behavior.

No failing unmutated implementation test/scanner run occurred in recorded checks. Preventative changes to reused code replaced native type tuple-membership with identity tests before custom metaclass behavior, propagated optimization to actual CLI children, and normalized mutation matching for CRLF; regression evidence verifies current behavior. Raw worker inaccuracies corrected, not executed. Final source/contract receipts and narrow credential-pattern hygiene are recorded separately; absence of matches is not comprehensive secret assurance. No Git/history/remote/independent audit/hosted proof or publication was performed.
