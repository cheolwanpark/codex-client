import type { Thread, Turn } from "../../src/generated.js";

export function makeThread(
  threadId: string,
  overrides: Partial<Thread> = {},
): Thread {
  return {
    cliVersion: "0.1.0",
    createdAt: 0,
    cwd: "/tmp",
    ephemeral: true,
    id: threadId,
    modelProvider: "openai",
    name: null,
    preview: "",
    source: "appServer",
    status: { type: "idle" },
    turns: [],
    updatedAt: 0,
    ...overrides,
  };
}

export function makeTurn(
  turnId: string,
  overrides: Partial<Turn> = {},
): Turn {
  return {
    error: null,
    id: turnId,
    items: [],
    status: "inProgress",
    ...overrides,
  };
}
