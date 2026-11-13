# Configuration

`hutches/tmo.toml` and `hutches/ued.toml` contain non-secret hutch defaults, also
packaged for use outside the checkout. `report --hutch tmo` and
`report --hutch ued` select their respective profiles; `--config` overrides
the profile with a custom file whose hutch must match. Python 3.11+ parses TOML
without an extra dependency.

Required fields: `hutch`, `timezone`, and `model`. Optional fields:
`provider_config`, `opencode`, `runtime`, `claude`, `claude_deployment`,
`claude_effort`, `claude_cache_ttl`, `output_root`, `log_root`, `known_conditions`,
and the pinned `daq_skills` table. A legacy numeric `partition` field is validated and discarded
when loading old configuration; it does not appear in new report settings. Platform values from source logs remain metadata.

Both packaged profiles use shared LCLS Claude and the same exact upstream skill
revision. UED enables no known-condition exclusions and assumes Pacific source
time pending confirmation; see [UED settings](../docs/workflows/ued-logs.md).
See [model runtimes](../docs/workflows/model-runtimes.md) and
[known conditions](../docs/workflows/known-conditions.md) for field semantics.

Configuration does not establish model entitlement or source access. Credentials
remain external references in the provider configuration. Keep private overrides
outside the repository or in ignored `config/local/`; never commit credential
values. CLI options override corresponding profile fields.
