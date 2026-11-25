# Runtime 0.1.7 — community fixes (beta)

This beta publishes the exact `0.1.7-pr-integration.1` archive installed and
successfully used on Fedora 44 with CLI revision 20 and Desktop 2.160.1151.0.

It includes the multi-monitor placement, primary selection, resize visibility
and maximum-date fixes from PR #6, named-pipe discovery from PR #8, and the
integration correction that preserves the first directory-query mask on restart.

Use CLI **0.1.0-20** for the new Desktop recipe and current WinRT shim. The CLI
selects its exact Desktop recipe independently of the runtime's embedded build
default. Runtime build sources correspond to commit `2c886b4`; this immutable
archive is published without changing its binary checksum.

Assets include the runtime binary, complete corresponding sources, provenance,
SHA256SUMS and `release-evidence-beta.json` with technical validation details.

Thanks to **Tim ([@InsightfulAnalytics](https://github.com/InsightfulAnalytics))**
for the community PRs and contributions!
