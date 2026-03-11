import { spawnSync } from "node:child_process";

import { describe, expect, it } from "vitest";

import { ProtocolConnection, StdioTransport } from "../src/index.js";
import type {
  JsonRpcMessage,
  JsonRpcNotification,
  JsonRpcResponse,
} from "../src/messages.js";

const hasCodex = spawnSync("which", ["codex"], { encoding: "utf8" }).status === 0;
type ThreadStartResponseMessage = JsonRpcResponse & { result: { thread: { id: string } } };
type TurnStartResponseMessage = JsonRpcResponse & { result: { turn: { id: string; status: string } } };
type TurnCompletedNotificationMessage = JsonRpcNotification & {
  method: "turn/completed";
  params: { threadId: string; turn: { status: string } };
};

describe("Protocol core integration", () => {
  it("initializes successfully and returns handshake metadata", async () => {
    if (!hasCodex) {
      return;
    }

    const connection = new ProtocolConnection(new StdioTransport());
    const iterator = connection[Symbol.asyncIterator]();

    try {
      await connection.send({
        id: 1,
        method: "initialize",
        params: { clientInfo: { name: "vitest", version: "0.1.0" } },
      });
      const initialized = await waitForMessage(
        iterator,
        (message) => isResponseForId(message, 1),
        10_000,
      );
      expect(initialized.result).toHaveProperty("userAgent");
    } finally {
      await connection.close();
    }
  }, 15_000);

  it("reaches turn completion after initialize and thread start", async () => {
    if (!hasCodex) {
      return;
    }

    const connection = new ProtocolConnection(new StdioTransport());
    const iterator = connection[Symbol.asyncIterator]();
    const deltas: string[] = [];

    try {
      await connection.send({
        id: 1,
        method: "initialize",
        params: { clientInfo: { name: "vitest", version: "0.1.0" } },
      });
      await waitForMessage(iterator, (message) => isResponseForId(message, 1), 10_000);

      await connection.send({ method: "initialized" });

      await connection.send({ id: 2, method: "thread/start", params: { ephemeral: true } });
      const threadStarted = await waitForMessage(
        iterator,
        (message): message is ThreadStartResponseMessage => isThreadStartResponse(message, 2),
        15_000,
      );
      const threadId = threadStarted.result.thread.id;

      await connection.send({
        id: 3,
        method: "turn/start",
        params: {
          input: [{ text: "Reply with exactly OK.", type: "text" }],
          threadId,
        },
      });
      const turnStarted = await waitForMessage(
        iterator,
        (message): message is TurnStartResponseMessage => isTurnStartResponse(message, 3),
        15_000,
      );
      expect(turnStarted.result.turn.status).toBe("inProgress");

      const completed = await waitForMessage(
        iterator,
        (message) => captureTurnCompletion(message, deltas, threadId),
        60_000,
      );
      expect(["completed", "failed"]).toContain(completed.params.turn.status);
      if (completed.params.turn.status === "completed") {
        expect(deltas.join("").trim()).toBe("OK");
      }
    } finally {
      await connection.close();
    }
  }, 70_000);
});

async function waitForMessage<TMessage extends JsonRpcMessage>(
  iterator: AsyncIterator<JsonRpcMessage>,
  predicate: (message: JsonRpcMessage) => message is TMessage,
  timeoutMs: number,
): Promise<TMessage> {
  const read = async (): Promise<TMessage> => {
    while (true) {
      const next = await iterator.next();
      if (next.done || next.value === undefined) {
        throw new Error("Protocol stream ended before the expected message arrived");
      }
      if (predicate(next.value)) {
        return next.value;
      }
    }
  };

  return await new Promise<TMessage>((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      reject(new Error(`Timed out after ${timeoutMs}ms waiting for protocol message`));
    }, timeoutMs);
    void read().then(
      (message) => {
        clearTimeout(timeoutId);
        resolve(message);
      },
      (error: unknown) => {
        clearTimeout(timeoutId);
        reject(error);
      },
    );
  });
}

function isResponseForId(
  message: JsonRpcMessage,
  id: number,
): message is JsonRpcResponse {
  return "id" in message && message.id === id && "result" in message;
}

function isNotificationMethod<M extends JsonRpcNotification["method"]>(
  message: JsonRpcMessage,
  method: M,
): message is JsonRpcNotification & { method: M } {
  return "method" in message && message.method === method;
}

function isThreadStartResponse(
  message: JsonRpcMessage,
  id: number,
): message is ThreadStartResponseMessage {
  return isResponseForId(message, id) && hasObject(message.result) && hasObject(message.result.thread);
}

function isTurnStartResponse(
  message: JsonRpcMessage,
  id: number,
): message is TurnStartResponseMessage {
  return isResponseForId(message, id) && hasObject(message.result) && hasObject(message.result.turn);
}

function captureTurnCompletion(
  message: JsonRpcMessage,
  deltas: string[],
  threadId: string,
): message is TurnCompletedNotificationMessage {
  if (isNotificationMethod(message, "item/agentMessage/delta")) {
    const params = message.params as { delta: string; threadId: string };
    if (params.threadId === threadId) {
      deltas.push(params.delta);
    }
  }

  return (
    isNotificationMethod(message, "turn/completed")
    && hasObject(message.params)
    && typeof message.params.threadId === "string"
    && hasObject(message.params.turn)
    && typeof message.params.turn.status === "string"
    && message.params.threadId === threadId
  );
}

function hasObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
