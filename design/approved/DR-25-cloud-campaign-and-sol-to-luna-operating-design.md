# DR-25 — Cloud Campaign and Sol-to-Luna Operating Design

| Field | Value |
|---|---|
| Design ID | `DR-25` |
| Status | `APPROVED` |
| Approval date | 2026-08-16 |
| Project owner | Joseph Abbud |
| Product, architecture, benchmark, and experiment designer | ChatGPT |
| Independent implementation and evidence reviewer | ChatGPT |
| Depends on | DR-01; DR-02 revision 2 and supplements; DR-03; DR-04; DR-05; DR-06; DR-07; DR-08; DR-09; DR-10; DR-11; DR-12; DR-13; DR-14; DR-15; DR-16; DR-17; DR-18; DR-19; DR-20; DR-21; DR-22; DR-23; DR-24 |
| Implementation authority | GPT-5.6 Sol exclusively implements and repairs campaign, Lambda, archive, watchdog, transfer, security, evidence, and delegation machinery according to approved designs |
| Execution authority | GPT-5.6 Luna may perform only frozen, machine-authorized launch, monitor, checkpoint, transfer-coordination, termination, cleanup, and evidence-collection operations delegated by Sol; Luna may not create or modify code, executable configuration, data, model, benchmark, experiment, threshold, budget, provider, destination, or scientific interpretation |
| Experiment authority | ChatGPT designs every campaign's scientific identity and promotion logic; Joseph reviews and approves consequential campaigns, budget, progression, model promotion, public claims, and release |
| Approved cloud provider | Lambda.ai / Lambda Cloud only for project-controlled cloud training and evaluation |
| Authoritative artifact destination | Owner-controlled external storage volume attached to the MacBook Pro through Thunderbolt; Lambda storage is temporary execution scratch only |
| Approved owner amendment | Replaces hard-coded Lambda regions with a dynamic nearest-available eligible-region policy. The policy—not one region—is approved in the campaign envelope; the selected region is measured and recorded per launched resource. |
| Approved change | Establishes immutable campaign envelopes, campaign classes, standing smoke authority, one-use owner approval, Sol-led/Luna-operated delegation, durable controller and broker boundaries, least-privilege credential handling despite full-access Lambda API keys, Lambda resource and network policy, watchdogs, cost accounting, retries, artifact draining, Thunderbolt archival, provider termination, cleanup, evidence, consolidated review handoffs, and the implementation gates required before any scientific cloud campaign |

## 1. Purpose

DR-23 defines how an approved model-training or evaluation stage becomes a reproducible job, checkpoint, exposure record, result bundle, and authoritative external archive.

DR-24 defines which experiments may occur, their dependencies, promotion gates, and staged budget release.

DR-25 defines **how a reviewed experiment or evaluation becomes an owner-authorized cloud campaign; how Sol delegates frozen mechanical execution to Luna without delegating engineering or scientific authority; how Lambda resources, credentials, networking, cost, watchdogs, checkpoints, artifact transfer, termination, cleanup, and evidence are controlled; and where review boundaries occur so the project remains efficient without sacrificing governance**.

A scientifically valid experiment can still become operationally invalid if:

- A natural-language prompt is treated as sufficient launch authorization;
- A Lambda API key with full account access is exposed to an agent or cloud instance;
- Luna repairs code or changes a hyperparameter to keep a run alive;
- Sol changes the experiment while implementing an operational repair;
- A campaign launches from an unreviewed commit or dirty worktree;
- A model, tokenizer, dataset, benchmark, container, kernel, precision, instance class, region-selection policy, price bound, or artifact destination changes after approval;
- A smoke test requires a separate manual user kickoff for every mechanical sub-job;
- A parent Sol session ends and the watchdog, termination path, or audit trail disappears with it;
- A transient provider error is confused with a scientific failure—or vice versa;
- A wrong answer, failed gate, or poor metric is rerun as though it were an infrastructure retry;
- An instance is powered down from inside Linux rather than terminated through the provider API, leaving billing active;
- A Lambda filesystem remains allocated after the instance is gone;
- The MacBook Pro archive volume is missing, replaced, unencrypted, read-only, unhealthy, or full;
- A checkpoint exists only on Lambda when the instance terminates;
- A failed archive transfer causes the instance to remain billable beyond the approved cap;
- A cloud run completes but no one can reconstruct who launched it, what it cost, what it changed, which artifacts survived, or whether all billable resources were actually destroyed.

DR-25 is intended to prevent those failures.

## 2. Governing principle

> **Sol owns implementation and accountable synthesis; Luna owns only frozen mechanical operation; the durable campaign controller owns enforcement; ChatGPT owns experiment design and scientific review; Joseph owns approval and progression. A campaign may automate every transition that is fully specified and machine-checkable inside one approved envelope, but no agent may improvise beyond that envelope, convert a failed scientific gate into a retry, or keep billable infrastructure alive merely to avoid returning for review.**

The intended operating flow is:

```text
ChatGPT-authored experiment or evaluation design
    → Joseph approval
    → Sol implementation and preflight compilation
    → immutable campaign envelope
    → owner approval grant or approved standing-smoke policy
    → Sol delegates approved mechanical jobs to Luna
    → durable campaign controller launches and supervises Lambda
    → trainer/evaluator produces frozen artifacts and events
    → owner-controlled archive relay drains artifacts to Thunderbolt storage
    → cryptographic and required load verification
    → provider-side termination and filesystem cleanup
    → Luna returns operational evidence to Sol
    → Sol produces one consolidated implementation/run handoff
    → ChatGPT reviews code, evidence, results, cost, and design conformance
    → Joseph approves merge, progression, publication, or stop
```

Internal Luna invocations are not separate scientific review boundaries. The parent Sol root turn and the immutable campaign are the accountable units.

## 3. Authority model

### 3.1 Joseph Abbud

Joseph alone may:

- Approve or revoke campaign authority;
- Approve a campaign cost ceiling;
- Approve use of the standing smoke allowance;
- Approve model, checkpoint, or stage progression;
- Approve budget reallocation;
- Approve changes to the cloud provider or authoritative archive policy;
- Approve public claims and release;
- Merge reviewed implementation into `main`.

Owner approval does not become scholarly SME validation.

### 3.2 ChatGPT

ChatGPT:

- Designs campaign scientific identity and transition logic;
- Defines named hypotheses, controls, metrics, thresholds, stop rules, and permitted claims;
- Reviews Sol's implementation and consolidated evidence;
- Distinguishes engineering failure, operational failure, benchmark failure, and scientific outcome;
- Recommends GO, REPAIR, REDESIGN, NO-GO, STOP, or RELEASE;
- Does not launch billable resources directly.

### 3.3 GPT-5.6 Sol

