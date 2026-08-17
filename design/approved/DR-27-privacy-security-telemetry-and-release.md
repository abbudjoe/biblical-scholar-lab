# DR-27 — Privacy, Security, Telemetry, and Release

| Field | Value |
|---|---|
| Design ID | `DR-27` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Product, architecture, benchmark, and experiment designer | ChatGPT |
| Independent implementation and evidence reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14; DR-15; DR-16; DR-17; DR-18; DR-19; DR-20; DR-21; DR-22; DR-23; DR-24; DR-25; DR-26 |
| Implementation authority | GPT-5.6 Sol exclusively implements and repairs the approved privacy, security, telemetry, incident-response, release, supply-chain, identity, access, audit, signing, deployment, rollback, and vulnerability-management machinery |
| Execution authority | GPT-5.6 Luna may execute only frozen security scans, conformance tests, staging deployments, release-candidate packaging, rollback drills, incident-evidence collection, or exact owner-approved release operations delegated by Sol; Luna may not change code, policy, telemetry fields, retention, access, release contents, credentials, severity, or incident interpretation |
| Governance authority | ChatGPT designs the privacy, security, telemetry, incident, and release contracts and reviews implementation and evidence; Joseph Abbud approves consequential data-processing purposes, public-preview exposure, incident disclosures, release candidates, and release or rollback actions |
| Cloud and archive constraints | Project-controlled cloud training and evaluation remain Lambda-only; retained generated training and evaluation artifacts remain authoritative on the owner-controlled Thunderbolt archive; user-serving infrastructure remains separately design- and release-gated |
| Approved change | Establishes the product threat model, sensitive-data and trust-zone architecture, privacy-by-design defaults, consent and user-rights model, identity and least-privilege controls, secrets and provider-routing policy, content-security and LLM-specific defenses, telemetry and audit separation, incident response and kill switches, secure-development and supply-chain gates, signed release artifacts, staged deployment, rollback and revocation, vulnerability disclosure, public-preview security gates, and Sol/Luna implementation boundaries |

## 1. Purpose

DR-03 defines the sensitive-use policy.

DR-10 defines source and artifact rights, lineage, and release authorization.

DR-14 defines page-image provenance and indirect-prompt-injection isolation.

DR-16 defines the Runtime Scholar Harness, narrow tool capabilities, and audit receipts.

DR-23 and DR-25 define training, Lambda execution, secrets isolation, Thunderbolt archival, and cloud closeout.

DR-26 defines the user experience, private-upload defaults, evidence inspection, public collaboration preview, and anti-overtrust controls.

DR-27 defines **how the product protects users, source material, benchmarks, models, infrastructure, releases, and the project itself; how operational telemetry remains useful without becoming surveillance; how religious, health, sexuality, abuse, mental-health, and research activity remain sensitive; how incidents are detected, contained, investigated, corrected, disclosed, and learned from; and how code, containers, models, datasets, benchmarks, adapters, and public applications are securely promoted, signed, revoked, and rolled back**.

This project handles unusually sensitive combinations of information. A user may reveal:

- Religious or philosophical belief;
- Denominational identity or uncertainty;
- Health, mental-health, sexuality, abuse, family, or crisis information;
- Private Bible-page images and handwritten notes;
- Unpublished scholarship or manuscripts;
- Licensed research-library content;
- Exact study behavior and controversial questions;
- User corrections, annotations, and expert judgments;
- Private benchmark and model-evaluation material.

Under the GDPR, personal data revealing religious or philosophical beliefs, health, sex life, and sexual orientation receive special-category treatment; the same regulation also requires purpose limitation, data minimization, storage limitation, integrity and confidentiality, and data protection by design and by default.[^gdpr]

Even where a particular law does not classify every field identically, Biblical Scholar Lab will treat these data as sensitive because misuse can expose belief, identity, vulnerability, safety concerns, or private research activity.

A source-grounded assistant can still be unsafe or untrustworthy if:

- Raw questions and Bible-study history are sent to analytics vendors;
- A user’s selected theological lens is used to profile or categorize them;
- A private page image enters training without consent;
- A prompt-injected document causes data exfiltration;
- One user’s retrieval results or session state appear in another user’s answer;
- Model output is rendered as executable HTML, URLs, formulas, or commands;
- A compromised model, container, dependency, font, OCR engine, or dataset enters production;
- Public CI exposes secrets or private benchmark material;
- A release cannot be traced to reviewed source, build, model, data, and evaluation identities;
- A security or rights incident cannot be contained without taking the entire project offline;
- Telemetry needed for debugging is confused with research consent;
- Logs retain raw content indefinitely;
- A public preview launches before the project can revoke credentials, disable uploads, roll back models, or notify affected users.

DR-27 is intended to prevent those failures.

## 2. Governing principle

> **Biblical Scholar Lab will collect, retain, transmit, and expose the minimum data necessary for one explicit purpose; keep user content, scholarly evidence, telemetry, audit, benchmark, and training lineages separate; grant every person, model, tool, service, and agent only the capabilities needed for one bounded operation; treat all external content and model output as untrusted; make security and privacy state visible and revocable; and release only artifacts whose source, build, rights, evaluation, signing, rollback, and incident-response evidence are complete. Public usefulness may never depend on hidden surveillance, silent training consent, unbounded agency, or unreviewed supply-chain trust.**

The operating priorities are:

```text
protect people
protect private and restricted evidence
preserve scholarly and benchmark integrity
limit authority and blast radius
keep operations observable without collecting content by default
make releases reproducible and revocable
recover honestly from incidents
```

## 3. Privacy and security are related but separate

The project will maintain distinct assessments for:

```text
PRIVACY_RISK
CYBERSECURITY_RISK
SAFETY_RISK
RIGHTS_AND_LICENSE_RISK
SCHOLARLY_INTEGRITY_RISK
BENCHMARK_INTEGRITY_RISK
RELEASE_AND_SUPPLY_CHAIN_RISK
```

Encryption can reduce unauthorized access while a collection practice still creates privacy risk.

A source may be legally licensed while its use still exposes a user’s private research question.

A model may be secure from external attackers while producing unsupported or harmful answers.

A telemetry system may contain no obvious names while still making a person identifiable through unique session patterns.

No one score will collapse these risks into a declaration that the system is “safe.”

The project will use the NIST Privacy Framework and Cybersecurity Framework as outcome-oriented reference models, NIST SP 800-61r3 for incident-response integration, and NIST SP 800-218/218A for secure software and AI development.[^nist-privacy][^nist-ir][^nist-ssdf]

These frameworks remain adapters and guidance—not substitutes for project-specific design, qualified legal advice, or owner decisions.

## 4. Data subjects and sensitive inference

The system may process information relating to:

