# DR-30 — Implementation Readiness, Simplicity, and Anti-Slop Contract

| Field | Value |
|---|---|
| Design ID | `DR-30` |
| Status | `APPROVED` |
| Approval date | 2026-08-17 |
| Project owner | Joseph Abbud |
| Product, architecture, benchmark, and experiment designer | ChatGPT |
| Independent implementation and evidence reviewer | ChatGPT |
| Depends on | DR-01 through DR-29 |
| Scope | All production code, tests, schemas, migrations, infrastructure, prompts, CI, adapters, generated code, and Sol root turns implementing the approved design baseline |
| Implementation authority | GPT-5.6 Sol exclusively writes, repairs, and refactors production implementation and is accountable for activation and simplicity conformance |
| Execution authority | GPT-5.6 Luna may execute only frozen operations delegated by Sol and may not write, repair, refactor, configure, or redesign code |
| Governance authority | ChatGPT defines activation scope and reviews exact-head implementation evidence; Joseph Abbud approves activations, waivers, merges, progression, and releases |
| Approved change | Establishes immutable implementation activation manifests, vertical-slice-first delivery, globally unique code identifiers, hard simplicity and dependency budgets, anti-scaffolding rules, public-repository governance, the initial Mac mini/MacBook topology, and implementation-readiness gates that prevent the approved future architecture from becoming speculative code bloat |

## 1. Governing principle

> **Build the smallest complete system that proves the currently approved capability. Do not implement a future abstraction, package, table, service, interface, adapter, flag, or extension point until an activated requirement and present consumer justify it. Correctness, auditability, and simplicity outrank architectural ceremony. Removing unnecessary code is progress.**

DR-01–DR-29 remain the normative future design. DR-30 governs **when and how those designs become physical code**.

## 2. Authority

- Joseph approves the implementation activation, waivers, merges, and releases.
- ChatGPT defines activation scope, reviews implementation and evidence, and recommends repair or progression.
- GPT-5.6 Sol is the exclusive production-code author and is accountable for simplicity conformance.
- GPT-5.6 Luna performs only frozen operations delegated by Sol. It cannot write, repair, refactor, configure, or redesign code.

No task prompt or nested `AGENTS.md` may weaken this contract.

## 3. Normative design versus activated implementation

Every approved design requirement has one implementation state:

```text
NORMATIVE_FUTURE
ACTIVATED_FOR_CURRENT_SLICE
IMPLEMENTED_AND_VERIFIED
DEFERRED_BY_APPROVED_NON_GOAL
SUPERSEDED
BLOCKED_REQUIRES_DESIGN_REVIEW
```

`NORMATIVE_FUTURE` means the future system must eventually respect the design. It does **not** authorize immediate scaffolding.

### Prohibited inference

```text
A contract is named in a DR
    therefore
create a class/table/package/API for it now
```

is invalid.

## 4. Implementation Activation Manifest

Every Sol root turn receives one immutable `ImplementationActivationManifest` containing:

```text
activation_id
approved design IDs and commits
root-turn objective
vertical-slice identity
activated user-visible capability
activated invariants
activated contracts and schema revisions
activated modules and data stores
activated endpoints/CLI commands
activated tables and migrations
activated external adapters
required tests and evidence
explicit non-goals
prohibited future scaffolding
size/dependency budgets
waivers already approved
completion criteria
```

The manifest is the implementation boundary.

### Activation rules

1. Unactivated contracts receive no production stub, public type, database table, migration, endpoint, feature flag, service, or TODO.
2. A future contract may be represented in design documents and fixtures without production code.
3. Sol may report that another contract is now required, but must stop with `BLOCKED_REQUIRES_DESIGN_REVIEW` rather than activating it independently.
4. A root turn may activate only the minimum contracts needed for one coherent capability.
5. Every implementation handoff maps changed code back to activated requirements.

## 5. Vertical-slice-first implementation

The first implementation must follow one observable user workflow from source acquisition through answer rendering and audit.

It must not begin by constructing all infrastructure layers independently.

The default first slice is the separately approved `VS-01`.

A vertical slice may use deliberately simple internal implementations when they satisfy the current contract and leave a clear migration path. It may not use fake behavior, hard-coded scholarly conclusions, or hidden data that bypass the intended authority model.