Sol is the exclusive lead implementation engineer.

Sol may:

- Implement campaign, training, evaluation, transfer, archive, watchdog, and control-plane code;
- Compile an approved experiment design into a campaign envelope;
- Validate exact hashes and runtime compatibility;
- Delegate frozen mechanical execution to Luna;
- Diagnose defects;
- Implement repairs within the approved scientific design;
- Interpret operational logs sufficiently to produce the consolidated handoff;
- Propose—but not execute—scientific or architectural changes.

Sol may not:

- Change the hypothesis, benchmark, model family, data mixture, objective, threshold, budget, provider, archive destination, or scientific interpretation without a new approved design;
- Use a different experiment merely because the approved one failed;
- Merge, approve, or push directly to `main`;
- Allow Luna to repair code or modify executable configuration.

### 3.4 GPT-5.6 Luna

Luna is the frozen campaign runner.

Luna may:

- Validate a signed campaign envelope through the approved control interface;
- Launch exactly approved Lambda resources;
- Wait for approved provider states;
- Execute exact frozen commands;
- Monitor heartbeats, GPU utilization, progress, checkpoints, runtime, and cost;
- Trigger deterministic transitions encoded in the campaign;
- Retry an identical operation after an approved transient failure;
- Resume an exact approved checkpoint;
- Coordinate owner-pull artifact transfer through the approved archive interface;
- Stop work when a machine-checkable gate triggers;
- Terminate resources through the provider API;
- Verify cleanup and collect evidence;
- Return an operational report to Sol.

Luna may not:

- Create, edit, repair, refactor, or delete source code, tests, schemas, prompts, dependencies, containers, infrastructure definitions, or executable configuration;
- Change data, model, tokenizer, benchmark, objective, learning rate, batch size, sequence length, precision, kernel, hardware class, region-selection policy, transition, retry policy, timeout, cost cap, or archive destination;
- Diagnose a scientific failure as “close enough”;
- Reclassify a wrong answer or failed metric as an infrastructure retry;
- Increase budget or runtime;
- Substitute Sol for itself, another model for Luna, or another cloud provider for Lambda;
- Interpret scientific meaning, promote a checkpoint, or write the final review conclusion.

When a modification is required, Luna stops with:

```text
BLOCKED_REQUIRES_SOL_REPAIR
```

When a scientific or experimental change is required, it stops with:

```text
BLOCKED_REQUIRES_EXPERIMENT_DESIGN_REVIEW
```

## 4. Campaign classes

DR-25 establishes the following operational classes.

### `CC-0_LOCAL_OR_NONBILLABLE`

- No Lambda resources.
- Used for local mocks, schemas, unit tests, dry runs, and static validation.
- No owner cloud-spend approval required.
- Still produces reviewable evidence when it changes project state.

### `CC-1_STANDING_SMOKE`

A standing, owner-approved low-cost allowance intended to prevent excessive manual launch overhead.

Approved initial limits:

```text
maximum aggregate Lambda cost per Sol root turn: $25
maximum provider runtime: 60 minutes
maximum simultaneous instances: 1
maximum campaign jobs: 3
persistent Lambda filesystem: prohibited
restricted or user-private data: prohibited
checkpoint/model promotion: prohibited
main training or final benchmark claims: prohibited
automatic provider termination: mandatory
Thunderbolt archive receipt for retained artifacts: mandatory
```

A `CC-1` campaign may validate:

- Instance and image compatibility;
- Container startup;
- Model loading;
- Short forward/backward passes;
- Tiny inference/evaluation batches;
- Checkpoint creation and resume;
- Archive transfer and cleanup;
- Watchdog and failure behavior.

It may not support a scientific promotion claim beyond implementation conformance or screening.

Joseph may revoke or change the standing allowance at any time. A campaign outside any one bound becomes `CC-2` or higher and requires explicit approval.

### `CC-2_BOUNDED_EVALUATION`

- Frozen benchmark or prior-art evaluation.
- Explicit campaign approval unless an approved DR-24 envelope already covers it.
- No training objective or model weights changed.
- Private or restricted cases require provider-routing authorization under DR-10.

### `CC-3_ADAPTATION_PILOT`

- Bounded smoke, proxy, strategy, or pilot training.
- Explicit owner approval.
- Exact checkpointing, archive, and stop rules.
- May support `EL-1` or `EL-2` evidence only under DR-24.

### `CC-4_MAIN_TRAINING_OR_FINAL_EVALUATION`

- Main CPT, mid-training, SFT, preference, private final evaluation, or other promotion-critical campaign.
- Explicit one-use owner approval.
- Secondary provider-termination path required.
- Strongest archive, reproducibility, audit, and closeout requirements.

### `CC-5_RELEASE_OR_PUBLICATION_OPERATION`

- Model, adapter, data, benchmark, website, or report publication.
- Separately governed by DR-10 and a release design.
- Luna may execute only an exact publication command after owner approval.
- It is never implied by successful training or evaluation.

## 5. Canonical campaign objects

The logical architecture includes:

```text
CampaignDesignRecord
CampaignEnvelope
CampaignJobSpecification
CampaignTransitionRule
CampaignApprovalPolicy
CampaignApprovalGrant
CampaignRevocationRecord
SolDelegationReceipt
LunaInvocationRecord
RegionSelectionPolicy
RegionSelectionReceipt
ProviderResourceRecord
ProviderOperationRecord
CampaignStateRecord
JobStateRecord
OperationalEvent
HeartbeatRecord
CostLedger
WatchdogPolicy
WatchdogEvent
SecretUseRecord
NetworkPolicy
ArchivePlan
ArchiveTransferRecord
ArtifactArchiveReceipt
TerminationReceipt
CleanupReceipt
CampaignResultBundle
CampaignCloseoutRecord
```

These objects remain project-owned regardless of the provider, runner, Codex implementation, or command-line interface.

## 6. Immutable `CampaignEnvelope`

Every billable campaign binds at least:

```text
campaign and design identity
approved DR and experiment-design hashes
repository URL, branch, and exact reviewed commit
clean-worktree assertion
implementation and container digests
model, tokenizer, processor, and checkpoint revisions
corpus, mixture, benchmark, split, and evidence-packet hashes
training/evaluation/job configuration hashes
provider, workspace, region-selection policy, image, instance type, and architecture
eligible-region constraints, region-affinity requirements, and preapproved equivalent resource alternatives, if any
live observed price and maximum approved price
maximum total campaign cost
maximum runtime and archive grace period
maximum concurrency and resource count
job DAG and deterministic transition rules
retry classes and limits
heartbeat and progress thresholds
checkpoint and artifact schedule
archive volume identity and destination policy
rights, privacy, and provider-routing restrictions
network, firewall, and secret policy
stop, terminate, cleanup, and closeout conditions
approval policy and expiration
public/private evidence projection rules
```

