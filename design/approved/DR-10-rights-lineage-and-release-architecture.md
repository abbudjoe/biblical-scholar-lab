# DR-10 — Rights, Lineage, and Release Architecture

| Field | Value |
|---|---|
| Design ID | `DR-10` |
| Status | `APPROVED` |
| Approval date | 2026-08-15 |
| Project owner | Joseph Abbud |
| Designer and independent reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09 |
| Implementation authority | GPT-5.6 Sol, under the approved design |

## 1. Purpose

Biblical Scholar Lab will combine materials whose legal, contractual, ethical, cultural, and release conditions differ substantially.

A single source package may contain separately governed components such as:

- an ancient work whose underlying wording is in the public domain;
- a modern critical edition or transcription;
- a copyrighted modern translation;
- morphology, syntax, alignment, or semantic annotation;
- manuscript or printed-page images owned or controlled by a repository;
- an apparatus governed by a publisher or subscription agreement;
- software under an open-source license;
- a database subject to separate database rights;
- metadata available more broadly than the full text;
- user-uploaded material authorized only for a private session;
- derived embeddings, indexes, training examples, benchmark cases, adapters, or model weights.

The project's noncommercial research purpose broadens the materials that may be worth evaluating. It does not establish that every acquisition, transformation, training use, hosted service, quotation, benchmark release, adapter release, or model-weight release is permitted.

Likewise:

```text
publicly viewable
≠ public domain
≠ openly licensed
≠ downloadable in bulk
≠ trainable
≠ redistributable
≠ releasable in model weights
```

DR-10 defines the authoritative logical contract for:

- component-level rights identity;
- rights evidence, legal basis, permissions, restrictions, and uncertainty;
- operation-specific authorization;
- jurisdiction, purpose, user, and time scope;
- open, reciprocal, noncommercial, licensed, private, transient, holdout, and excluded storage zones;
- corpus, benchmark, retrieval, model, adapter, quantized, and mobile lineages;
- attribution, notice, reciprocity, noncommercial, no-derivatives, confidentiality, and access-control obligations;
- source revocation, rights disputes, quarantine, impact analysis, and rebuild requirements;
- artifact-specific review and release decisions;
- public-repository boundaries;
- model and dataset cards, bills of materials, training-data summaries, and release terminology;
- runtime enforcement, validation, benchmark cases, and hard failures.

DR-10 is a technical and governance design. It does not provide legal advice or replace qualified counsel. Any consequential reliance on fair use, statutory text-and-data-mining exceptions, custom contracts, disputed licenses, or the release of weights trained on non-open material requires a separately documented legal review approved by the project owner.

## 2. Governing principle

> **Permission is specific to the component, operation, purpose, jurisdiction, actor, time, and resulting artifact. Lawful access, internal analysis, model training, public display, corpus redistribution, and model release are separate decisions. A transformation never erases the rights, restrictions, provenance, or ethical obligations of its inputs. Unknown permission fails closed.**

The system must preserve this chain:

```text
rights-bearing component
    → exact rights and access evidence
    → operation-specific authorization decision
    → controlled storage and processing lane
    → exact derivation lineage
    → artifact-specific obligations and risk assessment
    → owner-approved release, restricted use, quarantine, or destruction
```

No later artifact may silently become more permissive than its approved lineage.

## 3. Rights architecture is multidimensional

DR-10 rejects one flat `license` field as an adequate rights model.

A rights assessment may need to consider independently:

```text
copyright and neighboring rights
public-domain status
contract and terms of use
clickthrough or access conditions
sui generis database rights
moral rights
privacy and publicity rights
confidentiality
trade secrets
repository and image-reuse terms
community and cultural protocols
research-ethics commitments
model or software acceptable-use terms
security and access-control obligations
statutory exceptions and limitations
jurisdiction-specific regulation
```

A source is authorized only when every applicable layer required for the proposed operation has an adequate basis or an explicit reviewed exception.

A Creative Commons license, for example, may grant copyright and applicable database permissions while leaving privacy, publicity, moral, cultural, contractual, or third-party rights unresolved. Creative Commons itself cautions that a license may not provide every permission necessary and that separately held elements must be identified.[^cc-considerations]

## 4. Rights subjects are component-specific

The canonical `RightsSubject` can identify any bounded object or revision whose conditions may differ from its container.

Required subject classes include:

```text
WORK
TEXTUAL_FORM
EDITION
TRANSLATION
APPARATUS
TRANSCRIPTION
ANNOTATION_LAYER
ALIGNMENT_LAYER
DATABASE_OR_COLLECTION
METADATA_RECORD
IMAGE_OR_SCAN
PAGE_REGION
AUDIO_OR_VIDEO
SOFTWARE
MODEL_ARCHITECTURE
BASE_MODEL
TOKENIZER
CHECKPOINT
ADAPTER
QUANTIZED_MODEL
EMBEDDING
INDEX
DATASET
TRAINING_EXAMPLE
BENCHMARK_CASE
EVALUATION_OUTPUT
REPORT
USER_UPLOAD
GENERATED_OUTPUT
```

A container-level license may not be propagated automatically to every component.

Examples:

- An open dataset repository may include a modern translation under another license.
- A public-domain ancient text may appear in a copyrighted modern edition.
- Open metadata may describe a restricted image.
- An open running text may be accompanied by a restricted critical apparatus.
- Source code and bundled data may use unrelated licenses.
- A model repository may use one license for weights and another for code.

Every consequential component receives its own rights subject or an explicit inheritance relationship whose scope has been reviewed.

## 5. Rights evidence is immutable and source-preserving

A `RightsEvidenceRecord` preserves what the project actually relied upon.

It records at least:

```text
evidence_id
rights_subject_id
source or grantor
asserted authority of grantor
license or terms identity
exact legal text or terms snapshot
canonical URL and retrieval time
content hash
version and jurisdiction
scope of licensed elements
permission letter or contract, if any
public-domain rationale, if any
statutory-exception analysis, if any
machine-readable reservation or opt-out, if any
repository or image-use policy
community or cultural labels and notices
reviewer
review state
valid-from and expiry or review date
superseding evidence
known conflicts
```

A link to a live webpage is not sufficient by itself. The system preserves a dated, hashed snapshot or an authoritative record sufficient to reconstruct the decision.

The grantor's authority is separate from the stated license. A dataset compiler cannot grant rights it does not hold in underlying translations, images, articles, annotations, or database contents.

## 6. Rights assertions and decisions remain separate

A `RightsAssertion` records a sourced proposition such as:

```text
this component is marked CC BY 4.0
this image is controlled by repository X
this translation is public domain in jurisdiction Y
this source reserves Article 4 text-and-data-mining rights
this contract permits local noncommercial research training
this permission excludes redistribution of derivatives
```

