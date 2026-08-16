# Biblical Scholar Lab — Design Baseline

This repository is the authoritative pre-implementation design record for Biblical Scholar Lab.

Production code is intentionally absent. Approved product, scholarly, architecture, benchmark, experiment, governance, and execution decisions are recorded here before GPT-5.6 Sol implements them.

## Authority

- Joseph Abbud is the project owner and final approver.
- ChatGPT designs experiments and product contracts and reviews Sol's implementation and evidence.
- GPT-5.6 Sol is the exclusive implementation engineer.
- GPT-5.6 Luna may operate only as a frozen campaign runner delegated by Sol.

## Design-review lifecycle

1. ChatGPT proposes a numbered design review.
2. Joseph approves it or requests amendments.
3. The approved text is written to `design/approved/` and committed.
4. Every later implementation must cite the applicable design ID and approved commit.
5. Material changes require an explicit amendment or a new design review.

See [`DESIGN_GOVERNANCE.md`](DESIGN_GOVERNANCE.md) and [`design/DECISION_INDEX.md`](design/DECISION_INDEX.md).

## Current approved baseline

- `DR-01` — Version-One Product Contract
- `DR-02` revision 2 — Scholarly Epistemology and Methodology, including the approved architecture-contract schedule, model-capacity and family-bake-off policy, Gemma budget posture, and mobile/quantization direction
- `DR-03` — Scope, Refusal, and Sensitive-Use Policy
- `DR-04` — Canon, Reference, and Versification Model
- `DR-05` — Textual-History and Provenance Graph
- `DR-06` — Translation Nuance Core, including the approved A0–A6 architecture-extension ladder and profiling-gated compute-kernel policy
- `DR-07` — Linguistic Representation, including stand-off multilingual analysis, explicit source-text views and coordinate contracts, source-native annotation preservation, language-specific Greek/Hebrew/Aramaic profiles, and word-study-fallacy guardrails
- `DR-08` — Ancient Versions and Apparatus Policy, including passage-scoped version roles, evidential-distance tracking, R0–R5 retroversion restraint, apparatus scope and silence contracts, edition-local sigla, daughter-version dependencies, and component-specific access lanes
- `DR-09` — Scholarship and Citation Model, including work/version/manifestation separation, assertion-based bibliographic identity, claim-level citation entailment, quotation and translation provenance, publication-status awareness, source-dependence tracking, and dated scholarly-landscape assessment

Supporting official-source verification for DR-02 revision 2 is recorded under `design/evidence/`.