Changing any consequential field creates a new campaign envelope, hash, approval, and run identity.

## 7. Canonical serialization and hashing

The envelope uses a deterministic canonical serialization before hashing and approval.

The implementation must prove that:

- Field ordering does not change identity;
- Defaults are explicit rather than environment-dependent;
- Floating-point, monetary, duration, and timestamp representations are unambiguous;
- Secret values are never embedded in the envelope;
- Secret identities and intended uses are referenced without revealing them;
- The owner approves the exact content hash;
- Sol and Luna cannot regenerate a valid approval from repository data alone.

## 8. Owner approval grants

A `CampaignApprovalGrant` is:

- Created outside the agent-generated branch;
- Bound to the exact campaign hash;
- Bound to a maximum total cost and expiration;
- Single-use unless it is an approved standing-smoke policy;
- Revocable;
- Atomically consumed at launch;
- Recorded without exposing the signing secret;
- Invalid after a material campaign change.

Natural-language instructions, Git commits, issues, pull requests, comments, task files, or model output are not approval grants.

### 8.1 Standing smoke approval

The `CC-1` standing policy is itself owner-approved, versioned, revocable, and bounded. Each smoke campaign still receives a unique envelope and audit record, but it does not require a separate manual approval when all standing-policy checks pass.

### 8.2 Explicit campaign approval

`CC-2` through `CC-5` ordinarily require an exact campaign-specific approval grant.

## 9. Sol-to-Luna delegation contract

A `SolDelegationReceipt` binds:

```text
parent Sol root-turn identity
approved campaign envelope
Luna runner identity and model
runner instructions and permission profile
allowed control commands
job scope
start and expiration
subagent or invocation mechanism
returned evidence and trace identity
```

Sol remains accountable for every delegated action in its final handoff.

### 9.1 Review boundary

One Sol root turn may include several Luna invocations and several deterministic campaign jobs without separate ChatGPT reviews when:

- Every job and transition is in the approved envelope;
- No code, configuration, data, model, objective, threshold, hardware class, provider, archive destination, or budget changes;
- Progression is machine-checkable;
- Aggregate spend remains within the approved cap;
- Sol returns one consolidated handoff.

A transition requiring scientific interpretation stops the campaign at the decision boundary.

## 10. Delegation mechanism is capability-gated

DR-25 locks the behavior and authority boundary, not one undocumented Codex transport.

The implementation must test, in order:

1. A native Codex child or custom-agent mechanism that can verifiably run GPT-5.6 Luna with a stricter permission profile under a parent Sol root turn;
2. A project-owned Luna invocation adapter through an approved OpenAI model/task interface, returning an auditable invocation record to Sol;
3. An automatically dispatched Luna runner task under the same campaign identity, requiring no separate user kickoff and returning control to Sol;
4. A controller-driven Luna invocation at event or milestone boundaries rather than continuous token-consuming observation.

The selected path must prove:

- Exact Luna model identity;
- No repository-write or code-edit capability;
- No raw Lambda or SSH credential exposure;
- Auditable inputs, outputs, commands, and timestamps;
- Return of evidence to the parent Sol workflow;
- Cancellation and timeout behavior;
- No silent inheritance of Sol's broader permissions.

If no safe mixed-model delegation route exists, the implementation stops with:

```text
BLOCKED_REQUIRES_ORCHESTRATION_DESIGN_REVIEW
```

It may not silently run Luna's duties with Sol or require a chain of manual micro-turns. A temporary exception requires a new owner-approved design.

OpenAI currently positions GPT-5.6 Sol for flagship capability and GPT-5.6 Luna for efficient high-volume work; DR-25 uses that distinction only after the actual orchestration and permission boundary is verified.[^openai-model-guidance]

## 11. Durable controller independent of agent lifetime

The campaign controller must continue to enforce:

- Heartbeats;
- Cost and time limits;
- Checkpoint schedules;
- Archive schedules;
- Stop conditions;
- Provider termination;
- Cleanup;

without requiring a Sol or Luna language-model session to remain continuously active.

Agents issue and inspect bounded control operations. They are not the only watchdogs.

The approved project-owned command surface is:

```text
campaignctl validate
campaignctl approve-status
campaignctl preflight
campaignctl launch
campaignctl status
campaignctl jobs
campaignctl pause-work
campaignctl resume-work
campaignctl checkpoint
campaignctl archive
campaignctl stop-work
campaignctl terminate
campaignctl cleanup
campaignctl collect
campaignctl close
campaignctl emergency-stop
```

Training and evaluation subcommands remain available through `trainctl` and `evalctl`, but provider and campaign authority remains centralized in `campaignctl`.

## 12. Lambda credential and control-broker architecture

Lambda Cloud API keys currently have full access to all Lambda API operations.[^lambda-access]

Therefore:

> **Raw Lambda API keys must never be provided to Sol, Luna, a Lambda instance, a container, a repository, a CI runner, or an ordinary shell environment.**

The project will implement an owner-controlled:

```text
LambdaControlBroker
```

running on an approved local controller host.

The broker:

- Retrieves the Lambda API key from macOS Keychain or another approved owner-controlled secret store;
- Accepts only campaign-hash-bound operations;
- Revalidates approval, state, budget, and transition rules;
- Restricts provider endpoints and resource identities;
- Rate-limits API calls;
- Records request and response hashes with secrets redacted;
- Refuses general-purpose API access;
- Exposes only the narrow `campaignctl` operations;
- Can terminate all campaign-tagged resources independently of the trainer and runner.

The campaign may not place a full-access Lambda API key on the cloud instance merely to let that instance terminate itself.

## 13. SSH and remote-command boundary

A dedicated project SSH key pair is used for Lambda instances.

Requirements:

- The private key remains on an owner-controlled controller host;
- The private key is never stored in Git, the campaign envelope, cloud-init, logs, or the Lambda instance;
- File permissions and Keychain/agent use are verified;
- Host keys are pinned after instance identity is obtained;
- Remote commands are invoked through the campaign broker, not arbitrary agent SSH;
- SSH agent forwarding is prohibited for ordinary campaigns;
- Any exception receives a separate security review;
- The key can be rotated and revoked without changing scientific identity.

Lambda requires an SSH key to be selected when an on-demand instance is launched, and supports API or console management of those keys.[^lambda-connect]

## 14. Workspace and account isolation

The preferred implementation uses a dedicated Lambda workspace for Biblical Scholar Lab where practical.

Because Lambda account roles and API keys currently retain broad resource authority, workspace separation is treated as defense in depth—not a substitute for the local broker.[^lambda-access]

The campaign records:

