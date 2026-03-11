import { describe, expect, it } from "vitest";

import { JsonRpcCodec, ProtocolConnection, ProtocolStreamError } from "../src/index.js";
import type { Transport } from "../src/index.js";

const QUEUE_EOF = Symbol("queue eof");

class AsyncQueue<T> {
  private readonly items: T[] = [];
  private readonly waiters: Array<(value: T) => void> = [];

  enqueue(value: T): void {
    const waiter = this.waiters.shift();
    if (waiter !== undefined) {
      waiter(value);
      return;
    }

    this.items.push(value);
  }

  dequeue(): Promise<T> {
    const value = this.items.shift();
    if (value !== undefined) {
      return Promise.resolve(value);
    }

    return new Promise((resolve) => {
      this.waiters.push(resolve);
    });
  }
}

class FakeTransport implements Transport {
  readonly sent: string[] = [];
  closed = false;
  private readonly queue = new AsyncQueue<string | Error | typeof QUEUE_EOF>();

  async send(data: string): Promise<void> {
    this.sent.push(data);
  }

  async close(): Promise<void> {
    this.closed = true;
    this.queue.enqueue(QUEUE_EOF);
  }

  async inject(frame: string): Promise<void> {
    this.queue.enqueue(frame);
  }

  async fail(error: Error): Promise<void> {
    this.queue.enqueue(error);
  }

  async *[Symbol.asyncIterator](): AsyncIterator<string> {
    while (true) {
      const item = await this.queue.dequeue();
      if (item === QUEUE_EOF) {
        return;
      }
      if (item instanceof Error) {
        throw item;
      }
      yield item;
    }
  }
}

describe("ProtocolConnection", () => {
  it("sends compact single-line frames", async () => {
    const transport = new FakeTransport();
    const connection = new ProtocolConnection(transport);

    const message = {
      id: 1,
      method: "initialize",
      params: { clientInfo: { name: "probe", version: "0.1.0" } },
    } as const;

    await connection.send(message);

    expect(transport.sent).toEqual([JsonRpcCodec.encode(message)]);
    expect(transport.sent[0]).not.toContain("\n");
  });

  it("preserves incoming message order", async () => {
    const transport = new FakeTransport();
    const connection = new ProtocolConnection(transport);
    const iterator = connection[Symbol.asyncIterator]();

    await transport.inject('{"id":1,"result":{"first":true}}');
    await transport.inject('{"id":2,"result":{"second":true}}');

    const first = await iterator.next();
    const second = await iterator.next();

    expect(first.value?.id).toBe(1);
    expect(second.value?.id).toBe(2);
  });

  it("wraps decode failures", async () => {
    const transport = new FakeTransport();
    const connection = new ProtocolConnection(transport);
    const iterator = connection[Symbol.asyncIterator]();

    await transport.inject("{");

    await expect(iterator.next()).rejects.toThrowError(
      expect.objectContaining({
        message: expect.stringContaining("Failed to decode incoming JSON-RPC frame"),
      }),
    );
  });

  it("propagates transport errors", async () => {
    const transport = new FakeTransport();
    const connection = new ProtocolConnection(transport);
    const iterator = connection[Symbol.asyncIterator]();

    await transport.fail(new Error("transport blew up"));

    await expect(iterator.next()).rejects.toThrow("transport blew up");
  });

  it("delegates close to the transport", async () => {
    const transport = new FakeTransport();
    const connection = new ProtocolConnection(transport);

    await connection.close();

    expect(transport.closed).toBe(true);
  });
});
