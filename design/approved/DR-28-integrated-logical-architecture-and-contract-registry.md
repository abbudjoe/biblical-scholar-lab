# DR-28 — Integrated Logical Architecture and Contract Registry

| Field | Value |
|---|---|
| Design ID | `DR-28` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Product, architecture, benchmark, and experiment designer | ChatGPT |
| Independent implementation and evidence reviewer | ChatGPT |
| Depends on | DR-01 through DR-27, including DR-02 revision 2 and supplements |
| Implementation authority | GPT-5.6 Sol exclusively implements and repairs the approved integrated architecture, contracts, schemas, migrations, storage adapters, APIs, indexes, event records, services, conformance tests, and operational projections |
| Execution authority | GPT-5.6 Luna may execute only frozen migrations, imports, rebuilds, backups, restores, conformance tests, deployments, or campaign operations delegated by Sol; Luna may not change contracts, schemas, storage authority, migrations, rights boundaries, indexes, retention, routing, or architecture |
| Governance authority | ChatGPT defines the integrated logical and physical architecture, contract registry, authoritative-store boundaries, and conformance rules; Joseph Abbud approves consequential architecture, migration, deployment, and release decisions |
| Approved change | Consolidates DR-01 through DR-27 into one implementation-ready architecture; selects the initial authoritative stores, serialization and identity standards, service and package boundaries, graph and retrieval strategy, embedding and reranking registry, prompt/policy/configuration authority, model-serving gateway, retention and deletable private-vault architecture, source-acquisition and freshness framework, PostgreSQL work-control plane, event and audit model, external-archive layout, API conventions, migration policy, public-preview projection, and implementation gates required before Sol begins production code |


## 1. Purpose

DR-01 through DR-27 define the product promise, scholarly epistemology, scope and safety, canon and reference system, provenance graph, Translation Nuance Core, linguistic model, ancient versions and apparatuses, scholarship and citations, rights, foundation models, learned integration, multilingual and multimodal behavior, context and compaction, runtime, corpus, training, preferences, benchmark, evaluation, cloud execution, UX, privacy, security, and release.

Those decisions deliberately deferred several cross-cutting implementation choices until the components could be reconciled as a whole. DR-28 resolves those choices.

It defines:

- Which store is authoritative for each class of information;
- Which objects are immutable, which are versioned mutable identities, and which support governed erasure;
- How identities, revisions, hashes, external aliases, and cryptographic key scopes work;
- How graph, text, binary artifact, private-vault, vector, lexical, event, session, benchmark, evaluation, training, campaign, configuration, acquisition, inference, retention, and work data coexist;
- Which schemas and serializations are normative;
- Which indexes, model-serving records, framework checkpoints, configuration projections, and analytical tables are disposable projections;
- How prompts, policies, feature flags, source connectors, background workers, model routes, and services operate without ceding authority to a framework;
- How rights, privacy, provenance, user isolation, and benchmark firewalls are enforced in storage and retrieval;
- How the owner-controlled Thunderbolt archive participates in every data and model lifecycle;
- Which technology choices Sol must implement first;
- Which changes require another design review.

DR-28 is the final integrated preimplementation architecture review before production implementation begins. DR-29 remains a separately scoped mobile, edge, quantization, and distillation review.


## 2. Governing principle

> **Biblical Scholar Lab will use one project-owned contract registry, one authoritative transactional metadata and assertion store, one owner-controlled content-addressed research archive, and one separately encrypted, purge-capable private vault. Every graph cache, text index, vector index, prompt bundle, feature flag, source snapshot, work item, model endpoint, runtime checkpoint, framework state, model-facing packet, public-service database, training materialization, and analytical table will be an explicitly versioned projection that can be traced to—and, where claimed, rebuilt from—those authoritative records. Convenience frameworks, serving engines, connectors, queues, and indexes may accelerate the system; they may not become hidden sources of truth, hidden policy, or hidden authority.**

The architecture should remain:

```text
scholarly and evidence aware
rights and privacy partitioned
local-first for research authority
cloud-ephemeral for Lambda execution
modular but not prematurely distributed
portable across model families and runtime frameworks
rebuildable from immutable sources and manifests
observable without leaking user or restricted content
```


## 3. Architectural style: modular monolith first

The initial implementation will be a **modular monolith with separately runnable workers and controllers**, not a microservice fleet.

The reasons are:

- Most invariants span several scholarly domains and benefit from one transactional boundary;
- The project begins with one owner, one implementation engineer, a bounded research corpus, and limited compute;
- Premature service decomposition would multiply deployment, authentication, migration, observability, and consistency failure modes;
- The approved contracts already provide logical boundaries that can later become services if evidence justifies it;
- Local-first operation on the owner MacBook Pro and Mac mini should remain simple enough to reproduce and inspect.

The baseline process topology is:

```text
BSL API / application process
    → domain services and deterministic kernels
    → PostgreSQL authoritative metadata/assertion store
    → runtime configuration and policy activation
    → Thunderbolt research archive and private vault
    → rebuildable lexical/vector/read projections

BSL worker process
    → source acquisition, admission, normalization, indexing,
      evidence compilation, retention/purge work, evaluation import,
      artifact validation, and public projections

Background work controller
    → PostgreSQL work items, dependencies, leases, and backpressure
    → bounded local CPU/GPU/network/archive workers

Scholar Runtime process
    → project-owned Runtime Core
    → LangGraph operational adapter
    → Context Composer, TNSK, PEK, and verifiers
    → Model Inference Gateway
    → model and tool adapters

Campaign controller process on owner-controlled Mac
    → LambdaControlBroker
    → trainctl / evalctl / campaignctl
    → Lambda ephemeral instances
    → owner-pull Thunderbolt archive
```

These may initially run on one machine. They remain separate authority domains even when colocated.

A component may be split into an independent service only when a later review establishes at least one of:

- A materially different security or rights boundary;
- A materially different scaling profile;
- A need for independent failure containment;
- An independent deployment lifecycle;
- A benchmarked performance requirement that the modular monolith cannot satisfy;
- A public-service isolation requirement.

Microservice decomposition is not a prestige goal.


## 4. Authoritative-store hierarchy

### 4.1 Git repository

The public or private project Git repository is authoritative for:

- Approved design records;
- Source code;
- Contract schemas;
- Database migrations;
- Public-safe source manifests;
- Public benchmark material;
- Configuration templates;
- Test fixtures that are safe to publish;
- Small public-safe evaluation summaries;
- Release manifests and signatures where appropriate.

Git is **not** authoritative for:

- Corpus bytes;
- Restricted or user-private data;
- Private benchmark gold;
- Training materializations;
- Checkpoints;
- Vector indexes;
- Provider credentials;
- Large evaluation logs;
- Lambda scratch data.

### 4.2 PostgreSQL authoritative metadata and assertion store

The initial authoritative transactional database family will be **PostgreSQL**. PostgreSQL 18 is the verified stable reference baseline at the date of this design; the exact supported major and patch revision will be frozen at `IA-02` after compatibility, security, extension, migration, and local/hosted deployment validation.

It is authoritative for:

- Stable domain identities;
- Revision records;
- Assertions, evidence links, counterevidence, review state, and operational selections;
- Canon, reference, textual-history, linguistic, Translation Nuance, apparatus, scholarship, rights, acquisition, retrieval, configuration, inference, retention, work, benchmark, runtime, evaluation, training, campaign, security, and release metadata;
- User/session metadata where later authorized;
- Tool grants and state transitions;
- Append-only project events and transactional outbox records;
- Pointers and hashes for content stored in the artifact archive;
- Public/private/restricted partition and tenancy metadata.

PostgreSQL 18 is the current stable PostgreSQL release at the date of this design and provides the reference feature baseline. The selected implementation major must provide transactional relational storage, JSON/JSONB support, recursive queries, declarative partitioning, full-text search, row-level security, UUIDv7 support or a contract-compatible implementation, and approved extension compatibility. Row-level security becomes default-deny when enabled without a matching policy, which fits the project’s fail-closed private and restricted data model.[^postgres-rls] [^postgres-recursive] [^postgres-partition] [^postgres-json]

### 4.3 Owner-controlled Thunderbolt artifact archive

The owner-controlled external drive connected to the MacBook Pro through Thunderbolt remains the canonical retained store for:

- Acquired raw source artifacts;
- Immutable normalized-data artifacts;
- Parquet corpus snapshots and exposure ledgers;
- Images and page derivatives;
- Embedding and index build artifacts;
- Training and evaluation materializations;
- Resumable and model-only checkpoints;
- Adapters, merges, quantizations, and mobile conversions;
- Canonical raw training/evaluation logs;
- Result bundles, archive receipts, release candidates, and incident evidence;
- Database backups and immutable database snapshot manifests.

The external drive must use an encrypted APFS container exposing separately identified `BSL-Archive` and `BSL-Private` volumes, or an owner-approved equivalent that provides the same encryption-at-rest, stable-volume-identity, immutable-archive, and deletable-private-vault boundaries. Apple supports password-protected encrypted APFS formatting and multiple APFS volumes sharing one container.[^apple-apfs] [^apple-apfs-volumes]

The archive is immutable-by-convention and content addressed. It is not mounted as an ordinary mutable working directory for application logic.

### 4.4 Deletable private vault

The same external APFS container will expose a second encrypted volume with a separate stable volume identity:

```text
BSL-Archive
    immutable research and generated-artifact authority

BSL-Private
    deletable user-private and sensitive working vault
```

`BSL-Private` is authoritative for retained user uploads, private notes, saved sessions, personal corrections, private connected-library extracts, sensitive expert-review working material, and approved raw diagnostic captures. It is **not** content-address deduplicated across users or privacy domains.

Private objects receive envelope encryption in addition to volume encryption. Each object or bounded erasure domain receives an independently generated data-encryption key. Content is sealed with an approved authenticated-encryption construction; the initial reference is AES-256-GCM through a vetted cryptographic library, with unique nonces and authenticated metadata. Data-encryption keys are wrapped under owner-controlled key-encryption keys held in macOS Keychain or an approved equivalent owner-controlled secret store. The project will not implement cryptographic primitives itself.[^apple-keychain] [^apple-aes]