## 6. Initial physical repository layout

DR-28 logical authorities do not require one physical package each.

The initial Python implementation should begin with:

```text
src/bsl/
    contracts/          # activated normative schemas and IDs
    domain/             # activated scholarly and policy logic
    application/        # use cases and orchestration
    infrastructure/     # PostgreSQL, archive, model/tool adapters
    interfaces/         # CLI and later HTTP boundary

contracts/              # canonical JSON Schema/OpenAPI/fixtures
migrations/
tests/
docs/
```

A web application may be added only when the first UX slice is activated:

```text
web/
```

The following do **not** become separate applications in the initial slice:

```text
worker
scholar-runtime
model-gateway
campaign-controller
```

They begin as modules or CLI subcommands in the same Python distribution. A separate process or deployable is created only for a demonstrated security, hardware, scaling, failure-containment, or lifecycle need.

### No empty namespaces

A directory or package is created only when it contains real activated behavior. Empty `__init__.py` forests, placeholder packages, and future-service shells are prohibited.

## 7. Globally unique identifiers

Short names that collide across designs may appear only in local explanatory prose.

Code, schemas, database records, metrics, logs, events, handoffs, and public contracts use globally unique canonical names.

Initial canonical map:

```text
TNC-A0 … TNC-A6           Translation Nuance architecture ladder
ACCESS-A0 … ACCESS-A6     ancient-version/apparatus access lanes
ASSURE-A0 … ASSURE-A3     runtime assurance classes
RETRO-R0 … RETRO-R5       retroversion restraint
RELEVANCE-R0 … R4         corpus relevance
TRAIN-S0 … TRAIN-S8       training curriculum stages
SENS-S0 … SENS-S8         sensitivity classes
QUALITY-Q0 … QUALITY-Q6   corpus quality
QUANT-Q0 … QUANT-Q6       quantization ladder
CTX-P0 … CTX-P3           context priority
```

Additional collisions discovered during implementation require registry amendment before use.

## 8. Simplicity order of preference

When several designs satisfy the activated contract, choose in this order:

1. Plain immutable typed data plus pure functions.
2. Explicit composition of small stateful objects.
3. Direct use of a mature library behind the approved boundary.
4. A narrow project-owned adapter that enforces authority or compatibility.
5. A generalized abstraction only after at least two real consumers require it.
6. A new service or framework only after measured evidence shows the simpler arrangement is inadequate.

## 9. Code size and complexity budgets

These are default hard review thresholds. Exceeding them requires a committed `SIMPLICITY_WAIVER` explaining why splitting would make correctness or auditability worse.

```text
Function or method:
    <= 60 logical lines

Cyclomatic complexity:
    <= 10

Logical nesting:
    <= 3 levels

Handwritten production class:
    <= 250 logical lines

Handwritten production module:
    <= 500 logical lines

Root-turn PR target:
    300–1,000 substantive changed lines

Mandatory split-or-waiver review:
    > 1,500 substantive changed lines
    or > 25 handwritten production files
    or > 5 new public contracts
    or > 3 new database migrations
```

Generated files, dependency lockfiles, approved benchmark fixtures, imported source snapshots, and mechanical migrations are reported separately and must be reproducible.

A numeric limit may never justify obscuring behavior, compressing code unnaturally, or combining unrelated responsibilities.

## 10. Abstraction rules

### Prohibited by default

- Generic repository pattern over SQLAlchemy
- Generic unit-of-work framework
- Service locator
- Dependency-injection framework
- Generic plugin system
- Custom ORM
- Custom migration engine
- Custom logging framework
- Custom cryptography
- Custom event broker
- Generic rule engine
- Generic workflow DSL
- Speculative cache abstraction
- Catch-all “manager” classes
- Broad “base” classes without shared semantics

### Interface threshold

An abstract interface is created only when:

- There are at least two real implementations; or
- The boundary is already approved because it isolates external authority, provider behavior, persistence, inference, framework execution, security, or irreversible artifacts.

### No dumping grounds

These names are prohibited as catch-all modules:

```text
utils.py
helpers.py
common.py
manager.py
base.py
misc.py
```

A narrowly named local helper module is acceptable only when its responsibility is explicit.

