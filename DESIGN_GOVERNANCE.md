# Design Governance

## Purpose

The design repository prevents implementation from silently becoming experiment design. It creates an immutable, reviewable contract between the project owner, ChatGPT as experiment/product designer and independent reviewer, GPT-5.6 Sol as implementation engineer, and GPT-5.6 Luna as delegated run operator.

## States

A design review may be:

- `PROPOSED`
- `APPROVED`
- `AMENDED`
- `SUPERSEDED`
- `REJECTED`

Only `APPROVED` or explicitly current `AMENDED` designs authorize implementation.

## Required metadata

Every approved design document records:

- Design ID and title
- Status
- Approval date
- Project owner
- Designer/reviewer
- Scope
- Binding decisions
- Explicit non-goals
- Decisions intentionally deferred
- Change-control conditions
- Approval statement
- Amendment history

## Commit policy

Each approved design review is committed after owner approval. The commit SHA becomes part of the implementation contract. A Sol handoff must identify:

```text
Approved design IDs
Approved design commit
Implementation conformance: CONFORMING | DEVIATION_PROPOSED | BLOCKED_REQUIRES_DESIGN_REVIEW
Unapproved design changes executed: none
```

Draft discussion in chat is not an implementation authorization. Material changes to an approved design require an amendment document or a new design review approved by the project owner.

Approved supplemental decisions use the parent design ID plus an `Sxx` suffix. A supplement is binding within its stated scope, must be indexed, hashed, and committed, and may not silently contradict its parent. Any discovered conflict stops implementation for design review.

## Implementation scope records

Approved vertical slices use a `VS-xx` identifier. A vertical slice is a binding implementation scope rather than a replacement for the design reviews it cites. It activates only the minimum named contracts, user-visible behavior, evidence, tests, and non-goals needed for that slice. Every approved vertical slice must be indexed, hashed, and committed.

Approved source-admission plans use a `SOURCE-PLAN-xx` identifier. They freeze exact sources, revisions, components, rights evidence, authorized operations, exclusions, derived-artifact boundaries, and hard-stop conditions for an approved implementation scope. They do not by themselves authorize acquisition; acquisition requires active repository governance and an approved implementation activation manifest. Every approved source plan and its machine-readable manifest must be indexed, hashed, and committed.

Approved benchmark-content batches use a `BENCH-<scope>-BATCH-xx` identifier. ChatGPT owns case-family blueprints, prompts, evidence and answer contracts, accepted alternatives, required qualifications, prohibited claims, semantic rubrics, relationships, contamination clusters, and case-content amendments; the project owner approves each authoritative batch. Sol may implement only the approved schemas, deterministic generators, loaders, scorers, reports, and execution adapters. An approved benchmark batch freezes content but does not authorize execution until its sources and derivatives are verified and an implementation activation manifest is active. Fixed-evidence cases define what may be concluded from deliberately supplied evidence; they do not override full-runtime requirements to acquire available approved evidence proactively. Every approved batch and machine-readable case file must be indexed, hashed, and committed.

Approved repository-governance packages use a `GOV-xx` identifier. They define static authority, review, branch, credential-use, handoff, merge, and integrity contracts that must exist before production implementation. A governance package may include non-executable schemas, templates, owner setup instructions, and a proposed activation, but executable checks remain Sol-authored. Every approved governance package must be indexed, hashed, and committed.


Approved public-repository governance packages use a `GOV-xx` identifier. A governance package freezes static authority, review, GitHub-operation, model-role, handoff, schema, and activation-template artifacts before production implementation. Active static governance files may live at repository root while the approved governing record remains under `design/approved/`. Executable checks and automation remain Sol-authored under a separately approved activation. Every approved governance package must be indexed, hashed, committed, and bound to its active package manifest.


Approved implementation activations use an `ACT-<task>-<name>-vN` identifier. An activation binds one Sol root turn to exact approved design IDs, one approved design commit, activated contracts/paths/interfaces, explicit non-goals, tests, evidence, budgets, completion criteria, and owner approval. It authorizes no work until repository bootstrap prerequisites in the activation and task prompt are satisfied. Activations must be indexed, schema-valid, hashed, committed, and superseded rather than edited after execution begins.

Every Sol root turn must also receive an immutable implementation activation manifest conforming to DR-30. Unactivated design concepts remain normative future obligations and must not receive production stubs, tables, interfaces, packages, services, feature flags, or TODOs. Material activation expansion requires ChatGPT design review and project-owner approval.

## Implementation boundary

Approved design documents define what must be built, evaluated, or run. Consequential logical architecture, external contracts, storage and rights boundaries, retrieval semantics, validation behavior, reporting, benchmark identity, and experiment design are project-design decisions and must be approved before implementation.

Sol is the exclusive implementation engineer. Sol retains discretion only over reversible, local, design-neutral coding mechanics that preserve all approved semantics, interfaces, evidence, metrics, reproducibility, security, privacy, cost boundaries, and user-visible behavior. A material architectural or experimental decision must stop with `BLOCKED_REQUIRES_DESIGN_REVIEW`; Sol may recommend alternatives but may not implement one before ChatGPT designs it and the project owner approves it.
