# UED initial settings review scope

Implement matching source and packaged UED profiles using the existing bounded
read-only collector, shared LCLS runtime defaults and exact general DAQ skill
pin. Enable no known-condition exclusions. Update CLI help and user documentation.
Keep Pacific time explicitly assumed until source confirmation is available.

Acceptance: offline unit suite; synthetic preparation preserving UED identity
and unexcluded conditions; completed fake-runtime report/resource scope and
hutch-specific viewing; built wheel profile lookup outside the checkout; separate
bounded private UED `--prepare-only` check with retained pinned guidance and zero
model calls. Production contents and raw review records stay outside Git.

Excluded: detector pattern/guidance changes, production operations, model-backed
diagnostic evaluation, changing the active installation, and merging the PR.

Codex implements; restricted Claude independently reviews exact commits in a
detached scratch worktree. Maximum three rounds, 900 seconds each. Fix blocking
findings and re-review changed code; publish a compact result record.
