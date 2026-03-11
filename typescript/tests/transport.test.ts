import * as path from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { ProtocolStreamError, StdioTransport } from "../src/index.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const HELPER = path.join(__dirname, "helpers", "stdio-child.mjs");

describe("StdioTransport", () => {
  it("round-trips single-line frames", async () => {
    const transport = new StdioTransport({
      command: process.execPath,
      args: [HELPER, "echo"],
    });
    const iterator = transport[Symbol.asyncIterator]();

    try {
      await transport.send('{"id":1,"result":{"ok":true}}');
      const frame = await iterator.next();
      expect(frame.value).toBe('{"id":1,"result":{"ok":true}}');
    } finally {
      await transport.close();
    }
  });

  it("rejects multiline frames", async () => {
    const transport = new StdioTransport({
      command: process.execPath,
      args: [HELPER, "echo"],
    });

    try {
      await expect(transport.send('{"id":1}\n{"id":2}')).rejects.toThrow(/single line/);
    } finally {
      await transport.close();
    }
  });

  it("reports child exit with stderr tail", async () => {
    const transport = new StdioTransport({
      command: process.execPath,
      args: [HELPER, "crash-after-first-line"],
    });
    const iterator = transport[Symbol.asyncIterator]();

    try {
      await transport.send('{"id":1,"result":{"ok":true}}');
      await expect(iterator.next()).rejects.toThrowError(
        new ProtocolStreamError(
          "Transport process exited unexpectedly with code 7. stderr tail:\nchild saw line before crash",
        ),
      );
    } finally {
      await transport.close();
    }
  });

  it("honors cwd", async () => {
    const transport = new StdioTransport({
      command: process.execPath,
      args: [HELPER, "emit-path-and-exit"],
      cwd: __dirname,
    });
    const iterator = transport[Symbol.asyncIterator]();

    try {
      const frame = await iterator.next();
      expect(frame.value).toBe(__dirname);
    } finally {
      await transport.close();
    }
  });

  it("closes cleanly after use", async () => {
    const transport = new StdioTransport({
      command: process.execPath,
      args: [HELPER, "echo"],
    });
    const iterator = transport[Symbol.asyncIterator]();

    await transport.send('{"id":1,"result":{"ok":true}}');
    await iterator.next();
    await expect(transport.close()).resolves.toBeUndefined();
  });
});
