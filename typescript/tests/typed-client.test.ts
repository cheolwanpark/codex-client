import { describe, expect, it } from "vitest";

import {
  MiddlewareAbortedError,
  ProtocolConnection,
  RequestTimeoutError,
  TypedCodexClient,
  UnknownResponseIdError,
} from "../src/index.js";
import { MockTransport } from "./helpers/mock-transport.js";

describe("TypedCodexClient", () => {
  it("matches out-of-order responses by request id", async () => {
    const transport = new MockTransport();
    const client = new TypedCodexClient(new ProtocolConnection(transport));

    try {
      const first = client.request("initialize", { clientInfo: { name: "one" } });
      const second = client.request("thread/start", { ephemeral: true });

      const firstSent = await transport.nextSent();
      const secondSent = await transport.nextSent();

      await transport.inject({ id: secondSent.id, result: { request: "second" } });
      await transport.inject({ id: firstSent.id, result: { request: "first" } });

      await expect(first).resolves.toEqual({ request: "first" });
      await expect(second).resolves.toEqual({ request: "second" });
    } finally {
      await client.close();
    }
  });

  it("returns server request handler results", async () => {
    const transport = new MockTransport();
    const client = new TypedCodexClient(new ProtocolConnection(transport));
    client.onServerRequest("item/commandExecution/requestApproval", (params) => ({
      decision: "accept",
      itemId: params.itemId,
    }));

    try {
      await transport.inject({
        id: 9,
        method: "item/commandExecution/requestApproval",
        params: { itemId: "item_1", threadId: "thr_1", turnId: "turn_1" },
      });

      await expect(transport.nextSent()).resolves.toEqual({
        id: 9,
        result: { decision: "accept", itemId: "item_1" },
      });
    } finally {
      await client.close();
    }
  });

  it("returns method not found for missing server request handlers", async () => {
    const transport = new MockTransport();
    const client = new TypedCodexClient(new ProtocolConnection(transport));

    try {
      await transport.inject({
        id: 4,
        method: "item/fileChange/requestApproval",
        params: { itemId: "item_1", turnId: "turn_1", threadId: "thr_1", changes: [] },
      });

      await expect(transport.nextSent()).resolves.toMatchObject({
        id: 4,
        error: { code: -32601 },
      });
    } finally {
      await client.close();
    }
  });

  it("fires notification handlers in registration order", async () => {
    const transport = new MockTransport();
    const client = new TypedCodexClient(new ProtocolConnection(transport));
    const calls: string[] = [];

    client.onNotification("thread/started", (params) => {
      calls.push(`one:${params.thread.id}`);
    });
    client.onNotification("thread/started", (params) => {
      calls.push(`two:${params.thread.id}`);
    });

    try {
      await transport.inject({
        method: "thread/started",
        params: { thread: { id: "thr_1" } },
      });

      await new Promise((resolve) => setTimeout(resolve, 0));
      expect(calls).toEqual(["one:thr_1", "two:thr_1"]);
    } finally {
      await client.close();
    }
  });

  it("runs middleware in deterministic order for outgoing and incoming paths", async () => {
    const transport = new MockTransport();
    const client = new TypedCodexClient(new ProtocolConnection(transport));
    const events: string[] = [];

    const first = async (
      context: Parameters<typeof client.use>[0] extends (ctx: infer C, next: infer N) => Promise<void>
        ? C
        : never,
      next: Parameters<typeof client.use>[0] extends (ctx: never, next: infer N) => Promise<void>
        ? N
        : never,
    ) => {
      events.push(`before:first:${context.direction}:${String(context.method)}`);
      await next();
      events.push(`after:first:${context.direction}:${String(context.method)}`);
    };

    const second = async (
      context: Parameters<typeof client.use>[0] extends (ctx: infer C, next: infer N) => Promise<void>
        ? C
        : never,
      next: Parameters<typeof client.use>[0] extends (ctx: never, next: infer N) => Promise<void>
        ? N
        : never,
    ) => {
      events.push(`before:second:${context.direction}:${String(context.method)}`);
      await next();
      events.push(`after:second:${context.direction}:${String(context.method)}`);
    };

    client.use(first).use(second);
    client.onNotification("thread/started", () => {
      events.push("notification");
    });

    try {
      const requestTask = client.request("initialize", {
        clientInfo: { name: "test", version: "0.1.0" },
      });
      const sent = await transport.nextSent();
      await transport.inject({ id: sent.id, result: {} });
      await requestTask;

      await transport.inject({
        method: "thread/started",
        params: { thread: { id: "thr_1" } },
      });
      await new Promise((resolve) => setTimeout(resolve, 0));

      expect(events).toEqual([
        "before:first:outgoing:initialize",
        "before:second:outgoing:initialize",
        "after:second:outgoing:initialize",
        "before:first:incoming:undefined",
        "before:second:incoming:undefined",
        "after:first:outgoing:initialize",
        "after:second:incoming:undefined",
        "after:first:incoming:undefined",
        "before:first:incoming:thread/started",
        "before:second:incoming:thread/started",
        "notification",
        "after:second:incoming:thread/started",
        "after:first:incoming:thread/started",
      ]);
    } finally {
      await client.close();
    }
  });

  it("allows outgoing middleware to abort requests", async () => {
    const transport = new MockTransport();
    const client = new TypedCodexClient(new ProtocolConnection(transport));

    client.use(async (context, next) => {
      if (context.direction === "outgoing") {
        return;
      }
      await next();
    });

    try {
      await expect(
        client.request("initialize", { clientInfo: { name: "test", version: "0.1.0" } }),
      ).rejects.toThrow(MiddlewareAbortedError);
      expect(transport.sentFrames).toEqual([]);
    } finally {
      await client.close();
    }
  });

  it("times out requests and ignores late responses", async () => {
    const transport = new MockTransport();
    const client = new TypedCodexClient(new ProtocolConnection(transport));

    try {
      await expect(
        client.request("initialize", { clientInfo: { name: "test" } }, { timeoutMs: 10 }),
      ).rejects.toThrow(RequestTimeoutError);

      const timedOutSent = await transport.nextSent();
      expect(timedOutSent.id).toBe(0);
      await transport.inject({ id: 0, result: { late: true } });

      const followUp = client.request("thread/start", { ephemeral: true });
      const sent = await transport.nextSent();
      await transport.inject({ id: sent.id, result: { ok: true } });
      await expect(followUp).resolves.toEqual({ ok: true });
    } finally {
      await client.close();
    }
  });

  it("waits for the first matching notification payload", async () => {
    const transport = new MockTransport();
    const client = new TypedCodexClient(new ProtocolConnection(transport));

    try {
      const waiter = client.waitForNotification("thread/started", {
        predicate: (params) => params.thread.id === "thr_2",
        timeoutMs: 1_000,
      });

      await new Promise((resolve) => setTimeout(resolve, 0));
      await transport.inject({ method: "thread/started", params: { thread: { id: "thr_1" } } });
      await transport.inject({ method: "thread/started", params: { thread: { id: "thr_2" } } });

      await expect(waiter).resolves.toEqual({ thread: { id: "thr_2" } });
    } finally {
      await client.close();
    }
  });

  it("fails pending requests on unknown response ids", async () => {
    const transport = new MockTransport();
    const client = new TypedCodexClient(new ProtocolConnection(transport));

    try {
      const pending = client.request("initialize", { clientInfo: { name: "test" } });
      await transport.nextSent();
      await transport.inject({ id: 999, result: {} });

      await expect(pending).rejects.toThrow(UnknownResponseIdError);
    } finally {
      await client.close();
    }
  });

  it("rejects pending requests on transport failure", async () => {
    const transport = new MockTransport();
    const client = new TypedCodexClient(new ProtocolConnection(transport));

    try {
      const pending = client.request("initialize", { clientInfo: { name: "test" } });
      await transport.nextSent();
      await transport.fail(new Error("transport blew up"));

      await expect(pending).rejects.toThrow("transport blew up");
    } finally {
      await client.close();
    }
  });
});
