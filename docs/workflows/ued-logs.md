# UED profile and evidence preparation

Status: initial settings implemented. This enables the generic historical
reporting workflow for UED; it does not validate detector diagnosis.

The packaged `ued` profile and `config/hutches/ued.toml` contain matching settings:

| Setting | Default |
| --- | --- |
| Log root | `/sdf/home/u/uedopr/daq/logs` |
| Source timezone | `America/Los_Angeles` (assumed; confirmation pending) |
| Runtime | Shared LCLS Claude, `opus`, medium effort, one-hour cache |
| Known-condition exclusions | None |
| Diagnostic guidance | Same five general DAQ skills and exact revision as TMO |
| Output | `~/daq/agent-logs/ued/YYYY/MM/<unique-run>-report/` |

Run as an account with read access to the shared logs. Preparation needs no
model credentials, but needs the pinned skill cache or Git/HTTPS access to
synchronize it. The CLI works from any directory after installing this version.

```bash
daq-agent report --hutch ued --last 1h --prepare-only
```

For a reproducible window, replace `--last` with explicit bounds, for example
`--from 2026-11-13T09:00:00-08:00 --to 2026-11-13T10:00:00-08:00`.
These identify the requested instants; they do not prove the source logs use
Pacific time. Filenames and bare line timestamps use the configured timezone
conditionally. The sampled UED headers had no timezone marker. Confirm source
timezone for the selected launch before interpreting time-localized findings;
use an external `--config` to override it. All collection limits and carry-in
selection rules in [one-command reporting](rolling-report.md) apply.

Inspect `collection/collection.json` and `manifest.json` for source identity,
coverage, truncation, redaction and preparation status. Preparation retains
evidence and guidance with zero model sessions; it creates no findings, human
report or portable agent resource. Keep all real-log output private and outside
the repository. Basic masking is not a guarantee of complete sanitization.

To generate a draft using the configured model service, omit `--prepare-only`.
Completed reports contain `report.md`, `report.html` and
`agent-resource/report.json`; copy the whole resource directory for an external
agent. `daq-agent view --hutch ued` selects the latest completed UED report.
Model-backed generation may incur usage charges and requires human review.

No TMO known-condition exclusions are inherited. Current selection can still
miss bare ePixQuad1kfps subframe and ADC-calibration messages without a generic
error prefix or nearby selected context. Detector-specific patterns, synthetic
diagnostic fixtures and reviewed upstream detector guidance remain separate
work in the [UED roadmap](../proposals/008-ued-support.md). Successful collection
does not establish complete evidence coverage, detector health, diagnostic
quality or live DAQ state. No production control operations are introduced.