Deleting a wrapped key supports cryptographic erasure, but a purge is complete only after the project also removes or invalidates every live plaintext, ciphertext, index, cache, share, derivative, and backup reference required by the retention contract. A minimal nonrevealing tombstone may remain where lawful and necessary for audit.

Public or cross-user records may not expose predictable hashes of private content. Private integrity digests remain encrypted or keyed and access controlled.

### 4.5 Immutable tabular artifacts

Large normalized corpora, exposure ledgers, evaluation matrices, and other analytical datasets will use **Apache Parquet with explicit Apache Arrow schemas**.

Parquet is the canonical bulk columnar format because it supports efficient columnar storage and interoperates closely with Arrow. DuckDB will be the initial local analytical engine for querying Parquet snapshots without importing every analytical dataset into PostgreSQL.[^arrow-parquet] [^duckdb-parquet]

Parquet files are immutable artifacts. Updates create a new dataset manifest and new files.

### 4.6 Derived stores and indexes

The following are derived and rebuildable unless a later contract explicitly says otherwise:

- PostgreSQL materialized views;
- Lexical search vectors and trigram indexes;
- pgvector embeddings and approximate-nearest-neighbor indexes;
- Passage lookup projections;
- Graph adjacency and path caches;
- LangGraph checkpoints;
- Inspect AI logs after import into the project result bundle;
- Context packets and caches;
- Public-preview database projections;
- Model-server caches;
- Local analytical DuckDB databases;
- Frontend search indexes.

No derived store may contain information that cannot be traced to an authoritative revision and artifact hash.


## 5. Initial technology baseline

The initial implementation baseline is:

| Concern | Approved baseline |
|---|---|
| Primary implementation language | Python 3.12-compatible runtime for ML ecosystem stability; newer versions require compatibility evidence |
| Web client | TypeScript and React in a Vite-based application; exact accessible component primitives remain implementation-reviewed |
| HTTP API | FastAPI-compatible project adapter with project-owned schemas and OpenAPI 3.1.2 export |
| Authoritative metadata/assertions | PostgreSQL; version 18 is the design-date reference, exact supported major/patch frozen at `IA-02` |
| Vector retrieval | pgvector 0.8.x or later pinned compatible revision; exact model/configuration-specific homogeneous indexes |
| Provisional text embedding | `Qwen/Qwen3-Embedding-0.6B` at a frozen revision, subject to the approved retrieval bake-off |
| Provisional reranker | `Qwen/Qwen3-Reranker-0.6B` at a frozen revision, subject to the approved retrieval bake-off |
| Lexical retrieval | PostgreSQL full-text, trigram, exact canonical-reference, and domain-token indexes |
| Bulk tabular artifacts | Apache Parquet 2.6-compatible files with Arrow schemas |
| Local analytical query | DuckDB pinned revision |
| Runtime workflow | Project Runtime Core plus LangGraph v1 adapter |
| Runtime configuration | Git-authored immutable configuration artifacts plus PostgreSQL activation and deployment receipts |
| Reference inference | Direct Hugging Face Transformers adapter as the semantic reference path |
| Optimized inference | Project Model Inference Gateway with vLLM as the provisional primary adapter and SGLang as a mandatory comparator where model support permits |
| Evaluation execution | Project Evaluation Core plus Inspect AI adapter |
| Training execution | Project Training Core plus approved Transformers/FSDP2, ms-swift, and later gated adapters |
| Model tensors | Safetensors for model-only artifacts; PyTorch Distributed Checkpoint for resumable distributed state |
| Containers | OCI-compatible images pinned by digest |
| Contract language | JSON Schema Draft 2020-12 plus invariant validators |
| External API description | OpenAPI 3.1.2 |
| Canonical JSON hashing | RFC 8785 JSON Canonicalization Scheme |
| Stable IDs | UUIDv7 under RFC 9562 plus namespaced external aliases |
| Hash identity | SHA-256 |
| Event interchange | Canonical JSON/NDJSON event envelopes with schema IDs and hash-chain fields |
| Local archive filesystem | Encrypted APFS `BSL-Archive` volume, verified by stable volume identity |
| Private retained content | Separate encrypted APFS `BSL-Private` volume plus per-object envelope encryption and purge receipts |
| Source acquisition | Project-owned source connector and freshness framework with quarantine and immutable fetch receipts |
| Background work | PostgreSQL-backed leased work queue with `SKIP LOCKED`; `LISTEN/NOTIFY` only as a wake-up optimization |

OpenAPI 3.1.2 is selected rather than the newer 3.2 baseline because of current tooling maturity and its compatibility with JSON Schema-based API contracts. OpenAPI 3.2 may be adopted later through a compatibility-tested contract revision.[^openapi]


## 6. Why PostgreSQL is the initial integrated store

PostgreSQL provides the best initial balance of:

- Strong transactions;
- Referential integrity;
- Constraints and typed columns;
- Recursive graph traversal;
- JSONB for source-native extension data;
- Full-text search;
- Row-level security;
- Partitioning;
- Mature backup and migration tooling;
- Vector-search integration through pgvector;
- Local and hosted portability.

The project will **not** begin with Neo4j, a dedicated RDF triple store, Elasticsearch/OpenSearch, Qdrant, Weaviate, Kafka, or a separate event store.

Those may become adapters when a measured requirement justifies them. Starting with several authoritative databases would create cross-store consistency and rights-enforcement risks before the vertical slice proves a need.


## 7. Relational graph architecture

The textual-history and scholarly graph will initially be represented in PostgreSQL through a hybrid typed relational design.

### 7.1 Core graph records

The core contains typed records for:

```text
entity
entity_revision
assertion
assertion_revision
evidence_link
counterevidence_link
activity
activity_input
activity_output
agent
selector
external_identifier
review_record
operational_selection
snapshot
```

### 7.2 Domain-specific tables

High-value, frequently queried domain objects receive explicit typed tables, including:

```text
canon_profile
work_family
textual_form
edition
reference_scheme
reference_slot
text_segment
slot_binding
reference_mapping
linguistic_unit
linguistic_annotation
translation_work
translation_edition
translation_realization
translation_alignment
translation_difference_unit
translation_diagnosis
version_witness_role
apparatus_entry
scholarly_work
publication_version
scholarly_claim
rights_subject
benchmark_case
runtime_request
evaluation_campaign
training_run
cloud_campaign
artifact
```

The project will not reduce the entire scholarly domain to one generic EAV table.

### 7.3 JSONB boundary

JSONB is allowed for:

- Source-native metadata that must be preserved losslessly;
- Framework-specific operational state;
- Forward-compatible extension fields;
- Raw imported records before normalization;
- Debug or evidence projections that are not the normative domain contract.

JSONB is **not** allowed to hide required fields, rights decisions, stable relationships, or frequently queried normative values that belong in typed columns and constraints.

### 7.4 Graph traversal

Recursive CTEs and indexed adjacency tables are the first graph-query path. Materialized path and neighborhood projections may accelerate bounded queries.

A dedicated graph database becomes eligible only if benchmarked workloads show that PostgreSQL cannot meet an approved latency, traversal-complexity, or memory requirement without unreasonable complexity.


## 8. Initial hybrid retrieval architecture

The retrieval system begins with PostgreSQL and project-owned ranking logic.

### 8.1 Candidate channels

```text
exact canonical reference
exact source or identifier lookup
structured metadata filters
lexical full-text search
trigram/fuzzy alias search
domain-token and lemma search
citation-network expansion
translation-family expansion
vector semantic search
language- and source-specific specialist retrieval
```

### 8.2 Vector search

The initial vector extension is pgvector. It supports exact search and approximate HNSW and IVFFlat indexes, while retaining PostgreSQL transactions and joins. Approximate search trades recall for speed, so every promoted index configuration must be evaluated against exact search and retain its recall measurements.[^pgvector]

### 8.3 Partition and rights policy

Vector and lexical indexes must be partitioned or otherwise isolated by:

- Tenant/user privacy boundary;
- Rights/access zone;
- Private benchmark boundary;
- Public versus restricted source class;
- Embedding model revision where incompatible.

A filtered approximate index must not allow another tenant or rights zone to affect result recall in an unmeasured way. pgvector itself warns that multitenant approximate indexes can affect recall and recommends partitioning or separate tables for stronger isolation.[^pgvector]

### 8.4 Retrieval order and hybrid ranking

The initial logical route is:

```text
exact canonical and persistent-identifier resolution
    → rights, tenant, language, date, method, and source-type filtering
    → lexical, lemma, morphology, citation, and relation retrieval
    → dense or multi-vector semantic candidate retrieval
    → candidate fusion
    → query-conditioned reranking
    → source-diversity and dependence audit
    → exact evidence-span acquisition
```

The first hybrid ranker may use reciprocal-rank fusion followed by a cross-encoder or model reranker, but:

- Rights and tenancy filters run before model-facing selection;
- Exact canonical and source identity outrank semantic similarity;
- Source fitness and methodological relevance are explicit features;
- Dependent evidence does not gain authority merely through repeated retrieval;
- Retrieval logs preserve rejected candidates and route identity;
- A specialized search backend may replace a channel only after matched evaluation.


## 9. Embedding, reranker, and vector-index artifact architecture

The vector layer is not an invisible library default. It is a versioned retrieval subsystem whose exact model, instructions, dimensions, precision, chunking, and index parameters are part of the result identity.

### 9.1 Canonical embedding and reranking records

The Contract Registry defines:

```text
EmbeddingModelArtifact
EmbeddingProjection
VectorIndexSnapshot
RerankerArtifact
RetrievalRouteSpecification
RetrievalBakeoffRecord
IndexMigrationReceipt
```

`EmbeddingModelArtifact` binds:

```text
repository and immutable revision
weight and tokenizer hashes
license and rights lineage
pooling and normalization
maximum input length
query and document instructions
supported and selected dimensions
precision and quantization
runtime and hardware
validation and retirement state
```