```text
anonymous visitor
pseudonymous visitor
authenticated user
expert reviewer
project contributor
source author or contributor
person depicted or named in an upload
project owner or operator
security reporter
incident-affected person
```

The project must not infer or persist a person’s:

- Religion, denomination, conversion status, doubt, or theological identity;
- Political view;
- Sexual orientation or gender identity;
- Health or mental-health status;
- Abuse-survivor status;
- Clergy status or institutional affiliation;
- Race, ethnicity, disability, or other sensitive identity;

unless the person explicitly supplies the information for a defined immediate purpose and the processing path is approved for it.

A user may select a theological, methodological, canon, language, or translation profile for one request or session. That selection is a **research control**, not permission to create a behavioral or religious profile.

Persistent storage of such a selection requires a separate explicit choice. It may not be used for advertising, ranking users, engagement targeting, eligibility, or third-party analytics.

## 5. Sensitivity classification is separate from rights classification

Every data object receives a `SensitivityClassification` independent of DR-10 rights and lineage.

The initial classes are:

```text
S0_PUBLIC
    intentionally public, reviewed, and release-approved

S1_PUBLIC_SAFE_INTERNAL
    nonpublic operational material whose disclosure would cause little harm

S2_CONFIDENTIAL_PROJECT
    internal designs, pre-release code, nonpublic results, or operational metadata

S3_USER_PRIVATE
    prompts, sessions, page images, notes, exports, account data, or private libraries

S4_HIGHLY_SENSITIVE_PERSONAL
    religion, health, sexuality, abuse, crisis, children, precise location,
    identity documents, or comparable sensitive disclosures

S5_RESTRICTED_RESEARCH
    licensed sources, unpublished research, private expert review, or contractual data

S6_PRIVATE_BENCHMARK_AND_GOLD
    private holdouts, fresh cases, scoring keys, SME judgments, and leakage-sensitive material

S7_SECRETS_AND_SECURITY_CONTROL
    credentials, signing material, approval secrets, recovery codes, vulnerability details,
    firewall rules, incident evidence, and exploit reproductions

S8_QUARANTINE_OR_INCIDENT
    suspected malware, poisoned data, leaked content, disputed artifacts, or forensic copies
```

A single object can carry several labels, and the most protective applicable handling rule governs.

A public-domain Bible text embedded inside a private user note remains private as part of that note.

A public benchmark prompt paired with a private final gold answer remains private as a composite.

## 6. Data inventory and processing-purpose registry

No production processing begins without a versioned `DataProcessingPurpose` recording:

```text
purpose ID
purpose description
data subjects
data categories
sensitivity classes
source and collection method
lawful or contractual basis where applicable
processors and destinations
retention and deletion policy
access roles
security controls
user notice and consent state
training eligibility
sharing and release eligibility
risk assessment
owner approval
```

Examples of distinct purposes include:

```text
serve one answer
retain a user-requested research note
authenticate an account
prevent abuse and fraud
debug a failed request
measure aggregate latency
conduct an opted-in research study
review a user-submitted correction
investigate a security incident
```

Data collected for one purpose does not silently become available for another.

In particular:

```text
serve a user request
    ≠ train the shared model

save a private note
    ≠ publish a benchmark case

security audit
    ≠ product analytics

product analytics
    ≠ research participation

expert review
    ≠ permission to expose the reviewer’s identity or raw comments
```

## 7. Privacy by design and by default

The default product posture is:

```text
no user-content training
no third-party advertising
no behavioral advertising
no religious profiling
no sale of personal data
no public sharing
no cross-user memory
no private content in public telemetry
no indefinite retention
no external model route for sensitive material without an approved path
```

The implementation must minimize:

- The amount of personal data collected;
- The precision of identifiers;
- The number of services receiving the data;
- The duration of retention;
- The number of people and agents with access;
- The number of copies;
- The resolution of telemetry;
- The relationship among separate sessions unless the user requests continuity.

Where a purpose can be met through aggregate or local processing, raw identifiable content should not be collected.

The system should permit useful study without requiring an account wherever practical.

## 8. Consent and user control

Consent, where used, must be:

```text
specific
granular
informed
freely given
recorded
revocable
separate from unrelated terms
```

One checkbox cannot authorize:

- Saving a session;
- Training on it;
- Publishing it;
- Sharing it with experts;
- Using it in a benchmark;
- Sending it to an external model provider;
- Retaining a page image;
- Using telemetry for research.

The user interface must separately support, where applicable:

```text
use transiently
save privately
export
share through a controlled link
submit a correction
contribute to research
contribute to training
contribute to a public benchmark
```

Revoking a future-use consent stops new use and triggers the approved downstream impact analysis. It does not support false promises that a previously trained model can always be made to forget one contribution without retraining or other verified remediation.

## 9. User privacy rights and controls

When the product retains personal data, it must provide an approved mechanism to:

- Inspect retained user data;
- Correct user-controlled profile and session information;
- Export user-created notes and settings;
- Delete retained sessions, uploads, notes, and account data subject to narrow incident or legal holds;
- Revoke sharing links;
- Revoke optional telemetry or research consent;
- See active devices or sessions where accounts exist;
- Understand which model/provider route handled a request;
- Contact the project about privacy or security concerns.

Exact statutory rights and response timelines require qualified legal review for each launch jurisdiction.

The design may provide broader controls than a particular law requires.

## 10. Children and vulnerable users

The version-one public preview is not designed as a child-directed service and will not intentionally profile children or solicit sensitive disclosures from them.

The product may still be used in supervised educational or family settings, and ordinary biblical questions from a minor must not be treated as wrongdoing.

Any launch involving:

- Accounts known to belong to children;
- Persistent child profiles;
- School-managed access;
- Parental dashboards;
- Child-directed engagement;
- Collection of age or parental-consent records;

requires a separate privacy, legal, safety, and UX design review.

Sensitive-use responses continue to follow DR-03 regardless of age uncertainty.

## 11. Trust zones

DR-27 proposes the following logical trust zones:

```text
TZ-0_PUBLIC_CLIENT
    untrusted browser or mobile client

TZ-1_PUBLIC_EDGE
    rate limiting, request validation, session entry, and security controls

TZ-2_PRODUCT_RUNTIME
    Runtime Scholar Harness and public-safe orchestration

TZ-3_EVIDENCE_AND_TOOL_SERVICES
    exact passage, linguistic, Translation Nuance, citation, and retrieval services

TZ-4_PRIVATE_USER_DATA
    private sessions, uploads, notes, and account-scoped indexes

TZ-5_RESTRICTED_RESEARCH_AND_BENCHMARK
    restricted corpora, private gold, SME review, and protected evaluation

TZ-6_MODEL_EXECUTION
    local or approved external model routes

TZ-7_TRAINING_AND_EVALUATION_CONTROL
    Sol-authored control plane, Lambda broker, campaign and evaluation controllers

TZ-8_OWNER_ARCHIVE_AND_SECURITY
    Thunderbolt archive, keychain, signing, incident, and recovery material

TZ-9_PUBLIC_REPOSITORY_AND_CI
    public code, public tests, public artifacts, and untrusted PR execution
```

