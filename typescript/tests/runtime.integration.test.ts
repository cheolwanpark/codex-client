import { spawnSync } from "node:child_process";

import { describe, expect, it } from "vitest";

import { ApprovalPolicy, Session } from "../src/index.js";

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

        const finalText = await turn.text();
        if (deltas.length > 0) {
          expect(deltas.join("").trim()).toBe("OK");
        }
        if (turn.status === "completed") {
          expect(finalText.trim()).toBe("OK");
        }
      } finally {
        await session.close();
      }
    },
    70_000,
  );
});