An `OperationAuthorizationDecision` is the project's reviewed conclusion for a particular proposed use.

It identifies:

```text
rights_subject revision
operation
purpose profile
actor or role
jurisdiction profile
time window
resulting artifact class
authorization status
legal or contractual basis
conditions and obligations
required controls
reviewer and approver
supporting evidence
unresolved risks
review or expiry date
```

The system does not turn a provider's self-reported license label directly into project authorization.

## 7. Operation taxonomy

DR-10 requires separate authorization for materially different operations.

The minimum taxonomy is:

```text
DISCOVER_METADATA
VIEW_INTERACTIVELY
DOWNLOAD_OR_ACQUIRE
RETAIN_RAW_COPY
CREATE_BACKUP
OCR_OR_TRANSCRIBE
NORMALIZE_OR_CLEAN
TRANSLITERATE
TRANSLATE
ANNOTATE
ALIGN
COLLATE
TEXT_AND_DATA_MINE
CREATE_LEXICAL_INDEX
CREATE_VECTOR_EMBEDDING
CREATE_VECTOR_INDEX
INTERNAL_RAG_RETRIEVAL
USER_FACING_RAG_DISPLAY
PRIVATE_EVALUATION
PUBLIC_BENCHMARK_USE
QUOTE_OR_DISPLAY_EXCERPT
CREATE_DERIVED_DATASET
CONTINUED_PRETRAIN
SUPERVISED_FINE_TUNE
PREFERENCE_TRAIN
DISTILL
MODEL_MERGE
QUANTIZE_OR_CONVERT
RELEASE_RAW_SOURCE
RELEASE_DERIVED_DATA
RELEASE_EMBEDDINGS_OR_INDEX
RELEASE_ADAPTER
RELEASE_FULL_WEIGHTS
RELEASE_QUANTIZED_OR_MOBILE_MODEL
HOST_INFERENCE_SERVICE
PUBLISH_REPORT_OR_MODEL_CARD
ARCHIVE
DELETE_OR_DESTROY
```

Authorization for one operation does not imply authorization for another.

Examples:

- Permission to read a subscription article does not imply permission to download and index the complete publication.
- Permission for local research training does not imply permission to release the trained weights.
- Permission to quote short evidence passages does not imply permission to publish a benchmark containing full chapters.
- Permission to use a dataset does not imply permission to redistribute its embeddings or normalized derivative.
- Permission to release an adapter does not imply permission to release merged full weights.

## 8. Purpose profiles

Every consequential operation identifies an approved purpose profile.

The initial profiles are:

```text
INTERNAL_NONCOMMERCIAL_RESEARCH
PUBLIC_NONCOMMERCIAL_RESEARCH
EDUCATIONAL_DEMONSTRATION
PRIVATE_USER_ANALYSIS
PUBLIC_RESEARCH_PREVIEW
OPEN_RESEARCH_RELEASE
COMMERCIAL_OR_REVENUE_DIRECTED
LEGAL_COMPLIANCE_OR_AUDIT
PRESERVATION
UNKNOWN_PURPOSE
```

The project owner's present intention is noncommercial research. This is recorded as project context, not used as an automatic determination that every `NonCommercial` license or statutory exception applies.

Whether a use is noncommercial may depend on the complete factual context, including hosting, sponsorship, downstream use, organizational structure, or indirect commercial advantage. Ambiguous cases remain `REVIEW_REQUIRED`.

## 9. Jurisdiction profiles

Rights decisions are jurisdiction-scoped.

The system records:

```text
place of project operation
place of acquisition
place of training
place of storage
place of model distribution
intended market or user geography
relevant choice-of-law or contract clause
jurisdictions considered in the review
```

A United States fair-use analysis does not automatically authorize distribution or training in the European Union or another jurisdiction.

Similarly, European Union text-and-data-mining rules distinguish research-organization and cultural-heritage uses from the broader Article 4 exception, which is subject to lawful access and rights reservations. The project may not assume that it qualifies as a research organization or that a source has not opted out.[^eu-dsm]

## 10. Authorization statuses

Every operation decision has one status:

```text
ALLOWED
ALLOWED_WITH_CONDITIONS
INTERNAL_ONLY
TRANSIENT_ONLY
REVIEWED_EVIDENCE_PACKET_ONLY
METADATA_ONLY
OWNER_PERMISSION_REQUIRED
QUALIFIED_LEGAL_REVIEW_REQUIRED
HOLD_CONFLICTING_RIGHTS
DENIED
UNKNOWN
EXPIRED_OR_REVOKED
```

`UNKNOWN`, missing evidence, and conflicting terms fail closed.

A system may use a more restrictive status than the law strictly requires as a project governance choice. It may not silently use a more permissive status than the approved decision.

## 11. Public-domain material

A public-domain determination is component- and jurisdiction-specific.

The system distinguishes:

```text
underlying ancient work
specific textual reconstruction
editorial selection and arrangement
critical apparatus
modern transcription
translation
annotation
introduction or commentary
page image or scan
collection database
```

The age of an ancient work does not place every modern representation of that work in the public domain.

A public-domain determination records:

- the relevant component;
- the jurisdiction and date;
- the author or publication facts used;
- the status of anonymous, corporate, unpublished, or posthumous material where relevant;
- the reviewer and evidence;
- any separately controlled elements.

CC0 and the Public Domain Mark are also distinct. CC0 is a rights-waiver and fallback-license tool; the Public Domain Mark is a status label for works believed to be free of known copyright restrictions.[^cc-public-domain]

## 12. Creative Commons licenses

The system records the exact Creative Commons license, version, jurisdiction port if any, licensed component, attribution request, and modifications.

### 12.1 Attribution

For CC BY and every other CC license containing BY, public sharing must satisfy the applicable attribution and change-notice requirements.

The project generates an `AttributionBundle` rather than expecting a model to remember attribution from weights.

### 12.2 NonCommercial

CC BY-NC and CC BY-NC-SA material remains in a dedicated noncommercial lineage.

It may not enter an artifact intended for commercial or unrestricted downstream use without separate permission or a reviewed legal basis.

The project may use noncommercial material internally only after the operation is approved; the label `research` alone is insufficient.

### 12.3 ShareAlike

CC BY-SA, CC BY-NC-SA, ODbL, and other reciprocal licenses remain in separate reciprocal lineages.

DR-10 does not declare whether every trained model, embedding, index, adapter, benchmark, or derived record is legally an adaptation or derivative database. That issue can vary by artifact and jurisdiction.

Instead, the project requires:

- explicit source lineage;
- license-compatibility analysis before combining reciprocal sources;
- a separate release review for every potentially covered artifact;
- no claim that a restrictive obligation disappeared during training or transformation.

Creative Commons maintains a specific compatibility list for ShareAlike licenses; compatibility is not inferred merely because two licenses are both described as open.[^cc-compatible]

### 12.4 NoDerivatives

CC BY-ND and CC BY-NC-ND permit sharing only in unadapted form under their stated conditions.

The project does not assume that normalization, annotation, translation, benchmark conversion, or model training is either permitted or prohibited in every jurisdiction merely from the ND label.

Until an operation-specific review concludes otherwise:

```text
public redistribution of modified ND content → DENIED
weight training on ND content → QUALIFIED_LEGAL_REVIEW_REQUIRED
internal exact-text retrieval → case-specific review
quotation under an exception or limitation → case-specific review
```

### 12.5 Other rights

A CC license does not automatically clear third-party content, privacy, publicity, moral, database, contractual, cultural, or confidentiality concerns. Those layers remain separately reviewed.[^cc-by-nc-sa]

## 13. Open-data and database rights

Database structure and database contents may have different rights.

The system separately records:

```text
database copyright
sui generis database rights
rights in individual contents
API or access terms
collection-level license
record-level exceptions
```

CC 4.0 licenses can cover applicable sui generis database rights where the licensor holds them, while Open Data Commons provides database-specific tools such as ODbL, ODC-By, and PDDL.[^cc-database][^odbl]

A database license does not automatically clear copyright or other rights in each contained text, image, translation, or annotation.

Frequent extraction of small portions may still implicate database rights in some jurisdictions; the project records cumulative extraction and the reviewed basis for acquisition.

## 14. Custom licenses, clickthrough terms, and public access

A custom license or permission is represented as exact contract evidence, not translated into a familiar open-license label unless the equivalence is actually established.

The system records:

- parties;
- authorized users;
- authorized purpose;
- access method;
- permitted operations;
- confidentiality;
- security requirements;
- publication and attribution terms;
- governing law;
- term and termination;
- audit or deletion duties;
- downstream and subcontractor restrictions.

Gated or clickthrough access is not the same as open access. Access may be granted to an individual rather than the project or organization, may be revocable, and may carry terms beyond the visible license metadata. Hugging Face, for example, documents that gated dataset and model access is granted to individual users and can later be removed by the provider.[^hf-gated-datasets][^hf-gated-models]

A public GitHub repository is also not automatically open source. Without an explicit license, default copyright rules continue to apply beyond the platform's viewing and forking functionality.[^github-license]

## 15. Access controls and technical restrictions

The project does not bypass:

- authentication;
- paywalls;
- technical protection measures;
- rate limits;
- robots or machine-readable rights reservations;
- access controls;
- geographic restrictions;
- repository terms;
- expired credentials;
- revoked user grants.

Whether a technical access method is possible is separate from whether it is authorized.

Acquisition adapters must identify their access basis and may not silently switch from an authorized API to unapproved scraping.

Credentials remain outside Git, logs, model context, and public handoffs.

## 16. Exceptions, limitations, and text-and-data mining

Statutory exceptions are represented as reviewed, jurisdiction-specific legal bases—not generic source licenses.

### 16.1 United States

Fair use is fact-specific. Nonprofit scholarship and research are relevant considerations, but they do not make every use fair automatically. The U.S. Copyright Office's fair-use guidance describes a four-factor analysis, and the Congressional Research Service notes that generative-AI training outcomes cannot be prejudged categorically: some uses may qualify and others may not.[^us-fair-use][^crs-ai]

An authorization relying on fair use records:

```text
specific operation and purpose
nature and amount of material
transformative or substitutive character
security and retention controls
output and market-substitution risk
memorization and extraction tests
public versus internal use
counsel or qualified reviewer
review date and relevant legal developments
```

A fair-use conclusion for private research does not automatically authorize public release of a corpus or model.

### 16.2 European Union

The project distinguishes Article 3 and Article 4 text-and-data-mining bases under Directive 2019/790.

It records:

- whether the actor qualifies under the relevant rule;
- whether access was lawful;
- whether rights were reserved in an appropriate manner;
- permitted retention;
- security obligations;
- the member-state implementation considered.

It does not assume that a United States-based individual research project qualifies as a research organization for Article 3.

### 16.3 Other jurisdictions

Other jurisdictions require their own review. No global authorization is derived by selecting the most permissive country.

## 17. AI-specific legal uncertainty

DR-10 treats the legal status of training, embeddings, adapters, weights, and generated outputs as an evolving question.

The U.S. Copyright Office's May 2025 pre-publication report addresses copyright issues throughout acquisition, curation, training, retrieval, and outputs and does not establish one categorical answer for all training uses.[^usco-ai-part3]

Therefore:

- no source enters public-release model training solely because the project is noncommercial;
- no trained artifact is assumed to be free of input obligations merely because it contains learned parameters rather than readable text;
- no source is assumed to control weights merely because it appeared in training;
- no legal conclusion is inferred from technical vocabulary such as `embedding`, `adapter`, `delta`, or `distillation`;
- artifact-specific review and empirical extraction testing are mandatory before release.

## 18. Ethical and community authority may be stricter than legal permission

Legal copyright status does not exhaust the project's responsibilities.

The system can record:

```text
community authority
sacred or secret status
culturally sensitive use
gender, clan, family, or seasonal restrictions
requested attribution
community verification
commercialization conditions
repatriation or takedown request
```

Local Contexts provides Traditional Knowledge and Biocultural Labels and Notices designed to communicate Indigenous authority, provenance, protocols, and permissions around cultural heritage and data.[^local-contexts]

Such labels and community protocols do not need to function as copyright licenses to become binding project-governance constraints.

Materials marked sacred, secret, restricted, culturally sensitive, or subject to a credible community concern default to `HOLD_CONFLICTING_RIGHTS` or a more restrictive lane until reviewed.

## 19. Personal, confidential, and user-provided material

Rights and privacy are separate but interacting concerns.

User-uploaded Bible pages, research libraries, notes, annotations, emails, or unpublished manuscripts default to:

```text
PRIVATE_USER_ANALYSIS
TRANSIENT_ONLY or time-bounded private retention
NO_MODEL_TRAINING
NO_CROSS_USER_RETRIEVAL
NO_PUBLIC_BENCHMARK_USE
NO_PUBLIC_RELEASE
```

The user may grant a broader permission only through an explicit, informed, operation-specific opt-in.

The project does not assume that a user owns every element they upload. It can process material privately under the approved service terms while still prohibiting public redistribution or training reuse.

Sensitive personal information, confidential correspondence, peer-review material, unpublished research, and licensed private libraries remain isolated under DR-27 controls.

