import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App, validateWorkspace, Workspace } from "./App";
import schema from "./generated/vs01-study-workspace-projection.schema.json";
import { VS01_STUDY_WORKSPACE_PROJECTION } from "./generated/workspace";

beforeEach(() => {
  sessionStorage.clear();
  vi.restoreAllMocks();
});

function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(record[key])}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

describe("frozen workspace validation", () => {
  it("accepts only the exact projection const", () => {
    expect(schema.const).toEqual(VS01_STUDY_WORKSPACE_PROJECTION);
    expect(schema.type).toBe("object");
    expect(schema.required).toEqual(Object.keys(VS01_STUDY_WORKSPACE_PROJECTION));
    expect(schema.properties).toEqual(
      Object.fromEntries(Object.keys(VS01_STUDY_WORKSPACE_PROJECTION).map((key) => [key, {}])),
    );
    expect(schema.additionalProperties).toBe(false);
    expect(validateWorkspace(VS01_STUDY_WORKSPACE_PROJECTION)).toBe(true);
    expect(validateWorkspace({ ...VS01_STUDY_WORKSPACE_PROJECTION, route: "MODEL" })).toBe(false);
    expect(validateWorkspace({ ...VS01_STUDY_WORKSPACE_PROJECTION, unexpected: true })).toBe(false);
    const missing = structuredClone(VS01_STUDY_WORKSPACE_PROJECTION) as unknown as Record<string, unknown>;
    delete missing.question;
    expect(validateWorkspace(missing)).toBe(false);
  });

  it("rejects mutated data even when its workspace identity is recomputed", () => {
    const mutated = structuredClone(VS01_STUDY_WORKSPACE_PROJECTION) as unknown as Record<string, unknown>;
    mutated.question = "changed";
    delete mutated.workspace_identity;
    mutated.workspace_identity = createHash("sha256").update(canonicalJson(mutated)).digest("hex");
    expect(validateWorkspace(mutated)).toBe(false);
  });

  it("renders only an accessible failure when JSON fails the schema", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify({ contract: "wrong" }))),
    );
    render(<App />);
    expect((await screen.findByRole("alert")).textContent).toContain("No scholarly content");
    expect(screen.queryByRole("heading", { name: /John 1:5 Study workspace/ })).toBeNull();
  });

  it("renders the full semantic surface and native session disclosures", () => {
    render(<Workspace workspace={VS01_STUDY_WORKSPACE_PROJECTION} />);
    for (const heading of [
      "Question and direct answer",
      "Lexical evidence",
      "Textual-state limits and evidence horizon",
      "Page study",
      "Audit and publication details",
    ]) {
      expect(screen.getByRole("heading", { name: heading })).toBeTruthy();
    }
    expect(screen.getByText(/apparatus and witness evidence is absent/)).toBeTruthy();
    expect(screen.getByText(/not REV-P2 specialist gold/)).toBeTruthy();
    const studyBlocks = [...document.querySelectorAll<HTMLElement>("[data-block-id]")];
    expect(studyBlocks.map((block) => block.dataset.blockId)).toEqual(
      VS01_STUDY_WORKSPACE_PROJECTION.study_blocks.map((block) => block.block_id),
    );
    for (const block of VS01_STUDY_WORKSPACE_PROJECTION.study_blocks) {
      expect(screen.getAllByText(block.text)).toHaveLength(1);
    }
    const summary = screen.getByText(/CIT-T05-001/);
    fireEvent.click(summary);
    const details = summary.closest("details") as HTMLDetailsElement;
    fireEvent(details, new Event("toggle"));
    expect(details.open).toBe(true);
    expect(sessionStorage.getItem("bsl-disclosure:CIT-T05-001")).toBe("open");
  });

  it("fetches and validates before scholarly rendering", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify(VS01_STUDY_WORKSPACE_PROJECTION))),
    );
    render(<App />);
    await waitFor(() => expect(screen.getByRole("heading", { name: /John 1:5 Study workspace/ })).toBeTruthy());
  });

  it("contains no remote URL or forbidden persistence API", () => {
    const source = readFileSync(resolve(import.meta.dirname, "App.tsx"), "utf8");
    const generator = readFileSync(resolve(import.meta.dirname, "../scripts/generate-schema.mjs"), "utf8");
    expect(source).not.toMatch(/https?:\/\//);
    expect(source).not.toMatch(/localStorage|indexedDB|serviceWorker|document\.cookie/);
    expect(generator).toContain("ajv.compile(schema)");
    expect(generator).not.toMatch(/validatorSchema|strictTypes|strict:\s*false/);
  });
});