`EmbeddingProjection` binds an exact source revision and span, text view, language, script, context-expansion policy, embedding instructions, dimension, normalization, vector hash, generating activity, rights, sensitivity, and tenant scope.

`VectorIndexSnapshot` binds one homogeneous embedding configuration, one source/graph snapshot, one distance metric and vector representation, one index algorithm and parameter set, all metadata filters, the build environment, recall evidence, activation state, and content hash.

Vectors from incompatible spaces are never mixed in one index or compared directly. Cross-index fusion occurs only after each route returns a normalized rank or calibrated score under a registered fusion policy.

### 9.2 Provisional text embedding and reranker

The provisional primary research-route candidates are:

```text
Qwen/Qwen3-Embedding-0.6B
Qwen/Qwen3-Reranker-0.6B
```

The official Qwen3 Embedding family supplies 0.6B embedding and reranking models, more than 100 claimed languages, instruction-aware retrieval, a 32K context, up to 1,024 dimensions for the 0.6B embedder, and Matryoshka dimension support. The exact English query instruction and document treatment are immutable configuration artifacts because Qwen reports that instructions materially affect retrieval behavior.[^qwen-embedding]

The initial scientific reference projection is normalized 1,024-dimensional output. The first pgvector operational projection is `halfvec(1024)` using exact cosine-equivalent search as the reference and HNSW as the provisional approximate index. Half-precision and HNSW must pass parent-relative recall and ranking equivalence before production activation.

Dimensions 512 and 768 enter the Matryoshka storage/quality screen. The system does not reduce dimensions merely to save space when doing so degrades ancient-language, counterevidence, or cross-lingual retrieval beyond the approved margin.

### 9.3 Mandatory retrieval bake-off

The initial candidate set is:

```text
Qwen3-Embedding-0.6B + Qwen3-Reranker-0.6B
BGE-M3 and its approved reranking path
EmbeddingGemma 300M
Qwen3-Embedding-4B as the capacity comparator
```

BGE-M3 is included because it supports dense, sparse, and multi-vector retrieval over multilingual inputs up to 8,192 tokens.[^bge-m3] EmbeddingGemma is included as the mobile/edge control because Google documents a 308M multilingual model with configurable dimensions, a 2K context, and quantized on-device operation.[^embeddinggemma]

The bake-off measures:

- Canonical and translation retrieval;
- Greek, Hebrew, Aramaic, transliteration, diacritic, and cantillation behavior;
- Same-lemma/different-sense and similar-passage hard negatives;
- Cross-language scholarship retrieval;
- Supporting and counterevidence recall;
- Translation Nuance source-state and lineage retrieval;
- Rights-filter and tenant-isolation behavior;
- Recall at fixed candidate counts;
- Reranked precision;
- Worst-language and worst-script performance;
- Index build time, size, latency, memory, local-Mac feasibility, and quantized regression.

Generic MTEB rank cannot select the project winner. Hard floors apply to Greek, Hebrew, cross-lingual scholarship, material counterevidence, and rights-safe filtering.

### 9.4 Index coexistence, migration, and retirement

A model or material configuration change creates a new index snapshot. It never mutates an active index in place.

The migration flow is:

```text
build new homogeneous index
    → run exact/approximate and old/new comparison
    → validate rights and tenant filters
    → run benchmark and shadow queries
    → activate through configuration registry
    → retain rollback index
    → retire after evidence and owner-approved policy
```

Every evaluation and product receipt records the exact embedding, reranker, index, fusion, and route snapshots.

### 9.5 Text and multimodal embeddings remain separate

Version-one page retrieval uses publication identity, layout metadata, OCR/ATR text, canonical passage links, and the text embedding route. A visual embedding model is a separate DR-14-derived experiment and may not silently replace or contaminate the text index.

## 10. Content-addressed archive design

The canonical immutable archive layout is project owned and lives only on `BSL-Archive`. The deletable private-vault layout is separately governed under the retention architecture and never shares the archive's cross-artifact content-address deduplication.

```text
<archive-root>/
    registry/
    objects/sha256/<first-two>/<full-hash>
    manifests/<artifact-type>/<stable-id>/<revision>.json
    snapshots/<snapshot-type>/<stable-id>/<revision>/
    checkpoints/<lineage>/<stage>/<run>/<checkpoint>/
    results/<evaluation-or-training>/<run>/
    databases/backups/<database-id>/<timestamp>/
    public-projections/<release-id>/
    quarantine/
    incidents/
    .incoming/
```

### 10.1 Object rules

- Object bytes are immutable.
- Object names derive from SHA-256, not user filenames.
- Original filenames and media types are metadata.
- Writes enter `.incoming` and are promoted atomically after validation.
- A manifest references every object by digest, size, media type, rights state, sensitivity, and derivation.
- Partial or invalid objects remain quarantined.
- Deleting a manifest does not automatically delete a shared object.
- Garbage collection requires a reachability analysis and owner-approved policy.

### 10.2 Volume identity

The archive root is accepted only when:

- The expected stable volume UUID or equivalent identity matches;
- The mount path is approved;
- The volume is writable and encrypted;
- Filesystem health and free-space checks pass;
- Atomic rename and hash verification pass;
- The project archive marker and schema revision match.

There is no automatic internal-disk fallback.


## 11. Contract Registry

The Git repository will contain the normative `ContractRegistry`.

Proposed layout:

```text
contracts/
    registry.json
    json-schema/
        core/
        provenance/
        canon/
        text/
        linguistics/
        tnc/
        versions/
        scholarship/
        rights/
        acquisition/
        retrieval/
        configuration/
        inference/
        retention/
        work/
        benchmark/
        runtime/
        evaluation/
        training/
        campaign/
        security/
        release/
    openapi/
    arrow/
    sql/
    fixtures/
    migrations/
```

Every contract records:

```text
contract_id
semantic version
status
owning DR
schema URI
compatible predecessors
breaking-change classification
migration requirement
reference fixtures
validator revision
content hash
```

JSON Schema Draft 2020-12 is the normative portable structural-schema language. It provides explicit dialect identifiers, validation vocabularies, dynamic references, and schema bundling support.[^json-schema]

Schemas alone cannot express every scholarly invariant. Project-owned invariant validators remain equally normative and are linked from the contract registry.


## 12. Runtime configuration, prompt, policy, and feature-flag registry

The project introduces a project-owned `RuntimeConfigurationRegistry`. It will not allow prompts, policies, tool descriptions, routing thresholds, context rules, or feature flags to become unreviewed behavior hidden in environment variables, model-server arguments, vendor dashboards, or mutable database text.

### 12.1 Authoritative configuration records

The Contract Registry defines:

```text
PromptArtifact
PolicyBundle
ToolSchemaBundle
GenerationProfile
ModelRoutePolicy
ContextPolicy
CompactionPolicy
RetrievalPolicy
FeatureFlagDefinition
EnvironmentConfigurationSnapshot
ConfigurationActivation
DeploymentConfigurationReceipt
```

Git is authoritative for reviewed configuration content. PostgreSQL is authoritative for environment-specific activation, compatibility, effective time, actor, rollback target, and deployment receipt.

Every consequential runtime, evaluation, training, and public-preview invocation binds one complete `EnvironmentConfigurationSnapshot` hash.

### 12.2 Prohibited hidden configuration

The following may not exist only in a process environment, command line, dashboard, notebook, or model-provider console:

- System or developer prompts;
- Scope and safety policy;
- Tool name, description, schema, or authority;
- Model routing and fallback;
- Generation temperature, top-p, output limit, or reasoning mode;
- Context and compaction thresholds;
- Retrieval instructions, fusion, candidate limits, or reranking;
- Verification thresholds;
- Feature flags that change evidence, safety, privacy, public claims, or benchmark semantics.

Environment variables are reserved for secrets, local addresses, and nonsemantic deployment coordinates. They reference approved configuration identities rather than containing the policy itself.

### 12.3 Promotion and rollback

A configuration change follows:

```text
reviewed artifact
    → compatibility and fixture validation
    → environment-specific activation proposal
    → owner-authorized activation where consequential
    → deployment receipt
    → monitored rollout
    → rollback or promotion
```

New consequential feature flags default off. Flags are scoped by environment and approved population, expire or receive explicit review, and have tested rollback paths.

No feature flag, prompt, or policy may change during a frozen benchmark, training, or cloud campaign. A change creates a new system or campaign identity.

### 12.4 Configuration drift detection

Startup and periodic checks compare the active process configuration with the approved activation snapshot. Unknown, missing, or mismatched artifacts fail closed for consequential workflows.

The audit receipt records the exact active prompt, policy, tool, route, context, compaction, retrieval, and generation revisions. Vendor-side mutable presets are prohibited unless their full state can be frozen and reproduced.

## 13. Canonical serialization and hashing

### 13.1 JSON records

Normative JSON records will:

- Declare their contract ID and version;
- Use UTF-8;
- Preserve Unicode strings without hidden normalization;
- Avoid duplicate keys;
- Represent exact decimal, monetary, and very large integer values as strings where ordinary JSON numeric semantics are inadequate;
- Use explicit UTC timestamps;
- Use RFC 8785 JCS for content hashing and signing.

JCS creates an invariant JSON representation through I-JSON constraints, deterministic primitive serialization, and recursively sorted object keys. It explicitly does not perform Unicode normalization, which is compatible with DR-07’s requirement to preserve exact ancient-script data.[^jcs]

### 13.2 Event streams

Append-only events use newline-delimited canonical JSON envelopes with:

```text
event_id
event_type
event_version
stream_id
stream_sequence
occurred_at
recorded_at
actor
correlation_id
causation_id
payload_schema
payload
previous_event_hash
event_hash
sensitivity
visibility
```

### 13.3 Tabular records

Parquet files bind an Arrow schema ID, field IDs, schema revision, row count, partition values, source manifest, and aggregate hash.

### 13.4 Human-readable projections

Markdown, HTML, CSV, CSL renderings, and reports are projections. They are never the only representation of a consequential record.


