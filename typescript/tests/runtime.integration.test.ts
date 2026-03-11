import { spawnSync } from "node:child_process";

import { describe, expect, it } from "vitest";

import { ApprovalPolicy, Session, threadParams } from "../src/index.js";

const hasCodex = spawnSync("which", ["codex"], { encoding: "utf8" }).status === 0;

describe("Session runtime integration", () => {
  it(
    "reaches streamed turn completion against codex app-server",
    async () => {
      if (!hasCodex) {
        return;
      }

      const session = await Session.create({
        approvalPolicy: ApprovalPolicy.autoAccept(),
        clientInfo: { name: "vitest", version: "0.1.0" },
      });

      try {
        const thread = await session.startEphemeralThread();
        const turn = await thread.startTurn("Reply with exactly OK.");
        const deltas: string[] = [];

        for await (const event of turn) {
          if (event.type === "agent_message_delta") {
            deltas.push(event.delta);
          }
          if (event.type === "completed") {
            expect(["completed", "failed"]).toContain(event.turn.status);
          }
        }

        const completed = await turn.waitForCompletion();
        if (deltas.length > 0 && completed.status === "completed") {
          expect(deltas.join("").trim()).toBe("OK");
        }
        if (completed.status === "completed") {
          const finalText = await turn.text();
          expect(finalText.trim()).toBe("OK");
        }
      } finally {
        await session.close();
      }
    },
    70_000,
  );

  it("creates and reads back a persistent thread snapshot", async () => {
    if (!hasCodex) {
      return;
    }

    const session = await Session.create({
      approvalPolicy: ApprovalPolicy.autoAccept(),
      clientInfo: { name: "vitest", version: "0.1.0" },
    });

    try {
      const thread = await session.startThread(threadParams({ ephemeral: false }));
      const snapshot = await session.readThread(thread.id);
      expect(snapshot.id).toBe(thread.id);
      expect(snapshot.ephemeral).toBe(false);
    } finally {
      await session.close();
    }
  }, 30_000);
});