Cross-zone transfers require explicit contracts covering identity, authorization, content class, encryption, logging, retention, and failure behavior.

The implementation must not assume that being “inside the application” makes a component trusted.

## 12. Identity, authentication, and authorization

The minimum design principles are:

```text
least privilege
separation of duties
short-lived sessions and credentials
explicit resource ownership
default deny
server-side authorization
step-up authentication for sensitive operations
revocable access
complete security audit
```

Public reading and anonymous transient study may require no account.

Saving private material, expert review, administration, release approval, security investigation, signing, and cloud-control operations require distinct roles and stronger controls.

At minimum, the system distinguishes:

```text
ANONYMOUS_USER
AUTHENTICATED_USER
EXPERT_REVIEWER
CONTENT_EDITOR
BENCHMARK_REVIEWER
SECURITY_OPERATOR
RELEASE_OPERATOR
PROJECT_OWNER
SERVICE_IDENTITY
```

Role assignment is explicit. It is never inferred from a person’s denomination, institution, or self-presentation in a model conversation.

No client-side role or object identifier is trusted without server-side authorization.

Cross-user session, upload, note, retrieval-index, and export isolation must receive dedicated authorization tests.

## 13. Secrets and cryptographic material

Secrets must never appear in:

- Git;
- Public CI;
- Model context;
- Tool output;
- Telemetry;
- Error messages;
- Browser bundles;
- Container images;
- Training data;
- Benchmark cases;
- Pull-request handoffs.

Owner and operator secrets remain in approved secret stores such as macOS Keychain, hardware-backed credentials, or a later approved managed secret service.

Service credentials should be short-lived and scoped where provider capabilities permit.

The project must support:

- Inventory;
- Ownership;
- Rotation;
- Revocation;
- Expiration;
- Leak detection;
- Incident replacement;
- Test credentials separate from production;
- No reuse of personal owner credentials by Codex or cloud instances.

GitHub secret scanning and push protection are enabled for the public repository, but they supplement rather than replace local and CI secret detection; GitHub notes that public repositories receive secret scanning and push protection for supported patterns, while detection still has coverage limits.[^github-security]

## 14. Encryption and key boundaries

All network transport carrying nonpublic data must use authenticated encryption.

Sensitive retained data must be encrypted at rest through an approved platform or application mechanism.

The external Thunderbolt archive must satisfy DR-23/DR-25 encryption and volume-identity requirements before holding authoritative sensitive artifacts.

Keys and encrypted data should be separated where practical.

The project must not describe data as end-to-end encrypted unless the complete key and processing path satisfies that claim.

Backups and temporary copies retain the same sensitivity and deletion obligations as the primary object.

## 15. Provider and data-egress policy

Before a request, source, image, benchmark case, or trace leaves its trust zone, the route must verify:

```text
provider identity and contract
model and service identity
data categories and sensitivity
rights and privacy authorization
provider retention and training policy
region or transfer constraints
logging and abuse-monitoring behavior
subprocessors where material
request and response retention
user notice or consent
fallback behavior
```

Project-controlled cloud training and evaluation remain Lambda-only.

Frontier APIs may be used as bounded benchmark subjects or approved product routes only when the exact data class permits the transmission.

The default public-preview path must not send:

- `S4_HIGHLY_SENSITIVE_PERSONAL`;
- `S5_RESTRICTED_RESEARCH`;
- `S6_PRIVATE_BENCHMARK_AND_GOLD`;
- `S7_SECRETS_AND_SECURITY_CONTROL`;

into an external model API without a separate approved route and purpose.

A provider failure may not cause silent failover to a provider with broader retention or weaker privacy terms.

## 16. Telemetry, audit, research data, and user content are different systems

DR-27 distinguishes:

```text
SECURITY_AUDIT
OPERATIONAL_TELEMETRY
PRODUCT_ANALYTICS
RESEARCH_TELEMETRY
USER_CONTENT
SCHOLARLY_EVIDENCE
MODEL_AND_EVALUATION_ARTIFACTS
INCIDENT_EVIDENCE
```

These systems may share correlation handles but not raw data by default.

An operational trace is not a research dataset.

A security audit log is not a product-analytics event stream.

A user prompt is not telemetry.

A model output is not automatically eligible for training.

## 17. Telemetry classes

### `TEL-0_SECURITY_AND_AUDIT`

Mandatory, content-minimized records necessary for:

- Authentication and authorization;
- Credential use;
- Administrative actions;
- Release and rollback;
- Security detections;
- Rights and privacy decisions;
- Cloud lifecycle;
- Incident investigation.

### `TEL-1_ESSENTIAL_OPERATIONS`

Default content-free or allowlisted metrics needed for:

- Availability;
- Latency;
- Error and timeout rates;
- Tool and route health;
- Resource consumption;
- Cost control;
- Archive and cleanup state.

### `TEL-2_PRODUCT_USAGE_AGGREGATES`

Optional or separately disclosed aggregate product measurements such as surface use, answer-depth selection, and feature completion. These must not include raw prompts, answers, sources, images, religious profiles, or persistent cross-session identifiers by default.

### `TEL-3_OPTED_IN_RESEARCH`

Explicitly opted-in, purpose-specific data used for a named study, usability analysis, or model-improvement program. Its consent, review, retention, and release status remain independent of ordinary product use.

### `TEL-4_RAW_CONTENT_CAPTURE`

Prohibited by default. A bounded diagnostic or research capture requires an explicit approved purpose, narrow population, user notice or consent, short retention, access controls, and a deletion or promotion decision.

### `TEL-5_INCIDENT_FORENSICS`

Exceptional evidence retained for a defined incident under restricted access and hold/release procedures.

## 18. Telemetry minimization and redaction

Telemetry schemas must be allowlists.

Raw values are not exported merely because an instrumentation library captured them.

The default telemetry path prohibits:

- Prompt or answer bodies;
- Source quotations;
- Uploaded images;
- Bible passages selected by a user;
- Theological or denominational preferences;
- Search queries;
- User notes;
- Full URLs containing query strings;
- Tokens, credentials, or cookies;
- Raw IP addresses after the immediate security need expires;
- Persistent device fingerprints;
- High-cardinality user or session identifiers in metrics.

When correlation is necessary, use purpose-scoped pseudonymous IDs with rotation and separation from account identity.

