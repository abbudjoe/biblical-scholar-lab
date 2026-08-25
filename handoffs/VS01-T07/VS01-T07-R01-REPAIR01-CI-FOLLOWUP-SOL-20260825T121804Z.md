# VS01-T07-R01 Repair01 CI follow-up handoff

Disposition: `READY_FOR_CHATGPT_REVIEW`

This append-only pair supersedes `VS01-T07-R01-REPAIR01-SOL-20260825T114005Z` for exact-head review evidence. The authorized starting head was `b678f4d1dccbaa1aefd15eafe1ea1c6d08783469`. The single test-only corrective commit is `e3ef9bf91e06905bd68f652d6edbc0e906ce1045` / tree `334a067b326a7f97289c0cd44a3468f3e9c2a8e4`.

## CI root cause and correction

The previous `vs01-t01-ci` failure was caused solely by `test_inventory_child_and_fixture_hashes_stable` opening the intentionally ignored `.local/evidence/VS01-T07/Repair01/deterministic-check-inventory.json`. The GitHub runner correctly lacked that local evidence file. The failed run otherwise reached 90.13% coverage, and `vs01-t05-ci` passed.

The corrected test no longer references `.local` or any local evidence filename. It loads the committed byte-preserved benchmark authority, compiles each scorer plan through the production closed dispatcher, and requires this exact in-memory inventory:

```text
CLAIM_SOURCE_MAP        5
EXACT_FIELD             6
EXACT_STRING            3
FORBIDDEN_STRING        1
ONLY_CANONICAL_QUOTE    1
REGION_ROLE_MAP         1
REQUIRED_EVENT          1
REQUIRED_SOURCE_HANDLE  1
SESSION_STATE           2
TEXT_QUOTE_SELECTOR     1
total                  22
```

The in-memory inventory identity is `fb0acd381da02f3e309fda6b503c25a9cbdfbca3c03c3b769ea45edc01f4b33c`. The child-source identity remains `f1fc21fe8e822c6ed04ae184e597e36b8f92021c6c7b9472cdeaea9c6af2741a`.

Exactly one path changed in the corrective commit: `tests/test_vs01_benchmark.py`, with 17 additions and 2 removals. No ignored evidence was read during either final validation, and nothing under `.local` was committed, copied, or synthesized into Git.

## Preserved Repair01 implementation

The complete Repair01 production implementation remains `5be3910772d80d8a41716b67d42c71e40e1042e9` / tree `8e30d0607701bed95941bf002b810c17a36d2918`. Production modules, exactly four public contracts, generated schemas, fixtures, registry, benchmark sources, design, protocol, errata, activation, dependencies, lockfile, migrations, workflows, CLI, README, status, and decision-index files are byte-for-byte unchanged from the authorized starting head.

The approved batch Markdown/JSON remain `f1f0be8a3be9b4f56de0968ad3f166306a4fdfbdd57e7a45a5d972bbb50b66ff` / `4241a0bf5baf50a12ce5fe6dcfef6ed5492cde410f3d92f5aad8a9f26ba3113f`. B10 remains compatibility `dccf12a80604494847853850d86706da17dce45e4663cedbf6c07a68f2d3fa06` and RFC 8785 execution `f158ea959695243e18c6fc46661387d17f7fe2268bd479f24db02ef868ac7eab`. The complete matrix identity remains `c2b3c8748873ad7327fba09dacb3a6fec81f3fcd7a670684e8c707d3aa42c176`.

Schema hashes remain:

```text
execution specification 3eef6f98891bd50c9c7f599429640771a4a1822daf10c3b99bb99ab743926990
case result             5847505bad08ac1a833433b3bca4c0cfce9b968bb82cf7bf96cec48faec7283f
run result              8963a02d65337c637294c9d8eb2b5c0a2c0922925ad8d5e3279fa836ce79c6fc
execution receipt       c8caf7cb0bd32a0023b1c96b57d05f5be9edebf13b28b09b80d5b84fe2bd5d97
```

Reference fixture/projection hashes remain `ad582ad90758d60e6b3f773997f19565e86fdc59cf455baa1f9eec8859fe7c77` / `5954efa6c22eb3d295b8b01c58f61aced622ba7b10bda41d3081152a65f5f199`. Static compilation identity remains `fb1a2f7be5fd524bddac7b7b5d75d761c09488edef6e6150569221a3abb77be7`; operation-ledger conformance identity remains `4af2749d8c27539a3c3102683c332823de268c645da4af84c74c98a11d5cc7c5`.

## Follow-up Validation A and B

Both complete independent validations passed from `e3ef9bf91e06905bd68f652d6edbc0e906ce1045`:

- `uv sync --frozen` and `uv lock --check`;
- Ruff format, lint, complexity <=10, and nesting <=3;
- Pyright with zero diagnostics;
- complete pytest: 509 passed, 40 environment-gated skips, 90.10% branch coverage;
- offline Draft 2020-12 validation: four valid public documents accepted and four recomputed-identity structural adversaries rejected;
- schema drift and registry hashes;
- fixture double-reproduction, dual-hash matrix, static B01-B12 compilation, child isolation, 12 data-mutation adversaries, exact contracts, immutable ledger, verified-existing authority reload, and hardened store adversaries;
- `git diff --check` and `git fsck --full`.

The Validation A and B semantic receipts compare byte-for-byte equal. Each statically parsed 12 cases and compiled 12 subject packages, 12 scorer plans, and 12 reference fixtures. Real replay count, subject invocations, scoring invocations, case results, run results, receipts, and publication attempts all remained zero.

T04/T05/T06 fingerprints remained `27609cc1fd4cc6e1844fc4275dd5dd0ce8a485fb68f7f75dddd779005d70031d`, `b79810f9bf9cf327b0d40041b640a49079d9cbf5c043660e148ed2d5e38a14a1`, and `ec0b4018d30d7160213b20945461325be7821c4b7e666675de5529e4a76ed860`. Archive-root/incoming fingerprints remained `f45c8fe4be50573209e74d94214b94baf51a5f3a5b08108e855992063f79cd70` / `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`. Authority changed false; incoming changed false; archive writes and database writes zero.

## Simplicity and operational boundary

The owner-approved Repair01 waiver remains exactly production 1,568 + tests 524 + existing CLI/current-state prose 46 + registry/metadata 20 = 2,158. This follow-up reports its isolated test-only delta separately: 17 added + 2 removed substantive lines. It introduces no production file, contract, schema, fixture, dependency, migration, workflow, abstraction, or operational capability.

The public benchmark command was not invoked. No real benchmark case was executed or scored, no result or receipt was published, and no archive, database, model, OCR, VLM, network, web, cloud, training, T08, or later-task operation occurred. PR #16 remains open and draft; exact-head CI follows this handoff-only commit and push.