- Lambda account and workspace identity;
- Approved workspace membership;
- SSH key identity;
- API-key identity without the secret;
- Firewall ruleset;
- Existing provider resources before launch;
- Campaign-created resources;
- Resources remaining after closeout.

## 15. Lambda network policy

Lambda's default inbound firewall permits only ICMP and TCP/22, and the provider supports global and per-instance firewall rulesets.[^lambda-firewall]

The baseline policy is:

- No public JupyterLab, HTTP, HTTPS, VNC, database, dashboard, or model-server port;
- SSH only from approved source IP ranges where stable source addressing permits;
- Use SSH tunnels for local inspection where needed;
- Restrict new inbound ports to a separately approved campaign;
- Do not expose training dashboards publicly;
- Apply host and container outbound restrictions where practical;
- Permit only approved model, data, package, telemetry, and time endpoints;
- Record all material network-policy exceptions;
- Treat downloaded code and data as untrusted until validated.

## 16. Lambda image and container identity

Every launch binds:

```text
Lambda machine-image ID, family, version, and architecture
container image digest
CUDA, driver, NCCL, framework, and kernel revisions
cloud-init or user-data content hash
```

The Lambda API can select an exact image ID or family and exposes image architecture and region metadata.[^lambda-api]

The baseline will:

- Prefer an exact image ID for authoritative campaigns;
- Avoid unattended package upgrades;
- Use a pinned container for the project runtime;
- Record host and container compatibility;
- Reject an ARM/x86 mismatch;
- Treat a changed “latest” image as a new environment requiring validation.

## 17. Resource and dynamic region selection

Every campaign specifies:

- Exact preferred instance type or an approved hardware-equivalence class;
- Exact resource count;
- A versioned `RegionSelectionPolicy` rather than a hard-coded Lambda region;
- Maximum observed hourly price and total campaign cost;
- Preapproved equivalent resource alternatives, if any;
- Required local scratch capacity;
- Whether a Lambda filesystem is authorized;
- Network, rights, privacy, and data-location constraints;
- Any experiment-specific region-affinity requirement.

The default region rule is:

> **Select the nearest currently available eligible Lambda region at launch.**

For this project, `nearest` means the lowest measured median network round-trip latency from the approved owner-controlled controller and Thunderbolt archive host among regions that are eligible for the requested job. `Available` means the live Lambda inventory indicates that the approved image or compatible image, CPU architecture, instance type or approved equivalent, resource count, workspace access, and launch capacity can satisfy the campaign at preflight or launch time.

The controller applies the following process:

1. Query live Lambda region, image, instance, price, and capacity information.
2. Exclude any region that violates the campaign's rights, privacy, data-routing, workspace, network, image, architecture, hardware, cost, or archive-transfer constraints.
3. Measure or retrieve a current latency observation from the approved owner-controlled controller to each remaining region endpoint or approved probe.
4. Select the eligible region with the lowest median latency.
5. If latency cannot be measured before launch, use an owner-approved deterministic proximity order derived from provider region metadata and verify actual transfer latency after launch.
6. Record the candidates, exclusions, measurements, tie-breaks, selected region, timestamp, and policy revision in a `RegionSelectionReceipt`.
7. Freeze the selected region for the lifetime of that launched resource.

When two eligible regions are operationally indistinguishable within the approved latency tolerance, the controller may use lower live hourly price, stronger observed capacity, and finally a stable region identifier as deterministic tie-breaks. The exact tolerance is finalized in DR-28 or a campaign-specific design.

If the selected region becomes unavailable before a resource is successfully created, the controller may choose the next-nearest eligible region under the same immutable policy without requesting a new approval. This is not an experiment change because the owner approved the selection rule rather than a specific region. Once a resource launches, any move to another region creates a new resource and a new recorded operational attempt.

A campaign may require all jobs in a comparison group to share one dynamically selected region when region affinity is necessary for fair latency, throughput, or transfer comparisons. That requirement is part of the envelope, but the actual region remains selected from live eligible availability.

If no eligible region is available, the campaign enters:

```text
BLOCKED_BY_CAPACITY
```

It does not block for design review merely because the geographically nearest region lacks capacity, and it does not substitute another cloud provider.

A different instance type may be selected automatically only when it is inside the approved hardware-equivalence class, passes scientific and numerical compatibility checks, remains under the price and cost ceilings, and is recorded. No other cloud provider is an allowable alternative.

## 18. Lambda API rate limits and idempotency

The Lambda Cloud API currently documents a general one-request-per-second limit and a launch limit of one request per 12 seconds or five per minute.[^lambda-api]

The control broker must:

- Serialize launch operations;
- Apply provider-aware backoff;
- Avoid duplicate launches after ambiguous responses;
- Use campaign tags and deterministic names;
- Reconcile provider inventory before retrying;
- Treat a repeated launch as a new billable-resource risk;
- Record API errors and provider request identities where available.

If the provider API lacks a sufficient idempotency primitive, project-owned reconciliation and locking become mandatory.

## 19. Campaign state machine

The authoritative campaign state machine includes:

```text
DRAFT
DESIGN_APPROVED
ENVELOPE_FROZEN
APPROVAL_PENDING
APPROVED
PREFLIGHTING
PREFLIGHT_PASSED
LAUNCHING
PROVISIONING
RUNNING
PAUSING_WORK
WORK_PAUSED
CHECKPOINTING
DRAINING_ARTIFACTS
ARCHIVE_VERIFYING
STOPPING_WORK
TERMINATING_RESOURCES
TERMINATED
CLEANING_UP
CLEANUP_VERIFIED
CLOSING
CLOSED
```

Terminal or branch states include:

```text
BLOCKED_BY_APPROVAL
BLOCKED_BY_CAPACITY
BLOCKED_BY_PRICE
BLOCKED_BY_ARCHIVE
BLOCKED_BY_RIGHTS
BLOCKED_BY_SECURITY
BLOCKED_REQUIRES_SOL_REPAIR
BLOCKED_REQUIRES_EXPERIMENT_DESIGN_REVIEW
FAILED_INFRASTRUCTURE
FAILED_IMPLEMENTATION
FAILED_SCIENTIFIC_GATE
FAILED_ARCHIVE
FAILED_CLEANUP
CANCELLED_BY_OWNER
EMERGENCY_TERMINATED
ARTIFACT_ARCHIVE_INCOMPLETE
RUN_NOT_PROMOTABLE
```

State changes are append-only events. They are not mutable status fields without history.

## 20. Job state machine

Each job inside the campaign records:

```text
PENDING
ELIGIBLE
STARTING
RUNNING
CHECKPOINTING
WAITING_FOR_ARCHIVE
COMPLETED
SKIPPED_BY_GATE
RETRY_WAIT
RETRYING_IDENTICAL_OPERATION
STOPPED_BY_GATE
FAILED_TRANSIENT
FAILED_IMPLEMENTATION
FAILED_SCIENTIFIC
FAILED_RIGHTS_OR_SECURITY
CANCELLED
```