## 14. Identity and revision model

### 14.1 Stable entity IDs

Stable internal identities use UUIDv7. RFC 9562 defines UUIDv7 as a time-ordered UUID with a Unix-epoch millisecond field and random bits, giving sortable identities without encoding domain semantics.[^uuidv7]

Canonical string form:

```text
urn:bsl:<namespace>:<uuidv7>
```

Examples:

```text
urn:bsl:work:<uuid>
urn:bsl:edition:<uuid>
urn:bsl:assertion:<uuid>
urn:bsl:artifact:<uuid>
```

### 14.2 Revision IDs

Every mutable identity has immutable revisions:

```text
stable_id
revision_id
revision_number
content_hash
previous_revision
supersession_state
created_at
created_by
```

The revision ID is UUIDv7; the content hash is derived from canonical serialization. Neither substitutes for the other.

### 14.3 Content objects

Immutable bytes use SHA-256 content identity.

### 14.4 External aliases

DOIs, ISBNs, USFM codes, OSIS IDs, shelfmarks, sigla, ORCID, ROR, source database IDs, and model repository revisions are namespaced aliases attached through sourced assertions. They never become the internal primary key.


## 15. Schema evolution and migrations

### 15.1 Contract semantic versioning

```text
MAJOR
    breaking semantic or structural change

MINOR
    backward-compatible field or capability addition

PATCH
    clarification or validator correction without instance reinterpretation
```

### 15.2 Database migrations

PostgreSQL migrations will use an approved migration framework with SQL-visible, reviewed migration files. The initial implementation candidate is Alembic with SQLAlchemy 2 metadata, but migrations remain authoritative as reviewed SQL and migration manifests rather than ORM state alone.

Every migration records:

- Source and target schema revision;
- Reversibility or explicit irreversibility;
- Data migration logic;
- Preflight and postflight checks;
- Expected row and artifact impact;
- Backup/snapshot requirement;
- Rollback or forward-repair path;
- Content hash.

No production migration runs automatically on merge.

### 15.3 Artifact migrations

Immutable artifacts are not rewritten in place. A migration creates a new artifact, new manifest, and derivation event.

### 15.4 Projection compatibility

A stale projection is rejected or rebuilt. It cannot silently operate against an incompatible authoritative schema.


## 16. Database namespace and isolation layout

The initial PostgreSQL database will use explicit schemas:

```text
bsl_core
bsl_provenance
bsl_canon
bsl_text
bsl_linguistics
bsl_tnc
bsl_versions
bsl_scholarship
bsl_rights
bsl_benchmark
bsl_runtime
bsl_evaluation
bsl_training
bsl_campaign
bsl_security
bsl_config
bsl_inference
bsl_acquisition
bsl_work
bsl_retention
bsl_public_projection
bsl_outbox
```

### 16.1 Row-level security

RLS is mandatory for:

- User-private sessions, uploads, notes, and indexes;
- Restricted-source access;
- Private benchmark cases and gold;
- Reviewer assignments and blind judgments;
- Sensitive incident records;
- Public/private release projections.

Application database roles do not own protected tables and cannot use `BYPASSRLS`. Owner/admin access uses separate audited roles.

### 16.2 No silent delete

Ordinary corrections supersede records. User deletion or legal/rights removal uses a purpose-built purge workflow that:

- Removes or cryptographically destroys the targeted private content where required;
- Preserves a minimal nonrevealing tombstone and audit record where lawful;
- Invalidates derived indexes, caches, shares, and artifacts;
- Runs a downstream-impact analysis.


## 17. Retention, deletable private vault, purge, and cryptographic erasure

DR-10 and DR-27 require both immutable research provenance and effective deletion of user-private or withdrawn material. DR-28 resolves that tension by separating the immutable research archive from a deletable private vault and by making purge a versioned system workflow.

### 17.1 Retention objects

The Contract Registry defines:

```text
RetentionPolicy
RetentionAssignment
LegalOrRightsHold
PurgeRequest
PurgePlan
PurgeReceipt
CryptographicErasureReceipt
Tombstone
DependentArtifactImpact
DeletionPropagationStatus
```

Every retained object receives a purpose, sensitivity, retention class, expiration or event trigger, backup behavior, permitted derivatives, hold state, and purge authority.

### 17.2 Private-vault encryption and deduplication

`BSL-Private` uses encrypted APFS plus application-level envelope encryption.

- No cross-user or cross-purpose content-address deduplication;
- Random opaque object identities;
- One independently generated data-encryption key per object or approved erasure domain;
- Authenticated encryption using a vetted library, initially AES-256-GCM with unique nonces and authenticated metadata;
- Wrapped data-encryption keys under owner-controlled key-encryption keys in macOS Keychain or an approved equivalent;
- No raw private key material in Git, PostgreSQL, telemetry, model context, Lambda, CI, or public artifacts.

Apple Keychain is designed to store cryptographic keys and other secrets, and CryptoKit exposes authenticated AES-GCM operations. Those are approved platform interfaces; Sol may use a vetted cross-language equivalent where the same key, nonce, authentication, and audit contract is proven.[^apple-keychain] [^apple-aes]

### 17.3 Purge and cryptographic erasure

A valid purge performs, as applicable:

```text
freeze further use
    → resolve authoritative and derived locations
    → remove active plaintext and ciphertext
    → destroy wrapped data-encryption key
    → invalidate indexes, caches, packets, shares, and sessions
    → propagate through backups under the approved lifecycle
    → assess dataset, benchmark, model, checkpoint, and release lineage
    → write nonrevealing tombstone and receipts
```

Cryptographic erasure is not claimed merely because one file or database row was deleted. It requires evidence that the relevant key material and accessible copies are no longer usable under the approved threat model.

### 17.4 Holds, backups, and derived artifacts

A lawful or approved hold pauses destruction but does not authorize new use outside the held purpose.

Backups containing private ciphertext remain inaccessible without the wrapped keys and expire under the approved backup lifecycle. Restore procedures must preserve deletion tombstones and must not resurrect purged content.

If private or withdrawn material entered an index, benchmark candidate, dataset, checkpoint, adapter, or released artifact, the impact record determines whether to rebuild, retrain, restrict, revoke, withdraw, or disclose. Deleting source bytes is never represented as proof that model weights forgot them.

### 17.5 Separation from the immutable archive

`BSL-Archive` may retain public/open and approved research artifacts under immutable provenance rules. `BSL-Private` retains deletable personal and sensitive artifacts. Moving an artifact between these authorities requires an explicit rights, privacy, review, and owner-approved promotion event; it is never a filesystem copy performed for convenience.

## 18. Transactional event and outbox architecture

State changes that must produce downstream work use a transactional outbox in PostgreSQL.

Within one transaction:

```text
write domain revision or state transition
write append-only audit event
write outbox command/event
commit
```

A worker then processes the outbox idempotently.

This avoids an early dependency on Kafka or another distributed broker while preserving an upgrade path.

Each event stream forms a SHA-256 hash chain over JCS-canonical event envelopes. Periodic signed checkpoints anchor the event stream. Exact signing-key and private attestation mechanics remain under DR-27 release/security implementation review, but the event model is fixed here.

The hash chain provides tamper evidence, not magical immutability. PostgreSQL permissions, backups, external receipts, and signed release evidence remain necessary.


## 19. Background work, backpressure, and resource governance

The transactional outbox records durable intent. A project-owned PostgreSQL work-control plane schedules and governs the bounded background work that fulfills that intent.

### 19.1 Canonical work records

The Contract Registry defines:

```text
WorkItem
WorkDependency
WorkLease
WorkerCapability
WorkAttempt
WorkHeartbeat
WorkBudget
WorkProgressEvent
WorkReceipt
WorkQuarantineRecord
RequestBudgetPolicy
```

Work states include:

```text
PENDING
READY
LEASED
RUNNING
WAITING_DEPENDENCY
WAITING_RESOURCE
RETRY_SCHEDULED
SUCCEEDED
FAILED
DEAD_LETTER
QUARANTINED
CANCEL_REQUESTED
CANCELLED
```

Every work item binds immutable inputs, an output contract, an idempotency key, resource class, priority, rights and sensitivity scope, maximum attempts, retry classes, deadline, budget, cancellation policy, and expected receipts.

### 19.2 PostgreSQL queue mechanics

Workers claim eligible rows in a short transaction using row locks with `FOR UPDATE SKIP LOCKED`. PostgreSQL documents `SKIP LOCKED` as suitable for avoiding contention among multiple consumers of a queue-like table.[^postgres-queue]

`LISTEN/NOTIFY` may wake workers, but the database table remains authoritative. Notifications can be lost across disconnected sessions and therefore never carry the only copy of a job or state transition.[^postgres-notify]

Leases expire. Workers heartbeat and renew only within the approved job budget. Expired work can be reclaimed after idempotency and partial-output checks.

### 19.3 Backpressure and quotas

The work controller enforces:

- Per-resource-class concurrency;
- Per-user, tenant, source, campaign, and project quotas;
- Bounded fan-out;
- Maximum queued bytes and artifact estimates;
- Priority aging without starvation;
- Rate limits for external sources and providers;
- Circuit breakers for failing connectors, model routes, and indexes;
- Dead-letter and quarantine policies;
- Cancellation and graceful shutdown.

No Celery, Redis, RabbitMQ, Kafka, or managed queue enters the initial vertical slice. A replacement requires benchmarked PostgreSQL limitations and a design amendment.

### 19.4 Runtime request budgets

Every scholar request receives a registered `RequestBudgetPolicy` limiting, as appropriate:

```text
model calls
tool calls
retrieval candidates and reranker pairs
context and output tokens
wall-clock time
monetary cost
repair attempts
escalation depth
page regions or image tokens
background work fan-out
```

Exact values are versioned configuration artifacts by assurance class and deployment route. Sol cannot invent or silently change them. Exhaustion produces qualification, partial results, escalation under an approved route, cancellation, or abstention—not an unbounded autonomous research loop.

