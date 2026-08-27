import { useEffect, useState } from "react";
import validateWorkspace from "./generated/validate-workspace.js";
import type { VS01StudyWorkspaceProjection } from "./generated/workspace";

export { validateWorkspace };

type LoadState =
  | { status: "loading" }
  | { status: "failed" }
  | { status: "ready"; workspace: VS01StudyWorkspaceProjection };

function useDisclosure(key: string): [boolean, (open: boolean) => void] {
  const storageKey = `bsl-disclosure:${key}`;
  const [open, setOpen] = useState(() => sessionStorage.getItem(storageKey) === "open");
  return [
    open,
    (next) => {
      setOpen(next);
      sessionStorage.setItem(storageKey, next ? "open" : "closed");
    },
  ];
}

export function App() {
  const [state, setState] = useState<LoadState>({ status: "loading" });
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/v1/vs01/john-1-5/workspace", { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error("workspace request failed");
        return response.json();
      })
      .then((value: unknown) => {
        setState(
          validateWorkspace(value)
            ? { status: "ready", workspace: value as VS01StudyWorkspaceProjection }
            : { status: "failed" },
        );
      })
      .catch((error: unknown) => {
        if (!(error instanceof DOMException && error.name === "AbortError")) setState({ status: "failed" });
      });
    return () => controller.abort();
  }, []);
  if (state.status === "loading") return <p role="status">Loading the verified local workspace…</p>;
  if (state.status === "failed") {
    return <p role="alert">The local workspace could not be validated. No scholarly content has been displayed.</p>;
  }
  return <Workspace workspace={state.workspace} />;
}

export function Workspace({ workspace }: { workspace: VS01StudyWorkspaceProjection }) {
  const [direct, texts, greek, lexicon, alternatives, textualState, assessment] = workspace.study_blocks;
  return (
    <>
      <ContextHeader workspace={workspace} />
      <main id="main-content" tabIndex={-1}>
        <Question workspace={workspace} block={direct} />
        <Translations workspace={workspace} block={texts} />
        <Greek workspace={workspace} block={greek} />
        <Lexical block={lexicon} />
        <Alternatives workspace={workspace} block={alternatives} />
        <Limits workspace={workspace} textualState={textualState} assessment={assessment} />
        <Inspector workspace={workspace} />
        <PageStudy workspace={workspace} />
        <Audit workspace={workspace} />
      </main>
      <footer>
        <p>
          Local, read-only, same-origin Study surface. Automated checks support but do not prove complete WCAG 2.2 AA
          conformance.
        </p>
      </footer>
    </>
  );
}

function ContextHeader({ workspace }: { workspace: VS01StudyWorkspaceProjection }) {
  const context = workspace.active_context;
  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to study content
      </a>
      <header className="site-header">
        <p className="eyebrow">Biblical Scholar Lab · local read-only study</p>
        <h1>John 1:5 Study workspace</h1>
        <nav aria-label="Active study context">
          <ul className="context-list">
            <li>{context.display_reference}</li>
            <li>{context.greek_edition}</li>
            <li>ASV</li>
            <li>WEB Classic</li>
            <li>{workspace.answer_mode}</li>
            <li>{context.method}</li>
            <li>{workspace.route}</li>
            <li>model route {context.model_route}</li>
            <li>{context.evidence_state}</li>
          </ul>
        </nav>
      </header>
    </>
  );
}

type StudyBlock = VS01StudyWorkspaceProjection["study_blocks"][number];

function StudyBlockText({ block }: { block: StudyBlock }) {
  return (
    <article data-block-id={block.block_id}>
      <h3>{block.heading}</h3>
      <p>{block.text}</p>
    </article>
  );
}

function Question({ workspace, block }: { workspace: VS01StudyWorkspaceProjection; block: StudyBlock }) {
  return (
    <section aria-labelledby="question-heading">
      <h2 id="question-heading">Question and direct answer</h2>
      <p className="question">{workspace.question}</p>
      <StudyBlockText block={block} />
    </section>
  );
}

function Translations({ workspace, block }: { workspace: VS01StudyWorkspaceProjection; block: StudyBlock }) {
  return (
    <section aria-labelledby="translations-heading">
      <h2 id="translations-heading">ASV and WEB Classic comparison</h2>
      <StudyBlockText block={block} />
      <p>
        This is a translation-choice and interpretive-effect comparison, not a ranking of a globally best translation.
      </p>
      <ol className="translations">
        {workspace.translations.map((translation) => (
          <li key={translation.translation_id}>
            <h3>{translation.edition}</h3>
            <blockquote>{translation.text}</blockquote>
            <p>
              <strong>Focal span:</strong> <mark>{translation.focal_span}</mark>
            </p>
          </li>
        ))}
      </ol>
    </section>
  );
}

function Greek({ workspace, block }: { workspace: VS01StudyWorkspaceProjection; block: StudyBlock }) {
  return (
    <section aria-labelledby="greek-heading">
      <h2 id="greek-heading">Greek and morphology</h2>
      <StudyBlockText block={block} />
      <p lang="grc" className="greek">
        {workspace.greek.clause}
      </p>
      <dl className="facts">
        <div>
          <dt>Target</dt>
          <dd lang="grc">{workspace.greek.target}</dd>
        </div>
        <div>
          <dt>Lemma</dt>
          <dd lang="grc">{workspace.greek.lemma}</dd>
        </div>
        <div>
          <dt>Parse</dt>
          <dd>{Object.values(workspace.greek.morphology).join(" · ")}</dd>
        </div>
      </dl>
    </section>
  );
}

