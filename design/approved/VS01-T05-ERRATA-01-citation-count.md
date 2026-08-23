# VS01-T05-ERRATA-01 — Citation Count

| Field | Value |
|---|---|
| Erratum ID | `VS01-T05-ERRATA-01` |
| Status | **APPROVED NONSEMANTIC IMPLEMENTATION CLARIFICATION** |
| Applies to | `VS01-T05` and `VS01-T05-RUNTIME-SPEC-v1` |
| Design authority | ChatGPT |
| Owner implementation authorization | Joseph Abbud, 2026-08-22 |
| Semantic change | **None** |

## Correction

The frozen design contains ten stable citation records:

```text
CIT-T05-001
CIT-T05-002
CIT-T05-003
CIT-T05-004
CIT-T05-005
CIT-T05-006
CIT-T05-007
CIT-T05-008
CIT-T05-009
CIT-T05-010
```

The following two natural-language sentences incorrectly say “nine”:

- `verification_rules[VR-T05-006].requirement`
- `implementation_tests[6]`

For implementation and conformance, both sentences mean **all ten citation
records**.

The exact authoritative behavior remains:

- The structured candidate references all ten citation records.
- Study mode uses all ten citation records.
- Brief mode uses nine unique citation records and intentionally omits only
  `CIT-T05-005` from its rendered Markdown.
- The public contract contains the full ten-record citation ledger.
- Every one of the ten records must match its exact T04 evidence selector,
  excerpt, source label, and display role.
- No citation record, answer block, claim, alternative, verification status,
  or rendered text changes.

The frozen Markdown and JSON design artifacts remain byte-preserved. This
erratum is the only authorized reconciliation of the citation-count typo.
