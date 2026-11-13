# Portable report resource review scope

The requested workflow centers on report generation using retained, pinned
diagnostic skills and references. Completed reports must provide human-readable
Markdown/HTML and a portable resource that an independent agent can investigate
without daq-agent chat, provider credentials, the original cache or original logs.

Review changes against baseline commit
`45af495502848e75efccf1d4dd43436596cb63a4` (draft PR #8). The implementation is
proposed as a separate stacked draft PR; no merge or deployment is included.
Codex coordinates implementation and fixes; Claude independently reviews a clean
detached checkout with read-only tools. Maximum: three review rounds, each with
a 15-minute timeout. Review must cover the latest implementation commit.

Acceptance criteria:

- Completed reports publish both human output and the agent resource; failures
  and prepare-only runs cannot be advertised as completed resources.
- Existing completed reports can export without a model call, fetching skills,
  scanning original logs, changing retained evidence or replacing a destination.
- Copied bundles preserve findings, global citation mappings, hutch/window,
  partition/release evidence, coverage, known conditions and pinned skill identity.
- Evidence and skill integrity is checked, artifact paths remain contained and
  portable, and credentials/provider settings/runtime transcripts are excluded.
- Resource retention is independent of the deprecated chat input ceilings.
- Batched, local-only and deterministic known-condition reports remain supported.
- Chat/task-transfer are temporarily deprecated compatibility commands. Native
  agents own new investigation sessions; full deletion is not part of this patch.
- Documentation describes implemented versus proposed behavior accurately. UED
  onboarding remains a proposal, updated for the resource workflow.
- Run the full offline unittest suite and verify a built/installed package outside
  the checkout, including profile/skill package data. No live DAQ or paid model
  calls are ordinary tests; the explicitly requested independent review is separate.

Excluded: production operations, UED profile implementation, new live adapters,
agent launchers or personal-skill installation, report discovery APIs, note import,
automatic publishing/merging, and changes to the active installed environment.

Large test and reviewer artifacts stay in shared scratch. Only concise scope,
findings dispositions and validation summaries belong in committed documentation;
raw reviewer sessions, production evidence and credentials do not.
