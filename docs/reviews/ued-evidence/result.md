# UED detector evidence review result

Date: 2026-11-13. Result: **pass**, after two independent restricted Claude
review rounds. No unresolved findings. Scope: [detector evidence selection](scope.md).

- Base after merging PR #10: `a14536e49caab5da5a95a990e9d032b6db3ee701`.
- Initial reviewed implementation: `159f3d389e2693ac6cf1f1374777edc679186323`.
- Final reviewed code: `d9ed73fbcb9e609185405a209b176f24ab8e2d96`.
- This result is a subsequent evidence-only commit.

## Findings and responses

Round 1 passed with two low, nonblocking findings. Both were accepted and fixed;
round 2 confirmed their resolution and found no new issues.

| ID | Finding | Fix and validation |
| --- | --- | --- |
| UED-EV-001 | Exempting whole subframe lines from numeric normalization could let unrelated varying PIDs/counters consume example slots | Protect only significant subframe index/size/count tokens. Synthetic varying-prefix repeats collapse into one signature while distinct payload messages retain separate examples. |
| UED-EV-002 | Numeric-only calibration hashes could normalize together | Protect calibration hash values, including numeric-only and hexadecimal values, while normalizing unrelated tokens. Synthetic distinct hash pairs remain separate examples. |

The reviewer used read-only tools in separate detached checkouts and inspected
matching, normalization, sampling bounds, source/time identity, redaction and
documentation. The invocation helper checked each full SHA and clean detached
checkout before launch. Tests and diffs were supplied by the coordinator;
the reviewer did not run commands or inspect production logs.

## Validation

- Eight focused synthetic detector-evidence tests passed.
- `python -m unittest discover -s tests -v`: **182 passed**, with the opt-in
  offline OpenCode integration enabled and source imports verified by the test
  environment's explicit `PYTHONPATH=src`.
- Fixtures cover bare signatures and healthy near-matches, multiple launches
  and control/TEB/detector identities, platforms/releases, explicit/conditional/
  untimed buckets, original line numbers, traceback context, sensitive-field
  masking, noisy-log budget omissions and preserved detector values.
- A fake-runtime completed report preserves detector evidence in human report
  output artifacts and hashed portable-resource sources. This tests plumbing
  and retention, not model interpretation or diagnostic quality.
- `git diff --check` passed. No profile, dependency or package-data changes.
  No production reads/operations or diagnostic model calls were used.

## Limits and retained evidence

Existing bounded sampling can still omit messages. This milestone adds message
selection, not hardware checks, expected payload constants or confirmed causes.
Reviewed upstream detector guidance, source-timezone confirmation and
model-backed diagnostic evaluation remain separate work. The active application
installation was not changed.

Raw test logs, review prompts/results and task status remain in private task
scratch under `agent-work/daq-agent/ued-evidence-20261113/`. This record is the
durable review outcome; raw artifacts are not public attachments.
