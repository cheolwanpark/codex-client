import { describe, expect, it } from "vitest";

import { JsonRpcCodec, JsonRpcCodecError } from "../src/index.js";

describe("JsonRpcCodec", () => {
  it("round-trips all message shapes", () => {
    const messages = [
      {
        id: 1,
        method: "initialize",
        params: { clientInfo: { name: "test", version: "0.1.0" } },
        trace: { traceparent: "abc" },
      },
      { method: "initialized" },
      { id: 2, result: { userAgent: "probe/1.0" } },
      { id: 3, error: { code: -32600, message: "Not initialized" } },
    ] as const;

    for (const message of messages) {
      const encoded = JsonRpcCodec.encode(message);
      expect(encoded).not.toContain("\n");
      expect(JsonRpcCodec.decode(encoded)).toEqual(message);
    }
  });

  it("accepts explicit jsonrpc but omits it on encode", () => {
    const message = {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        clientInfo: {
          name: "test",
          version: "0.1.0",
        },
      },
    } as const;

    const decoded = JsonRpcCodec.decode(
      '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"test","version":"0.1.0"}}}',
    );

    expect(decoded).toEqual(message);
    expect(JsonRpcCodec.encode(decoded)).toBe(
      '{"id":1,"method":"initialize","params":{"clientInfo":{"name":"test","version":"0.1.0"}}}',
    );
  });

  it.each([
    ["{", "Invalid JSON"],
    ["[]", "JSON-RPC message must be an object"],
    ['{"result":{}}', "JSON-RPC response must include an id"],
    [
      '{"id":1,"method":"x","result":{}}',
      "JSON-RPC message cannot contain both method and result/error fields",
    ],
    ['{"id":1,"error":{"message":"oops"}}', "JSON-RPC error must include code and message"],
    ['{"jsonrpc":"1.0","id":1,"result":{}}', 'JSON-RPC jsonrpc field must be exactly "2.0"'],
  ])("rejects invalid frames: %s", (frame, message) => {
    expect(() => JsonRpcCodec.decode(frame)).toThrowError(
      expect.objectContaining({
        message: expect.stringContaining(message),
      }),
    );
  });

  it("rejects invalid request ids", () => {
    expect(() =>
      JsonRpcCodec.encode({
        id: true as unknown as number,
        method: "initialize",
      }),
    ).toThrowError(new JsonRpcCodecError("JSON-RPC id must be a string or integer"));
  });
});