## 20. Canonical storage and access zones

The logical storage topology includes at least:

```text
Z0_PUBLIC_REPOSITORY
Z1_OPEN_PERMISSIVE
Z2_OPEN_RECIPROCAL
Z3_RESEARCH_NONCOMMERCIAL
Z4_LICENSED_RESTRICTED
Z5_TRANSIENT_AUTHORIZED
Z6_USER_PRIVATE
Z7_PRIVATE_BENCHMARK_HOLDOUT
Z8_QUARANTINE_OR_RIGHTS_HOLD
Z9_SECRETS_AND_CREDENTIALS
```

### Z0 — Public repository

Contains only public-safe code, design documents, schemas, manifests, public benchmark material, aggregate reports, and review handoffs.

No restricted source text, credentials, private holdout, user upload, licensed image, subscription apparatus, or reconstructable private index may enter this zone.

### Z1 — Open permissive

Contains components approved for the intended open operations under public-domain, CC0, CC BY, permissive open-data, or equivalent terms, with attribution and other conditions retained.

### Z2 — Open reciprocal

Contains CC BY-SA, ODbL, or other reciprocal material whose obligations require separate compatibility and release handling.

### Z3 — Research noncommercial

Contains CC BY-NC, CC BY-NC-SA, and other components approved only for the project's noncommercial research operations.

### Z4 — Licensed restricted

Contains subscription, negotiated, institutionally licensed, or local-only resources.

### Z5 — Transient authorized

Contains material that may be processed for a bounded session or request but not retained beyond the approved period.

### Z6 — User private

Contains user-specific material isolated from all other users and all training lineages.

### Z7 — Private benchmark holdout

Contains protected final evaluation cases and evidence unavailable to model builders and public CI.

### Z8 — Quarantine or rights hold

Contains disputed, incompletely documented, revoked, conflicting, or potentially mislicensed material. No downstream use occurs while in this zone.

### Z9 — Secrets and credentials

Contains credentials and security-sensitive authorization material outside source control and model-visible context.

DR-28 will choose the physical stores and service boundaries that realize these zones.

## 21. Corpus and model lineage classes

The canonical artifact lineage classes are:

```text
L0_OPEN_PERMISSIVE
L1_OPEN_RECIPROCAL
L2_RESEARCH_NONCOMMERCIAL
L3_LOCAL_RESEARCH_ONLY
L4_RAG_ONLY_RESTRICTED
L5_USER_PRIVATE_TRANSIENT
L6_PRIVATE_HOLDOUT
L7_QUARANTINED_OR_EXCLUDED
```

Every dataset materialization, index, training run, checkpoint, adapter, merge, quantized artifact, report, and evaluation records the complete set of input lineages.

An artifact produced from several classes receives an `AggregateRightsState`.

The aggregate state is conservative:

- It does not declare that the most restrictive input license legally attaches to the output merely because the input was used.
- It does prevent the project from releasing the output more permissively until artifact-specific review establishes that release.
- It preserves every input obligation and uncertainty for the release reviewer.

This is a governance taint model, not an assertion about derivative-work law.

## 22. No license laundering through transformation

The following operations do not automatically erase input restrictions:

```text
OCR
normalization
transliteration
translation
annotation
alignment
deduplication
chunking
embedding
vector indexing
synthetic-question generation
continued pretraining
fine-tuning
preference training
distillation
model merging
quantization
format conversion
```

Every derived artifact retains a machine-readable `DerivationRightsManifest` linking it to exact input rights subjects and operation decisions.

A model-generated paraphrase, translation, annotation, or benchmark question is not automatically unrestricted. It retains model, prompt, retrieved-source, and human-review provenance.

Human editing also does not erase upstream lineage.

## 23. Embeddings, lexical indexes, and retrieval systems

Embeddings and indexes can preserve or expose protected information even when they are not ordinary readable copies.

The project therefore treats them as separately reviewable artifacts.

Required properties include:

```text
input source revisions
index or embedding model
chunking and normalization
reconstruction or inversion risk
access zone
query authorization
user-visible display limit
retention and deletion policy
release status
```

A public vector index is not presumed safe merely because raw text files are absent.

RAG access is source-aware:

- retrieval permission is checked before candidate selection;
- user identity and entitlement constrain the search space;
- display permission and quotation limits are checked after retrieval;
- a citation does not grant permission to reproduce the source;
- restricted evidence may support an internal answer only under the approved access contract;
- the system must not expose source text to a user who lacks access merely because the model or index can retrieve it.

## 24. Training stages receive independent rights decisions

Authorization for continued pretraining does not imply authorization for SFT, preference training, or distillation, and vice versa.

Each stage records:

```text
training purpose
source components
text or annotation fields used
sampling weights
sequence construction
whether text may be memorized verbatim
model and tokenizer
output artifact classes
planned release status
jurisdictions
legal and contractual basis
memorization controls
attribution and reporting obligations
```

Modern scholarship remains retrieval-first under DR-09 unless DR-10 and the later curriculum review authorize a specific training use.

Restricted apparatus, copyrighted translations, and subscription full text remain outside model weights by default.

## 25. Base-model, tokenizer, and software licenses

The upstream base model, tokenizer, code, kernels, libraries, and runtime dependencies form part of every downstream release lineage.

The project records:

```text
exact upstream revision
license and acceptable-use terms
redistribution rights
fine-tuning and derivative-model rights
notice requirements
patent provisions
trademark restrictions
export or territory terms
use restrictions
compatibility with the planned release
```

A permissively licensed training corpus cannot make a downstream model releasable if the base-model terms prohibit or condition that release.

Likewise, an open-weight base model is not automatically an Open Source AI system.

The project uses precise terminology:

```text
PUBLICLY ACCESSIBLE
OPEN WEIGHTS
OPEN MODEL
OPEN SOURCE SOFTWARE
OPEN DATA
OPEN SOURCE AI
RESEARCH-ONLY MODEL
NONCOMMERCIAL MODEL
GATED MODEL
PROPRIETARY MODEL
```

The label `Open Source AI` is used only when the released system satisfies the approved definition and evidence requirements. The Open Source Initiative's definition requires freedoms to use, study, modify, and share, along with access to the preferred form for modification, including data information, code, and parameters.[^osaid]

## 26. Adapters, merged weights, quantized models, and mobile packages

The following are separate release artifacts:

```text
LoRA or other adapter
merged full weights
intermediate checkpoint
optimizer state
quantized weights
mobile runtime package
Core ML or LiteRT conversion
vision or OCR component
retrieval index
tool database
```

Permission to release one does not authorize the others.