Simple hashing does not automatically anonymize a low-entropy identifier. OpenTelemetry’s own sensitive-data guidance warns that hashes can be reversible in practice for predictable identifier spaces and provides deletion, transformation, truncation, and allowlist-based redaction mechanisms.[^otel-sensitive]

Redaction must occur **before** telemetry leaves the application or local collector boundary.

## 19. OpenTelemetry is an adapter—not the authoritative data model

OpenTelemetry may be used to collect, process, and export traces, metrics, and logs through a local or controlled collector.[^otel-signals]

The project owns:

- Telemetry event schemas;
- Sensitivity labels;
- Allowed attributes;
- Retention;
- Export routes;
- Consent state;
- Audit semantics;
- Correlation policy.

OpenTelemetry resource attributes, baggage, spans, and logs do not become canonical project records.

Sensitive data must not be placed in baggage or other implicitly propagated fields.

A local collector is preferred where it can enforce batching, encryption, filtering, and redaction before export; OpenTelemetry documents the Collector as a vendor-neutral layer that can perform these functions, including sensitive-data filtering.[^otel-collector]

No telemetry vendor is selected by DR-27.

## 20. Audit architecture

Security, release, benchmark, training, rights, and administrative audit records are append-only, tamper-evident project records.

An `AuditEvent` contains:

```text
event ID
event type
actor or service identity
role and capability
resource identity
action and outcome
time and observed time
source system
request or campaign identity
sensitivity class
redaction state
prior-event or integrity link
retention class
incident hold state
content hash
```

Audit records should contain handles and hashes rather than raw sensitive content wherever possible.

Tamper evidence may use hash chains, signatures, append-only stores, or another approved mechanism. Exact implementation is deferred to DR-28.

Users do not receive access to unrelated system or security audit records, but they should receive appropriate records of their own saved data, sharing, exports, and account actions.

## 21. Threat actors and failure sources

The threat model includes:

```text
malicious unauthenticated user
malicious or compromised authenticated user
cross-tenant attacker
malicious uploaded document or web source
prompt-injected scholarly content
compromised dependency or build action
compromised model, adapter, tokenizer, processor, or quantization
poisoned corpus or embedding index
compromised cloud or hosting credential
malicious or mistaken project contributor
mistaken Sol implementation
unauthorized Luna operation
stolen or failed owner device or external drive
provider outage or ambiguous lifecycle result
privacy-invasive analytics configuration
benchmark leakage or gold exfiltration
supply-chain substitution
unbounded-cost or denial-of-service attacker
```

Security design must address both malicious behavior and ordinary human or agent mistakes.

## 22. LLM-specific threat classes

The project explicitly tests and mitigates:

```text
prompt injection and goal hijacking
sensitive information disclosure
model and dependency supply-chain compromise
data and model poisoning
improper output handling
excessive agency and tool misuse
system-prompt or policy leakage
vector and embedding weaknesses
misinformation and unsupported authority
unbounded consumption
```

These categories correspond closely to the OWASP Top 10 for LLM applications and reflect risks already addressed throughout DR-10, DR-14, DR-16, DR-17, DR-23, and DR-25.[^owasp-llm]

DR-27 consolidates their product-security treatment.

## 23. Untrusted content has no execution or instruction authority

The following are always untrusted data:

- User prompts;
- Uploaded pages and PDFs;
- OCR and VLM text;
- Retrieved websites and scholarship;
- Tool results;
- Model output;
- Citations, URLs, QR codes, and embedded metadata;
- Benchmark subjects and prior-art applications.

They may be analyzed and quoted.

They may not:

- Change system policy;
- Grant capabilities;
- Authorize a tool or release;
- Access another user’s data;
- Open a URL automatically;
- Trigger a shell command;
- Execute code or macros;
- Reveal secrets;
- Change telemetry or retention;
- Bypass rights, safety, or evidence verification.

Instruction and evidence channels remain structurally separate.

## 24. Upload and document security

Every upload path requires:

- File-type and content-type validation;
- Size, page, pixel, and decompression limits;
- Archive-depth and expansion limits;
- Malware and suspicious-content screening where appropriate;
- No execution of macros, scripts, embedded binaries, active PDF content, or fonts from untrusted sources;
- Image and document decoding in isolated, resource-bounded processes;
- Removal or controlled preservation of metadata such as EXIF;
- Safe filename generation;
- No direct placement in a web-accessible path;
- Rights, sensitivity, retention, and user-ownership assignment;
- Prompt-injection scanning as an advisory signal, not a claim that content has been made safe.

Password-protected or encrypted uploads remain unsupported unless a later design supplies a secure, user-controlled decryption path.

A document parser crash, malformed file, or model-recognition error must not expose neighboring user content.

## 25. Retrieval and embedding security

Every retrieval index is bound to:

```text
source and rights snapshot
sensitivity and tenant scope
embedding model and revision
chunking and normalization
access policy
poisoning and provenance state
reconstruction and extraction risk
retention and deletion policy
```

Required defenses include:

- Server-side tenant and rights filters before retrieval;
- No post-retrieval attempt to remove forbidden content after it has already reached the model;
- Separation of public, restricted, private-user, and private-benchmark indexes;
- Source-provenance display;
- Poisoning and unexpected-source detection;
- Duplicate and source-dependence awareness;
- Retrieval-output size and cost limits;
- No arbitrary index writes from a model response;
- Deletion and revocation propagation;
- Tests for cross-user and cross-lineage retrieval leakage.

Embeddings and indexes receive their own DR-10 release and extraction review.

## 26. Model-output handling

Model output remains untrusted until validated and safely rendered.

The application must:

- Escape or sanitize HTML and Markdown;
- Prevent script, iframe, style, event-handler, and dangerous URL execution;
- Prevent automatic external image or link fetching that can exfiltrate data;
- Mark model-generated citations and links until verified;
- Validate tool arguments against typed schemas;
- Prevent spreadsheet-formula injection in exports;
- Prevent shell, SQL, template, and path injection;
- Enforce Content Security Policy and safe link behavior where applicable;
- Avoid rendering model output as executable code by default;
- Preserve the distinction between text, quotation, URL, command, and data.

A model’s confidence or “safe” label cannot bypass output validation.

## 27. Model, data, and software supply chain

Every consequential dependency receives an identity and provenance record, including:

```text
source repository or registry
exact version and digest
maintainer or publisher identity
license
signature or checksum
build provenance
known vulnerabilities
review state
transitive dependencies
update and revocation state
```

This applies to:

- Python, JavaScript, Rust, and system packages;
- GitHub Actions;
- Containers and base images;
- Models and adapters;
- Tokenizers and processors;
- Fonts;
- OCR and document models;
- Datasets and benchmark imports;
- Quantized and converted artifacts;
- Native libraries, kernels, and compiler toolchains.