### Wrapper rule

A project-owned wrapper must enforce at least one material property:

- Scholarly semantics
- Rights/privacy/security
- Identity/provenance
- Verification
- Audit
- Framework/provider replaceability
- Resource/budget authority

A wrapper that merely renames a library call is deleted.

## 11. Dependency discipline

Every new direct dependency requires a handoff entry stating:

- Capability it provides
- Why the standard library or an existing dependency is insufficient
- License and maintenance status
- Security and supply-chain implications
- Alternatives considered
- Removal strategy

### Initial budgets

```text
Core Python runtime direct dependencies:
    <= 12, excluding separately installable adapter extras

Initial web runtime direct dependencies:
    <= 10
```

Optional model, evaluation, training, provider, OCR, and mobile adapters must live in separately installable extras or packages so the core installation does not pull the entire research stack.

Two libraries may not perform substantially the same role in production until an approved bakeoff selects one or explicitly preserves both for different roles.

## 12. Initial implementation toolchain

The build package should require the following baseline unless a compatibility probe produces a design-reviewed exception:

### Python

```text
Python 3.12
uv for environment and lock management
Pydantic v2 for activated portable contracts
SQLAlchemy 2 + psycopg 3 for PostgreSQL
Alembic for migrations
FastAPI only when the HTTP interface is activated
Ruff format and lint
Pyright strict
pytest + Hypothesis
coverage.py
```

### Web, when activated

```text
TypeScript strict
pnpm
React + Vite
Biome
Vitest
Playwright
Ajv or generated validators from project JSON Schemas
```

Sol pins exact compatible versions after one reviewed compatibility probe. Sol may not replace the toolchain because of personal preference.

## 13. Public API and schema discipline

- One canonical schema source exists for every public record.
- Generated language types derive from canonical schemas where practical.
- No duplicate handwritten Python and TypeScript definitions are allowed to drift.
- Breaking contract changes require design approval and migration evidence.
- Internal classes do not become public contracts by accident.
- JSONB does not substitute for activated typed domain fields.
- No endpoint is created without an activated client or workflow.

## 14. Database and migration discipline

- No table is created only because a logical object appears in a DR.
- A table needs an activated transaction, query, invariant, isolation requirement, or lifecycle.
- Migrations are small, reviewed, forward-tested, and restore-tested where material.
- No automatic production migration occurs on application startup or merge.
- Foreign keys, uniqueness, check constraints, and RLS encode critical invariants where appropriate.
- No generic entity-attribute-value schema is used to avoid designing activated fields.
- No premature partitioning, sharding, or replication.

## 15. Error and fallback discipline

- Failures are explicit typed outcomes.
- No silent fallback among models, providers, editions, languages, indexes, storage locations, or security routes.
- Broad exceptions are caught only at process or external boundaries, logged without sensitive content, and converted to approved typed failures.
- Retry policy belongs to the approved operation and error class.
- A fallback that changes scholarly or experimental meaning requires design review.

## 16. Prohibited merged code

The following are not mergeable in production code:

- Required behavior represented by `TODO` or `FIXME`
- Commented-out code
- Dead code
- Unused public API
- Production `pass`
- Production `NotImplementedError`
- Placeholder return values
- Hard-coded benchmark gold or scholarly conclusions
- Hidden network calls
- Hidden configuration or feature flags
- Broad mutable global state
- Untyped public functions
- Runtime monkey-patching
- Copy-pasted logic that should be one local function
- Snapshot-only assertions for semantic behavior
- A mock that bypasses the invariant under test

A deliberately unimplemented future capability stays absent and is recorded as an explicit non-goal, not a stub.

## 17. Testing contract

### Required layers

- Pure unit tests for domain rules
- Property-based tests for identifiers, hashes, state transitions, rights intersections, and serialization
- Contract tests for adapters
- PostgreSQL integration tests for database behavior
- Golden fixtures only for deterministic portable formats
- End-to-end vertical-slice tests
- Failure-injection tests for irreversible or billable operations

### Coverage floors

```text
Changed handwritten production code:
    >= 90% branch coverage

Critical invariant modules:
    target 100% branch coverage
```

Critical modules include:

- Rights decisions
- Retention and purge
- Canonical serialization and hashing
- State-machine transitions
- Campaign cost and authority
- Archive promotion
- Benchmark split firewall
- User/tenant isolation

Coverage is not proof. A test suite that does not assert the approved invariants fails review even at 100%.

Every bug receives a regression test before the repair is accepted.

Default tests make no live network or paid-provider calls.

## 18. Documentation and comments

- Comments explain why, invariants, provenance, legal/scholarly constraints, or nonobvious tradeoffs.
- Comments do not narrate obvious code.
- Public APIs have concise contract documentation.
- Architecture diagrams are generated or kept close to active code; no speculative component diagrams are added.
- One source of truth exists for setup and commands.
- Root documentation remains short and links to authoritative detail.

## 19. Generated code and artifacts

Generated outputs are allowed only when:

- The generator is versioned and reviewed.
- Inputs and command are recorded.
- Regeneration is deterministic where claimed.
- Generated files are clearly marked.
- Generated output is not hand-edited.
- CI verifies that committed generated artifacts are current.

## 20. Performance and optimization

- No performance framework is introduced without a measured bottleneck.
- Optimize after correctness and profiling.
- Every optimization has a before/after benchmark and semantic-equivalence test.
- Caches require an explicit invalidation contract.
- A custom kernel requires the profiling and equivalence gates already approved in DR-06/DR-12/DR-23.
- “More scalable” is not a reason to add infrastructure before the vertical slice demonstrates need.

## 21. Security, rights, privacy, and public-data boundaries

Simplicity may not weaken:

- Rights checks
- Tenant isolation
- Private benchmark firewall
- Secrets boundaries
- Provider routing
- Audit receipts
- Purge and deletion
- Thunderbolt archive authority
- Lambda budget and termination controls

A shorter implementation that bypasses these requirements is not elegant; it is incorrect.

## 22. Root-turn and pull-request budget

One Sol root turn should implement one coherent capability and produce one draft PR.

Every PR must:

- Start from reviewed `main`.
- Reference one activation manifest.
- Contain no unrelated cleanup.
- Separate mass formatting or dependency upgrades from behavior changes.
- Preserve reviewed commit history without force-push after review begins.
- Produce one consolidated handoff after all delegated Luna operations finish.

### Complexity receipt

The handoff records:

```text
handwritten production LOC added/removed
test LOC added/removed
generated/imported LOC
production files added/removed
packages/modules added/removed
database tables and migrations added/removed
endpoints and CLI commands added/removed
direct dependencies added/removed
public contracts added/changed
abstractions introduced and their current consumers
simpler alternatives considered
known duplication or debt
waivers
SIMPLICITY_CONFORMANCE
```

Allowed dispositions:

```text
PASS
WAIVER_REQUIRED
BLOCKED_REQUIRES_SPLIT
BLOCKED_REQUIRES_DESIGN_REVIEW
```

Sol may not call its own work merge-ready.

## 23. Review and waiver policy

A simplicity waiver must state:

- Rule exceeded
- Exact measured amount
- Why splitting or simplifying would make correctness, auditability, or safety worse
- Alternatives attempted
- Removal or reevaluation condition
- ChatGPT review disposition
- Joseph approval

A waiver is scoped to one artifact or root turn. It is not precedent.

New commits invalidate prior code review.

## 24. Public repository governance

Before production implementation begins, the public repository must include:

- Root `AGENTS.md` containing this contract and the authority model
- `.github/CODEOWNERS` assigning Joseph as owner of all paths
- Draft PR template requiring activation and complexity receipts
- Machine-readable handoff schema
- Protected `main`
- No direct pushes or force pushes
- Stale approval dismissal
- Required review-conversation resolution
- Separate non-owner Codex identity
- Joseph as the only account able to submit the owner approval and merge
- ChatGPT review record bound to the exact PR head

The independent Codex PR review may supplement but not replace ChatGPT review.

## 25. Public repository licensing

Approved bootstrap policy:

```text
Code:                         Apache-2.0
Project-authored docs/design: CC BY 4.0
Public P0/P1 benchmark cases: CC BY 4.0, subject to component rights
Third-party assets/data:      original component licenses
Contributions:                DCO 1.1 sign-off
```

No repository-level license may silently relicense third-party content, model weights, datasets, images, or restricted evidence.