Adapters and deltas may encode memorized source material or reveal the base model's licensed parameters when combined improperly. They require their own extraction, compatibility, and license review.

Quantization and format conversion preserve upstream model and data lineage. They do not create a new unrestricted model.

A mobile package may include licensed Bible text, morphology, embeddings, fonts, OCR models, or other components whose conditions differ from the language-model weights.

## 27. Distillation, synthetic data, and teacher models

A teacher-generated dataset records:

```text
teacher model and license
prompt and system policy
retrieved evidence
source rights
output generation settings
human review
student training use
release plan
```

Distillation does not automatically erase restrictions on:

- the teacher model;
- protected prompts or retrieved evidence;
- reproduced passages;
- generated outputs substantially similar to inputs;
- user or private data.

Synthetic examples derived from restricted material remain in a restricted lineage unless a reviewed process establishes an independently releasable artifact.

## 28. Benchmark and evaluation rights

Public development cases, public reproducibility cases, private holdout cases, and fresh expert challenge cases remain distinct.

Every case records:

```text
question rights and author
source evidence rights
quoted-text limits
image rights
annotation rights
scorer and rubric rights
public or private status
model contamination status
release license
```

A public benchmark must not become a vehicle for redistributing copyrighted translations, complete apparatus entries, subscription scholarship, or page scans.

Where a restricted source is needed for valid evaluation, the benchmark may use:

- a private evidence packet;
- a licensed evaluator environment;
- a minimal lawful quotation;
- a deterministic source lookup performed under access control;
- a public-safe synthetic analogue whose limitations are disclosed.

Private holdout hashes and aggregate reports may be public while cases remain private.

## 29. Attribution and notices are generated from lineage

Every public artifact receives an automatically generated but human-reviewed obligations bundle.

It can include:

```text
source title and identifier
creator, editor, translator, or institution
copyright notice
license and legal-code link
required attribution text
change notice
share-alike or reciprocal terms
third-party notices
base-model notice
software dependency notices
dataset and model lineage summary
community or cultural notices
citation and acknowledgment requests
```

Attribution is not delegated to the model's memory.

The project preserves both human-readable and machine-readable notices.

## 30. Rights manifests and bills of materials

Every consequential artifact has an `ArtifactRightsManifest` containing:

```text
artifact identity and revision
artifact class
complete derivation lineage
component rights subjects
declared and concluded licenses
operation authorizations
purpose and jurisdiction profiles
attribution obligations
reciprocity and noncommercial conditions
access and security requirements
cultural and ethical protocols
privacy flags
unknowns and conflicts
release decision
reviewer and owner approval
content hashes
superseding manifest
```

SPDX 3.0.1 provides useful Dataset, AI, Build, and Licensing profiles for exchanging dataset, model, build, and concluded-license information. Biblical Scholar Lab will support an SPDX adapter while retaining its more detailed internal operation and scholarship contracts.[^spdx-dataset][^spdx-ai]

RightsStatements.org URIs may be retained as cultural-heritage status assertions where supplied, but they are not substituted for licenses or project authorization decisions.[^rights-statements]

## 31. Rights compatibility analysis

Before combining sources or releasing an artifact, the system performs compatibility analysis across:

- component licenses;
- commercial/noncommercial purposes;
- share-alike and reciprocal terms;
- no-derivatives restrictions;
- custom contracts;
- base-model and software terms;
- public and private storage requirements;
- attribution feasibility;
- jurisdiction-specific exceptions;
- cultural and ethical protocols;
- intended release license and distribution channel.

A compatibility solver may assist. Its result remains a reviewable candidate, not legal authority.

No artifact is described as `license-compatible` when the conclusion depends on unresolved legal treatment of model weights, embeddings, or training.

## 32. Rights changes, revocation, disputes, and quarantine

When rights evidence changes or is challenged, the system creates a `RightsIncident`.

Possible triggers include:

- corrected license metadata;
- evidence that the uploader lacked authority;
- access revocation;
- updated repository terms;
- a rights reservation;
- expiration of permission;
- privacy or confidentiality concern;
- community request;
- court or regulatory change;
- source takedown;
- discovered restricted content inside an open package.

The immediate actions are:

1. Quarantine the affected component and stop new downstream use.
2. Preserve the prior evidence and decision history.
3. Identify every dataset, index, benchmark, checkpoint, adapter, model, report, and release that depends on it.
4. Suspend affected releases or access where required.
5. Determine whether deletion, reindexing, dataset rebuild, retraining, model withdrawal, or updated disclosure is necessary.
6. Record the owner-approved disposition.

The project does not assume that deleting source files removes their influence from already trained weights.

It also does not assume that every later license change revokes a prior irrevocable license properly relied upon. The incident review determines the effect from the exact evidence and law.

## 33. Memorization and extraction review

Before releasing any model, adapter, embedding index, or tool package trained or built from nontrivial source material, the project evaluates:

- exact and near-exact passage reproduction;
- source-specific extraction attacks;
- rare-sequence memorization;
- copyrighted translation continuation;
- apparatus or commentary reconstruction;
- private and holdout leakage;
- user-upload leakage;
- attribution and source-identification behavior;
- suppression or access-control bypass.

A release may be blocked even where the underlying training use was authorized if the artifact exposes source content beyond the approved output rights.

Memorization testing is a release control, not a substitute for legal authorization.

## 34. Release artifact classes

The project reviews independently:

```text
PUBLIC_SOURCE_CODE
DESIGN_DOCUMENTATION
PUBLIC_METADATA_MANIFEST
PUBLIC_CORPUS
PUBLIC_DERIVED_DATASET
PUBLIC_BENCHMARK
GATED_RESEARCH_DATASET
RETRIEVAL_SERVICE
MODEL_ADAPTER
FULL_MODEL_WEIGHTS
QUANTIZED_MODEL
MOBILE_PACKAGE
HOSTED_RESEARCH_PREVIEW
EVALUATION_REPORT
RESEARCH_PAPER
ATTRIBUTION_OR_TRAINING_SUMMARY
```

A public code release does not imply a public corpus release. A public model card does not imply public weights. A public benchmark harness does not imply public holdout cases.

## 35. Release statuses

Every artifact revision has exactly one release status:

```text
NOT_REVIEWED
INTERNAL_RESEARCH_ONLY
PRIVATE_LICENSED_USE
TRANSIENT_USE_ONLY
GATED_RESEARCH_RELEASE_APPROVED
PUBLIC_METADATA_ONLY
PUBLIC_RELEASE_APPROVED
PUBLIC_RELEASE_APPROVED_WITH_CONDITIONS
HOLD_LEGAL_REVIEW
HOLD_RIGHTS_CONFLICT
HOLD_PRIVACY_OR_SECURITY
WITHDRAWN_OR_RECALLED
RELEASE_PROHIBITED
```

