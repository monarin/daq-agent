# UED reporting support

Status: initial profile milestone implemented 2026-11-13; detector evidence
selection and richer upstream guidance remain proposed. See [UED settings](../workflows/ued-logs.md)
for the implemented scope and [review scope](../reviews/ued-profile/scope.md)
for acceptance checks. Source timezone confirmation remains open.

## Scope and findings

Extend the existing historical, read-only report/view and external-agent resource workflow to UED.
Live DAQ control, hardware access, Grafana and ConfigDB adapters remain outside
this change. A profile enables collection; detector-specific evidence selection
and diagnostic guidance determine how useful the resulting report is.

The application already validates any lowercase three-letter hutch code and
loads profiles by name (`reporting.report_settings`). Reports and viewing already retain hutch identity. TMO and UED profiles are now packaged; both use the existing generic reporting path.

Read-only inspection of the shared UED log tree found the existing
`YYYY/MM/DD_HH:MM:SS_<host>:<component>.log` layout. Sampled control, TEB and
ePixQuad1kfps headers contained all six fields the collector recognizes:
PLATFORM, HOST, ID, SLURM_JOB_ID, TESTRELDIR and GIT_DESCRIBE. The recent
48-hour candidate selection fit current discovery/file/byte bounds. This was
metadata discovery and bounded header inspection, not a complete collection,
model evaluation, timezone verification or determination of detector health.
Operational paths and raw evidence are deliberately not recorded here.

The verified local cache of configured upstream revision
`179b2bfbe73901f394222922571a0753e7ce9a06` supplies general DAQ diagnostics,
but lacks the detailed UED ePixQuad1kfps troubleshooting guidance available in
the maintainer's personal detector skill. Interactive personal skills are not
automatically imported into application model sessions.

## Implementation roadmap

| Area | Change and remaining work |
| --- | --- |
| Hutch configuration | Add matching `config/hutches/ued.toml` and `src/daq_agent/profiles/ued.toml`, with `hutch = "ued"`, accessible log root and verified timezone, explicit runtime settings and a reviewed exact upstream skill pin. Keep deployment-private settings in an external config when necessary. |
| Default exclusions | Start with `known_conditions = []`. Review applicability before enabling any TMO exclusions; detector damage and calibration failures must remain visible. |
| CLI and documentation | Update the TMO-only help in `cli.py`, README, config guide and reporting walkthrough. Document UED report/view and resource commands and source-access requirements. |
| Evidence selection | Extend `collectors/session_logs.py` patterns and context selection for UED failure signatures, with synthetic positive and negative cases. |
| Diagnostic knowledge | Contribute reviewed detector guidance to maintained upstream LCLS2 skills, then select its exact reviewed revision. Do not copy personal skill contents into this repository. |
| Verification | Add UED profile, collection, report/view/resource isolation and diagnostic fixtures; verify installed package data and run the existing test suite. |

No new configuration schema, hutch-specific collector class or SSH tool is
needed for the observed shared-log layout. `profiles/*.toml` is already included
by `pyproject.toml`; confirm the built wheel actually contains the new profile.
An explicit UED config can exercise the generic code before packaging defaults.

## Evidence and diagnostic gaps

Direct checks against the current collector regexes found no category matches
for these synthetic bare messages:

- `Missing data: subframe count 3 [expected 4]`
- `Missing data: subframe[2] size 0`
- `AxiVersion.GitHash = abc != Calibration Githash = def`
- `Please re-train the ADC lanes`

A severity marker or adjacent selected context may capture these messages, but
the message itself is insufficient today. Add narrow signatures for spaced
“Missing data”/subframes and ADC calibration mismatch. Preserve associated
configuration verification tracebacks, frame-size and timing context. An
ordinary `Setting ... AsicMask ...` line is context, not a failure by itself.
Test that sampling still retains detector evidence amid repeated generic errors.

Upstream guidance should distinguish missing timing subframes, zero versus
short image payloads, ADC startup/calibration problems, AsicMask verification,
and run-trigger versus DAQ-trigger timing. Treat historical explanations as
hypotheses until the selected launch supplies evidence; do not claim the
zero-byte-frame issue has an established cure. Preserve control/TEB/detector
launch correlation, release identity and uncertainty about absent node/register
checks. Other observed components (Andor, Piranha, Wave8 and AMI) need fixture
coverage and an explicit statement of diagnostic coverage as support expands.

The follow-up workflow now uses portable agent resources. The deprecated chat's
192 KiB skill ceiling does not constrain UED resources. Retain complete selected
references within the upstream synchronization limits; report model sessions
still have their own evidence, step and time bounds. An external agent selects
relevant guidance using its own context management.

## Implementation and acceptance order

1. Initial settings implemented: two UED profiles and user documentation reuse the current runtime
   and pinned general skill integration. Verify log access as the actual runtime
   account and verify the filename/line timezone assumption. Keep missing
   coverage explicit. Basic reporting can ship separately from richer diagnosis.
2. Add synthetic UED launch groups and the missing evidence signatures. Cover
   control/TEB/DRP correlation, multiple launches/platforms, untimed lines,
   normal AsicMask setup, and detector symptoms without generic error prefixes.
3. Review and pin upstream UED diagnostic guidance. Check retained skill sizes,
   immutable skill provenance and application tool restrictions across reporting
   and resource export.
4. Run `python -m unittest discover -s tests -v`; verify installation and profile
   lookup outside the checkout. Use fake runtimes for completed-report, citation,
   latest-UED selection and TMO/UED resource-scope checks. Keep production logs
   and paid model calls out of ordinary tests.
5. Perform a separate bounded `--prepare-only` UED acceptance check with private
   output and an explicit window. Inspect launch coverage, retained detector
   excerpts, redaction and time assumptions. A reviewed model-backed evaluation
   is a separate step before claiming diagnostic quality.

Acceptance commands after implementation are `daq-agent report --hutch ued
--last 2d`, `daq-agent view --hutch ued`, and an external agent reading the generated
`agent-resource/report.json`.
No production restart, register/configuration write or service adapter is
required for this reporting milestone.