## 20. Service and package boundaries

The implementation monorepo will contain project-owned packages corresponding to logical authorities.

Proposed layout:

```text
apps/
    api/
    worker/
    web/
    scholar-runtime/
    model-gateway/
    campaign-controller/

packages/
    contracts/
    domain/
    provenance/
    archive/
    persistence/
    canon/
    text/
    linguistics/
    tnc/
    versions/
    scholarship/
    rights/
    retrieval/
    context/
    page/
    runtime/
    benchmark/
    evaluation/
    training/
    campaign/
    security/
    configuration/
    inference/
    acquisition/
    work/
    retention/
    release/

migrations/
infra/
tests/
```

These names are architectural namespaces; Sol may refine nonsemantic filenames and class names without changing responsibility.

The package dependency direction is constrained:

```text
contracts/domain
    ↓
provenance, rights, archive, retention, persistence, configuration
    ↓
canon, text, linguistics, scholarship, versions, acquisition
    ↓
tnc, retrieval, page, context, inference, work
    ↓
runtime, benchmark, evaluation, training
    ↓
API, web, workers, campaign controller
```

Lower layers may not import application orchestration or model-provider packages.


## 21. Source acquisition, connector, and freshness architecture

Every external source enters through a project-owned `SourceAcquisitionFramework`. A source adapter may automate transport; it may not decide rights, scholarly authority, admission, or training eligibility.

### 21.1 Canonical acquisition records

The Contract Registry defines:

```text
SourceConnectorSpecification
AcquisitionAuthorization
AcquisitionPlan
AcquisitionAttempt
FetchReceipt
SourceSnapshot
SourceChangeObservation
FreshnessPolicy
RefreshSchedule
RightsChangeEvent
RetractionOrWithdrawalEvent
ConnectorHealthRecord
AdmissionDecision
```

Connector classes include:

```text
manual owner import
Git repository
versioned release archive
public HTTP resource
authenticated API
ordinary public API
IIIF or document repository
Hugging Face model or dataset repository
local licensed directory
user-private upload
```

### 21.2 Rights-first acquisition flow

The required flow is:

```text
rights and terms preflight
    → exact connector and revision plan
    → bounded fetch into quarantine
    → malware/archive/content checks
    → raw-byte hashes and metadata
    → completeness and mutation validation
    → source snapshot
    → human or approved automated admission decision
    → immutable archive or private-vault promotion
    → downstream invalidation/build events
```

Public reachability is never admission authority. Downloaded code, scripts, notebooks, macros, fonts, and embedded instructions remain untrusted and are not executed during ingestion.

### 21.3 Exact revisions and transport evidence

Where the source exposes an immutable revision, the connector must use it:

- Full Git commit object;
- Full Hugging Face commit revision;
- DOI/version or release artifact;
- IIIF manifest revision;
- API snapshot or dated export;
- Raw object checksum.

Hugging Face `snapshot_download` and `hf_hub_download` can bind downloads to a specified revision, including a full commit hash, and return the corresponding snapshot path. The project still computes and archives its own file manifest and hashes.[^hf-download]

HTTP connectors preserve URL, redirect chain, status, headers, ETag, Last-Modified, response time, and content hash. Conditional requests are discovery/freshness optimizations, not substitutes for byte-level identity.[^http-conditional]

### 21.4 Freshness and change policy

Freshness is source- and claim-specific:

```text
IMMUTABLE_PINNED
CHECK_BEFORE_CONSEQUENTIAL_USE
PERIODIC
EVENT_DRIVEN
MANUAL_REVIEW
EXPIRED_OR_UNAVAILABLE
```

A model or dataset used in a frozen run remains pinned even if upstream changes. A catalog, publication status, rights statement, source API, or current-resource registry may require refresh before consequential use.

A detected byte, metadata, rights, retraction, or availability change creates a new observation. It never overwrites the old source snapshot. The event triggers impact analysis and invalidation of affected indexes, caches, evidence packets, landscape assessments, public projections, and release claims.

### 21.5 Connector isolation

Connectors use the narrowest credentials, scopes, network routes, rate limits, and storage access needed for one source. User uploads enter the private-vault path and cannot share bulk-source connector credentials or caches.

An unexpected upstream mutation, incomplete snapshot, changed terms, authentication expansion, or missing provenance causes quarantine and design/review escalation rather than silent replacement.

## 22. API contract

### 22.1 External and internal HTTP APIs

HTTP JSON APIs use:

- OpenAPI 3.1.2;
- Project-owned JSON Schemas;
- Explicit API versions;
- Idempotency keys for state-changing operations;
- ETags or revision IDs for optimistic concurrency;
- Stable problem/error records;
- Cursor pagination;
- Correlation and causation IDs;
- Explicit rights, sensitivity, and evidence-horizon metadata where material.

### 22.2 Streaming

Server-Sent Events are the default for read-only workflow progress and public-safe status. WebSockets require a measured bidirectional need and separate security review.

### 22.3 Tool contracts

Model tools are adapters over the same domain APIs and schemas. A tool wrapper cannot weaken authorization, omit provenance, or invent a second semantic contract.

### 22.4 Compatibility

Breaking API changes require a MAJOR contract revision and migration or coexistence plan.


## 23. Runtime and framework integration

### 23.1 Runtime authority

The project-owned Runtime Core and state machine remain authoritative.

LangGraph state and checkpoints are operational projections. They store project record IDs and bounded operational data rather than duplicating restricted evidence without need.

### 23.2 Evaluation authority

Inspect AI logs are imported into project-owned EvaluationResultBundles. Scoring revisions remain independent from generation artifacts.

### 23.3 Training authority

Training frameworks consume immutable TrainingJobSpecifications and materialization manifests. Their native configs are projections retained for reproduction.

### 23.4 Campaign authority

Lambda resources are controlled only through the owner-controlled broker and campaign envelope. Provider objects are external operational resources linked to project campaign IDs.

### 23.5 Default nearest-region policy

The controller implements DR-25's nearest-available eligible-region rule through a versioned `RegionSelectionPolicy`.

The default policy is:

1. Query live eligible Lambda regions, images, architectures, instance types, prices, and capacity.
2. Exclude any region that fails the campaign's rights, privacy, data-routing, workspace, image, hardware, network, price, or archive-transfer requirements.
3. Collect at least five successful round-trip latency probes from the primary controller/archive host to an approved endpoint for every remaining region during a bounded preflight interval.
4. Rank candidates by median round-trip latency.
5. Treat two candidates as operationally indistinguishable when their medians differ by no more than the greater of:
   - `10 milliseconds`; or
   - `10 percent` of the lower median.
6. Break a tie by lower live hourly price, then stronger observed capacity, then stable region identifier.
7. Record raw measurements, exclusions, tie-breaks, selected region, policy revision, and timestamp in the `RegionSelectionReceipt`.

A campaign-specific approved design may impose a stricter tolerance or require all comparison jobs to share one dynamically selected region. It may not hard-code a preferred region merely for convenience.

If a safe latency probe is unavailable before launch, the controller uses DR-25's deterministic proximity fallback, records the limitation, and verifies actual latency immediately after launch.

### 23.6 Owner-controlled controller allocation

The initial controller allocation is:

```text
primary campaign controller and Thunderbolt archive relay:
    owner-controlled MacBook Pro attached to the authoritative external APFS container and its `BSL-Archive`/`BSL-Private` volumes

secondary CC-4 provider-termination observer:
    owner-controlled Mac mini
```

The primary host owns normal campaign state, provider control, watchdog, archive transfer, termination, cleanup, and closeout.

The secondary host receives only the minimum owner-controlled authority needed to observe the exact active `CC-4` campaign and provider-terminate its resources if the primary controller becomes unavailable. It does not gain corpus, checkpoint, development, benchmark, or general provider authority merely because it can terminate the campaign.

A `CC-4` campaign does not launch when either required host is unavailable unless Joseph approves a separately designed equivalent resilience arrangement.


## 24. Model inference gateway and serving contract

All model inference—local, Lambda-hosted, or approved external API—passes through a project-owned `ModelInferenceGateway`. The Runtime Scholar Harness, evaluation core, and public application do not call model servers directly.

### 24.1 Canonical serving records

The Contract Registry defines:

```text
ModelDeploymentArtifact
ModelEndpointCapability
InferenceRouteSpecification
InferenceRequest
InferenceAttempt
InferenceReceipt
BatchingPolicy
ConcurrencyPolicy
InferenceBudget
InferenceCachePolicy
RouteHealthRecord
InferenceEquivalenceRecord
```

Every inference attempt records:

```text
model, tokenizer, processor, and template
prompt/policy/configuration snapshot
reasoning and generation mode
precision and quantization
serving engine and revision
kernel and compilation path
hardware and endpoint
context-packet hash
input, output, tool, and modality usage
cache behavior
latency and cost
retry, cancellation, and fallback
completion and validation state
```

### 24.2 Serving adapters

The initial adapters are:

```text
TransformersReferenceInferenceAdapter
    semantic and family-compatibility reference

VLLMInferenceAdapter
    provisional primary optimized serving candidate

SGLangInferenceAdapter
    mandatory optimized comparator, especially for shared-prefix,
    multimodal, and Qwen-family routes where supported

ApprovedProviderAPIAdapter
    bounded frontier-ceiling or explicitly approved product route
```

vLLM exposes OpenAI-compatible serving, prefix caching, structured-output controls, streaming, and concurrency features suitable for an optimized candidate.[^vllm-serving] SGLang provides native and OpenAI-compatible serving and benchmarking across text, image, shared-prefix, streaming, and concurrency workloads.[^sglang-serving]

Neither engine is the source of prompt, tool, cache, route, or output semantics. A route wins only after reference-equivalence, model-family compatibility, structured-output, tool, multimodal, long-context, cancellation, latency, memory, and cost tests.

### 24.3 Rights-, privacy-, and tenant-aware routing

Before transmission, the gateway verifies:

- Source and user sensitivity;
- Rights and provider permissions;
- Allowed region and route;
- Model and endpoint capability;
- Context, modality, and output limits;
- Cache and logging policy;
- Cost and assurance budget.

