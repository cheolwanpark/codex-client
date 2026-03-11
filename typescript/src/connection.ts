import { JsonRpcCodec } from "./codec.js";
import { JsonRpcCodecError, ProtocolStreamError } from "./errors.js";
import type { JsonRpcMessage } from "./messages.js";
import type { Transport } from "./transport.js";

export class ProtocolConnection implements AsyncIterable<JsonRpcMessage> {
  constructor(private readonly transport: Transport) {}

  async send(message: JsonRpcMessage): Promise<void> {
    await this.transport.send(JsonRpcCodec.encode(message));
  }

  async close(): Promise<void> {
    await this.transport.close();
  }

  async *[Symbol.asyncIterator](): AsyncIterator<JsonRpcMessage> {
    for await (const frame of this.transport) {
      try {
        yield JsonRpcCodec.decode(frame);
      } catch (error: unknown) {
        if (error instanceof JsonRpcCodecError) {
          throw new ProtocolStreamError(
            `Failed to decode incoming JSON-RPC frame: ${error.message}`,
            { cause: error },
          );
        }
        throw error;
      }
    }
  }
}
