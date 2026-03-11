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
