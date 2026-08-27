# VS01-T09-ERRATA-01 — Study workspace JSON Schema satisfiability

| Field | Value |
|---|---|
| Erratum identity | `a72e39da8625e4f9abd9ebd2d8994e33f715489f5153f5a6c6228a6b3b2a1df8` |
| Repository base | `95d587a2b09d8c07ac7574050a5d7afa0969a625` |
| Repository tree | `ccba7f3673f2ed918a8c4cdf5556156bbad3ca18` |
| Affected contract | `VS01StudyWorkspaceProjection` `1.0` |
| Workspace identity | `9f9f9dd44384d90da5b3918e96ad3623e1235016f6283d224259cba9b670816d` |
| Projection fixture SHA-256 | `6e55a7f77cc8b51e632f5a07877abe4fc12145c8b0b27b3eb7a7fde2de24d96e` |
| Defective schema SHA-256 | `296a49c51b261eb0fa5ef366787a6049426488d791ef5c77460811ee8c53ef2e` |
| Expected local T09B compatibility commit | `63b9d24c200aa23c663d9e5d99a9157b6765dfe9` |
| Disposition | **P1 implementation blocker; narrow authority repair required** |

## Defect

The merged schema contains a nonempty object `const` together with
`additionalProperties: false`, but it declares neither `type: object` nor
top-level `properties`.

Consequently, the exact frozen projection is rejected as containing additional
properties, and Ajv strict mode rejects the schema's object-keyword usage.

The defect originates in `_projection_schema`, which clears Pydantic's generated
object shape and emits only `$schema`, `title`, `additionalProperties`, and
`const`.

## Frozen correction

The committed schema must contain:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "VS01StudyWorkspaceProjection",
  "type": "object",
  "properties": {
    "<each exact frozen top-level key>": {}
  },
  "required": [
    "<all exact frozen top-level keys>"
  ],
  "additionalProperties": false,
  "const": {
    "<the exact unchanged committed workspace projection>"
  }
}
```

The exact top-level keys are:

```text
accepted_alternative_ids
active_context
answer_mode
audit_bindings
citation_records
claim_records
contract
evidence_horizon
evidence_inspector
evidence_records
greek
material_unknown_claim_ids
operation_disclosure
page_study
question
route
schema_version
study_blocks
translations
workspace_id
workspace_identity
```

The `properties` entries may be empty schemas because the exact `const` remains
the complete semantic authority. The explicit object shape exists to make the
schema satisfiable and standards-conforming while preserving
`additionalProperties: false`.

## Authority effects

This erratum changes only the machine-readable schema and its registry hash.

It does **not** change:

- contract name or schema version;
- workspace identity;
- projection fixture bytes;
- scholarly content, claims, evidence, citations, page authority, or audit bindings;
- any endpoint, dependency, persistence, or runtime authorization.

The corrected schema is generated in the Python contract. Web tooling must copy
and consume it exactly. No in-memory repair, replacement schema, relaxed Ajv
mode, or alternative schema authority is permitted.

## Same-PR continuation waiver

To avoid discarding the preserved T09B work, the owner may authorize this
erratum and T09B continuation in the same branch and eventual PR:

```text
63b9d24c200aa23c663d9e5d99a9157b6765dfe9
    -> focused schema-authority repair commit
    -> T09B implementation commit
    -> handoff-only commit
```

The existing activation/compatibility commit remains unchanged. This erratum
supersedes only its old-schema-unchanged clauses.

## Required validation

Positive:

1. Python Draft 2020-12 schema check passes.
2. Python validates the exact committed fixture.
3. Ajv 8 strict mode compiles the exact committed schema.
4. Ajv validates the exact committed fixture.

Negative:

1. Extra top-level property rejects.
2. Missing top-level property rejects.
3. Changed projection content rejects after outer identity recomputation.
4. Browser-local schema copy must be byte-identical to the committed schema.

## Additional T09B findings to close

- Render all seven frozen Study blocks exactly once and in order.
- Disable and test trailing-slash redirects.
- Use lazy CLI imports for the web command.
- Strengthen keyboard and responsive assertions across every frozen surface.

## Freeze statement

> VS01-T09-ERRATA-01 repairs only the satisfiability of the exact T09A JSON
> Schema. The workspace instance, identity, scholarly authority, and T09B
> product boundary remain unchanged.
