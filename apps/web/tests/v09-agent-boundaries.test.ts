import { readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { describe, expect, test } from "vitest";

const srcRoot = path.resolve(__dirname, "../src");

function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((entry) => {
    const full = path.join(dir, entry);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

describe("v0.9/v1.0 Agent evidence boundaries", () => {
  test("Agent evidence components are only imported by organizer-facing files", () => {
    const files = walk(srcRoot).filter((file) => file.endsWith(".tsx") || file.endsWith(".ts"));
    const importers = files
      .filter((file) => !file.includes(`${path.sep}components${path.sep}agent${path.sep}`))
      .filter((file) => readFileSync(file, "utf8").includes("components/agent"))
      .map((file) => path.relative(srcRoot, file).split(path.sep).join("/"));

    expect(importers.sort()).toEqual([
      "pages/organizer/OrganizerEventWorkspacePage.tsx",
      "pages/organizer/OrganizerExceptionCenterPage.tsx",
      "pages/organizer/OrganizerReviewPage.tsx"
    ]);
  });

  test("merchant tourist and public page source does not import Agent evidence or raw Agent labels", () => {
    const forbidden = [
      "components/agent",
      "AgentRun",
      "AgentStep",
      "AgentToolCall",
      "AgentDraft",
      "AgentModelCall",
      "AgentEvaluation",
      "AgentTrace",
      "Qwen",
      "QwenPaw",
      "deterministic",
      "schema",
      "fallback",
      "runtime state",
      "backend"
    ];
    const files = walk(path.join(srcRoot, "pages")).filter(
      (file) =>
        file.includes(`${path.sep}merchant${path.sep}`) ||
        file.includes(`${path.sep}tourist${path.sep}`) ||
        file.includes(`${path.sep}public${path.sep}`)
    );

    for (const file of files) {
      const source = readFileSync(file, "utf8");
      for (const term of forbidden) {
        expect(source).not.toContain(term);
      }
    }
  });
});
