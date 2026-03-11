import { JsonRpcCodec } from "../../src/codec.js";
import type { Transport } from "../../src/transport.js";

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

export class MockTransport implements Transport {
  readonly sentFrames: string[] = [];
  closed = false;
  private readonly queue = new AsyncQueue<string | Error | typeof QUEUE_EOF>();

  async send(data: string): Promise<void> {
    this.sentFrames.push(data);
  }

  async close(): Promise<void> {
    this.closed = true;
    this.queue.enqueue(QUEUE_EOF);
  }

  async inject(message: unknown): Promise<void> {
    if (typeof message === "string") {
      this.queue.enqueue(message);
      return;
    }
    this.queue.enqueue(JsonRpcCodec.encode(message as never));
  }

  async fail(error: Error): Promise<void> {
    this.queue.enqueue(error);
  }

  async nextSent(): Promise<Record<string, unknown>> {
    while (this.sentFrames.length === 0) {
      await new Promise((resolve) => setTimeout(resolve, 0));
    }

    const frame = this.sentFrames.shift();
    if (frame === undefined) {
      throw new Error("Expected a sent frame");
    }
    return JsonRpcCodec.decode(frame) as unknown as Record<string, unknown>;
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
