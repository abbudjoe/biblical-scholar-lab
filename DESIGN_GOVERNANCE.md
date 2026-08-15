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

## Implementation boundary

Approved design documents define what must be built, evaluated, or run. Sol retains engineering discretion only where it does not change hypotheses, product promises, data policy, model identity, objectives, metrics, gates, budget, scientific interpretation, or release posture.
