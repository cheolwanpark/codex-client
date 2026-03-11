import { GeneratedTypedCodexClient } from "./generated-client.js";
import { ProtocolConnection } from "./connection.js";
import {
  SERVER_NOTIFICATION_METHODS,
  SERVER_REQUEST_METHODS,
  type ServerNotificationMethod,
  type ServerNotificationParamsByMethod,
  type ServerRequestMethod,
  type ServerRequestParamsByMethod,
  type ServerRequestResultByMethod,
} from "./generated.js";
import {
  ClientClosedError,
  MiddlewareAbortedError,
  ProtocolClientError,
  RequestTimeoutError,
  UnknownResponseIdError,
} from "./errors.js";
import type {
  JsonRpcErrorObject,
  JsonRpcErrorResponse,
  JsonRpcMessage,
  JsonRpcNotification,
  JsonRpcRequest,
  JsonRpcResponse,
  JSONValue,
  RequestId,
} from "./messages.js";
import type { Transport } from "./transport.js";

export type MiddlewareDirection = "incoming" | "outgoing";

export interface RequestOptions {
  timeoutMs?: number;
}

export interface MiddlewareContext {
  client: TypedCodexClient;
  direction: MiddlewareDirection;
  message: JsonRpcMessage;
  method?: string | undefined;
  requestId?: RequestId | undefined;
  timestamp: number;
}

export type MiddlewareNext = () => Promise<void>;
export type Middleware = (context: MiddlewareContext, next: MiddlewareNext) => Promise<void>;
type MaybePromise<T> = T | Promise<T>;
type AnyNotificationHandler = (params: unknown) => MaybePromise<void>;
type AnyServerRequestHandler = (params: unknown) => MaybePromise<unknown>;
type NotificationPredicate<T> = (params: T) => boolean;
type PendingRequest = {
  reject: (reason?: unknown) => void;
  resolve: (value: unknown) => void;
};

const KNOWN_SERVER_NOTIFICATION_METHODS = new Set<string>(SERVER_NOTIFICATION_METHODS);
const KNOWN_SERVER_REQUEST_METHODS = new Set<string>(SERVER_REQUEST_METHODS);

export class TypedCodexClient extends GeneratedTypedCodexClient {
  static fromTransport(transport: Transport): TypedCodexClient {
    return new TypedCodexClient(new ProtocolConnection(transport));
  }

  private readonly middleware: Middleware[] = [];
  private readonly pendingRequests = new Map<RequestId, PendingRequest>();
  private readonly timedOutRequestIds = new Set<RequestId>();
  private readonly serverRequestHandlers = new Map<string, AnyServerRequestHandler>();
  private readonly notificationHandlers = new Map<string, AnyNotificationHandler[]>();
  private readonly readerLoopPromise: Promise<void>;
  private nextRequestId = 0;
  private closed = false;
  private fatalError: unknown = null;

  constructor(private readonly connection: ProtocolConnection) {
    super();
    this.readerLoopPromise = this.readerLoop();
  }

  use(middleware: Middleware): this {
    this.middleware.push(middleware);
    return this;
  }

  onServerRequest<M extends ServerRequestMethod>(
    method: M,
    handler: (
      params: ServerRequestParamsByMethod[M],
    ) => MaybePromise<ServerRequestResultByMethod[M]>,
  ): () => void {
    const typedHandler: AnyServerRequestHandler = (params) =>
      handler(params as ServerRequestParamsByMethod[M]) as unknown as MaybePromise<unknown>;
    this.serverRequestHandlers.set(method, typedHandler);

    return () => {
      const current = this.serverRequestHandlers.get(method);
      if (current === typedHandler) {
        this.serverRequestHandlers.delete(method);
      }
    };
  }

  onNotification<M extends ServerNotificationMethod>(
    method: M,
    handler: (params: ServerNotificationParamsByMethod[M]) => MaybePromise<void>,
  ): () => void {
    const handlers = this.notificationHandlers.get(method) ?? [];
    const typedHandler: AnyNotificationHandler = (params) =>
      handler(params as ServerNotificationParamsByMethod[M]);
    handlers.push(typedHandler);
    this.notificationHandlers.set(method, handlers);

    return () => {
      const currentHandlers = this.notificationHandlers.get(method);
      if (currentHandlers === undefined) {
        return;
      }
      const index = currentHandlers.indexOf(typedHandler);
      if (index >= 0) {
        currentHandlers.splice(index, 1);
      }
    };
  }