function Lexical({ block }: { block: StudyBlock }) {
  return (
    <section aria-labelledby="lexical-heading">
      <h2 id="lexical-heading">Lexical evidence</h2>
      <StudyBlockText block={block} />
    </section>
  );
}

function Alternatives({ workspace, block }: { workspace: VS01StudyWorkspaceProjection; block: StudyBlock }) {
  return (
    <section aria-labelledby="alternatives-heading">
      <h2 id="alternatives-heading">Alternatives</h2>
      <StudyBlockText block={block} />
      <ul>
        {workspace.accepted_alternative_ids.map((id) => (
          <li key={id}>{id}</li>
        ))}
      </ul>
    </section>
  );
}

function Limits({
  workspace,
  textualState,
  assessment,
}: {
  workspace: VS01StudyWorkspaceProjection;
  textualState: StudyBlock;
  assessment: StudyBlock;
}) {
  return (
    <section aria-labelledby="limits-heading">
      <h2 id="limits-heading">Textual-state limits and evidence horizon</h2>
      <StudyBlockText block={textualState} />
      <StudyBlockText block={assessment} />
      <p>
        No different Greek reading is required for this controlled contrast. This is not a claim that no textual variant
        exists, and translations are not manuscript witnesses.
      </p>
      <h3>Evidence not present in this workspace</h3>
      <ul>
        {workspace.evidence_horizon.map((limit) => (
          <li key={limit}>{limit} is absent.</li>
        ))}
      </ul>
      <p className="boundary">
        Deterministic and model-free · one passage only · not REV-P2 specialist gold · no broad product-capability claim
      </p>
    </section>
  );
}

function Inspector({ workspace }: { workspace: VS01StudyWorkspaceProjection }) {
  return (
    <section aria-labelledby="inspector-heading">
      <h2 id="inspector-heading">Claim, evidence, and citation inspector</h2>
      <p>Open any citation to inspect its projected authority. Disclosures stay open only for this browser session.</p>
      <div className="disclosures">
        {workspace.evidence_inspector.map((entry) => (
          <Citation key={entry.citation_id} entry={entry} workspace={workspace} />
        ))}
      </div>
    </section>
  );
}

function PageStudy({ workspace }: { workspace: VS01StudyWorkspaceProjection }) {
  return (
    <section aria-labelledby="page-heading">
      <h2 id="page-heading">Page study</h2>
      <p>{workspace.page_study.label}</p>
      <div className="pages">
        <figure>
          <img src="/api/v1/vs01/john-1-5/page/base.png" alt="Legible BASE synthetic John 1:5 study page" />
          <figcaption>BASE · legible synthetic page</figcaption>
        </figure>
        <figure>
          <img
            src="/api/v1/vs01/john-1-5/page/degraded.png"
            alt="DEGRADED_ILLEGIBILITY synthetic page with intentionally unreadable areas; no expected text is substituted"
          />
          <figcaption>
            DEGRADED_ILLEGIBILITY · partially illegible; canonical text is not substituted for unreadable pixels
          </figcaption>
        </figure>
      </div>
      <h3>Ordered page-region alternative</h3>
      <ol>
        {workspace.page_study.regions.map((region) => (
          <li key={region.region_id}>
            <strong>{region.role}</strong> — {region.text}
          </li>
        ))}
      </ol>
    </section>
  );
}

function Citation({
  entry,
  workspace,
}: {
  entry: VS01StudyWorkspaceProjection["evidence_inspector"][number];
  workspace: VS01StudyWorkspaceProjection;
}) {
  const [open, setOpen] = useDisclosure(entry.citation_id);
  return (
    <details open={open} onToggle={(event) => setOpen(event.currentTarget.open)}>
      <summary>
        {entry.citation_id} · {entry.source_role}
      </summary>
      <dl className="citation-grid">
        <div>
          <dt>Evidence ID</dt>
          <dd>{entry.evidence_id}</dd>
        </div>
        <div>
          <dt>Source role</dt>
          <dd>{entry.source_role}</dd>
        </div>
        <div>
          <dt>Source handle</dt>
          <dd>{entry.source_handle}</dd>
        </div>
        <div>
          <dt>Selector</dt>
          <dd>{entry.selector}</dd>
        </div>
        <div>
          <dt>Quoted span</dt>
          <dd>{entry.quoted_span ?? "No projected quotation"}</dd>
        </div>
        <div>
          <dt>Inspection level</dt>
          <dd>{entry.inspection_level}</dd>
        </div>
      </dl>
      <h3>Linked claims</h3>
      <ul>
        {entry.claims.map((claim) => {
          const proposition = workspace.claim_records.find((record) => record.claim_id === claim.claim_id)?.proposition;
          return (
            <li key={claim.claim_id}>
              <strong>
                {claim.claim_id} · {claim.epistemic_status}
              </strong>
              <p>{proposition}</p>
              {claim.required_qualifications.map((qualification) => (
                <p key={qualification}>Qualification: {qualification}</p>
              ))}
            </li>
          );
        })}
      </ul>
    </details>
  );
}

function Audit({ workspace }: { workspace: VS01StudyWorkspaceProjection }) {
  const [open, setOpen] = useDisclosure("audit");
  return (
    <section aria-labelledby="audit-heading">
      <h2 id="audit-heading">Audit and publication details</h2>
      <details open={open} onToggle={(event) => setOpen(event.currentTarget.open)}>
        <summary>Inspect deterministic publication identities and operation counts</summary>
        <p>
          Workspace identity: <code>{workspace.workspace_identity}</code>
        </p>
        <pre>{JSON.stringify(workspace.audit_bindings, null, 2)}</pre>
        <pre>{JSON.stringify(workspace.operation_disclosure, null, 2)}</pre>
      </details>
    </section>
  );
}