There is no silent fallback to another model, provider, region, quantization, reasoning mode, or prompt configuration. Every escalation or fallback appears in the receipt and must be authorized by the route policy.

Model servers receive no PostgreSQL, archive, private-vault, Lambda-control, or general network credentials. They receive only the approved request packet or handle-resolved content necessary for one inference.

### 24.4 Batching, caching, cancellation, and isolation

Batching may not mix users or rights scopes in a way that leaks prompt, cache, timing, or output state. Prefix, KV, prompt, and response caches are scoped by model, configuration, tenant/user, rights, sensitivity, context hash, and expiration.

Cancellation must stop further token generation, tool continuation, and billable route use as soon as the serving engine permits and must produce a final receipt.

A server restart, OOM, context overflow, malformed structured output, tool-parser failure, or provider error remains an explicit attempt outcome. It does not authorize semantic rerolls.

### 24.5 Reference and optimized equivalence

Each optimized route must pass a project-owned equivalence suite against the reference path covering:

- Prompt and template bytes;
- Tokenization and special tokens;
- Processor and image transforms;
- Structured schemas;
- Tool calls;
- Ancient scripts;
- Long contexts and compaction;
- Deterministic/greedy outputs where meaningful;
- Fixed evidence and hard-failure cases;
- Usage accounting and cancellation.

A serving-engine upgrade creates a new deployment artifact and route evaluation. It cannot silently replace a validated route.

## 25. Context, packet, and claim-ledger architecture

The following packet, configuration, inference, retention, acquisition, and work types remain canonical project records:

```text
TranslationNuanceEvidencePacket
MultimodalPageEvidencePacket
ContextPacket
ContextCompactionArtifact
ScholarAnswerCandidate
VerifiedClaimLedger
RuntimeAuditReceipt
EvaluationResultBundle
TrainingResultBundle
ArtifactArchiveReceipt
CampaignCloseoutReceipt
EnvironmentConfigurationSnapshot
InferenceReceipt
VectorIndexSnapshot
PurgeReceipt
FetchReceipt
WorkReceipt
```

Packets are immutable once issued.

A packet may reference exact source handles instead of copying restricted or large content. Rights and sensitivity determine whether the content is embedded, encrypted, transient, or handle-only.

Model-facing serialization is a projection of the canonical packet. The projection records all omitted, compressed, translated, reordered, or redacted material.


## 26. Public-preview projection architecture

The public expert preview will **not** connect directly to the owner’s authoritative research database or Thunderbolt archive.

A release process creates a separately signed, rights-filtered, public-safe projection containing only:

- Public benchmark cases and evidence;
- Approved public corpus records;
- Public-safe model and runtime metadata;
- Public-safe evaluation results;
- Public collaboration candidates;
- Sanitized citations and source handles;
- Explicit limitations and review status.

The public preview database is disposable and rebuildable from the release bundle.

No private holdout, user upload, restricted source, private note, owner credential, or unpublished artifact is copied into the public projection.

Exact hosting and authentication provider remain release-specific decisions under DR-27.


## 27. Caching architecture

Caches are derived, content addressed, and scoped by:

```text
source and graph snapshot
rights and sensitivity
user/tenant
model and processor
runtime and tool revision
query and context hash
language and modality
expiration and invalidation dependencies
```

The system may cache:

- Exact public passage results;
- Public evidence packets;
- Embeddings;
- Retrieval candidates;
- Context projections;
- Model outputs only where privacy and policy permit.

Private or restricted caches cannot be shared across users or rights scopes.

A cache hit is never allowed to bypass a current rights, publication-status, user-permission, or revocation check.


## 28. Backup, restore, and disaster-recovery baseline

### 28.1 Required research backups

The Thunderbolt archive remains canonical. The initial system must create:

- Database logical backups;
- Database physical or equivalent restorable snapshots where supported;
- Contract and migration identity;
- Artifact manifests and reachability reports;
- APFS snapshots or approved equivalent local snapshots;
- Restore-test receipts.

### 28.2 Second-copy policy

A second owner-controlled backup is strongly recommended before main training and becomes mandatory before the public expert preview for:

- Approved design and contract registry;
- Database backups;
- Rights and provenance manifests;
- Private benchmark metadata;
- Milestone checkpoints and result bundles that cannot be economically regenerated.

The exact second medium is deferred. It may not silently become a general-purpose cloud archive or weaken DR-23’s Thunderbolt authority requirement.

### 28.3 Restore testing

Backups do not count as valid until a separate restore environment can reconstruct:

- The contract registry;
- PostgreSQL state;
- Artifact reachability;
- At least one corpus snapshot;
- At least one evaluation or training result bundle;
- Relevant rights and provenance links.


## 29. Analytical and reporting architecture

DuckDB operates over immutable Parquet snapshots for:

- Corpus census;
- Exposure analysis;
- Evaluation statistics;
- Error analysis;
- Cost and throughput reports;
- Leakage and concentration analysis.

Analytical queries must bind exact snapshot and schema revisions.

A `.duckdb` file is a cache or analytical workspace unless explicitly archived; the Parquet files and manifests remain the authoritative analytical inputs.

Public reports are generated from approved result bundles and public-safe projections—not directly from mutable notebooks.


## 30. Notebook policy

Notebooks may be used for exploration and visualization, but they are not production or authoritative implementation units.

A consequential notebook result must be promoted into:

- Versioned code;
- An immutable input manifest;
- A repeatable command;
- A result bundle;
- Tests or validation;
- An archived environment identity.

No benchmark, training, or release conclusion may depend only on the interactive state of a notebook.


## 31. Rights, privacy, and security enforcement points

Rights and sensitivity checks occur at:

```text
source acquisition
artifact admission
normalization and materialization
index creation
retrieval candidate generation
model/provider transmission
context composition
answer rendering
export and sharing
training/evaluation inclusion
public projection
release
```

A rights or sensitivity record is not merely informational metadata.

The system must make it structurally difficult to:

- Add a restricted source to an open index;
- Send private content to an unauthorized provider;
- include private benchmark material in a training snapshot;
- expose a user upload in telemetry;
- publish a model or dataset without a rights manifest.


## 32. Failure semantics

The integrated architecture uses explicit failure classes, including:

```text
CONTRACT_VALIDATION_FAILED
SCHEMA_VERSION_UNSUPPORTED
MIGRATION_REQUIRED
ARTIFACT_HASH_MISMATCH
ARCHIVE_UNAVAILABLE
ARCHIVE_VOLUME_ID_MISMATCH
DATABASE_UNAVAILABLE
PROJECTION_STALE
INDEX_REBUILD_REQUIRED
RIGHTS_UNKNOWN_OR_DENIED
SENSITIVITY_ROUTE_DENIED
TENANT_ISOLATION_FAILED
EVIDENCE_HANDLE_UNRESOLVED
PACKET_INCOMPLETE
AUDIT_CHAIN_INVALID
RESTORE_VALIDATION_FAILED
PUBLIC_PROJECTION_CONTAMINATED
BLOCKED_REQUIRES_SOL_REPAIR
BLOCKED_REQUIRES_DESIGN_REVIEW
```

A missing derived index may trigger a controlled rebuild. A missing authoritative object, rights decision, or contract cannot be “worked around” by the model.


## 33. Implementation-conformance gates

Sol must implement the architecture in bounded root turns.

### `IA-00 — Contract registry and identity primitives`

- Contract Registry;
- JSON Schema validation;
- JCS canonicalization;
- UUIDv7 identities;
- Revision and hash contracts;
- Cross-language generated-type conformance.

### `IA-01 — External volumes, immutable archive, and private vault`

- `BSL-Archive` and `BSL-Private` stable volume identities;
- Encrypted APFS and free-space/reserve checks;
- Content-addressed archive and `.incoming` promotion;
- Private-vault envelope encryption;
- Keychain-backed key wrapping;
- No cross-user private deduplication;
- Atomic promotion, quarantine, purge, and cryptographic-erasure fixtures.

### `IA-02 — PostgreSQL authoritative schema and configuration activation`

- Namespace layout;
- Typed core tables;
- Revisions and assertions;
- RLS and roles;
- Transactions and invariant validators;
- Migrations and outbox;
- Runtime Configuration Registry and activation receipts.

### `IA-03 — Provenance and graph conformance`

- Graph and evidence records;
- Recursive traversal;
- Competing assertions;
- Snapshot creation;
- External-standard adapters;
- No-last-write-wins tests.

### `IA-04 — Corpus, Parquet, analytical, and source-acquisition projections`

- Arrow schemas and Parquet materialization;
- DuckDB analytical reports;
- Exposure and snapshot identity;
- Source connector framework;
- Exact revision and conditional-fetch receipts;
- Quarantine, freshness, change, and invalidation tests.

### `IA-05 — Retrieval, embedding, reranking, and index bake-off`

- Exact, canonical, lexical, lemma, citation, and relation retrieval;
- Embedding and reranker artifact registry;
- Qwen, BGE-M3, EmbeddingGemma, and Qwen-4B capacity comparison;
- pgvector exact and approximate search;
- Matryoshka dimension and `halfvec` evaluation;
- Rights/tenant partitioning;
- Old/new index migration, shadowing, recall, and rollback.

### `IA-06 — Runtime configuration and model inference gateway`

- Prompt, policy, tool, route, generation, context, compaction, retrieval, and feature-flag artifacts;
- Drift and compatibility checks;
- Transformers reference inference;
- vLLM and SGLang optimized adapters;
- Rights-aware route selection;
- Cache/batching isolation;
- Cancellation and inference receipts;
- Reference-versus-optimized equivalence.

### `IA-07 — Runtime, packet, compaction, and work-control integration`

- Context and evidence-packet persistence;
- Runtime events and LangGraph projection;
- Claim ledger and audit receipt;
- PostgreSQL work queue;
- Leases, heartbeats, cancellation, backpressure, quotas, and request budgets;
- Cache identity and invalidation.