A job's final status cannot be changed from failure to success by deleting the failed attempt.

## 21. Machine transitions versus scientific decisions

An automatic transition is allowed only when the envelope defines:

- Exact inputs;
- Exact metric or provider state;
- Exact threshold;
- Exact comparison;
- Exact next job;
- Exact stop behavior;
- No requirement for qualitative scientific interpretation.

Examples of machine-checkable transitions:

```text
container smoke exits 0
    → run 1M-token data-loader smoke

peak memory below approved threshold and no nonfinite values
    → run bounded 10M-token training smoke

archive hash and load verification pass
    → authorize cloud-copy deletion
```

Examples that require review:

```text
Translation Nuance improves slightly but multilingual performance declines

loss curve is stable but benchmark gain is concentrated in one passage family

27B is better but serving cost is materially higher
```

Those stop at a decision boundary.

## 22. Failure taxonomy and retries

Failures are classified as:

```text
TRANSIENT_PROVIDER
TRANSIENT_API
TRANSIENT_NETWORK
TRANSIENT_SSH
TRANSIENT_TRANSFER
TRANSIENT_PACKAGE_OR_MIRROR
CAPACITY_UNAVAILABLE
PRICE_EXCEEDS_ENVELOPE
IMPLEMENTATION_DEFECT
CONFIGURATION_DEFECT
DATA_OR_RIGHTS_DEFECT
NUMERICAL_OR_TRAINING_DEFECT
SCIENTIFIC_GATE_FAILURE
ARCHIVE_DEFECT
WATCHDOG_DEFECT
SECURITY_OR_PRIVACY_DEFECT
UNKNOWN_FAILURE
```

### Retryable without new review

Only exact same-identity operations may retry automatically, within the approved count and time window, after a classified transient failure.

### Not retryable as infrastructure

The following are outcomes or defects, not transient retries:

- Wrong answer;
- Benchmark failure;
- Failed promotion metric;
- Model refusal;
- Citation failure;
- Nonfinite training caused by the approved configuration;
- OOM under the approved resource plan;
- Unacceptable retention regression;
- Rights or security violation;
- An unavailable artifact or invalid source;
- Any change in model, data, objective, configuration, hardware class, or budget.

An OOM or numerical defect may lead Sol to implement a reviewed repair or ChatGPT to redesign the experiment. Luna does not improvise around it.

## 23. Cost model and ledger

Lambda on-demand billing currently begins when the launched instance passes health checks and ends when the instance is terminated; instances continue billing while running even when idle, and billing is measured in one-minute increments.[^lambda-billing]

Every campaign records:

```text
approved cost cap
live observed hourly price
estimated compute cost
estimated archive-grace cost
filesystem cost estimate, if any
provider launch and health timestamps
provider termination timestamp
billed runtime estimate
actual usage and transfer time
cost by job
cost lost to idle, setup, failure, archive, and cleanup
provider-reconciled cost when available
credits remaining before and after where observable
```

The estimated cost may not be reported as the final actual cost.

## 24. Cost and runtime watchdogs

The watchdog architecture separates:

```text
local authoritative provider watchdog
cloud-local work watchdog
manual emergency termination path
secondary owner-controlled termination observer for CC-4
```

### Local authoritative watchdog

Runs on an owner-controlled host and can terminate campaign resources through the Lambda Control Broker.

It enforces:

- Maximum campaign cost;
- Maximum runtime;
- Archive grace;
- Missing heartbeat;
- Idle GPU;
- No token/sample progress;
- Job DAG violations;
- Owner cancellation;
- Resource-count anomalies.

### Cloud-local work watchdog

Runs without Lambda API credentials.

It may:

- Stop training or evaluation;
- Flush logs;
- Write an emergency checkpoint;
- Mark the run failed or paused;

but it cannot provider-terminate the instance.

### Manual emergency path

The owner retains provider-console and `campaignctl emergency-stop` instructions outside the agent workflow.

### Secondary termination observer

For `CC-4`, the campaign must provide a second owner-controlled provider-termination path or a separately approved equivalent resilience design. The intended implementation may use another owner-controlled Mac or controller process. The exact host is deferred to DR-28.

This is required because Lambda API credentials are intentionally withheld from cloud instances and agents.

## 25. Controller-host readiness

A billable campaign cannot launch unless the approved controller host reports:

- AC power or approved power policy;
- Sleep inhibition;
- Stable network connectivity;
- Correct system clock;
- Lambda Control Broker healthy;
- Archive relay healthy;
- External archive volume mounted and verified;
- Sufficient free space;
- Required secrets available in the local secret store;
- Emergency termination instructions available;
- No conflicting active campaign;
- Monitoring process configured to restart after a local process crash where possible.

The exact controller and secondary-watchdog host allocation is consolidated in DR-28.

## 26. Authoritative Thunderbolt archive preflight

Every retained-artifact campaign verifies:

```text
stable volume UUID or equivalent device identity
approved mount point
writable state
approved encryption-at-rest state
owner and permission state
filesystem health
available and reserved free space
archive-root identity
incoming-staging directory
atomic rename behavior
hashing and load-validation tools
backup-policy status
```

A matching volume name alone is insufficient.

There is no silent fallback to an internal disk, another removable device, a network share, or Lambda storage.

## 27. Owner-pull artifact transfer

The preferred security direction is:

```text
owner-controlled archive relay pulls from Lambda over SSH/rsync
```

rather than allowing the Lambda instance to open an inbound connection to the owner network.

The transfer design supports:

- Partial and resumable transfer;
- Manifest-first or manifest-final verification;
- Per-file and aggregate hashes;
- Byte counts;
- Sparse and sharded checkpoint handling;
- Transfer retries classified independently from training retries;
- Bandwidth and time budgeting;
- `.incoming` staging;
- Atomic promotion after verification;
- No secret or restricted path leakage in public logs.

Lambda's own data-transfer guidance documents `rsync` as a supported method for copying data between a local environment and on-demand instances.[^lambda-transfer]

## 28. Artifact archive receipts

An `ArtifactArchiveReceipt` records:

```text
artifact and campaign identity
source instance, path, and hash
external volume and destination identity
transfer start and end
byte count and file count
transfer tool and configuration
verification algorithm
hash result
load or structural validation result
rights and visibility state
atomic promotion result
cloud-deletion authorization state
review and content hash
```

A checkpoint or result that lacks a valid receipt is:

```text
NOT_AUTHORITATIVELY_ARCHIVED
NOT_PROMOTABLE
```

## 29. Periodic draining and maximum unsynchronized window