NIST’s SSDF and AI-specific SSDF profile provide the reference secure-development posture for software and model supply chains.[^nist-ssdf]

SLSA provenance and Sigstore/Cosign signing are approved candidate interoperability mechanisms for build and artifact provenance, subject to privacy and release constraints.[^slsa][^sigstore]

Public transparency logs must not receive private artifact contents or metadata whose disclosure would expose restricted model, benchmark, or user information.

## 28. Public repository and CI security

The public repository must enforce the previously approved owner-only merge and review model.

In addition, public CI must:

- Run untrusted PR code without production, Lambda, archive, signing, benchmark, or provider secrets;
- Use minimal default token permissions;
- Pin external actions to reviewed immutable commits;
- Avoid privileged `pull_request_target` execution of untrusted code;
- Block secret exposure and detect accidental credentials;
- Scan dependencies, containers, infrastructure, and source code under approved tools;
- Prevent private benchmark and restricted data from entering public workflows;
- Produce public-safe reports;
- Require reviewed changes to security policy, workflows, CODEOWNERS, and release configuration;
- Keep build and release workflows separate.

No PR merge automatically authorizes a public deployment or model release.

## 29. Secure development and testing program

The implementation program must include, as applicable:

```text
threat modeling
secure design review
static analysis
dependency and license analysis
secret scanning
container and image scanning
infrastructure and workflow scanning
unit and integration security tests
authorization and cross-tenant tests
property and fuzz testing
malicious-file and parser testing
prompt-injection and data-exfiltration testing
RAG poisoning and leakage tests
model artifact and unsafe-serialization tests
rate-limit and unbounded-cost tests
backup and restore tests
rollback and revocation drills
independent penetration or security review before public exposure
```

The project will maintain security regression cases for every confirmed incident and serious near miss.

Security tooling output remains evidence requiring triage, not an automatic declaration that a release is secure.

## 30. Telemetry and privacy validation

Before enabling any telemetry stream beyond `TEL-0` and `TEL-1`, the project must demonstrate:

- Approved purpose and schema;
- No prohibited fields;
- Redaction before export;
- Expected aggregation and cardinality;
- Retention and deletion;
- User notice and consent where applicable;
- Cross-session and cross-user isolation;
- Vendor and subprocessor review;
- Export-disable behavior;
- Sample event inspection;
- Adversarial tests for content leakage;
- A public description understandable to users.

Synthetic test content alone is insufficient; controlled canary values must verify that raw prompts, answers, images, notes, citations, and secrets do not enter the exported stream.

## 31. Incident categories

The incident system distinguishes, at minimum:

```text
SECURITY_INTRUSION
CREDENTIAL_OR_SECRET_EXPOSURE
PRIVACY_OR_USER_DATA_EXPOSURE
RIGHTS_OR_LICENSE_INCIDENT
RESTRICTED_SOURCE_OR_BENCHMARK_LEAK
MODEL_OR_DATA_POISONING
SUPPLY_CHAIN_COMPROMISE
UNAUTHORIZED_CLOUD_OR_COST_EVENT
CROSS_USER_DATA_LEAK
PROMPT_INJECTION_OR_TOOL_MISUSE
MALICIOUS_FILE_OR_PARSER_EVENT
PUBLIC_RELEASE_INTEGRITY_FAILURE
SCHOLARLY_OR_BENCHMARK_INTEGRITY_INCIDENT
SAFETY_OR_HARMFUL_OUTPUT_INCIDENT
AVAILABILITY_OR_DESTRUCTIVE_EVENT
```

One event may receive several categories.

A wrong scholarly answer is not automatically a cybersecurity incident, but a systematic hidden corruption of gold labels, a poisoned dataset, or a fabricated-evidence release may be a scholarly-integrity and supply-chain incident.

## 32. Incident severity

The initial severity ladder is:

```text
IR-SEV0_OBSERVATION
    unusual event requiring no immediate containment

IR-SEV1_LOW
    limited issue with low expected impact and contained scope

IR-SEV2_MATERIAL
    confirmed or likely material impact requiring coordinated response

IR-SEV3_HIGH
    significant sensitive-data, credential, model, rights, or public-release impact

IR-SEV4_CRITICAL
    active broad compromise, dangerous public behavior, major private-data leak,
    uncontrolled cloud authority, or inability to contain ongoing harm
```

Severity considers:

- People affected;
- Data sensitivity;
- Scope and duration;
- Ongoing exploitability;
- Rights and legal obligations;
- Safety impact;
- Public release and supply-chain impact;
- Reversibility;
- Confidence in containment.

Sol and Luna may report indicators and execute frozen containment actions. They may not unilaterally lower severity or close an incident.

## 33. Incident response lifecycle

The project follows an integrated lifecycle:

```text
prepare
→ detect and validate
→ contain
→ preserve evidence
→ eradicate or correct
→ recover
→ notify or disclose where required
→ review impact
→ add regression controls
→ close with owner approval
```

NIST SP 800-61r3 treats incident response as part of the broader cybersecurity-risk lifecycle rather than a process that begins only after compromise.[^nist-ir]

Each incident receives an immutable record containing:

```text
incident identity and categories
time and detection source
severity and rationale
affected users, sources, models, artifacts, and services
known and suspected timeline
evidence and chain of custody
containment actions
credential and artifact revocation
rights and privacy analysis
communications and notifications
recovery and validation
downstream model, dataset, index, benchmark, and release impact
post-incident actions
owner closure
```

## 34. Kill switches and containment controls

The system must support independent, owner-controlled controls to:

- Disable public access;
- Disable user uploads;
- Disable external model routes;
- Disable a tool family;
- Disable retrieval from one source or index;
- Revoke a model, adapter, dataset, benchmark, container, or release;
- Revoke credentials and sessions;
- Stop Lambda campaigns through DR-25;
- Suspend telemetry export;
- Invalidate sharing links;
- Force read-only mode;
- Roll back to a known approved release;
- Display an accurate service or incident notice.

A kill switch must not depend solely on the compromised service it is intended to stop.

Kill-switch operation and restoration require audit evidence.

## 35. Vulnerability reporting and disclosure

Before public code or service release, the project publishes a reviewed `SECURITY.md` containing:

- A private reporting channel;
- Scope;
- Information requested;
- Safe-harbor posture subject to qualified legal review;
- Expected acknowledgement process;
- Coordinated-disclosure expectations;
- Prohibited public disclosure of private user or benchmark data;
- Supported release versions.

Security reports are treated as confidential incident candidates, not public issues by default.

A reporter’s identity is collected only when needed and is not used for marketing or unrelated purposes.

Public disclosure should be accurate, timely, and coordinated with affected users, upstream maintainers, providers, and qualified legal advice where applicable.