### `IA-08 — Evaluation, training, and campaign integration`

- Evaluation and training result bundles;
- Job specifications and exposure records;
- Artifact archive receipts;
- Lambda campaign linkage;
- Sol/Luna control boundaries;
- Public-safe projections.

### `IA-09 — Retention, purge, and downstream-impact conformance`

- Retention assignments and holds;
- Private purge and cryptographic erasure;
- Index/cache/session/share propagation;
- Backup tombstone and restore behavior;
- Dataset/model/checkpoint/release impact analysis;
- Purge and nonpromotability receipts.

### `IA-10 — Security, backup, public projection, and disaster recovery`

- RLS attack and tenant-isolation tests;
- Private benchmark firewall;
- Audit hash chain;
- Database and artifact restore drill;
- Public projection contamination test;
- Kill switch and rollback interfaces;
- Second-copy readiness report.

### `IA-11 — Integrated vertical-slice conformance`

One bounded passage and page workflow must prove source acquisition, rights admission, canonical resolution, linguistic and Translation Nuance evidence, retrieval, model routing, verification, session state, compaction, evaluation, archive, purge simulation, audit, and public-safe projection under one immutable contract set.

No downstream implementation may bypass a failed gate.


## 34. Sol implementation discretion

Sol may decide:

- Internal class, function, and module names within the approved package boundaries;
- Equivalent SQL query plans and indexes that preserve semantics;
- Test implementation;
- Design-neutral dependency substitutions after proving contract compatibility;
- Performance optimizations that preserve all output, rights, audit, and migration semantics;
- UI component decomposition within DR-26.

Sol may not independently change:

- Authoritative-store assignments;
- Database family;
- Artifact archive authority;
- ID, revision, or hash rules;
- Contract dialect;
- Public/private/restricted boundaries;
- Graph authority or typed-table policy;
- Retrieval rights filtering;
- RLS requirement;
- API compatibility policy;
- Event/audit semantics;
- Packet authority;
- public-projection isolation;
- Backup or archive requirements;
- Service decomposition;
- Framework authority;
- Embedding/reranker candidate set, route semantics, or index authority;
- Prompt, policy, tool, feature-flag, or activation authority;
- Model inference gateway, fallback, cache, or tenant-isolation semantics;
- Archive/private-vault separation, encryption, retention, or purge semantics;
- Source connector, freshness, admission, or invalidation semantics;
- PostgreSQL work-queue, budget, or backpressure authority;
- Any scholarly, benchmark, experiment, or release contract.

