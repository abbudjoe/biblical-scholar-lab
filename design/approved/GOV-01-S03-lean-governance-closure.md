# GOV-01-S03 — Lean Governance Closure and Manual Exact-Head Control

| Field | Value |
|---|---|
| Design ID | `GOV-01-S03` |
| Parent | `GOV-01` |
| Status | `APPROVED` |
| Approval date | `2026-08-20` |
| Project owner | Joseph Abbud |
| Designer and exact-head reviewer | ChatGPT |
| Implementation authority | GPT-5.6 Sol |
| Scope | Close custom universal governance automation and retain a lean, exact-head human-control model |
| Approved base | `35a7f5a5967f12cb6e8c043218fb2e8fdf7d592c` |

## Decision

Biblical Scholar Lab retires custom universal integrity automation as a prerequisite for product work.

The active governance model is:

```text
approved activation and task scope
→ Sol implements on one task branch and draft PR
→ task-specific CI and evidence
→ ChatGPT reviews the exact live PR head
→ Joseph explicitly approves that exact head
→ a separate Sol merge-only turn verifies the unchanged head
→ gh pr merge --squash --match-head-commit <SHA>
```

GitHub account identity is not treated as independent proof of human approval because Joseph and Codex share `@abbudjoe` and the existing `gh` credential.

## Retired

- `project-integrity` as a universal required status check.
- `turn-handoff-integrity` as a universal required status check.
- `chatgpt-review-integrity` and `owner-merge-record-integrity` as planned universal checks.
- `OwnerMergeAuthorizationRecord` as an active merge prerequisite.
- W00A1b static-policy and restricted-policy implementations.
- W00A2 and W00B as VS-01 prerequisites.
- The dummy W01 merge proof.
- ACT-W00A1B-STATIC-POLICY-v1.
- ACT-W00A1B-RESTRICTED-POLICY-v2.
- ACT-W00G-GENERIC-HANDOFF-v1.

## Preserved

- Pull requests before merge.
- Empty ruleset bypass list.
- Squash-only merge and linear history.
- Review-conversation resolution.
- Force-push and branch-deletion protection.
- Auto-merge disabled.
- Approved activation scope.
- Sol-only implementation authorship.
- Luna's frozen-operations-only boundary.
- Task-specific CI selected by each activation.
- Concise append-only root-turn handoffs.
- ChatGPT exact-head review.
- Joseph exact-head approval.
- A separate merge-only Sol turn using `--match-head-commit`.

## W00A1a historical treatment

PR #1 was squash-merged as `35a7f5a5967f12cb6e8c043218fb2e8fdf7d592c`. Its validator, tests, W00A1a schema, handoff registry, handoffs, and evidence remain historical, byte-preserved bootstrap evidence. The workflow `.github/workflows/governance-integrity.yml` is retired and deleted by W00C-01. Historical machinery is not a universal contract for later tasks.

Known unpushed terminal identities:

```text
W00A1b static-policy terminal:      689825b51613d87b07eb1454e26add77ee78027a
W00A1b restricted-policy terminal:  f8f4c2716d87c7b692ebb1849b00e39df1af972b
W00G design commit:                 8bed091c42296b0266c513f631a371229a117825
W00G activation commit:             0e347617ac8f760b29652642712db06c823aaf9e
W00G implementation terminal:       e52cfb070e608d411e3552f722d58e73266763e1
```

These local branches are not pushed, repaired, or merged.

## W00C-01

W00C-01 is documentation and workflow retirement only. It may update active governance prose, the GOV-01 package manifest/checksum, the decision index, and the merge-only template. It adds no production code, test code, workflow, schema, dependency, source, benchmark, model, database, runtime, UI, cloud, or billable behavior.

Before W00C-01 starts, Joseph removes `project-integrity` and `turn-handoff-integrity` from the `main` ruleset's required status checks while preserving every structural rule above.

## Closure

After W00C-01 is exact-head reviewed, approved, and merged, governance implementation is closed. The next authorized project-design step is `VS01-T01 — Local Archive and Source-Admission Foundation`.

## Approval

Joseph approved this supplement and W00C-01 in the current ChatGPT conversation on August 20, 2026.