Release approval is revision-specific. A new checkpoint, dataset refresh, merged adapter, updated benchmark, or changed license requires a new review.

## 36. Release workflow

The required workflow is:

```text
candidate artifact frozen
→ exact lineage and rights manifest generated
→ source obligations and unknowns reviewed
→ license and purpose compatibility assessed
→ privacy, security, cultural, and confidentiality review
→ memorization and extraction evaluation
→ model/dataset/benchmark card and training-content summary prepared
→ public-safe attribution and notices generated
→ independent ChatGPT evidence review
→ project-owner release approval
→ publication through approved channel
→ post-release monitoring and incident capability
```

Sol may prepare release candidates and evidence. Sol may not approve release.

Luna may execute a frozen publication command only inside an owner-approved release campaign and may not alter the artifact or terms.

## 37. Public repository policy

The repository will be public for transparent code and review, but visibility is not used as a content license.

The repository must distinguish:

```text
project-authored code
project-authored documentation
public schemas and examples
third-party code
third-party data
public-domain content
licensed content
nonredistributable references
private or restricted artifacts
```

The root license must state its exact scope. It cannot silently relicense third-party texts, images, datasets, model weights, fonts, or generated artifacts.

The repository should include, as applicable:

```text
LICENSE or LICENSES/
NOTICE
THIRD_PARTY_NOTICES
ATTRIBUTION
DATA_LICENSES
MODEL_LICENSES
RIGHTS_MANIFESTS
SECURITY
CONTRIBUTING
```

The exact code and documentation licenses remain an owner decision deferred until the release review. Until then, public visibility does not grant reuse beyond platform terms.

## 38. Model, dataset, and benchmark cards

Every released artifact receives documentation appropriate to its class.

A model card records at least:

- exact base model and lineage;
- code and runtime dependencies;
- training stages and approved data summaries;
- source and license categories;
- rights and release limitations;
- supported languages and tasks;
- evaluations and hard failures;
- memorization and extraction results;
- intended and prohibited uses;
- known gaps and current status.

A dataset or benchmark card records:

- composition and provenance;
- component licenses and rights lanes;
- acquisition and processing;
- languages and coverage;
- private/public split;
- known biases and limitations;
- access and redistribution rules.

Hugging Face model and dataset cards support explicit license, base-model, dataset, language, and evaluation metadata and can be used as one release adapter, not as the internal source of truth.[^hf-model-cards][^hf-dataset-cards]

## 39. Training-data transparency and EU release readiness

The project records training data at sufficient granularity to support future regulatory and release obligations.

For any general-purpose model placed on the European Union market, current European Commission guidance says providers must maintain a copyright-compliance policy and publish a sufficiently detailed summary of training content; the public-summary obligation applies to open-source models as well.[^eu-gpai]

Therefore, every training run must preserve:

```text
source categories and main collections
provenance and acquisition method
rights reservations and copyright policy
selection, filtering, and cleaning
languages and modalities
synthetic-data sources
fine-tuning and preference datasets
private and user-data exclusions
material data gaps
model version relationship
```

The project will not wait until release to reconstruct this information from memory.

## 40. Runtime rights tools

DR-10 requires logical operations including:

```text
resolve_rights_subject
get_rights_evidence
check_operation_authorization
check_user_entitlement
check_quote_and_display_permission
get_attribution_bundle
get_artifact_rights_manifest
trace_rights_lineage
check_license_compatibility
check_release_readiness
quarantine_subject
calculate_impact_set
render_training_content_summary
render_third_party_notices
```

Every response returns:

- exact subject and revision;
- requested operation, purpose, jurisdiction, and artifact;
- authorization status;
- conditions and controls;
- evidence and review state;
- expiry or refresh date;
- unresolved conflicts;
- required next action.

The model may not override a deterministic `DENIED`, `HOLD`, `UNKNOWN`, or entitlement failure.

## 41. Validation invariants

The following invariants are mandatory:

1. No component enters processing without a rights subject and evidence state.
2. A container license cannot silently propagate to separately governed components.
3. Every operation identifies its purpose, jurisdiction, actor, and resulting artifact.
4. Authorization for access does not imply authorization for training or redistribution.
5. Authorization for training does not imply authorization for model release.
6. Public domain in one component does not imply public domain in its edition, translation, image, annotation, or database.
7. Public visibility does not imply an open license.
8. Unknown or conflicting permission fails closed.
9. Every derived artifact preserves complete input rights lineage.
10. No transformation launders restrictions or removes attribution history.
11. Reciprocal and noncommercial lineages remain separable.
12. Restricted content cannot enter public CI, PRs, handoffs, logs, or artifacts.
13. User-private material cannot enter shared retrieval or training.
14. Private benchmark holdouts cannot enter training or public model context.
15. Rights reservations, access revocation, and expiration are enforced.
16. An artifact's release status is revision-specific.
17. Every public release has a reviewed rights manifest and obligations bundle.
18. Model, adapter, index, and quantized releases receive independent review.
19. Fair use and statutory exceptions are jurisdiction- and operation-specific decisions.
20. Automated license parsing and compatibility results remain candidates until reviewed.
21. Rights, privacy, cultural authority, and contract constraints remain separate.
22. Rights incidents produce complete downstream impact analysis.
23. Retention and deletion obligations are executable and audited.
24. Release terminology such as `open source`, `open weights`, and `public` is used precisely.
25. Every experiment and release binds to exact rights-manifest revisions.

## 42. Benchmark and evaluation implications

DR-10 creates a dedicated **Rights, Lineage, and Release** benchmark and validation track.

Required case families include:

- public-domain ancient work with copyrighted modern edition;
- open repository with one restricted translation;
- public metadata with restricted full text;
- open running text with restricted apparatus;
- CC BY attribution and change notice;
- CC BY-NC internal research versus public model release;
- CC BY-SA or ODbL reciprocal compatibility;
- CC BY-ND exact display versus adaptation and training uncertainty;
- custom local-research permission;
- clickthrough or individually gated access;
- EU TDM reservation;
- United States fair-use review with insufficient facts;
- user-uploaded copyrighted Bible page;
- restricted manuscript image with open transcription;
- model-generated synthetic example derived from a restricted source;
- adapter, merged-weight, quantized, and mobile-package release distinctions;
- public vector index reconstruction risk;
- revoked or mislicensed source impact analysis;
- cultural or community protocol more restrictive than copyright;
- private benchmark and user-data leakage;
- public repository without an explicit reuse license;
- false `open source` labeling;
- model and dataset card completeness;
- training-content summary generation.

Primary metrics include:

