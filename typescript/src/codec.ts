import { JsonRpcCodecError } from "./errors.js";
import type {
  JsonRpcErrorObject,
  JsonRpcMessage,
  JSONObject,
  RequestId,
  W3cTraceContext,
} from "./messages.js";

export class JsonRpcCodec {
  static encode(message: JsonRpcMessage): string {
    const normalized = validateMessage(message);
    const { jsonrpc: _jsonrpc, ...payload } = normalized;
    return JSON.stringify(payload);
  }

  static decode(frame: string): JsonRpcMessage {
    let payload: unknown;

    try {
      payload = JSON.parse(frame);
    } catch (error: unknown) {
      const detail = error instanceof Error ? error.message : String(error);
      throw new JsonRpcCodecError(`Invalid JSON: ${detail}`, { cause: asError(error) });
    }

    return validateMessage(payload);
  }
}

function validateMessage(value: unknown): JsonRpcMessage {
  if (!isObject(value)) {
    throw new JsonRpcCodecError("JSON-RPC message must be an object");
  }

  const payload: Record<string, unknown> = { ...value };
  validateJsonRpcField(payload);

  const hasMethod = Object.hasOwn(payload, "method");
  const hasId = Object.hasOwn(payload, "id");
  const hasResult = Object.hasOwn(payload, "result");
  const hasError = Object.hasOwn(payload, "error");

  if (hasMethod) {
    if (hasResult || hasError) {
      throw new JsonRpcCodecError(
        "JSON-RPC message cannot contain both method and result/error fields",
      );
    }

    if (typeof payload.method !== "string") {
      throw new JsonRpcCodecError("JSON-RPC method must be a string");
    }

    if (hasId) {
      validateRequestId(payload.id);
      validateTrace(payload.trace);
    }

    return payload as unknown as JsonRpcMessage;
  }

  if (!hasId) {
    throw new JsonRpcCodecError("JSON-RPC response must include an id");
  }

  validateRequestId(payload.id);

  if (hasResult === hasError) {
    throw new JsonRpcCodecError(
      "JSON-RPC response must contain exactly one of result or error",
    );
  }

  if (hasError) {
    payload.error = validateErrorObject(payload.error);
  }

  return payload as unknown as JsonRpcMessage;
}

function validateJsonRpcField(payload: Record<string, unknown>): void {
  if (!Object.hasOwn(payload, "jsonrpc")) {
    return;
  }

  if (payload.jsonrpc !== "2.0") {
    throw new JsonRpcCodecError('JSON-RPC jsonrpc field must be exactly "2.0"');
  }
}

function validateRequestId(value: unknown): asserts value is RequestId {
  if (typeof value === "string") {
    return;
  }

  if (typeof value === "number" && Number.isInteger(value)) {
    return;
  }

  throw new JsonRpcCodecError("JSON-RPC id must be a string or integer");
}

function validateTrace(value: unknown): asserts value is W3cTraceContext | null | undefined {
  if (value === undefined) {
    return;
  }

  if (value === null) {
    return;
  }

  if (!isObject(value)) {
    throw new JsonRpcCodecError("JSON-RPC trace field must be an object or null");
  }

  for (const key of ["traceparent", "tracestate"] as const) {
    const traceValue = value[key];
    if (traceValue !== undefined && traceValue !== null && typeof traceValue !== "string") {
      throw new JsonRpcCodecError(`JSON-RPC trace.${key} must be a string or null`);
    }
  }
}

function validateErrorObject(value: unknown): JsonRpcErrorObject {
  if (!isObject(value)) {
    throw new JsonRpcCodecError("JSON-RPC error must be an object");
  }

  if (!Object.hasOwn(value, "code") || !Object.hasOwn(value, "message")) {
    throw new JsonRpcCodecError("JSON-RPC error must include code and message");
  }

  if (typeof value.code !== "number" || !Number.isInteger(value.code)) {
    throw new JsonRpcCodecError("JSON-RPC error code must be an integer");
  }

  if (typeof value.message !== "string") {
    throw new JsonRpcCodecError("JSON-RPC error message must be a string");
  }

  return value as unknown as JsonRpcErrorObject;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asError(error: unknown): Error {
  return error instanceof Error ? error : new Error(String(error));
}