  async request<TResult = unknown>(
    method: string,
    params?: unknown,
    options: RequestOptions = {},
  ): Promise<TResult> {
    this.ensureOpen();

    const requestId = this.allocateRequestId();
    const pending = createPendingRequest();
    this.pendingRequests.set(requestId, pending);

    const message: JsonRpcMessage = {
      id: requestId,
      method,
      ...(params !== undefined ? { params: params as JSONValue | null } : {}),
    };

    try {
      const delivered = await this.runMiddleware(message, "outgoing", async (context) => {
        await this.connection.send(context.message);
      });
      if (!delivered) {
        throw new MiddlewareAbortedError(`Outgoing request "${method}" was aborted by middleware`);
      }
    } catch (error) {
      this.pendingRequests.delete(requestId);
      throw error;
    }

    let timeoutId: NodeJS.Timeout | undefined;
    let resultPromise = pending.promise as Promise<TResult>;
    if (options.timeoutMs !== undefined) {
      resultPromise = Promise.race([
        resultPromise,
        new Promise<TResult>((_, reject) => {
          timeoutId = setTimeout(() => {
            this.pendingRequests.delete(requestId);
            this.timedOutRequestIds.add(requestId);
            reject(
              new RequestTimeoutError(
                `JSON-RPC request "${method}" timed out after ${options.timeoutMs}ms`,
              ),
            );
          }, options.timeoutMs);
        }),
      ]);
    }

    try {
      return await resultPromise;
    } finally {
      if (timeoutId !== undefined) {
        clearTimeout(timeoutId);
      }
    }
  }

  async notify(method: string, params?: unknown): Promise<void> {
    this.ensureOpen();
    const message: JsonRpcMessage = {
      method,
      ...(params !== undefined ? { params: params as JSONValue | null } : {}),
    };

    await this.runMiddleware(message, "outgoing", async (context) => {
      await this.connection.send(context.message);
    });
  }

  async sendInitialized(): Promise<void> {
    await this.notify("initialized");
  }

  async waitForNotification<M extends ServerNotificationMethod>(
    method: M,
    options: {
      predicate?: NotificationPredicate<ServerNotificationParamsByMethod[M]>;
      timeoutMs?: number;
    } = {},
  ): Promise<ServerNotificationParamsByMethod[M]> {
    this.ensureOpen();

    const pending = createPendingRequest<ServerNotificationParamsByMethod[M]>();
    const unsubscribe = this.onNotification(method, (params) => {
      if (options.predicate && !options.predicate(params)) {
        return;
      }
      pending.resolve(params);
    });

    let timeoutId: NodeJS.Timeout | undefined;
    let resultPromise = pending.promise;
    if (options.timeoutMs !== undefined) {
      resultPromise = Promise.race([
        resultPromise,
        new Promise<ServerNotificationParamsByMethod[M]>((_, reject) => {
          timeoutId = setTimeout(() => {
            reject(
              new RequestTimeoutError(
                `Notification "${method}" timed out after ${options.timeoutMs}ms`,
              ),
            );
          }, options.timeoutMs);
        }),
      ]);
    }

    try {
      return await resultPromise;
    } finally {
      unsubscribe();
      if (timeoutId !== undefined) {
        clearTimeout(timeoutId);
      }
    }
  }

  async close(): Promise<void> {
    if (this.closed) {
      await this.readerLoopPromise;
      return;
    }

    this.closed = true;
    this.failPendingRequests(new ClientClosedError("TypedCodexClient is closed"));
    await this.connection.close();
    await this.readerLoopPromise;
  }

  private async readerLoop(): Promise<void> {
    try {
      for await (const message of this.connection) {
        await this.runMiddleware(message, "incoming", async (context) => {
          await this.dispatchIncomingMessage(context.message);
        });
      }
    } catch (error) {
      if (this.closed) {
        return;
      }
      this.fatalError = error;
      this.failPendingRequests(error);
    }
  }

  private async runMiddleware(
    message: JsonRpcMessage,
    direction: MiddlewareDirection,
    terminal: (context: MiddlewareContext) => Promise<void>,
  ): Promise<boolean> {
    const context: MiddlewareContext = {
      client: this,
      direction,
      message,
      ...("method" in message ? { method: message.method } : {}),
      ...("id" in message ? { requestId: message.id } : {}),
      timestamp: Date.now(),
    };
    let delivered = false;

    const callChain = async (index: number): Promise<void> => {
      if (index === this.middleware.length) {
        delivered = true;
        await terminal(context);
        return;
      }

      await this.middleware[index]!(context, async () => {
        await callChain(index + 1);
      });
    };

    await callChain(0);
    return delivered;
  }

