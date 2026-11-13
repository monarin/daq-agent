# UED profile and evidence preparation

Status: initial settings and detector-message selection implemented. This enables the generic historical
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

No TMO known-condition exclusions are inherited. Automatic collection now selects
bare messages in two narrow categories, even without an error severity prefix:

| Category | Message signatures |
| --- | --- |
| `detector_subframe` | `Missing data: subframe count ...`, `Missing data: subframe[N] ...` (including zero timing/meta size and zero/short image payload messages) |
| `adc_calibration` | `AxiVersion.GitHash = ... != Calibration Githash = ...`, `Please re-train the ADC lanes` |

These signatures apply to any hutch that emits them. They record messages, not
hardware checks or diagnoses; no expected payload size is inferred. Healthy
AsicMask assignments, equal hash messages and ordinary subframe size logs do not
trigger these categories. Existing generic patterns still apply.

Detector categories receive representative context before broader errors within
the existing document budget. Subframe indices and numeric sizes remain distinct
for sampling. At most four distinct signatures per category/time bucket are
retained; additional matches remain in counts. Context includes two preceding
and three following lines; existing traceback capture retains up to 64 lines.
Nearby timing, frame and setup messages can therefore remain context without
being counted as failures themselves. No distant configuration search is claimed.
Source launch/component/platform/release, line numbers and time buckets remain
in evidence; sensitive fields are masked using the existing limited rules.
Budget omissions and clipping remain explicit. Many distinct detector messages
or large inventories can still exhaust the bounded evidence budget.

Synthetic regression tests cover bare signatures, healthy near matches, multiple
control/TEB/detector launches and platforms, configuration-verification tracebacks,
redaction, noisy-log sampling, and retention in completed report resources using
a fake runtime. They do not evaluate model diagnostic quality. Richer reviewed
upstream detector guidance remains the next step in the
[UED roadmap](../proposals/008-ued-support.md). Successful collection does not
establish complete evidence coverage, detector health or live DAQ state. No
production control operations are introduced.
