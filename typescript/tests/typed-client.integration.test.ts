import { spawnSync } from "node:child_process";

import { describe, expect, it } from "vitest";

import { StdioTransport, TypedCodexClient } from "../src/index.js";

const hasCodex = spawnSync("which", ["codex"], { encoding: "utf8" }).status === 0;

describe("TypedCodexClient integration", () => {
  it("reaches turn completion against codex app-server", async () => {
    if (!hasCodex) {
      return;
    }

    const client = TypedCodexClient.fromTransport(new StdioTransport());
    const deltas: string[] = [];
    let resolveCompleted: ((value: { turn: { status: string } }) => void) | undefined;
    const completed = new Promise<{ turn: { status: string } }>((resolve) => {
      resolveCompleted = resolve;
    });

    client.onNotification("item/agentMessage/delta", (params) => {
      deltas.push(params.delta);
    });
    client.onNotification("turn/completed", (params) => {
      resolveCompleted?.(params);
    });

    try {
      await client.initialize(
        { clientInfo: { name: "vitest", version: "0.1.0" } },
        { timeoutMs: 10_000 },
      );
      await client.sendInitialized();

      const thread = await client.threadStart({ ephemeral: true }, { timeoutMs: 10_000 });
      const turn = await client.turnStart(
        {
          threadId: thread.thread.id,
          input: [{ type: "text", text: "Reply with exactly OK." }],
        },
        { timeoutMs: 10_000 },
      );

      expect(turn.turn.status).toBe("inProgress");
      const finalTurn = await completed;
      expect(["completed", "failed"]).toContain(finalTurn.turn.status);
      if (finalTurn.turn.status === "completed") {
        expect(deltas.join("").trim()).toBe("OK");
      }
    } finally {
      await client.close();
    }
  }, 70_000);
});