  private async dispatchIncomingMessage(message: JsonRpcMessage): Promise<void> {
    if (isResponse(message)) {
      this.handleResponse(message);
      return;
    }
    if (isRequest(message)) {
      await this.handleServerRequest(message);
      return;
    }
    if (isNotification(message)) {
      await this.handleNotification(message);
    }
  }

  private handleResponse(message: JsonRpcResponse | JsonRpcErrorResponse): void {
    const pending = this.pendingRequests.get(message.id);
    if (pending === undefined) {
      if (this.timedOutRequestIds.has(message.id)) {
        this.timedOutRequestIds.delete(message.id);
        return;
      }
      throw new UnknownResponseIdError(
        `Received response for unknown request id ${JSON.stringify(message.id)}`,
      );
    }

    this.pendingRequests.delete(message.id);
    if ("error" in message) {
      pending.reject(this.jsonRpcErrorToException(message.error));
      return;
    }

    pending.resolve(message.result);
  }

  private async handleServerRequest(message: JsonRpcRequest) {
    const handler = this.serverRequestHandlers.get(message.method);
    if (!KNOWN_SERVER_REQUEST_METHODS.has(message.method) || handler === undefined) {
      await this.sendErrorResponse(message.id, {
        code: -32601,
        message: `No server request handler registered for "${message.method}"`,
      });
      return;
    }

    try {
      const result = await handler(message.params);
      const response: JsonRpcMessage = { id: message.id, result: result as JSONValue };
      const delivered = await this.runMiddleware(response, "outgoing", async (context) => {
        await this.connection.send(context.message);
      });
      if (!delivered) {
        throw new MiddlewareAbortedError(
          `Outgoing response for server request "${message.method}" was aborted by middleware`,
        );
      }
    } catch (error) {
      if (error instanceof MiddlewareAbortedError) {
        throw error;
      }
      await this.sendErrorResponse(message.id, {
        code: -32000,
        message:
          error instanceof Error && error.message.length > 0
            ? error.message
            : "Server request handler failed",
      });
    }
  }

  private async handleNotification(message: JsonRpcNotification): Promise<void> {
    if (!KNOWN_SERVER_NOTIFICATION_METHODS.has(message.method)) {
      return;
    }

    const handlers = [...(this.notificationHandlers.get(message.method) ?? [])];
    for (const handler of handlers) {
      await handler(message.params);
    }
  }

  private async sendErrorResponse(
    requestId: RequestId,
    error: JsonRpcErrorObject,
  ): Promise<void> {
    const message: JsonRpcMessage = { id: requestId, error };
    const delivered = await this.runMiddleware(message, "outgoing", async (context) => {
      await this.connection.send(context.message);
    });
    if (!delivered) {
      throw new MiddlewareAbortedError(
        `Outgoing error response for request id ${JSON.stringify(requestId)} was aborted by middleware`,
      );
    }
  }

  private failPendingRequests(error: unknown): void {
    const pending = [...this.pendingRequests.values()];
    this.pendingRequests.clear();
    for (const request of pending) {
      request.reject(error);
    }
  }

  private ensureOpen(): void {
    if (this.closed) {
      throw new ClientClosedError("TypedCodexClient is closed");
    }
    if (this.fatalError !== null) {
      throw this.fatalError;
    }
  }

  private allocateRequestId(): number {
    const requestId = this.nextRequestId;
    this.nextRequestId += 1;
    return requestId;
  }

  private jsonRpcErrorToException(error?: JsonRpcErrorObject): ProtocolClientError {
    if (!error) {
      return new ProtocolClientError("JSON-RPC request failed");
    }
    return new ProtocolClientError(
      `${error.message ?? "JSON-RPC request failed"} (code: ${error.code})`,
      {
        code: error.code,
        data: error.data,
      },
    );
  }
}

function createPendingRequest<T = unknown>(): PendingRequest & { promise: Promise<T> } {
  let resolve = (_value: T) => {};
  let reject = (_reason?: unknown) => {};
  const promise = new Promise<T>((promiseResolve, promiseReject) => {
    resolve = promiseResolve;
    reject = promiseReject;
  });
  return {
    promise,
    reject,
    resolve: resolve as (value: unknown) => void,
  };
}

function isRequest(message: JsonRpcMessage): message is JsonRpcRequest {
  return "method" in message && "id" in message;
}

function isNotification(message: JsonRpcMessage): message is JsonRpcNotification {
  return "method" in message && !("id" in message);
}

function isResponse(message: JsonRpcMessage): message is JsonRpcResponse | JsonRpcErrorResponse {
  return "id" in message && ("result" in message || "error" in message);
}