## 36. Release objects remain separate

The following are independently versioned and approved release objects:

```text
source code
container or runtime image
web or mobile application
model weights
adapter
merged model
quantized or mobile model
training or evaluation dataset
benchmark and gold
retrieval index
tool database
documentation and design record
evaluation or research report
public demo configuration
```

Approval of one does not authorize the others.

A public repository release does not authorize a model release.

A model release does not authorize publication of its training corpus.

A public benchmark does not authorize release of private gold or evidence.

DR-10 remains authoritative for rights and lineage; DR-27 adds security, privacy, supply-chain, signing, deployment, rollback, and incident gates.

## 37. Release environments and channels

The initial environment sequence is:

```text
LOCAL_DEVELOPMENT
PUBLIC_SAFE_CI
PRIVATE_INTEGRATION
PRIVATE_STAGING
EXPERT_COLLABORATION_PREVIEW
PUBLIC_RESEARCH_PREVIEW
```

Promotion skips no required environment.

The release channels are:

```text
DEVELOPMENT
INTERNAL_ALPHA
EXPERT_PREVIEW
PUBLIC_PREVIEW
STABLE_RESEARCH_RELEASE
RETIRED
REVOKED
```

Version-one work does not need to reach `STABLE_RESEARCH_RELEASE` before it becomes useful.

No release is described as production-ready merely because it is publicly accessible.

## 38. Release-candidate manifest

Every candidate release includes:

```text
release identity and channel
reviewed Git commit
complete artifact digests
build and training provenance
SBOM and dependency inventory
container and model identities
rights and sensitivity manifests
benchmark and evaluation revisions
security and privacy test results
known vulnerabilities and accepted risks
model, data, benchmark, evaluation, and rights cards
telemetry and retention behavior
provider and deployment configuration
migration and rollback plan
kill-switch validation
incident contacts
signatures and verification instructions
owner approval
```

A release candidate may not be reconstructed from a website deployment and a verbal description.

## 39. Signing, provenance, and verification

Public release artifacts should be cryptographically signed or attested through an approved mechanism.

Sigstore/Cosign is the preferred initial interoperability candidate for containers and release blobs because it supports identity-bound short-lived signing, verification bundles, and public transparency.[^sigstore]

The project must decide per artifact whether public transparency is appropriate.

Private model, benchmark, security, or user artifacts must not be exposed through a public transparency log merely to obtain a signature.

Verification policy binds:

- Expected signer identity;
- Issuer;
- Artifact digest;
- Provenance predicate;
- Build or release workflow;
- Release channel;
- Timestamp or transparency evidence;
- Revocation state.

A valid signature proves an approved identity signed an artifact; it does not prove the artifact is safe, accurate, lawful, or promotion-worthy.

## 40. Deployment authority

Only an owner-approved release campaign may publish or deploy a consequential artifact.

Sol may:

- Build and verify the candidate;
- Generate manifests, SBOMs, signatures, and deployment plans;
- Execute private staging;
- Repair implementation defects;
- Produce one consolidated release handoff.

Luna may:

- Execute frozen build, scan, package, staging-deploy, smoke-test, rollback-test, or publication commands under an approved campaign;
- Collect exact operational evidence.

Luna may not:

- Change the release contents;
- Change telemetry or retention;
- Bypass a scan or gate;
- Substitute a model, container, host, route, or license;
- Expand the audience;
- Publish after a failed gate;
- Decide whether a vulnerability is acceptable.

A merge to `main` does not automatically deploy.

## 41. Rollback, revocation, and recovery

Every public-preview or later release requires:

- A previous known-good version;
- A tested rollback procedure;
- Database and schema migration reversal or forward-recovery plan;
- Model and index version pinning;
- Cache invalidation;
- Credential revocation;
- Sharing-link revocation;
- Artifact revocation or retirement notice;
- User communication plan;
- Restore test from approved backup or artifact archive;
- Verification that the rollback does not reintroduce a known rights or security defect.

A model release may require disabling one capability or source without rolling back the entire application.

The architecture should support component-level revocation.

## 42. Public-preview gates

### Static public project release

A public repository and documentation-only release may occur after:

- Public-safe content and rights review;
- Secret and private-material scans;
- Owner-only branch protection;
- Security reporting channel;
- Clear license scope;
- No executable service handling user content.

### Expert collaboration preview

`MVP-01_EXPERT_COLLABORATION_PREVIEW` additionally requires:

- Approved P0/P1 benchmark and result materials;
- Public-safe demo or reproducible local workflow;
- Privacy notice;
- No user-content training by default;
- Minimal telemetry;
- Kill switch and rollback;
- Security and privacy conformance tests;
- Independent security review appropriate to the exposed features;
- Incident process and contacts;
- ChatGPT release review and owner approval.

### Public internet preview with persistent accounts or uploads

This requires a stronger gate including:

- Authentication and authorization review;
- Cross-user isolation and access-control testing;
- Upload and parser security testing;
- Data retention and deletion implementation;
- Provider and telemetry review;
- Privacy-impact assessment;
- Penetration or independent security testing;
- Incident and breach-response drill;
- Qualified legal review of privacy notice, terms, and launch jurisdictions;
- Load, abuse, and unbounded-cost testing.

The project may publish its serious engineering and research foundation before exposing a high-risk persistent public service.

## 43. Privacy and security benchmark track

The project must test:

- Cross-user and cross-session isolation;
- Unauthorized direct-object access;
- Session fixation and revocation;
- Sensitive-data logging;
- Raw-content telemetry leakage;
- Prompt injection and goal hijacking;
- Tool-capability escalation;
- Data exfiltration through links, images, Markdown, or citations;
- Malicious uploads and parser denial of service;
- Restricted-index and benchmark leakage;
- Model and dependency substitution;
- Poisoned data and embeddings;
- Secret exposure;
- Unbounded context, tool, and GPU consumption;
- Rollback and kill-switch behavior;
- Revoked source and model propagation;
- Deleted user-data propagation;
- Quantized and mobile privacy/security regression;
- Multilingual safety and privacy consistency.

Public red-team cases must not expose real private data, live secrets, private benchmark gold, or unpatched exploit details.

## 44. Principal hard failures

DR-27 treats the following as hard failures:

- Training on user content without explicit approved consent.
- Profiling or ranking users by inferred religion, denomination, sexuality, health, or vulnerability.
- Sending sensitive, restricted, private-benchmark, or secret material to an unauthorized provider.
- Raw prompts, answers, page images, notes, or sources entering ordinary telemetry.
- Cross-user retrieval, session, note, upload, or export leakage.
- A model or document gaining unapproved tool or instruction authority.
- Executing active content from an upload or model output.
- Exposing credentials to Sol, Luna, CI, a cloud instance, a browser, or a public artifact.
- Using an unsigned, unhashed, incompatible, or unreviewed model, container, dataset, or release artifact.
- Public CI receiving privileged secrets while executing untrusted PR code.
- Silent provider, model, route, telemetry, retention, or release substitution.
- Hiding a confirmed privacy, security, rights, benchmark, or supply-chain incident.
- Losing private user corrections, deletions, or revocations through caches or compaction.
- Keeping sensitive content indefinitely because no retention policy was implemented.
- Treating pseudonymization or hashing as guaranteed anonymization.
- Publishing private benchmark gold, exploit details, user uploads, or restricted source content.
- Deploying directly from an unapproved PR or `main` merge.
- Releasing without rollback, kill-switch, incident, rights, evaluation, and signing evidence.
- Allowing Luna to modify code, policy, secrets, telemetry, incident severity, release contents, or audience.

## 45. Implementation gates

```text
PSR-00 — Data inventory, threat model, trust zones, and processing-purpose registry

PSR-01 — Sensitivity classification, privacy defaults, consent, retention,
         user access/export/delete, and provider-routing contracts

PSR-02 — Identity, authorization, session isolation, secrets, encryption,
         key rotation, and administrative-control conformance

PSR-03 — Telemetry and audit schemas, local redaction, content-leak canaries,
         retention, export-disable, and OpenTelemetry adapter conformance

PSR-04 — Upload, parser, page, prompt-injection, retrieval, embedding,
         output-rendering, and unbounded-consumption defenses

PSR-05 — Secure development, public CI, dependency/model/data supply chain,
         SBOM, provenance, signing, and verification

PSR-06 — Incident taxonomy, immutable incident records, kill switches,
         credential rotation, containment, restore, and recovery drills

PSR-07 — Release-candidate manifest, private staging, migration, rollback,
         revocation, component disablement, and public-safe packaging

PSR-08 — Independent security/privacy review and expert-preview gate

PSR-09 — Public persistent-service authentication, upload, isolation,
         privacy-impact, penetration, legal, abuse, and incident drill
```

A static public repository can precede every public-service gate, but no user-data-processing service may bypass the gates applicable to its exposed capabilities.

## 46. Sol and Luna authority

### Sol may

- Implement every approved privacy, security, telemetry, incident, release, signing, CI, and deployment contract;
- Choose design-neutral code structure and equivalent implementation mechanics;
- Produce threat-model evidence, tests, manifests, reports, and candidate mitigations;
- Stop and report an architectural or policy gap;
- Repair implementation defects after review.

### Sol may not

- Create a new data-processing purpose;
- Enable raw-content telemetry;
- Change consent or retention;
- Accept a security risk;
- Lower incident severity;
- Change a release audience;
- Approve a provider or subprocessor;
- Publish a vulnerability;
- Decide that legal, privacy, or security review is unnecessary;
- Release, deploy, or roll back without owner authority.

### Luna may

- Run exact frozen scans, tests, staging operations, release packaging, deployment, rollback, kill-switch drills, or incident-evidence collection delegated by Sol;
- Stop on a failed gate;
- Report exact operational evidence.

### Luna may not

- Write or repair code;
- Modify a scan, test, policy, threshold, telemetry field, retention rule, secret, provider, release object, audience, or incident state;
- Bypass a gate;
- Continue after a frozen stop condition;
- Interpret whether an incident is resolved or a release is safe.

Any implementation gap returns:

```text
BLOCKED_REQUIRES_SOL_REPAIR
```

Any policy, privacy, security, telemetry, or release-design gap returns:

```text
BLOCKED_REQUIRES_DESIGN_REVIEW
```

## 47. Decisions DR-27 would lock

Approval would establish that:

1. Religious-study activity and associated health, sexuality, abuse, and belief data are treated as sensitive.
2. Privacy, security, safety, rights, scholarly integrity, benchmark integrity, and release risk remain separately assessed.
3. Data sensitivity remains separate from rights and lineage.
4. Every processing purpose is explicit, versioned, and owner-approved.
5. Data minimization, purpose limitation, storage limitation, and privacy by default govern the product.
6. User content is excluded from shared training, analytics, and public release by default.
7. The project does not infer or profile religious or other sensitive identity.
8. Consent is operation-specific and revocable.
9. Persistent user data receives access, export, correction, and deletion controls.
10. Child-directed and school-managed use remains separately gated.
11. Trust zones and cross-zone transfer contracts are first-class.
12. Identity, authorization, and cross-user isolation are server-enforced.
13. Secrets never enter agent context, public CI, cloud instances, or user-facing artifacts.
14. Sensitive provider routing is explicit and fail-closed.
15. Telemetry, audit, research data, user content, evidence, and model artifacts remain separate systems.
16. Ordinary telemetry excludes raw prompts, answers, images, notes, sources, and religious profiles.
17. OpenTelemetry is an optional redacted transport adapter, not the canonical audit or privacy model.
18. External content and model output have no instruction or execution authority.
19. Upload, RAG, embedding, rendering, and tool surfaces receive dedicated security controls.
20. Software, model, data, font, action, container, and kernel supply chains are pinned and provenance-bearing.
21. Public CI is unprivileged for untrusted contributions.
22. Incident response, kill switches, vulnerability reporting, recovery, and disclosure are designed before public exposure.
23. Code, app, model, data, benchmark, index, and report releases remain separate objects.
24. Release candidates require SBOM, provenance, rights, evaluation, security, privacy, rollback, and incident evidence.
25. Public artifacts are signed or attested under an approved identity and verification policy.
26. A merge does not deploy.
27. Component-level rollback and revocation are mandatory.
28. Static public release, expert preview, and persistent public service receive progressively stronger gates.
29. Independent security review is required before the exposed expert preview, and qualified legal/privacy review is required before persistent public accounts or uploads in supported jurisdictions.
30. Sol implements; Luna only executes frozen operations; ChatGPT reviews; Joseph approves consequential processing, incidents, releases, and rollbacks.

## 48. Decisions intentionally deferred

DR-27 does not yet freeze:

- Exact application hosting provider;
- Exact identity provider or authentication protocol;
- Exact account model;
- Exact database, object store, or encryption product;
- Exact retention durations by data class;
- Exact privacy notice or terms text;
- Exact launch jurisdictions;
- Exact lawful bases or legal conclusions;
- Exact external model providers used for public requests;
- Exact telemetry backend or whether optional product analytics are enabled;
- Exact OpenTelemetry Collector distribution;
- Exact event-signing and append-only-audit implementation;
- Exact malware scanner, WAF, rate limiter, or SIEM;
- Exact SAST, SCA, container, secret, or infrastructure scanners;
- Exact SBOM and provenance serialization;
- Exact Sigstore, key-management, or private-signing configuration;
- Exact vulnerability-reporting email or platform;
- Exact incident notification timelines;
- Exact independent security reviewer;
- Exact penetration-testing scope;
- Exact deployment platform, CDN, domain, and DNS provider;
- Exact backup and disaster-recovery topology for user-serving data;
- Exact stable-release support period;
- Exact bug-bounty or safe-harbor program;
- Exact public service-level objectives;
- Exact deletion behavior for information already included in a verified training run;
- Any claim of regulatory certification or compliance.