Every `CC-3` or `CC-4` campaign defines:

- Checkpoint cadence;
- Archive-drain cadence;
- Maximum time or work since the last verified archive;
- Maximum unarchived bytes;
- Emergency checkpoint behavior;
- Whether a run may continue after one failed archive attempt;
- Archive-grace cost and duration.

The final run design must balance:

- GPU idle time;
- Transfer time;
- Checkpoint size;
- Failure exposure;
- MacBook/network availability;
- Remaining campaign budget.

## 30. Lambda filesystems are prohibited by default

Instance-local storage is temporary scratch.

A Lambda persistent filesystem may be used only when the exact campaign envelope authorizes it and records:

- Selected region from the campaign `RegionSelectionReceipt`;
- Workspace;
- Filesystem ID;
- Purpose;
- Maximum size or usage policy;
- Cost estimate;
- Attachment at launch;
- Transfer and deletion plan;
- Cleanup receipt.

Lambda filesystems are separately billed while they exist, must be created in the dynamically selected region for the instance, cannot be attached after instance launch, and cannot currently be transferred between regions.[^lambda-filesystems]

A filesystem must not become a forgotten pseudo-archive.

## 31. Archive failure and bounded grace

If a required artifact cannot be transferred or verified:

1. Stop new scientific work.
2. Attempt only approved transfer retries.
3. Use the separately approved archive-grace budget.
4. Produce the best available emergency checkpoint and manifest.
5. Terminate at the immutable total cost or safety cap.
6. Mark the run:

```text
ARTIFACT_ARCHIVE_INCOMPLETE
RUN_NOT_PROMOTABLE
```

The instance may not remain alive indefinitely merely to preserve an untransferred checkpoint.

## 32. Provider termination is mandatory

A Linux shutdown, halt, or poweroff command is not provider termination and may leave billing active. Lambda explicitly warns that operating-system shutdown commands do not terminate an instance as expected and billing continues.[^lambda-lifecycle]

Normal closeout requires:

1. Stop trainer/evaluator.
2. Write final events and checkpoint where approved.
3. Drain and verify required artifacts.
4. Invoke Lambda termination through the Control Broker.
5. Poll until the provider reports `terminated` or an approved terminal state.
6. Verify no campaign-tagged instance remains running.
7. Delete approved temporary filesystems after detachment.
8. Verify provider inventory and audit events.
9. Reconcile estimated cost.
10. Create termination and cleanup receipts.

## 33. Provider audit evidence

Lambda provides account audit logs and retains them for a documented period; the event catalog includes instance launch and termination and other resource actions.[^lambda-audit]

The campaign closeout should capture, where authorized and available:

- Launch event;
- Termination event;
- SSH key and firewall changes;
- Filesystem creation and deletion;
- API-key identity events;
- Workspace changes;
- Relevant timestamps and actor identities.

Provider audit logs supplement project records. They do not replace them.

## 34. Secrets and sensitive credentials

Secrets include:

- Lambda API keys;
- SSH private keys;
- Hugging Face or gated-dataset tokens;
- Publication or repository credentials;
- Encryption and signing keys;
- Private corpus access credentials.

Requirements:

- Owner-controlled secret storage;
- No Git, PR, handoff, benchmark, or artifact inclusion;
- No command-line echo or shell history where avoidable;
- Redacted process and environment logging;
- Narrow scope and short lifetime where the provider supports it;
- Explicit secret-use record without the secret;
- Rotation after suspected exposure;
- Secret scanning before public push;
- No forwarding into Luna's raw context.

## 35. Cloud-instance bootstrap and trust

Cloud-init and bootstrap scripts are part of the approved artifact identity.

The instance must verify:

- Repository commit or packaged source hash;
- Container digest;
- Dataset and model manifests;
- Clock and environment;
- GPU, driver, CUDA, NCCL, and storage;
- Firewall and network expectations;
- Absence of unauthorized credentials;
- Correct campaign and job ID;
- Correct archive and watchdog endpoints;

before scientific work begins.

A failed bootstrap terminates the resource under the campaign closeout policy.

## 36. Observability and heartbeats

The campaign emits append-only events including:

- Provider state;
- Job state;
- Trainer/evaluator heartbeat;
- GPU and memory utilization;
- Tokens, examples, or samples completed;
- Loss and objective summaries where public-safe;
- Checkpoint status;
- Archive status;
- Cost estimate;
- Watchdog decisions;
- Retry and failure classification;
- Luna invocation and command receipts;
- Sol delegation and final synthesis identity.

A remote dashboard may mirror public-safe metrics. It cannot become the sole authoritative record.

## 37. Consolidated Sol handoff

After campaign close or decision-boundary stop, Sol produces one review handoff containing:

```text
parent root-turn identity
approved design and campaign hash
implementation commit and PR
Luna invocation records
provider and resource identity
jobs executed, skipped, retried, and stopped
exact commands and exit states
training/evaluation result bundles
checkpoints and archive receipts
provider termination and cleanup receipts
cost and runtime reconciliation
hard failures and deviations
code or configuration changes during campaign: none, or exact reviewed repair
experiment-design conformance
Sol's bounded engineering interpretation
questions requiring ChatGPT review
recommended disposition: READY_FOR_CHATGPT_REVIEW or BLOCKED
```

Sol may summarize operational evidence but may not declare the scientific experiment promoted or the PR merge-ready.

## 38. Review cadence and efficiency

The default review cadence is:

```text
one pre-campaign design and approval
→ one Sol root turn containing approved Luna sub-jobs
→ one consolidated post-campaign review
```

Additional review boundaries occur only when:

- Code or executable configuration changes;
- The campaign envelope changes;
- A scientific decision is required;
- A hard failure occurs;
- An archive, rights, security, or provider issue cannot be resolved within the envelope;
- The campaign reaches its planned decision boundary.

This is intended to maximize implementation and experiment time while preserving meaningful review.

## 39. Standing smoke efficiency policy

The approved `CC-1` policy allows Sol to delegate low-cost mechanical compatibility and failure tests to Luna without requesting owner approval for each tiny launch.

The standing allowance does not authorize:

- Main training;
- Private final evaluation;
- Specialist benchmark claims;
- Persistent filesystems;
- Restricted data;
- Checkpoint promotion;
- A cumulative spend beyond the active program budget;
- Several simultaneous smoke campaigns.

Every smoke remains visible in the exposure, cost, and artifact ledgers.

## 40. Security and operational hard failures

DR-25 treats these as hard failures:

- Raw Lambda API credentials exposed to Sol, Luna, a cloud instance, CI, Git, logs, or public artifacts;
- Luna editing code or configuration;
- Sol or Luna changing the scientific experiment without approval;
- Launch from an unreviewed commit or dirty worktree;
- Natural-language approval substituted for a valid approval grant;
- Launch outside Lambda Cloud;
- Hardware, selected-region outcome, price, or image outside the approved resource and region-selection policy;
- Missing or invalid archive-volume identity;
- Silent archive fallback to another storage location;
- Provider billing continuing after claimed closeout;
- OS shutdown treated as termination;
- Forgotten billable Lambda filesystem;
- Cloud-only checkpoint used for promotion;
- Scientific failure rerolled as infrastructure retry;
- Wrong answer or model refusal omitted from an evaluation result;
- Failed archive causing unbounded runtime;
- Private or restricted data sent to an unauthorized provider route;
- Unapproved inbound ports or public Jupyter/dashboard exposure;
- Missing provider resource inventory, termination receipt, or cleanup receipt;
- Campaign results interpreted or promoted by Luna;
- A campaign controller dependent on one live model session for safety;
- Current cost or price assumptions accepted without live verification;
- A second main campaign launched because the first result was inconvenient rather than under an approved replication design.

## 41. Required implementation and conformance sequence

### `CE-00 — Canonical campaign schemas and reference state machine`

Implement:

- Campaign objects;
- Canonical serialization and hashing;
- State transitions;
- Approval validation;
- Deterministic mock provider;
- Reference cost and retry logic.

### `CE-01 — Lambda Control Broker and credential isolation`

Implement:

- Keychain-backed Lambda credential use;
- Narrow provider operations;
- Rate limiting and resource reconciliation;
- Audit redaction;
- Emergency termination;
- No agent-visible credentials.

### `CE-02 — Archive relay and Thunderbolt conformance`

Implement:

- Volume-identity preflight;
- Atomic `.incoming` staging;
- Resumable owner-pull transfer;
- Hash and load validation;
- Archive receipts;
- Interrupted-transfer tests;
- No fallback paths.

### `CE-03 — Watchdog, cost, and cleanup conformance`

Implement:

- Local and cloud-local watchdogs;
- Heartbeats;
- Cost calculation;
- Idle and no-progress detection;
- Provider termination;
- Filesystem cleanup;
- Provider audit reconciliation.

### `CE-04 — Sol-to-Luna delegation capability probe`

Prove:

- Luna's exact model identity;
- Stricter permissions than Sol;
- No code or repository writes;
- No raw provider credentials;
- Auditable commands and evidence;
- Return to one parent Sol handoff;
- No manual micro-turn requirement;
- Correct block behavior if the mechanism is unavailable.

### `CE-05 — Local and simulated campaign failure injection`

Test:

- Duplicate launch response;
- Provider timeout;
- Region selection outside the approved policy, missing selection evidence, or price above the approved bound;
- Dirty worktree;
- Expired approval;
- Missing archive drive;
- Wrong volume UUID;
- Low space;
- Interrupted transfer;
- Corrupt checkpoint;
- Lost heartbeat;
- Idle GPU;
- Scientific gate failure;
- Security/rights block;
- Luna modification attempt;
- Sol design-deviation attempt.

### `CE-06 — Live CC-1 Lambda closeout smoke`

Run one owner-policy-authorized smoke proving:

- Lambda-only launch;
- Exact image and instance identity;
- Frozen command execution;
- Checkpoint creation;
- Owner-pull archive;
- Hash and load validation;
- Provider termination;
- No remaining filesystem or instance;
- Cost reconciliation;
- One consolidated Sol handoff.

No `CC-2` or higher campaign may launch until `CE-00` through `CE-06` close cleanly.

## 42. Decisions DR-25 locks

Approval establishes that:

1. Campaigns—not raw launch commands—are the unit of cloud authorization.
2. Sol owns implementation and consolidated accountability; Luna owns only frozen mechanical operation.
3. ChatGPT owns experiment design and scientific review; Joseph owns approval and progression.
4. Internal Luna invocations do not create separate review boundaries when they remain inside an approved campaign.
5. `CC-1` creates an approved initial $25, one-hour standing smoke allowance under strict limits.
6. `CC-2` through `CC-5` ordinarily require explicit campaign approval.
7. Natural-language instructions cannot authorize spend.
8. Every campaign is canonically serialized, hashed, approved, and immutable.
9. A project-owned durable controller—not a live agent session—enforces safety and lifecycle.
10. A project-owned Lambda Control Broker retains the full-access Lambda API key outside agent and cloud contexts.
11. Luna receives no raw Lambda or SSH credential.
12. The Sol-to-Luna transport is capability-gated and must prove model and permission isolation.
13. No automatic Sol substitution or manual micro-turn fallback is permitted without a new design.
14. A dedicated Lambda workspace is preferred where practical.
15. Inbound networking remains closed except approved SSH; no public Jupyter or dashboards.
16. Exact Lambda image, container, architecture, instance class, price bounds, tags, and region-selection policy are campaign identity; the selected region is an immutable execution outcome recorded per resource.
17. API rate limits and duplicate-launch reconciliation are mandatory.
18. Machine-checkable transitions may run automatically; scientific decisions stop for review.
19. Only identical transient operations may retry automatically.
20. Wrong answers and failed scientific gates are not retries.
21. Lambda cost includes setup, idle, archive, and cleanup time until provider termination.
22. The local watchdog is the provider-termination authority; the cloud watchdog stops work but holds no Lambda API key.
23. `CC-4` requires a second owner-controlled termination path or separately approved equivalent.
24. The controller host and archive volume must pass readiness before launch.
25. Artifact transfer is owner-pull and provenance-preserving by default.
26. No checkpoint or result is promotable without an external archive receipt.
27. Periodic archive draining and a maximum unsynchronized window are campaign requirements.
28. Lambda persistent filesystems are prohibited by default and separately lifecycle-gated when used.
29. Archive failure receives bounded grace and never creates unbounded billing.
30. Provider termination and cleanup are verified states, not assumptions.
31. Provider audit events supplement project evidence.
32. Secrets remain owner-controlled and excluded from agents, cloud instances, logs, and Git.
33. Sol returns one consolidated handoff covering all Luna operations.
34. `CE-00` through `CE-06` must close before substantive Lambda campaigns.
35. Hard failures block promotion regardless of scientific metrics.

## 43. Decisions intentionally deferred

DR-25 does not yet freeze:

- Exact Lambda workspace ID;
- Exact controller host and secondary termination host;
- Exact external-volume UUID, mount path, filesystem, encryption implementation, and archive-root path;
- Exact macOS Keychain item names and signing implementation;
- Exact canonical serialization library or signature algorithm;
- Exact Lambda API client library;
- Exact SSH and host-key tooling;
- Exact transfer command, concurrency, compression, or bandwidth policy;
- Exact checkpoint and archive-drain cadence;
- Exact maximum unsynchronized window;
- Exact live instance type, image, price, region-selection measurements, and selected region outcome;
- Exact firewall source IPs and outbound allowlist;
- Exact notification and alert channels;
- Exact secondary-watchdog implementation;
- Exact Codex, Responses API, or task transport used to invoke Luna;
- Exact model aliases and snapshots at implementation time;
- Exact `CC-1` standing policy after the first conformance smoke if owner experience suggests adjustment;
- Exact Lambda filesystem policy for any future run that proves local scratch insufficient;
- Exact public dashboard or monitoring UI;
- Exact emergency-manual procedures and contact tree;
- Exact retention and secondary backup policy for the Thunderbolt archive.

Those are consolidated in DR-28 and campaign-specific designs after implementation evidence.

## 44. Approval statement

> **Biblical Scholar Lab will use immutable, owner-authorized cloud campaign envelopes rather than natural-language launch instructions or ad hoc commands. ChatGPT will design every campaign's scientific identity, comparisons, metrics, transitions, stop rules, budget, and permitted claims; Joseph Abbud will approve consequential campaigns, standing-smoke policy, budget, progression, and release; GPT-5.6 Sol will exclusively implement and repair the campaign, provider, archive, watchdog, security, and evidence machinery and remain accountable for one consolidated handoff; and GPT-5.6 Luna may perform only frozen, machine-authorized launch, monitor, checkpoint, exact resume, artifact-transfer coordination, termination, cleanup, and evidence-collection operations delegated by Sol. Internal Luna invocations will not create separate review boundaries when they remain inside one approved campaign, but no code, configuration, data, model, objective, threshold, resource class, provider, archive destination, budget, or scientific interpretation may change without a new review. Every campaign will bind exact design, repository, model, data, benchmark, runtime, container, instance class, dynamic nearest-eligible-region policy, price bounds, job-DAG, retry, watchdog, archive, rights, and closeout identity through a canonical hash and single-use approval grant; each selected region will be recorded as an immutable execution outcome in a Region Selection Receipt. A project-owned durable campaign controller will enforce state transitions independently of agent lifetime. Because Lambda API keys provide broad API authority, a keychain-backed owner-controlled Lambda Control Broker will retain provider credentials and expose only campaign-hash-bound operations; Sol, Luna, CI, cloud instances, and ordinary shells will not receive raw provider credentials. Lambda Cloud will remain the sole project-controlled training and evaluation cloud; the controller will select the nearest currently available eligible Lambda region under the approved latency-, capacity-, rights-, price-, and transfer-aware policy, while exact machine images, selected regions, containers, firewalls, SSH identities, resources, rates, API limits, audit events, and provider states remain explicit. The owner-controlled external Thunderbolt storage volume will remain the authoritative retained archive; artifacts will be pulled from temporary Lambda scratch into atomic external staging, cryptographically and where required load-verified, and promoted only after an Artifact Archive Receipt. A checkpoint, model, evaluation, or result lacking that receipt will remain nonpromotable. Lambda persistent filesystems will be prohibited by default and separately lifecycle-gated when needed. Campaign cost will include setup, idle, checkpoint, archive, termination, and cleanup time; archive failure will receive bounded grace and never authorize unbounded billing; operating-system shutdown will never substitute for provider termination; and closeout will require provider-confirmed instance termination, temporary-filesystem deletion, audit reconciliation, cleanup receipts, and cost evidence. A revocable `CC-1` standing smoke policy may authorize no more than $25 and 60 minutes per Sol root turn under strict nonpromotion, single-instance, no-persistent-filesystem, public-safe conditions, while substantive evaluation, pilot, main-training, final-evaluation, and release campaigns will require explicit owner approval. No campaign beyond standing smoke will launch until the reference state machine, credential broker, Thunderbolt archive relay, watchdog, failure injection, Sol-to-Luna delegation probe, and one live end-to-end Lambda closeout smoke have passed ChatGPT review and owner approval.**

## 45. Amendment history

- **2026-08-16 — Owner approval amendment:** The campaign no longer hard-codes a Lambda region. The approved envelope binds a dynamic nearest-available eligible-region policy. The controller selects the lowest-latency eligible available region from live Lambda inventory, records the decision in a `RegionSelectionReceipt`, and may move to the next-nearest eligible region before launch without a new approval. No other cloud provider is permitted.

---

## References

[^lambda-api]: Lambda, “Lambda Cloud API.” The API exposes instance, image, firewall, SSH-key, filesystem, region, workspace, and audit operations; documents general and launch-specific request limits; and uses bearer API-key authentication: <https://docs.lambda.ai/public-cloud/cloud-api/>.

[^lambda-access]: Lambda, “Access and security.” Lambda states that Cloud API keys have full access to all API operations, describes workspace and role behavior, firewall rulesets, and audit logs: <https://docs.lambda.ai/public-cloud/access-security/>.

[^lambda-connect]: Lambda, “Connecting to an instance.” Lambda documents workspace SSH-key setup and SSH access to on-demand instances: <https://docs.lambda.ai/public-cloud/on-demand/connecting-instance/>.

[^lambda-firewall]: Lambda, “Firewalls.” Lambda documents default inbound ICMP and SSH behavior and global/per-instance firewall rulesets: <https://docs.lambda.ai/public-cloud/firewalls/>.

[^lambda-billing]: Lambda, “Billing overview.” Lambda documents minute-level on-demand billing from successful health checks until provider termination and continuing filesystem billing while a filesystem exists: <https://docs.lambda.ai/public-cloud/billing/>.

[^lambda-lifecycle]: Lambda, “Creating and managing instances.” Lambda warns that `shutdown` or `poweroff` does not terminate an on-demand instance and billing continues; instances must be terminated through the console or API: <https://docs.lambda.ai/public-cloud/on-demand/creating-managing-instances/>.

[^lambda-filesystems]: Lambda, “Filesystems.” Lambda documents regional attachment, launch-time attachment, continuing billing, remote-copy options, deletion, and the inability to transfer filesystems between regions: <https://docs.lambda.ai/public-cloud/filesystems/>.

[^lambda-transfer]: Lambda, “Importing and exporting data.” Lambda documents `rsync` transfer between local environments and instances and warns that instance-local data are destroyed at termination: <https://docs.lambda.ai/public-cloud/importing-exporting-data/>.

[^lambda-audit]: Lambda, “Access and security.” Lambda documents audit event logs, automatic capture, a six-month retention period, and resource lifecycle events: <https://docs.lambda.ai/public-cloud/access-security/>.

[^openai-model-guidance]: OpenAI, “Model guidance.” OpenAI describes `gpt-5.6-sol` as the flagship-capability model and `gpt-5.6-luna` as the efficient high-volume model: <https://developers.openai.com/api/docs/guides/latest-model>.
