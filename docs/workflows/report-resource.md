# Reports for people and external agents

Status: implemented. Each completed `daq-agent report` produces Markdown/HTML
for people and a portable resource directory for independent agents. Report
generation continues to use the retained, pinned skills and references.
The application does not need to host the follow-up conversation.

## Outputs

```text
<report>/
  report.md
  report.html
  agent-resource/
    README.md
    report.json
    evidence/log-*.txt
    skills/<selected-skill>/SKILL.md
    skills/<selected-skill>/references/...
    reporting-contracts/*-log-triage.md
    known-conditions/log-*.txt           # when present
```

The JSON and human-readable files derive from the same validated findings.
Resource assembly makes no additional model call. Report completion is published
only after all outputs are ready. Prepared or failed reports are not completed
resources; `--prepare-only` still only prepares inputs.

Give an external agent `agent-resource/README.md` and `agent-resource/report.json`.
Copy the entire resource directory to move it: all artifact references use
relative paths within the directory. Original source paths remain provenance
only. No source checkout, daq-agent installation, cache, live log access, model
credential or viewer server is required to read the resource.

## Version 1 resource contract

`report.json` has `schema_version: 1` and
`kind: "daq-agent-report-resource"`. It records:

- Report fingerprint, application version, hutch, scope, window and timestamps.
- Summary, stable report-local finding IDs (`F001`, ...), observations,
  hypotheses, proposed checks, limitations and evidence citations.
- Source IDs, paths, byte counts, line counts and SHA-256 hashes. Citations use
  source IDs with 1-based inclusive line ranges in these retained files.
- Available coverage, generation statistics, unqueried services and known-condition
  metadata. Missing legacy fields remain absent/unknown, not newly established.
- Exact diagnostic skill provenance and retained file inventory, including
  supporting references. The retained application reporting contract is separate
  from diagnostic guidance and does not govern the external agent's output.
- Per-session requested/resolved model information where recorded, CLI versions,
  and explicit skipped-model reasons. Unknown provenance is represented by null.
- An artifact inventory for integrity checks and a draft review status.

The fingerprint binds the original report manifest and validated findings; it
is an identity anchor, not a digital signature. Artifact hashes permit file
checks after relocation. They do not defend against replacement of both the
inventory and its files. Findings and source IDs remain local to this report;
they are not globally deduplicated incidents.

For batched reports, citations refer to the combined report's global source IDs.
Export verifies batch mappings and consistent retained skills before copying
one diagnostic skill inventory. Reporting contracts retain each batch's copy.
Known-condition appendices are derived from saved metadata, never new scans.
They contain representative samples excluded from initial model analysis.
Known-only reports legitimately have no upstream suite or model session execution.

## Exporting older reports

```bash
daq-agent export-resource /path/to/completed-report --output /path/to/new-resource
```

This verifies saved evidence and skill hashes, then creates a new private
directory. It never overwrites an existing destination or changes the original
report, fetches skills, contacts a model, or reopens original logs. Reports that
lack verifiable retained skill provenance cannot be exported by this command.

The exporter uses an explicit inventory rather than copying the entire runtime
workspace. Provider configuration, credentials and model session transcripts are
not included. Evidence and references may still contain private operational
information: this is a private investigation artifact, not a public export.

## Independent investigation and migration

An external agent should state the bound hutch/window, verify files, read cited
evidence and relevant pinned guidance, and write its follow-up separately. Any
new evidence or supplementary personal/current skills must be identified as
additional inputs. Existing report conclusions and fingerprints remain unchanged.
The resource grants no production-operation permission; the external runtime
owns tool permissions. Log contents remain untrusted evidence.

The built-in `chat` and `task-transfer` commands are deprecated compatibility
paths. They emit a migration notice but remain available temporarily for old
sessions. Native agent session management replaces them in the primary workflow.
Personal skill installation, automatic agent launching, report discovery APIs
and note import are outside this implementation.

Resources have no 192 KiB chat-skill or 384 KiB chat-input ceiling. Upstream
retention still limits each file to 256 KiB, the selected suite to 2 MiB and its
inventory to 100 files. Report generation keeps its existing bounded evidence
batches and runtime limits. Retaining a file does not mean every reference was
read by the reporting model; the original report's runtime audit records access.