```text
component_scope_accuracy
operation_authorization_accuracy
false_permission_rate
false_denial_rate
lineage_completeness
rights_evidence_integrity
attribution_completeness
license_compatibility_accuracy
private_to_public_leakage_rate
user_entitlement_enforcement
incident_impact_recall
release_status_accuracy
memorization_and_extraction_detection
model_and_dataset_card_completeness
training_summary_traceability
expert_rated_release_faithfulness
```

No overall average may conceal unauthorized release, private-data leakage, or false open-source claims.

## 43. Hard failures

The following are hard failures when material:

- Treating public accessibility as permission to train or redistribute.
- Treating an underlying ancient work's public-domain status as covering a modern edition, translation, image, annotation, or apparatus.
- Accepting a dataset-level license for third-party contents without authority evidence.
- Using a source after access revocation or expiration.
- Bypassing a paywall, technical restriction, rights reservation, or authentication requirement.
- Assuming noncommercial intent automatically satisfies every NC license or legal exception.
- Training on ND, custom-restricted, or unknown material without approved review.
- Mixing open and restricted lineages without traceability.
- Releasing a corpus, benchmark, embedding, adapter, model, or mobile package beyond its approved rights state.
- Treating embeddings, synthetic data, distillation, model weights, or quantization as license-laundering mechanisms.
- Exposing restricted text through RAG to an unauthorized user.
- Allowing user-private material into shared training or retrieval.
- Publishing private benchmark cases.
- Omitting required attribution, change notices, reciprocity, or third-party notices.
- Claiming license compatibility where legal treatment remains unresolved.
- Claiming a model is Open Source AI without satisfying the approved definition.
- Failing to identify a base-model or tokenizer license restriction.
- Failing to quarantine and trace a disputed source.
- Treating deletion of source files as sufficient model unlearning.
- Fabricating or losing the legal evidence used for a rights decision.
- Allowing Sol, Luna, or the model to approve a rights or release decision reserved to the owner.

## 44. Sol's implementation boundary

The owner and ChatGPT define:

- rights subjects and component scope;
- operation, purpose, jurisdiction, status, and lineage taxonomies;
- authorization semantics;
- storage zones and access boundaries;
- rights-manifest and release-decision contracts;
- fail-closed rules;
- lineage aggregation;
- incident workflow;
- release gates and evidence;
- public/private and user-isolation rules;
- benchmark and hard-failure semantics.

Sol may implement:

- validated schemas and storage adapters;
- policy evaluation and entitlement checks;
- evidence snapshotting;
- attribution and notice generation;
- rights-lineage traversal;
- compatibility-analysis candidates;
- impact analysis;
- release-readiness reports;
- SPDX, CC, RightsStatements, Hugging Face, and provider adapters;
- tests and observability;
- approved reversible optimizations.

Sol may not:

- decide that a disputed legal use is permitted;
- broaden a source's approved operations;
- collapse rights dimensions into one permissive flag;
- change the lineage or release status taxonomy;
- approve model, dataset, benchmark, code, or report release;
- replace qualified legal review with an automated compatibility result;
- make an unknown permission permissive.

A missing, contradictory, or infeasible rights contract requires:

```text
BLOCKED_REQUIRES_DESIGN_OR_LEGAL_REVIEW
```

## 45. Decisions DR-10 would lock

Approval would freeze these principles:

1. Rights are component-, operation-, purpose-, jurisdiction-, actor-, time-, and artifact-specific.
2. Lawful access, analysis, training, display, redistribution, hosting, and model release remain separate decisions.
3. Copyright, contract, database, privacy, cultural, confidentiality, and other rights layers remain distinct.
4. Rights evidence is dated, hashed, source-preserving, and authority-aware.
5. Rights assertions remain separate from project authorization decisions.
6. Missing or conflicting permission fails closed.
7. Underlying public-domain works remain separate from modern editions, translations, images, annotations, apparatuses, and databases.
8. Creative Commons license conditions are handled by exact version and component.
9. NonCommercial, ShareAlike, and NoDerivatives sources remain in separately reviewed lineages.
10. Database and database-content rights remain separate.
11. Public, gated, clickthrough, subscription, and transient access states remain distinct.
12. Statutory exceptions and fair use are reviewed per jurisdiction and operation.
13. Legal permission does not override cultural or community protocols adopted by the project.
14. User-private material is excluded from shared retrieval, training, benchmarks, and release by default.
15. Public, permissive, reciprocal, noncommercial, local-only, RAG-only, user-private, holdout, and quarantined lineages remain identifiable.
16. No transformation launders restrictions or provenance.
17. Embeddings, indexes, adapters, merged weights, quantized models, and mobile packages are separately reviewable artifacts.
18. Model training and model release are independent authorization questions.
19. Base-model, tokenizer, code, kernel, dataset, and runtime licenses all remain in downstream lineage.
20. Synthetic data and distillation preserve teacher, prompt, retrieved-evidence, and source lineage.
21. Benchmarks preserve evidence rights and private/public separation.
22. Attribution and notices are generated from machine-readable lineage and human-reviewed.
23. Every consequential artifact has a rights manifest and release status.
24. Rights changes trigger quarantine and complete downstream impact analysis.
25. Model release requires memorization and extraction review.
26. Release terminology is precise; public visibility, open weights, and Open Source AI are not synonyms.
27. The public repository contains only public-safe artifacts and its root license has an explicit scope.
28. Current and future regulatory training-data transparency must be supported from run-time provenance, not reconstructed later.
29. Sol implements the approved rights system; only the owner approves consequential rights and release decisions.
30. Qualified legal review is required where the project relies on uncertain law, custom terms, or potentially restricted model release.

## 46. Decisions intentionally deferred

DR-10 does not yet select:

- the final license for project-authored source code;
- the final license for design documents or public schemas;
- the final license for public benchmark cases;
- the final license for any dataset, adapter, or model;
- final source-by-source rights decisions;
- the exact legal reviewer or counsel;
- the final jurisdictions in which the model will be offered;
- the exact public versus gated release channel;
- quantitative quotation limits;
- final retention periods;
- exact user-upload terms and consent interface;
- exact repository subscriptions or contracts;
- whether any restricted lineage will ever enter weights;
- the final policy on reciprocal licenses and model weights;
- exact memorization and extraction thresholds;
- the final physical database, object store, key management, or policy engine;
- final SPDX, REUSE, Croissant, or other exchange profiles;
- final EU GPAI provider classification;
- final model and data-card templates;
- the final incident-response service levels;
- final public release status of any artifact.

Those decisions belong to DR-17, DR-20 through DR-23, DR-25, DR-27 through DR-29, source-specific review, qualified legal review, and owner-approved release decisions.

