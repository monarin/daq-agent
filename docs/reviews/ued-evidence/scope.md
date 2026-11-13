# UED detector evidence selection

Next milestone after the UED profile: select bare missing-subframe and ADC
calibration messages for bounded report evidence, without asserting a diagnosis.
Keep subframe index/size distinctions in representative signatures. Prioritize
these narrow categories before broad errors, retaining the existing collection,
document, signature and traceback bounds. Preserve source line numbers, launch,
component, platform, release, time buckets, redaction and omission reporting.

Acceptance: synthetic positive/negative cases, including normal AsicMask setup;
multiple launch/control/TEB/detector fixtures; adjacent timing/frame context and
configuration-verification traceback; noisy-log sampling and bounds; report and
portable-resource retention with a fake runtime; full offline unit suite.

Excluded: production reads/operations, model-backed diagnostic evaluation,
upstream skill edits or pin changes, source timezone confirmation, active
installation changes and merging the new PR. General message signatures apply
across hutches; no hardware constants or detector-health inference are added.

Codex implements; restricted Claude independently reviews exact commits in
detached scratch worktrees. Up to three rounds, 900 seconds per invocation.
Keep raw review/test output on scratch and a compact final result in Git.
