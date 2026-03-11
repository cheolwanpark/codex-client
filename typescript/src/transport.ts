import { spawn, type ChildProcessWithoutNullStreams } from "node:child_process";
import { createInterface } from "node:readline";

import { ProtocolStreamError, TransportClosedError } from "./errors.js";

export interface Transport extends AsyncIterable<string> {
  send(data: string): Promise<void>;
  close(): Promise<void>;
}

export interface StdioTransportOptions {
  command?: string;
  args?: readonly string[];
  cwd?: string;
  env?: Readonly<Record<string, string>>;
  killTimeoutMs?: number;
}

type QueueItem =
  | { type: "frame"; frame: string }
  | { type: "error"; error: Error }
  | { type: "eof" };

const DEFAULT_KILL_TIMEOUT_MS = 2_000;

export class StdioTransport implements Transport {
  private readonly command: string;
  private readonly args: readonly string[];
  private readonly cwd: string | undefined;
  private readonly env: Readonly<Record<string, string>> | undefined;
  private readonly killTimeoutMs: number;
  private readonly stderrTail: string[] = [];
  private readonly queue = new AsyncQueue<QueueItem>();
  private process: ChildProcessWithoutNullStreams | null = null;
  private startupPromise: Promise<void> | null = null;
  private stdoutTask: Promise<void> | null = null;
  private stderrTask: Promise<void> | null = null;
  private closePromise: Promise<void> | null = null;
  private closed = false;

  constructor(options: StdioTransportOptions = {}) {
    this.command = options.command ?? "codex";
    this.args = options.args ?? ["app-server"];
    this.cwd = options.cwd;
    this.env = options.env;
    this.killTimeoutMs = options.killTimeoutMs ?? DEFAULT_KILL_TIMEOUT_MS;
  }

  async send(data: string): Promise<void> {
    if (data.includes("\n") || data.includes("\r")) {
      throw new ValueError("StdioTransport.send expects a single line without newlines");
    }

    await this.ensureStarted();

    if (this.closed) {
      throw new TransportClosedError("Transport is closed");
    }

    const child = this.requireProcess();
    const stdin = child.stdin;
    if (stdin.destroyed) {
      throw new TransportClosedError("Transport stdin is closed");
    }

    await new Promise<void>((resolve, reject) => {
      let settled = false;

      const finishResolve = () => {
        if (settled) {
          return;
        }

        settled = true;
        cleanup();
        resolve();
      };

      const finishReject = (error: unknown) => {
        if (settled) {
          return;
        }

        settled = true;
        cleanup();
        reject(new TransportClosedError("Transport stdin is closed", { cause: asError(error) }));
      };

      const onError = (error: Error) => {
        finishReject(error);
      };

      const onDrain = () => {
        finishResolve();
      };

      const cleanup = () => {
        stdin.off("error", onError);
        stdin.off("drain", onDrain);
      };

      stdin.once("error", onError);
      const canWrite = stdin.write(`${data}\n`, "utf8", (error) => {
        if (error) {
          finishReject(error);
          return;
        }

        if (canWrite) {
          finishResolve();
        }
      });

      if (!canWrite) {
        stdin.once("drain", onDrain);
      }
    });
  }

  async close(): Promise<void> {
    if (this.closePromise !== null) {
      return this.closePromise;
    }

    this.closed = true;
    this.closePromise = this.closeInternal();
    return this.closePromise;
  }

  async *[Symbol.asyncIterator](): AsyncIterator<string> {
    await this.ensureStarted();

    while (true) {
      const item = await this.queue.dequeue();
      if (item.type === "eof") {
        return;
      }
      if (item.type === "error") {
        throw item.error;
      }
      yield item.frame;
    }
  }

  private async closeInternal(): Promise<void> {
    const child = this.process;
    if (child === null) {
      return;
    }

    const exitPromise = this.waitForExit(child);
    if (!child.stdin.destroyed) {
      child.stdin.end();
      await onceStreamFinished(child.stdin);
    }

    const exitedAfterStdinClose = await promiseWithTimeout(exitPromise, this.killTimeoutMs);
    if (exitedAfterStdinClose === null && child.exitCode === null && child.signalCode === null) {
      child.kill("SIGTERM");
      const exitedAfterTerminate = await promiseWithTimeout(exitPromise, this.killTimeoutMs);
      if (exitedAfterTerminate === null && child.exitCode === null && child.signalCode === null) {
        child.kill("SIGKILL");
        await exitPromise;
      }
    }

    if (this.stdoutTask !== null) {
      await this.stdoutTask;
    }
    if (this.stderrTask !== null) {
      await this.stderrTask;
    }
  }