## 47. Approved statement

> **Biblical Scholar Lab will use a component-, operation-, purpose-, jurisdiction-, actor-, time-, and artifact-specific Rights, Lineage, and Release Architecture. Public access, lawful acquisition, private analysis, text-and-data mining, retrieval, quotation, continued pretraining, fine-tuning, preference training, distillation, embedding, indexing, corpus release, adapter release, full-weight release, quantization, hosted inference, and mobile distribution will remain separate authorization decisions. Copyright, public-domain status, contracts and terms, database rights, privacy, confidentiality, cultural authority, community protocols, base-model conditions, and statutory exceptions will remain distinct evidence layers. Every source and derivative will retain immutable rights evidence, exact component scope, operation decisions, attribution obligations, storage zone, lineage class, and downstream impact links. Unknown or conflicting permission will fail closed; no OCR, normalization, translation, annotation, embedding, synthetic generation, training, distillation, merge, or quantization operation will launder restrictions or provenance. Public, reciprocal, noncommercial, local-only, RAG-only, private-user, private-holdout, and quarantine lineages will remain separable, and every public artifact will receive an independent rights manifest, compatibility review, privacy and cultural review, memorization and extraction evaluation, documentation bundle, ChatGPT review, and owner release approval. Sol will implement the approved contracts, while consequential legal and release decisions remain reserved to qualified review and the project owner.**

---

## References

[^cc-considerations]: Creative Commons, “Considerations for licensors and licensees.” CC advises licensors and users to specify the exact licensed material, confirm that the licensor controls the relevant rights, and recognize that a CC license may not clear every element or other right: https://creativecommons.org/share-your-work/licensing-considerations/version4/

[^eu-dsm]: Directive (EU) 2019/790, Articles 3 and 4. Article 4 provides a text-and-data-mining exception for lawfully accessible works subject to appropriate rights reservations; Article 3 applies to qualifying research organizations and cultural-heritage institutions under its terms: https://eur-lex.europa.eu/eli/dir/2019/790/oj

[^cc-public-domain]: Creative Commons, “Public Domain List” and CC0 information. CC distinguishes CC0, the Public Domain Mark, and other public-domain tools: https://creativecommons.org/publicdomain/

[^cc-compatible]: Creative Commons, “Compatible Licenses.” CC maintains an explicit list of licenses approved as compatible with BY-SA and BY-NC-SA: https://creativecommons.org/compatible-licenses/

[^cc-by-nc-sa]: Creative Commons, CC BY-NC-SA 4.0 deed. The deed notes attribution, noncommercial, ShareAlike, and no-additional-restrictions requirements and cautions that other rights may limit use: https://creativecommons.org/licenses/by-nc-sa/4.0/

[^cc-database]: Creative Commons, “Data” and “Sui generis database rights.” CC 4.0 can cover applicable database rights held by the licensor, while rights in database contents may remain separate: https://wiki.creativecommons.org/wiki/data and https://wiki.creativecommons.org/wiki/4.0/Sui_generis_database_rights

[^odbl]: Open Data Commons, “Open Database License.” ODbL distinguishes rights in a database from rights in individual database contents: https://opendatacommons.org/licenses/odbl/index.html

[^hf-gated-datasets]: Hugging Face, “Gated datasets.” Access is granted to individual users, may require acceptance of terms, and can later be removed by the dataset author: https://huggingface.co/docs/hub/datasets-gated

[^hf-gated-models]: Hugging Face, “Gated models.” Model access is user-specific, authenticated, and revocable by the model author: https://huggingface.co/docs/hub/models-gated

[^github-license]: GitHub Docs, “Licensing a repository.” GitHub explains that a public repository is not automatically open source and that default copyright applies without a license beyond platform functionality: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository

[^us-fair-use]: U.S. Copyright Office, “Fair Use Index.” Fair use is assessed under the statutory four-factor framework, and nonprofit educational or research purpose is relevant but not automatically dispositive: https://copyright.gov/fair-use/

[^crs-ai]: Congressional Research Service, *Generative Artificial Intelligence and Copyright Law*, updated July 18, 2025. CRS notes the fact-specific character of fair use and the Copyright Office's conclusion that some training uses may qualify and others may not: https://www.congress.gov/crs-products/product/pdf/LSB/LSB10922

[^usco-ai-part3]: U.S. Copyright Office, *Copyright and Artificial Intelligence, Part 3: Generative AI Training*, pre-publication version, May 9, 2025. The report addresses acquisition, curation, training, retrieval, outputs, infringement, fair use, and licensing: https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-3-Generative-AI-Training-Report-Pre-Publication-Version.pdf

[^local-contexts]: Local Contexts. Traditional Knowledge and Biocultural Labels and Notices communicate Indigenous cultural authority, provenance, protocols, and permissions for heritage collections and data: https://localcontexts.org/

[^osaid]: Open Source Initiative, “The Open Source AI Definition 1.0.” The definition describes freedoms to use, study, modify, and share and the preferred form needed to modify a machine-learning system: https://opensource.org/ai/open-source-ai-definition

[^spdx-dataset]: SPDX Specification 3.0.1, Dataset Profile. The Dataset Profile represents dataset identity, versions, sources, characteristics, access, and licensing relationships: https://spdx.github.io/spdx-spec/v3.0.1/model/Dataset/Dataset/

[^spdx-ai]: SPDX Specification 3.0.1, AI Profile. The AI Profile represents AI model and system artifacts and their dependencies, licensing, build, and related information: https://spdx.github.io/spdx-spec/v3.0.1/model/AI/AI/

[^rights-statements]: RightsStatements.org. The service supplies machine-readable status statements for cultural-heritage digital objects, including in-copyright, no-copyright, and unclear-status categories: https://rightsstatements.org/en/statements/

[^hf-model-cards]: Hugging Face, “Model Cards.” Model cards can declare model license, base-model relation, datasets, languages, evaluation results, intended uses, and limitations: https://huggingface.co/docs/hub/model-cards

[^hf-dataset-cards]: Hugging Face, “Dataset Cards.” Dataset cards document license, language, composition, use context, and limitations: https://huggingface.co/docs/hub/datasets-cards

[^eu-gpai]: European Commission, “Guidelines on obligations for General-Purpose AI providers” and “Template for general-purpose AI model providers to summarise their training content.” The guidance states that GPAI providers must implement a copyright policy and publish a training-content summary, including for open-source models placed on the EU market: https://digital-strategy.ec.europa.eu/en/faqs/guidelines-obligations-general-purpose-ai-providers and https://digital-strategy.ec.europa.eu/en/faqs/template-general-purpose-ai-model-providers-summarise-their-training-content
