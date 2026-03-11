import { describe, expect, it } from "vitest";

import {
  approveCommand,
  approveFileChange,
  approveFileChangeForSession,
  clientInfo,
  declineCommand,
  declineFileChange,
  textInput,
  threadParams,
  toolAnswers,
  toolCallFailure,
  toolCallSuccess,
  turnOptions,
} from "../src/index.js";

describe("public helpers", () => {
  it("builds client info and text input payloads", () => {
    expect(clientInfo("demo", "0.1.0", { title: "Demo" })).toEqual({
      name: "demo",
      title: "Demo",
      version: "0.1.0",
    });
    expect(textInput("hello")).toEqual({ text: "hello", type: "text" });
  });

  it("defaults thread params to ephemeral and preserves overrides", () => {
    expect(threadParams()).toEqual({ ephemeral: true });
    expect(
      threadParams({
        approvalPolicy: "never",
        cwd: "/tmp/project",
        ephemeral: false,
        model: "gpt-5.1-codex",
      }),
    ).toEqual({
      approvalPolicy: "never",
      cwd: "/tmp/project",
      ephemeral: false,
      model: "gpt-5.1-codex",
    });
  });

  it("only includes provided turn options", () => {
    expect(
      turnOptions({
        effort: "medium",
        model: "gpt-5.1-codex",
        summary: "auto",
      }),
    ).toEqual({
      effort: "medium",
      model: "gpt-5.1-codex",
      summary: "auto",
    });
  });

  it("returns approval and tool helper payloads", () => {
    expect(approveCommand()).toEqual({ decision: "accept" });
    expect(declineCommand()).toEqual({ decision: "decline" });
    expect(approveFileChange()).toEqual({ decision: "accept" });
    expect(declineFileChange()).toEqual({ decision: "decline" });
    expect(approveFileChangeForSession()).toEqual({ decision: "acceptForSession" });
    expect(toolAnswers({ q1: ["yes"], q2: [] })).toEqual({
      answers: {
        q1: { answers: ["yes"] },
        q2: { answers: [] },
      },
    });
    expect(toolCallSuccess([{ text: "ok", type: "inputText" }])).toEqual({
      contentItems: [{ text: "ok", type: "inputText" }],
      success: true,
    });
    expect(toolCallFailure()).toEqual({ contentItems: [], success: false });
  });
});
