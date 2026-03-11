import type { Turn } from "./generated.js";

export class ProtocolError extends Error {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "ProtocolError";
  }
}

export class JsonRpcCodecError extends ProtocolError {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "JsonRpcCodecError";
  }
}

export class ProtocolStreamError extends ProtocolError {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "ProtocolStreamError";
  }
}

export class TransportClosedError extends ProtocolError {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "TransportClosedError";
  }
}

export interface ProtocolClientErrorOptions extends ErrorOptions {
  code?: number;
  data?: unknown;
}

export class ProtocolClientError extends ProtocolError {
  readonly code: number | undefined;
  readonly data: unknown;

  constructor(message: string, options: ProtocolClientErrorOptions = {}) {
    super(message, options);
    this.name = "ProtocolClientError";
    this.code = options.code;
    this.data = options.data;
  }
}

export class ClientClosedError extends ProtocolClientError {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "ClientClosedError";
  }
}

export class RequestTimeoutError extends ProtocolClientError {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "RequestTimeoutError";
  }
}

export class UnknownResponseIdError extends ProtocolClientError {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "UnknownResponseIdError";
  }
}

export class MiddlewareAbortedError extends ProtocolClientError {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = "MiddlewareAbortedError";
  }
}

export class TurnFailedError extends ProtocolClientError {
  readonly turn: Turn;

  constructor(turn: Turn) {
    const reason = turn.error?.message ?? `Turn ${turn.id} completed with status "${turn.status}"`;
    super(reason, { data: turn.error ?? turn });
    this.name = "TurnFailedError";
    this.turn = turn;
  }
}