Those decisions are resolved through DR-28, release-specific designs, implementation evidence, qualified legal and security review, and owner approval.

## 49. Approval statement

> **Biblical Scholar Lab will use a privacy-by-design, least-privilege, defense-in-depth architecture in which religious and philosophical study activity, health, sexuality, abuse, crisis, private-page, unpublished-research, licensed-source, expert-review, and private-benchmark information are treated as sensitive and remain separate from ordinary telemetry, shared training, public release, and cross-user state. Every processing purpose, data category, trust-zone transfer, provider route, retention rule, consent, access role, security control, telemetry field, audit event, incident action, and release artifact will be versioned and reviewable. User content will remain private and excluded from shared training, analytics, benchmark publication, and public release by default; the system will not infer or profile users by religion, denomination, health, sexuality, or vulnerability; and persistent storage or research contribution will require granular, revocable choices. Telemetry will use allowlisted, content-minimized schemas with redaction before export, separating essential security audit, operational metrics, optional aggregate analytics, opted-in research, raw diagnostic capture, and incident evidence. OpenTelemetry may serve as a redacted vendor-neutral transport, but project-owned privacy, audit, consent, and retention records remain authoritative. All external documents, retrieval results, model outputs, citations, URLs, QR codes, and uploaded media will remain untrusted data with no instruction or execution authority; tool calls, retrieval, rendering, uploads, embeddings, model routes, and cross-user access will be capability-scoped, rights-filtered, isolated, and adversarially tested. Software, model, data, container, action, font, kernel, tokenizer, processor, and benchmark supply chains will bind exact digests, dependencies, licenses, provenance, vulnerabilities, signatures, and review states under secure-development and AI-supply-chain practices. Public CI will receive no production, Lambda, archive, signing, model-provider, user-data, restricted-source, or private-benchmark authority while executing untrusted changes. The project will maintain an integrated incident-response lifecycle, immutable incident evidence, independent kill switches, credential and artifact revocation, component-level rollback, vulnerability reporting, recovery drills, and versioned public corrections. Code, containers, applications, models, adapters, quantizations, datasets, benchmarks, indexes, reports, and demos will remain separate release objects; each candidate will require a signed or attested identity, SBOM and provenance, rights and sensitivity manifests, benchmark and security evidence, privacy and telemetry description, migration and rollback plan, kill-switch validation, incident contacts, ChatGPT review, and Joseph Abbud’s approval. Sol will exclusively implement and repair the approved privacy, security, telemetry, incident, and release machinery; Luna may execute only frozen scans, staging, packaging, deployment, rollback, and evidence operations delegated by Sol; ChatGPT will design and review the controls and incidents; and Joseph will retain sole authority over consequential processing purposes, accepted risks, incident closure, public claims, deployment, rollback, and release.**

---

## References

[^gdpr]: European Parliament and Council, Regulation (EU) 2016/679 (GDPR). Article 5 establishes purpose limitation, data minimisation, storage limitation, and integrity/confidentiality; Article 9 covers special categories including religious or philosophical beliefs, health, sex life, and sexual orientation; Article 25 requires data protection by design and by default: <https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng/>.

[^nist-privacy]: NIST, “Privacy Framework.” The framework is a voluntary tool for managing privacy risk arising from data processing and for integrating privacy engineering into organizational risk management: <https://www.nist.gov/privacy-framework>.

[^nist-ir]: NIST SP 800-61 Rev. 3, “Incident Response Recommendations and Considerations for Cybersecurity Risk Management: A CSF 2.0 Community Profile,” April 2025. The publication integrates incident response across cybersecurity-risk-management functions: <https://csrc.nist.gov/pubs/sp/800/61/r3/final>.

[^nist-ssdf]: NIST SP 800-218, “Secure Software Development Framework (SSDF) Version 1.1,” and SP 800-218A, “Secure Software Development Practices for Generative AI and Dual-Use Foundation Models.” These provide secure-development practices for software and AI-model life cycles: <https://csrc.nist.gov/pubs/sp/800/218/final> and <https://csrc.nist.gov/pubs/sp/800/218/a/final>.

[^owasp-llm]: OWASP GenAI Security Project, “Top 10 for LLM Applications 2025.” The project identifies prompt injection, sensitive-information disclosure, supply-chain risks, data/model poisoning, improper output handling, excessive agency, system-prompt leakage, vector/embedding weaknesses, misinformation, and unbounded consumption: <https://genai.owasp.org/llm-top-10/>.

[^otel-signals]: OpenTelemetry, “Signals.” OpenTelemetry currently defines traces, metrics, logs, and baggage as telemetry signals: <https://opentelemetry.io/docs/concepts/signals/>.

[^otel-sensitive]: OpenTelemetry, “Handling sensitive data.” The guidance describes attribute deletion, filtering, redaction, transformation, truncation, and the limitations of simple hashing as anonymization: <https://opentelemetry.io/docs/security/handling-sensitive-data/>.

[^otel-collector]: OpenTelemetry, “Collector” and “Security.” The Collector provides vendor-neutral telemetry receiving, processing, and exporting and can perform batching, encryption, and sensitive-data filtering; its security guidance notes that telemetry can contain PII, application-specific data, and network patterns: <https://opentelemetry.io/docs/collector/> and <https://opentelemetry.io/docs/security/>.

[^github-security]: GitHub Docs, “GitHub security features” and “Enabling secret scanning for your repository.” Public repositories receive secret scanning, and supported push-protection features can block detected credentials before they enter the repository: <https://docs.github.com/en/code-security/getting-started/github-security-features> and <https://docs.github.com/en/code-security/how-tos/secure-your-secrets/detect-secret-leaks/enable-secret-scanning>.

[^slsa]: Supply-chain Levels for Software Artifacts, “SLSA v1.0.” SLSA defines supply-chain integrity and provenance levels for software artifacts: <https://slsa.dev/spec/v1.0/>.

[^sigstore]: Sigstore, “Cosign signing overview” and “Verifying signatures.” Sigstore supports identity-bound short-lived certificates, signatures, verification bundles, timestamps, and transparency-log evidence for artifact verification: <https://docs.sigstore.dev/cosign/signing/overview/> and <https://docs.sigstore.dev/cosign/verifying/verify/>.