  private async ensureStarted(): Promise<void> {
    if (this.process !== null) {
      return;
    }

    if (this.startupPromise !== null) {
      return this.startupPromise;
    }

    if (this.closed) {
      throw new TransportClosedError("Transport is closed");
    }

    this.startupPromise = this.startProcess();
    try {
      await this.startupPromise;
    } finally {
      this.startupPromise = null;
    }
  }

  private async startProcess(): Promise<void> {
    const child = spawn(this.command, this.args, {
      cwd: this.cwd,
      env: this.env === undefined ? process.env : { ...process.env, ...this.env },
      stdio: ["pipe", "pipe", "pipe"],
    });

    this.process = child;

    try {
      await new Promise<void>((resolve, reject) => {
        const onSpawn = () => {
          cleanup();
          resolve();
        };

        const onError = (error: Error) => {
          cleanup();
          reject(error);
        };

        const cleanup = () => {
          child.off("spawn", onSpawn);
          child.off("error", onError);
        };

        child.once("spawn", onSpawn);
        child.once("error", onError);
      });
    } catch (error: unknown) {
      this.process = null;
      throw error;
    }

    child.on("error", (error) => {
      if (!this.closed) {
        this.queue.enqueue({ type: "error", error });
      }
    });

    this.stdoutTask = this.pumpStdout(child);
    this.stderrTask = this.pumpStderr(child);
  }

  private async pumpStdout(child: ChildProcessWithoutNullStreams): Promise<void> {
    const reader = createInterface({
      input: child.stdout,
      crlfDelay: Infinity,
    });

    try {
      for await (const line of reader) {
        this.queue.enqueue({ type: "frame", frame: line });
      }

      const { code, signal } = await this.waitForExit(child);
      if (this.closed) {
        this.queue.enqueue({ type: "eof" });
        return;
      }

      this.queue.enqueue({
        type: "error",
        error: new ProtocolStreamError(this.formatProcessExitMessage(code, signal)),
      });
    } catch (error: unknown) {
      if (this.closed) {
        this.queue.enqueue({ type: "eof" });
        return;
      }

      this.queue.enqueue({ type: "error", error: asError(error) });
    } finally {
      reader.close();
    }
  }

  private async pumpStderr(child: ChildProcessWithoutNullStreams): Promise<void> {
    const reader = createInterface({
      input: child.stderr,
      crlfDelay: Infinity,
    });

    try {
      for await (const line of reader) {
        this.stderrTail.push(line);
        if (this.stderrTail.length > 50) {
          this.stderrTail.shift();
        }
      }
    } finally {
      reader.close();
    }
  }

  private formatProcessExitMessage(
    code: number | null,
    signal: NodeJS.Signals | null,
  ): string {
    const exitDetail =
      code === null
        ? `signal ${signal ?? "unknown"}`
        : `code ${code}`;

    let message = `Transport process exited unexpectedly with ${exitDetail}`;
    if (this.stderrTail.length > 0) {
      message += `. stderr tail:\n${this.stderrTail.join("\n")}`;
    }
    return message;
  }

  private requireProcess(): ChildProcessWithoutNullStreams {
    if (this.process === null) {
      throw new TransportClosedError("Transport process has not been started");
    }
    return this.process;
  }

  private waitForExit(
    child: ChildProcessWithoutNullStreams,
  ): Promise<{ code: number | null; signal: NodeJS.Signals | null }> {
    if (child.exitCode !== null || child.signalCode !== null) {
      return Promise.resolve({
        code: child.exitCode,
        signal: child.signalCode,
      });
    }

    return new Promise((resolve) => {
      child.once("exit", (code, signal) => {
        resolve({ code, signal });
      });
    });
  }
}

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

class ValueError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ValueError";
  }
}

function asError(error: unknown): Error {
  return error instanceof Error ? error : new Error(String(error));
}

function onceStreamFinished(
  stream: NodeJS.WritableStream & { writableFinished?: boolean; destroyed?: boolean },
): Promise<void> {
  if (stream.writableFinished || stream.destroyed) {
    return Promise.resolve();
  }

  return new Promise((resolve) => {
    stream.once("finish", () => resolve());
    stream.once("close", () => resolve());
    stream.once("error", () => resolve());
  });
}

async function promiseWithTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T | null> {
  let timer: NodeJS.Timeout | undefined;

  try {
    return await Promise.race([
      promise,
      new Promise<null>((resolve) => {
        timer = setTimeout(() => resolve(null), timeoutMs);
      }),
    ]);
  } finally {
    if (timer !== undefined) {
      clearTimeout(timer);
    }
  }
}
