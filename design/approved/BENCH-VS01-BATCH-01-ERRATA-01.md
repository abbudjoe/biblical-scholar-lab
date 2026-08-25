# BENCH-VS01-BATCH-01-ERRATA-01 — B10 Case-Hash Canonicalization Compatibility

| Field | Value |
|---|---|
| Erratum ID | `BENCH-VS01-BATCH-01-ERRATA-01` |
| Status | **CHATGPT FROZEN — OWNER APPROVAL REQUIRED** |
| Applies to | `BENCH-VS01-BATCH-01`, `VS01-T07` |
| Approved source batch SHA-256 | `4241a0bf5baf50a12ce5fe6dcfef6ed5492cde410f3d92f5aad8a9f26ba3113f` |
| Affected case | `VS01-B10-C01` |
| Source-declared B10 hash | `dccf12a80604494847853850d86706da17dce45e4663cedbf6c07a68f2d3fa06` |
| RFC 8785 B10 hash | `f158ea959695243e18c6fc46661387d17f7fe2268bd479f24db02ef868ac7eab` |
| Semantic benchmark change | **None** |
| Source case-file change | **None** |

## Finding

The implementation preflight correctly found that the declared B10 case hash
does not equal an RFC 8785 recomputation.

The defect is not stale case content. The approved batch's case hashes were
produced with a legacy canonicalizer equivalent to:

```python
json.dumps(
    case_without_case_content_sha256,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
```

B10 is the only case that exposes the difference because its degradation
specification contains the JSON number `18.0`.

```text
Legacy numeric serialization:
18.0

RFC 8785 / ECMAScript numeric serialization:
18
```

All other cases use values whose legacy and JCS lexical forms coincide, so
their declared and RFC 8785 hashes are identical.

## Binding resolution

The approved benchmark case file remains byte-for-byte authoritative:

```text
design/approved/BENCH-VS01-BATCH-01-cases.json
SHA-256: 4241a0bf5baf50a12ce5fe6dcfef6ed5492cde410f3d92f5aad8a9f26ba3113f
```

T07 must bind two non-equivalent identities:

```text
Source-declared compatibility identity:
dccf12a80604494847853850d86706da17dce45e4663cedbf6c07a68f2d3fa06

RFC 8785 execution identity:
f158ea959695243e18c6fc46661387d17f7fe2268bd479f24db02ef868ac7eab
```

The source-declared hash proves compatibility with the approved batch bytes.
The RFC 8785 hash is used in all new T07 sample, case-result, and run-result
identities.

Every T07 record must retain both values. Neither may be mislabeled.

## No semantic revision

This erratum does not change:

```text
prompt
evidence contract
degradation specification
answer contract
deterministic checks
rubric
reference response
review state
contamination state
rights state
case order
benchmark-file hashes
```

No B10 case revision is created because the measurement instrument is
unchanged. This is a serialization-compatibility repair only.

Future benchmark cases and any future content revision must use RFC 8785
directly and may not inherit this legacy exception.