## 26. Initial Mac topology

The initial physical role allocation is:

### Mac mini M4, 16 GB

- Local user application
- Active PostgreSQL database
- Local compact-model inference
- Bounded derived lexical/vector indexes
- Temporary scratch
- Local web/API interface

### MacBook Pro plus Thunderbolt volumes

- Authoritative `BSL-Archive`
- Authoritative `BSL-Private`
- Backups and restore authority
- Lambda Control Broker
- Campaign controller and archive relay
- Artifact promotion, release, and purge receipts

The Mac mini may consume signed/versioned projections from the MacBook archive workflow. It must not use a network-mounted archive as mutable application storage.

If the MacBook or authoritative drive is unavailable, the Mac mini may serve already activated local material in a degraded local mode. It may not:

- Launch Lambda
- Promote a new authoritative artifact
- Claim archival completeness
- Finalize a purge, release, or benchmark freeze
- Create a new canonical backup

## 27. Documentation normalization

Before package freeze, a nonsemantic cleanup must:

- Remove unused footnote definitions.
- Replace stale proposal language in approved records with current language.
- Normalize SHA sidecars to `<hash><two spaces><repo-relative-path>`.
- Keep historical Git commits intact.
- Generate a compact design summary and global terminology index.
- Mark every earlier build package obsolete.

The cleanup must produce zero semantic changes. Any semantic ambiguity found during cleanup returns for design review.

## 28. Implementation gates

```text
IR-00 — DR-30, namespace registry, and public-governance activation
IR-01 — Activation-manifest and complexity-receipt validators
IR-02 — Minimal repository/toolchain skeleton
IR-03 — VS-01 vertical-slice fixtures and acceptance contracts
IR-04 — Source-plan and seed-benchmark readiness
IR-05 — Documentation normalization and final package audit
IR-06 — Independent clean-room package review
```

No production domain implementation begins before IR-00 through IR-05 close. IR-06 closes before the first substantial Sol domain task.

## 29. Hard failures

- Creating packages, tables, interfaces, or services for unactivated future contracts
- Empty or placeholder production packages
- Unreviewed activation expansion
- Hidden fallback or configuration
- One class/table per design noun without present behavior
- A generic framework replacing explicit domain logic
- A direct dependency without justification
- An oversized PR without split or waiver review
- Tests that bypass the approved invariant
- Claiming completion with TODOs or stubs
- Sol or Luna changing experiment or benchmark semantics
- Luna writing code
- Direct or automatic merge to `main`
- Joseph’s owner approval being impersonated by a bot credential
- Public release of third-party material under the project license
- Using “future scalability” to bypass the modular-monolith and vertical-slice rules

## 30. Approval statement

> **Biblical Scholar Lab will translate the complete DR-01–DR-29 future architecture into production code only through immutable implementation activation manifests and bounded vertical slices. Unactivated future contracts will remain design obligations rather than production stubs. The physical repository will begin as one small modular Python application with explicit domain, application, infrastructure, contract, migration, test, and interface boundaries; logical design namespaces will not automatically become packages, tables, services, interfaces, or extension points. Sol will prefer plain typed data, pure functions, direct composition, mature libraries, and narrow authority-bound adapters; speculative abstractions, duplicate wrappers, catch-all modules, generic plugin or dependency-injection frameworks, hidden configuration, placeholder code, unnecessary dependencies, and future-service scaffolding will be prohibited. Every root turn will operate under code-size, complexity, dependency, test, activation, and review budgets and will publish an exact complexity receipt. Critical scholarly, rights, identity, purge, campaign, archive, benchmark, privacy, and security invariants will receive contract, property, integration, failure-injection, and regression testing. The Mac mini will host the initial active local application, PostgreSQL, inference, and derived projections, while the MacBook Pro and encrypted Thunderbolt volumes retain authoritative archive, private-vault, backup, Lambda-control, artifact-promotion, purge, and release responsibilities. A public repository will use protected `main`, Joseph-only owner approval and merge authority, exact-head ChatGPT review, a separate non-owner Codex identity, and an append-only Sol handoff after every root turn. No implementation will proceed merely to mirror the breadth of the future design; the project will add code only when one approved user-visible capability and its evidence require it.**