A proposed material change returns:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```


## 35. Hard failures

DR-28 treats these as hard failures:

- A framework-native object becoming the only record of a consequential project event.
- A vector, graph, or search index becoming an untracked source of truth.
- Storing required domain fields only in unvalidated JSONB.
- Using natural-language titles, verse strings, sigla, or external IDs as permanent internal primary keys.
- Mutating an immutable artifact or revision in place.
- Hashing noncanonical JSON while claiming canonical identity.
- Unicode normalization changing authoritative Greek, Hebrew, Aramaic, Syriac, Coptic, or transliteration text silently.
- A public service connecting directly to private research stores.
- Private, restricted, or benchmark data entering a shared index or cache.
- RLS bypass by the application role.
- An API or tool wrapper weakening the domain contract.
- An event, migration, or artifact without exact schema and revision identity.
- An unreviewed migration running automatically on merge.
- A derived projection that cannot be invalidated or rebuilt.
- A cache bypassing current rights, revocation, or user-permission checks.
- A notebook-only result supporting a promotion or public claim.
- A backup that has never passed restore validation.
- Fallback from the Thunderbolt archive to internal disk or another cloud.
- A public projection containing private holdout, user, restricted, or security material.
- Mixing vectors from incompatible embedding spaces or changing an active embedding configuration in place.
- Selecting an embedding or reranker solely from generic leaderboard performance without the project bake-off.
- Allowing a prompt, policy, tool description, route, threshold, or feature flag to change outside an approved configuration snapshot.
- A public client or Runtime Core calling a model server directly rather than through the Model Inference Gateway.
- Silent model, provider, region, quantization, reasoning-mode, prompt, or cache fallback.
- Cross-user prompt, prefix, KV, embedding, retrieval, or response-cache leakage.
- Storing deletable user-private content only in the immutable content-addressed archive.
- Claiming private deletion or cryptographic erasure without key, copy, index, cache, backup, and downstream-impact evidence.
- Executing acquired scripts, macros, fonts, notebooks, or embedded instructions during ingestion.
- Replacing an exact source snapshot silently after upstream mutation, rights change, retraction, or incomplete acquisition.
- Introducing Redis, Celery, Kafka, RabbitMQ, or another work broker without a measured PostgreSQL-queue limitation and design review.
- Running unbounded background research, retrieval, repair, or escalation loops without a registered request budget.
- Sol changing the architecture or Luna modifying any contract, schema, migration, store, configuration, model route, acquisition, work, retention, or index authority.


## 36. Decisions approved by DR-28

Approval locks:

1. The modular-monolith-first architecture.
2. Git as the authority for design, code, contracts, migrations, reviewed configuration content, and public-safe manifests.
3. PostgreSQL as the initial authoritative transactional database family, with the exact supported major and patch frozen at `IA-02`; PostgreSQL 18 is the design-date reference baseline.
4. The encrypted APFS `BSL-Archive` Thunderbolt volume as the canonical retained immutable research and generated-artifact store.
5. A separate encrypted APFS `BSL-Private` volume plus per-object envelope encryption as the deletable private-content authority.
6. Parquet plus Arrow schemas as the immutable bulk tabular format and DuckDB as the initial analytical projection engine.
7. PostgreSQL exact, lexical, trigram, recursive-graph, and pgvector retrieval as the initial hybrid stack.
8. `Qwen/Qwen3-Embedding-0.6B` and `Qwen/Qwen3-Reranker-0.6B` as provisional retrieval references, subject to the approved bake-off against BGE-M3, EmbeddingGemma, and Qwen3-Embedding-4B.
9. Homogeneous versioned vector indexes; model/configuration changes create new indexes rather than in-place mutation.
10. No dedicated graph, vector, search, event-streaming, message-broker, feature-flag, or microservice product in the initial vertical slice.
11. Typed relational tables plus evidence-bearing assertions rather than a universal EAV or property-graph-only schema.
12. JSONB only as a bounded extension and source-native preservation mechanism.
13. JSON Schema Draft 2020-12, OpenAPI 3.1.2, RFC 8785 JCS, SHA-256, UUIDv7, and explicit Parquet/Arrow schemas as the initial contract and identity foundation.
14. Immutable revisions, artifacts, packets, snapshots, result bundles, configuration artifacts, source snapshots, and index snapshots.
15. A Git-authored/PostgreSQL-activated Runtime Configuration Registry; no consequential hidden prompt, policy, tool, route, threshold, or feature-flag state.
16. A project-owned Model Inference Gateway with Transformers reference inference, vLLM as the provisional primary optimized adapter, and SGLang as a mandatory comparator where supported.
17. No silent model/provider/region/precision/reasoning/configuration fallback and no direct public-client or Runtime-Core access to model servers.
18. Rights-, privacy-, tenant-, budget-, cancellation-, batching-, and cache-aware inference receipts.
19. A project-owned Source Acquisition Framework with rights-first preflight, exact revisions, quarantine, raw-byte hashes, freshness policies, and downstream invalidation.
20. A PostgreSQL-backed leased work queue using `SKIP LOCKED`, with `LISTEN/NOTIFY` only as a wake-up optimization and no initial external broker.
21. Registered work and scholar-request budgets, backpressure, cancellation, quotas, and bounded fan-out.
22. A transactional outbox and append-only hash-chained project-event model.
23. Project-owned schemas, events, tools, packets, configuration, inference, acquisition, work, retention, and result bundles over framework-native objects.
24. RLS and explicit tenant, rights, sensitivity, benchmark, and public/private partitioning from the first schema.
25. Exact rights and privacy filtering before acquisition, storage, indexing, retrieval, model transmission, rendering, sharing, training, evaluation, and release.
26. Purpose-specific retention, legal holds, purge, private-vault deletion, cryptographic erasure, backup propagation, and downstream-impact analysis.
27. A separately built and signed public-preview projection with no direct private-store, private-vault, or Thunderbolt-archive access.
28. The package and service dependency direction defined in this review.
29. Restore-tested backups and a second owner-controlled backup requirement for irreplaceable milestone artifacts before public preview.
30. `IA-00` through `IA-11` as mandatory implementation gates.
31. The default nearest-region policy uses measured median latency and approved deterministic tie-breaks.
32. The MacBook Pro attached to the Thunderbolt volumes is the primary campaign/archive controller, and the owner-controlled Mac mini is the initial `CC-4` provider-termination observer.
33. Sol implementation is bounded by the approved contracts and our retained architecture authority.


## 37. Decisions intentionally deferred

DR-28 does not yet freeze:

- Exact public hosting, identity, authentication, CDN, domain, and DNS providers;
- Exact public database hosting product;
- Exact second owner-controlled backup medium;
- Exact APFS volume UUIDs, mount paths, archive/private-vault quotas, and retention durations;
- Exact PostgreSQL patch, distribution, extension bundle, connection pool, and deployment method;
- Exact winning embedding model, Matryoshka dimension, reranker, HNSW parameters, fusion weights, and retrieval latency objectives after `IA-05`;
- Exact winning optimized inference engine or route by model family after `IA-06`;
- Exact source-specific connector credentials, refresh intervals, and rate limits beyond the registered policy contracts;
- Exact per-assurance-class runtime budgets, which must be approved configuration artifacts before deployment;
- Exact accessible component, frontend state-management, and public telemetry libraries;
- Exact private-vault key-management implementation library, provided it satisfies the approved envelope-encryption and Keychain contract;
- Exact release-signing implementation;
- Exact public preview account model;
- Exact mobile/edge architecture, which belongs to DR-29;
- Any later dedicated graph database, vector database, search engine, external work broker, feature-flag service, or microservice decomposition.

Those choices require implementation evidence, DR-29, release-specific designs, and owner approval. Sol may not fill them silently when they become consequential.


## 38. Approval statement

> **Biblical Scholar Lab will use a modular-monolith-first, contract-registry-driven architecture with project-owned domain semantics and replaceable operational adapters. Git will remain authoritative for approved designs, code, schemas, migrations, reviewed prompts and policies, and public-safe manifests; PostgreSQL will be the initial authoritative transactional database family; the owner-controlled encrypted APFS `BSL-Archive` Thunderbolt volume will remain the canonical retained immutable store for acquired sources, datasets, media, indexes, checkpoints, result bundles, backups, receipts, and releases; and a separately identified encrypted APFS `BSL-Private` volume with per-object envelope encryption will remain the deletable authority for user-private and sensitive retained content. Large immutable tabular datasets will use Parquet with versioned Arrow schemas and DuckDB analytical projections. PostgreSQL exact, lexical, trigram, recursive-graph, and pgvector retrieval will form the initial hybrid stack, with `Qwen/Qwen3-Embedding-0.6B` and `Qwen/Qwen3-Reranker-0.6B` serving only as provisional references inside a project-specific bake-off against BGE-M3, EmbeddingGemma, and a larger Qwen capacity comparator. Every embedding, reranker, instruction, dimension, precision, chunking policy, index, fusion rule, and migration will be a versioned artifact; no vector index will become evidence authority. A Git-authored and PostgreSQL-activated Runtime Configuration Registry will own every consequential prompt, policy, tool schema, generation profile, route, context, compaction, retrieval policy, and feature flag, while a project-owned Model Inference Gateway will mediate all local, Lambda, and approved external inference through an exact request and receipt contract, using direct Transformers inference as the semantic reference and vLLM/SGLang as replaceable optimized adapters. No model, provider, route, region, quantization, reasoning mode, prompt, cache, or fallback may change silently. A project-owned Source Acquisition Framework will enforce rights-first authorization, exact revisions, quarantine, immutable fetch receipts, freshness, retraction and rights-change events, and downstream invalidation. A PostgreSQL-backed leased work controller will provide bounded idempotent background execution, backpressure, heartbeats, cancellation, quotas, and request budgets without introducing an external broker in the initial vertical slice. User-private and withdrawn content will receive purpose-specific retention, legal-hold, purge, cryptographic-erasure, backup-propagation, and downstream-impact records; deletion will never be claimed from one missing file or row, and private hashes or caches will not cross user or rights boundaries. Normative records will use JSON Schema Draft 2020-12, opaque UUIDv7 identities, immutable revision IDs, SHA-256 content identity, RFC 8785 canonical JSON, OpenAPI 3.1.2 projections, explicit Parquet/Arrow schemas, and project-owned append-only event envelopes with a transactional outbox and hash-chain fields. Typed domain tables and evidence-bearing assertions will remain authoritative; JSONB, materialized views, LangGraph checkpoints, Inspect logs, training-framework configs, vector indexes, model-server caches, dashboards, and public-service databases will remain bounded source-native fields or rebuildable projections. Rights, sensitivity, tenancy, benchmark, public/private, provider, cache, and deletion boundaries will be enforced before acquisition, storage, indexing, retrieval, model transmission, rendering, sharing, training, evaluation, and release. Every framework, configuration, packet, tool, API, migration, artifact, event, work item, source snapshot, cache, index, model, checkpoint, purge, campaign, and public release will bind an exact contract, revision, provenance, rights, sensitivity, and hash identity. Sol will implement the approved architecture through `IA-00`–`IA-11` and may optimize only design-neutral mechanics; Luna may execute only frozen migrations, imports, rebuilds, tests, backups, restores, deployments, and campaigns delegated by Sol; ChatGPT will review implementation and architecture evidence; and Joseph Abbud will retain sole authority over material architecture changes, migrations, configurations, deployment, public claims, and release.**

---


## References

[^postgres-rls]: PostgreSQL 18 Documentation, “Row Security Policies.” PostgreSQL row-level security can restrict row access and defaults to deny when row security is enabled without an applicable policy: <https://www.postgresql.org/docs/current/ddl-rowsecurity.html>.

[^postgres-recursive]: PostgreSQL 18 Documentation, “WITH Queries (Common Table Expressions),” including recursive queries: <https://www.postgresql.org/docs/current/queries-with.html>.

[^postgres-partition]: PostgreSQL 18 Documentation, “Table Partitioning,” describing declarative range, list, and hash partitioning and partition pruning: <https://www.postgresql.org/docs/current/ddl-partitioning.html>.

[^postgres-json]: PostgreSQL 18 Documentation, “JSON Functions and Operators” and JSON/JSONB data types, including SQL/JSON paths and indexed JSONB operations: <https://www.postgresql.org/docs/current/functions-json.html>.

[^pgvector]: pgvector, official project README. pgvector provides exact and approximate vector similarity search inside PostgreSQL, including HNSW and IVFFlat, filtered queries, partitioning guidance, half-precision vectors, and recall/performance controls: <https://github.com/pgvector/pgvector>.

[^arrow-parquet]: Apache Arrow, “Reading and Writing the Apache Parquet Format.” Parquet is a standardized open-source columnar format, and Arrow provides the in-memory transport and schema layer used by the project: <https://arrow.apache.org/docs/python/parquet.html>.

[^duckdb-parquet]: DuckDB Documentation, “Reading and Writing Parquet Files,” including direct queries, schema inspection, projection and filter pushdown, and Parquet export: <https://duckdb.org/docs/stable/data/parquet/overview>.

[^json-schema]: JSON Schema, “Draft 2020-12,” defining the selected schema dialect, validation vocabularies, dynamic references, and bundling features: <https://json-schema.org/draft/2020-12>.

[^openapi]: OpenAPI Initiative, “OpenAPI Specification.” DR-28 selects OpenAPI 3.1.2 as the initial API projection while retaining project-owned JSON Schemas as the source contract: <https://spec.openapis.org/oas/v3.1.2.html>.

[^jcs]: RFC 8785, “JSON Canonicalization Scheme (JCS).” JCS defines an invariant, hashable JSON representation using I-JSON constraints, deterministic primitive serialization, and recursive property sorting and does not perform Unicode normalization: <https://www.rfc-editor.org/rfc/rfc8785.html>.

[^uuidv7]: RFC 9562, “Universally Unique IDentifiers (UUIDs),” including UUID Version 7’s time-ordered Unix-epoch layout: <https://www.rfc-editor.org/rfc/rfc9562.html>.

[^apple-apfs]: Apple Support, “Protect your Mac information with encryption” and Disk Utility guidance for password-protected external storage. Apple documents that encrypting removable media converts it to encrypted APFS and protects it with a password: <https://support.apple.com/guide/mac-help/protect-your-mac-information-with-encryption-mh40593/mac>.

[^apple-apfs-volumes]: Apple Support, “Use more than one version of macOS on Mac” and Disk Utility guidance. APFS containers may contain multiple volumes that share container space, and each volume can be added or removed independently: <https://support.apple.com/en-us/118282>.

[^qwen-embedding]: QwenLM, “Qwen3 Embedding.” The official family provides 0.6B, 4B, and 8B text embedding and reranking models, 32K context, multilingual support, instruction-aware retrieval, and Matryoshka dimensions: <https://github.com/QwenLM/Qwen3-Embedding> and <https://huggingface.co/Qwen/Qwen3-Embedding-0.6B>.

[^bge-m3]: BAAI, `bge-m3` model card. BGE-M3 provides multilingual dense, sparse, and multi-vector retrieval with inputs up to 8,192 tokens under the MIT license: <https://huggingface.co/BAAI/bge-m3>.

[^embeddinggemma]: Google AI for Developers, “EmbeddingGemma model overview.” EmbeddingGemma is a 308M multilingual embedding model with configurable dimensions, a 2K context, and device-oriented quantized deployment: <https://ai.google.dev/gemma/docs/embeddinggemma>.

[^vllm-serving]: vLLM documentation, “OpenAI-Compatible Server” and “Structured Outputs.” vLLM provides an optimized serving adapter with streaming, concurrency, prefix caching, tool/parser and structured-output capabilities that remain subject to project equivalence testing: <https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html> and <https://docs.vllm.ai/en/latest/features/structured_outputs.html>.

[^sglang-serving]: SGLang documentation, “Bench Serving Guide.” SGLang exposes native and OpenAI-compatible endpoints and benchmarking for streaming, concurrency, shared-prefix, and multimodal workloads: <https://docs.sglang.ai/developer_guide/bench_serving>.

[^postgres-queue]: PostgreSQL 18 Documentation, `SELECT`. PostgreSQL states that `SKIP LOCKED` can be used to avoid lock contention among multiple consumers of a queue-like table: <https://www.postgresql.org/docs/18/sql-select.html>.

[^postgres-notify]: PostgreSQL Documentation, `LISTEN`/`NOTIFY`. Notifications are asynchronous wake-up signals; durable work state remains in database tables: <https://www.postgresql.org/docs/current/sql-listen.html> and <https://www.postgresql.org/docs/current/sql-notify.html>.

[^hf-download]: Hugging Face Hub documentation, “Download files from the Hub.” `snapshot_download` and `hf_hub_download` can bind acquisition to a specified revision, including a full commit hash: <https://huggingface.co/docs/huggingface_hub/en/guides/download>.

[^http-conditional]: RFC 9110, “HTTP Semantics,” including validators and conditional requests such as ETag and `If-None-Match`: <https://www.rfc-editor.org/rfc/rfc9110.html>.

[^apple-keychain]: Apple Developer Documentation, Keychain Services and key items. Apple documents Keychain storage for cryptographic keys and other secrets: <https://developer.apple.com/documentation/security/ksecclasskey>.

[^apple-aes]: Apple Developer Documentation, CryptoKit AES-GCM authenticated encryption: <https://developer.apple.com/documentation/cryptokit/aes/gcm>.
