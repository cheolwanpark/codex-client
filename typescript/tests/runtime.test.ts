import { describe, expect, it } from "vitest";

import {
  ApprovalPolicy,
  Session,
  turnOptions,
  type Thread as RuntimeThread,
  type Turn as RuntimeTurn,
} from "../src/index.js";
import type {
  CommandExecResponse,
  ModelListResponse,
  Thread,
  ThreadListResponse,
  Turn as ProtocolTurn,
} from "../src/generated.js";
import { MockTransport } from "./helpers/mock-transport.js";

describe("Session runtime", () => {
  it("initializes and closes cleanly", async () => {
    const transport = new MockTransport();
    const session = await createSession(transport);

    try {
      expect(session.client).toBeDefined();
    } finally {
      await session.close();
    }

    expect(transport.closed).toBe(true);
  });

  it("rejects a custom transport combined with stdio options", async () => {
    await expect(
      Session.create({
        clientInfo: { name: "vitest", version: "0.1.0" },
        cwd: "/tmp/project",
        transport: new MockTransport(),
      }),
    ).rejects.toThrow("transport cannot be combined with custom stdio transport options");
  });

  it("reuses thread wrappers for the same thread id", async () => {
    const transport = new MockTransport();
    const session = await createSession(transport);

    try {
      const startTask = session.startThread({ ephemeral: true });
      const started = await transport.nextSent();
      expect(started.method).toBe("thread/start");
      await transport.inject({
        id: started.id,
        result: { thread: makeThread("thr_1") },
      });
      const thread = await startTask;

      const resumeTask = session.resumeThread("thr_1");
      const resumed = await transport.nextSent();
      expect(resumed.method).toBe("thread/resume");
      await transport.inject({
        id: resumed.id,
        result: {
          approvalPolicy: "never",
          cwd: "/tmp",
          model: "gpt-5.1-codex",
          modelProvider: "openai",
          sandbox: { type: "readOnly" },
          thread: makeThread("thr_1", { name: "Renamed" }),
        },
      });

      const resumedThread = await resumeTask;
      expect(resumedThread).toBe(thread);
      expect(thread.name).toBe("Renamed");
    } finally {
      await session.close();
    }
  });

  it("forces ephemeral thread start payloads", async () => {
    const transport = new MockTransport();
    const session = await createSession(transport);

    try {
      const startTask = session.startEphemeralThread({ cwd: "/tmp/project", ephemeral: false });
      const sent = await transport.nextSent();
      expect(sent).toMatchObject({
        method: "thread/start",
        params: { cwd: "/tmp/project", ephemeral: true },
      });
      await transport.inject({
        id: sent.id,
        result: { thread: makeThread("thr_1") },
      });

      const thread = await startTask;
      expect(thread.id).toBe("thr_1");

      const defaultTask = session.startEphemeralThread();
      const defaultSent = await transport.nextSent();
      expect(defaultSent).toMatchObject({
        method: "thread/start",
        params: { ephemeral: true },
      });
      await transport.inject({
        id: defaultSent.id,
        result: { thread: makeThread("thr_2") },
      });

      const ephemeralThread = await defaultTask;
      expect(ephemeralThread.id).toBe("thr_2");
    } finally {
      await session.close();
    }
  });

  it("updates runtime state and emits raw session and thread notifications", async () => {
    const transport = new MockTransport();
    const session = await createSession(transport);

    try {
      const thread = await startThread(session, transport);
      const sessionEvents: Array<Record<string, unknown>> = [];
      const threadEvents: Array<Record<string, unknown>> = [];

      session.on("thread/status/changed", (params) => {
        sessionEvents.push(params as unknown as Record<string, unknown>);
      });
      thread.on("thread/name/updated", (params) => {
        threadEvents.push(params as unknown as Record<string, unknown>);
      });

      await transport.inject({
        method: "thread/status/changed",
        params: { status: { activeFlags: [], type: "active" }, threadId: thread.id },
      });
      await transport.inject({
        method: "thread/name/updated",
        params: { threadId: thread.id, threadName: "Updated Name" },
      });
      await tick();

      expect(thread.status).toEqual({ activeFlags: [], type: "active" });
      expect(thread.name).toBe("Updated Name");
      expect(sessionEvents).toEqual([
        { status: { activeFlags: [], type: "active" }, threadId: thread.id },
      ]);
      expect(threadEvents).toEqual([{ threadId: thread.id, threadName: "Updated Name" }]);
    } finally {
      await session.close();
    }
  });

  it("buffers turn events, updates state, and returns final text", async () => {
    const transport = new MockTransport();
    const session = await createSession(transport);

    try {
      const thread = await startThread(session, transport);
      const turnTask = thread.startTurn("Reply with hello");
      const sent = await transport.nextSent();
      expect(sent).toMatchObject({
        method: "turn/start",
        params: {
          input: [{ text: "Reply with hello", type: "text" }],
          threadId: thread.id,
        },
      });
      await transport.inject({
        id: sent.id,
        result: { turn: makeTurn("turn_1") },
      });
      const turn = await turnTask;

      await transport.inject({
        method: "item/started",
        params: {
          item: { id: "item_1", text: "", type: "agentMessage" },
          threadId: thread.id,
          turnId: turn.id,
        },
      });
      await transport.inject({
        method: "item/agentMessage/delta",
        params: { delta: "Hel", itemId: "item_1", threadId: thread.id, turnId: turn.id },
      });
      await transport.inject({
        method: "item/agentMessage/delta",
        params: { delta: "lo", itemId: "item_1", threadId: thread.id, turnId: turn.id },
      });
      await transport.inject({
        method: "turn/plan/updated",
        params: {
          explanation: "Plan changed",
          plan: [{ status: "completed", step: "reply" }],
          threadId: thread.id,
          turnId: turn.id,
        },
      });
      await transport.inject({
        method: "turn/completed",
        params: {
          threadId: thread.id,
          turn: makeTurn("turn_1", {
            items: [{ id: "item_1", text: "Hello", type: "agentMessage" }],
            status: "completed",
          }),
        },
      });

      const events = [];
      for await (const event of turn) {
        events.push(event);
      }

      expect(events.map((event) => event.type)).toEqual([
        "item_started",
        "agent_message_delta",
        "agent_message_delta",
        "plan_updated",
        "completed",
      ]);
      expect(turn.items).toEqual([{ id: "item_1", text: "Hello", type: "agentMessage" }]);
      await expect(turn.text()).resolves.toBe("Hello");
    } finally {
      await session.close();
    }
  });

  it("forwards turn options helper payloads", async () => {
    const transport = new MockTransport();
    const session = await createSession(transport);

    try {
      const thread = await startThread(session, transport);
      const turnTask = thread.startTurn(
        "Reply with hello",
        turnOptions({ effort: "medium", model: "gpt-5.1-codex" }),
      );
      const sent = await transport.nextSent();

      expect(sent).toMatchObject({
        method: "turn/start",
        params: {
          effort: "medium",
          input: [{ text: "Reply with hello", type: "text" }],
          model: "gpt-5.1-codex",
          threadId: thread.id,
        },
      });

      await transport.inject({
        id: sent.id,
        result: { turn: makeTurn("turn_1") },
      });

      const turn = await turnTask;
      expect(turn.id).toBe("turn_1");
    } finally {
      await session.close();
    }
  });

  it("allows turn iteration only once", async () => {
    const transport = new MockTransport();
    const session = await createSession(transport);

    try {
      const thread = await startThread(session, transport);
      const turn = await startTurn(thread, transport, "stream once");
      const iterator = turn[Symbol.asyncIterator]();

      expect(() => turn[Symbol.asyncIterator]()).toThrow("Turn can only be iterated once");

      await transport.inject({
        method: "turn/completed",
        params: {
          threadId: thread.id,
          turn: makeTurn("turn_1", { status: "completed" }),
        },
      });

      const events = [];
      while (true) {
        const next = await iterator.next();
        if (next.done) {
          break;
        }
        events.push(next.value);
      }
      expect(events.at(-1)?.type).toBe("completed");
    } finally {
      await session.close();
    }
  });

  it("mutates reasoning and command items from deltas", async () => {
    const transport = new MockTransport();
    const session = await createSession(transport);

    try {
      const thread = await startThread(session, transport);
      const turn = await startTurn(thread, transport, "explain");

      await transport.inject({
        method: "item/reasoning/textDelta",
        params: {
          contentIndex: 0,
          delta: "Think",
          itemId: "reason_1",
          threadId: thread.id,
          turnId: turn.id,
        },
      });
      await transport.inject({
        method: "item/reasoning/summaryTextDelta",
        params: {
          delta: "Summary",
          itemId: "reason_1",
          summaryIndex: 0,
          threadId: thread.id,
          turnId: turn.id,
        },
      });
      await transport.inject({
        method: "item/commandExecution/outputDelta",
        params: {
          delta: "stdout",
          itemId: "cmd_1",
          threadId: thread.id,
          turnId: turn.id,
        },
      });
      await tick();

      expect(turn.items[0]).toEqual({
        content: ["Think"],
        id: "reason_1",
        summary: ["Summary"],
        type: "reasoning",
      });
      expect(turn.items[1]).toEqual({
        aggregatedOutput: "stdout",
        command: "",
        commandActions: [],
        cwd: "",
        id: "cmd_1",
        status: "inProgress",
        type: "commandExecution",
      });
    } finally {
      await session.close();
    }
  });

  it("returns final agent text from ask", async () => {
    const transport = new MockTransport();
    const session = await createSession(transport);

    try {
      const thread = await startThread(session, transport);
      const askTask = thread.ask("Reply with OK");
      const sent = await transport.nextSent();
      await transport.inject({
        id: sent.id,
        result: { turn: makeTurn("turn_1") },
      });
      await transport.inject({
        method: "turn/completed",
        params: {
          threadId: thread.id,
          turn: makeTurn("turn_1", {
            items: [{ id: "item_1", text: "OK", type: "agentMessage" }],
            status: "completed",
          }),
        },
      });

      await expect(askTask).resolves.toBe("OK");
    } finally {
      await session.close();
    }
  });

  it("handles all supported approval-policy server requests", async () => {
    const transport = new MockTransport();
    const policyCalls: Array<[string, string]> = [];
    const session = await createSession(
      transport,
      ApprovalPolicy.custom({
        onCommandExecution: (params) => recordCall(policyCalls, "command", params.itemId, { decision: "accept" }),
        onDynamicToolCall: (params) =>
          recordCall(policyCalls, "tool", params.callId, {
            contentItems: [{ text: "tool output", type: "inputText" }],
            success: true,
          }),
        onFileChange: (params) =>
          recordCall(policyCalls, "file", params.itemId, { decision: "acceptForSession" }),
        onToolRequestUserInput: (params) =>
          recordCall(policyCalls, "input", params.itemId, {
            answers: { question_1: { answers: ["yes"] } },
          }),
      }),
    );

    try {
      await transport.inject({
        id: 10,
        method: "item/commandExecution/requestApproval",
        params: { itemId: "cmd_1", threadId: "thr_1", turnId: "turn_1" },
      });
      await expect(transport.nextSent()).resolves.toEqual({
        id: 10,
        result: { decision: "accept" },
      });

      await transport.inject({
        id: 11,
        method: "item/fileChange/requestApproval",
        params: { itemId: "file_1", threadId: "thr_1", turnId: "turn_1" },
      });
      await expect(transport.nextSent()).resolves.toEqual({
        id: 11,
        result: { decision: "acceptForSession" },
      });

      await transport.inject({
        id: 12,
        method: "item/tool/requestUserInput",
        params: {
          itemId: "input_1",
          questions: [{ header: "H", id: "question_1", question: "Q" }],
          threadId: "thr_1",
          turnId: "turn_1",
        },
      });
      await expect(transport.nextSent()).resolves.toEqual({
        id: 12,
        result: { answers: { question_1: { answers: ["yes"] } } },
      });

      await transport.inject({
        id: 13,
        method: "item/tool/call",
        params: {
          arguments: { probe: true },
          callId: "call_1",
          threadId: "thr_1",
          tool: "demo",
          turnId: "turn_1",
        },
      });
      await expect(transport.nextSent()).resolves.toEqual({
        id: 13,
        result: {
          contentItems: [{ text: "tool output", type: "inputText" }],
          success: true,
        },
      });

      expect(policyCalls).toEqual([
        ["command", "cmd_1"],
        ["file", "file_1"],
        ["input", "input_1"],
        ["tool", "call_1"],
      ]);
    } finally {
      await session.close();
    }
  });

  it("defaults approval policy to fail-closed", async () => {
    const transport = new MockTransport();
    const session = await createSession(transport);

    try {
      await transport.inject({
        id: 20,
        method: "item/commandExecution/requestApproval",
        params: { itemId: "cmd_1", threadId: "thr_1", turnId: "turn_1" },
      });
      await expect(transport.nextSent()).resolves.toEqual({
        id: 20,
        result: { decision: "decline" },
      });

      await transport.inject({
        id: 21,
        method: "item/tool/call",
        params: {
          arguments: {},
          callId: "call_1",
          threadId: "thr_1",
          tool: "demo",
          turnId: "turn_1",
        },
      });
      await expect(transport.nextSent()).resolves.toEqual({
        id: 21,
        result: { contentItems: [], success: false },
      });
    } finally {
      await session.close();
    }
  });

  it("wraps the remaining session and thread helpers", async () => {
    const transport = new MockTransport();
    const session = await createSession(transport);

    try {
      const listThreadsTask = session.listThreads({ limit: 5 });
      const listThreadsSent = await transport.nextSent();
      expect(listThreadsSent).toMatchObject({ method: "thread/list", params: { limit: 5 } });
      await transport.inject({
        id: listThreadsSent.id,
        result: { data: [makeThread("thr_1")] } satisfies ThreadListResponse,
      });
      await expect(listThreadsTask).resolves.toEqual({ data: [makeThread("thr_1")] });

      const readThreadTask = session.readThread("thr_1", true);
      const readThreadSent = await transport.nextSent();
      expect(readThreadSent).toMatchObject({
        method: "thread/read",
        params: { includeTurns: true, threadId: "thr_1" },
      });
      await transport.inject({
        id: readThreadSent.id,
        result: { thread: makeThread("thr_1") },
      });
      await expect(readThreadTask).resolves.toEqual(makeThread("thr_1"));

      const listModelsTask = session.listModels({ limit: 1 });
      const listModelsSent = await transport.nextSent();
      expect(listModelsSent).toMatchObject({ method: "model/list", params: { limit: 1 } });
      await transport.inject({
        id: listModelsSent.id,
        result: { data: [] } satisfies ModelListResponse,
      });
      await expect(listModelsTask).resolves.toEqual({ data: [] });

      const execTask = session.exec(["pwd"], { cwd: "/tmp/project", timeoutMs: 5000 });
      const execSent = await transport.nextSent();
      expect(execSent).toMatchObject({
        method: "command/exec",
        params: { command: ["pwd"], cwd: "/tmp/project", timeoutMs: 5000 },
      });
      await transport.inject({
        id: execSent.id,
        result: { exitCode: 0, stderr: "", stdout: "/tmp/project" } satisfies CommandExecResponse,
      });
      await expect(execTask).resolves.toEqual({
        exitCode: 0,
        stderr: "",
        stdout: "/tmp/project",
      });

      const thread = await startThread(session, transport);

      const reviewTask = thread.review({ type: "uncommittedChanges" });
      const reviewSent = await transport.nextSent();
      expect(reviewSent).toMatchObject({
        method: "review/start",
        params: { target: { type: "uncommittedChanges" }, threadId: thread.id },
      });
      await transport.inject({
        id: reviewSent.id,
        result: { reviewThreadId: "review_1", turn: makeTurn("review_turn") },
      });
      const reviewTurn = await reviewTask;
      expect(reviewTurn.reviewThreadId).toBe("review_1");

      const steerTask = thread.steer("Continue", "turn_1");
      const steerSent = await transport.nextSent();
      expect(steerSent).toMatchObject({
        method: "turn/steer",
        params: {
          expectedTurnId: "turn_1",
          input: [{ text: "Continue", type: "text" }],
          threadId: thread.id,
        },
      });
      await transport.inject({ id: steerSent.id, result: { turnId: "turn_2" } });
      await steerTask;

      const interruptTask = thread.interrupt("turn_2");
      const interruptSent = await transport.nextSent();
      expect(interruptSent).toMatchObject({
        method: "turn/interrupt",
        params: { threadId: thread.id, turnId: "turn_2" },
      });
      await transport.inject({ id: interruptSent.id, result: {} });
      await interruptTask;

      const archiveTask = thread.archive();
      const archiveSent = await transport.nextSent();
      expect(archiveSent).toMatchObject({
        method: "thread/archive",
        params: { threadId: thread.id },
      });
      await transport.inject({ id: archiveSent.id, result: {} });
      await archiveTask;

      const unarchiveTask = thread.unarchive();
      const unarchiveSent = await transport.nextSent();
      expect(unarchiveSent).toMatchObject({
        method: "thread/unarchive",
        params: { threadId: thread.id },
      });
      await transport.inject({
        id: unarchiveSent.id,
        result: { thread: makeThread("thr_1", { name: "Unarchived" }) },
      });
      const unarchived = await unarchiveTask;
      expect(unarchived).toBe(thread);
      expect(thread.name).toBe("Unarchived");

      const forkTask = thread.fork();
      const forkSent = await transport.nextSent();
      expect(forkSent).toMatchObject({
        method: "thread/fork",
        params: { threadId: thread.id },
      });
      await transport.inject({
        id: forkSent.id,
        result: {
          approvalPolicy: "never",
          cwd: "/tmp",
          model: "gpt-5.1-codex",
          modelProvider: "openai",
          sandbox: { type: "workspaceWrite" },
          thread: makeThread("thr_2"),
        },
      });
      const forked = await forkTask;
      expect(forked.id).toBe("thr_2");

      const rollbackTask = thread.rollback(1);
      const rollbackSent = await transport.nextSent();
      expect(rollbackSent).toMatchObject({
        method: "thread/rollback",
        params: { numTurns: 1, threadId: thread.id },
      });
      await transport.inject({
        id: rollbackSent.id,
        result: { thread: makeThread("thr_1", { turns: [makeTurn("turn_1")] }) },
      });
      await rollbackTask;
      expect(thread.data.turns).toEqual([makeTurn("turn_1")]);

      const compactTask = thread.compact();
      const compactSent = await transport.nextSent();
      expect(compactSent).toMatchObject({
        method: "thread/compact/start",
        params: { threadId: thread.id },
      });
      await transport.inject({ id: compactSent.id, result: {} });
      await compactTask;

      const unsubscribeTask = thread.unsubscribe();
      const unsubscribeSent = await transport.nextSent();
      expect(unsubscribeSent).toMatchObject({
        method: "thread/unsubscribe",
        params: { threadId: thread.id },
      });
      await transport.inject({ id: unsubscribeSent.id, result: { status: "unsubscribed" } });
      await unsubscribeTask;

      const setNameTask = thread.setName("Renamed");
      const setNameSent = await transport.nextSent();
      expect(setNameSent).toMatchObject({
        method: "thread/name/set",
        params: { name: "Renamed", threadId: thread.id },
      });
      await transport.inject({ id: setNameSent.id, result: {} });
      await setNameTask;
      expect(thread.name).toBe("Renamed");
    } finally {
      await session.close();
    }
  });
});

async function createSession(
  transport: MockTransport,
  approvalPolicy?: ApprovalPolicy,
): Promise<Session> {
  const sessionTask = Session.create({
    clientInfo: { name: "vitest", version: "0.1.0" },
    transport,
    ...(approvalPolicy !== undefined ? { approvalPolicy } : {}),
  });

  const initialize = await transport.nextSent();
  expect(initialize.method).toBe("initialize");
  await transport.inject({ id: initialize.id, result: { userAgent: "vitest" } });

  const initialized = await transport.nextSent();
  expect(initialized).toEqual({ method: "initialized" });

  return await sessionTask;
}

async function startThread(session: Session, transport: MockTransport): Promise<RuntimeThread> {
  const threadTask = session.startThread({ ephemeral: true });
  const sent = await transport.nextSent();
  await transport.inject({
    id: sent.id,
    result: {
      approvalPolicy: "never",
      cwd: "/tmp",
      model: "gpt-5.1-codex",
      modelProvider: "openai",
      sandbox: { type: "readOnly" },
      thread: makeThread("thr_1"),
    },
  });
  return await threadTask;
}

async function startTurn(
  thread: RuntimeThread,
  transport: MockTransport,
  text: string,
): Promise<RuntimeTurn> {
  const turnTask = thread.startTurn(text);
  const sent = await transport.nextSent();
  await transport.inject({
    id: sent.id,
    result: { turn: makeTurn("turn_1") },
  });
  return await turnTask;
}

function makeThread(
  threadId: string,
  overrides: Partial<Thread> = {},
): Thread {
  return {
    cliVersion: "0.1.0",
    createdAt: 0,
    cwd: "/tmp",
    ephemeral: true,
    id: threadId,
    modelProvider: "openai",
    name: null,
    preview: "",
    source: "appServer",
    status: { type: "idle" },
    turns: [],
    updatedAt: 0,
    ...overrides,
  };
}

function makeTurn(
  turnId: string,
  overrides: Partial<ProtocolTurn> = {},
): ProtocolTurn {
  return {
    error: null,
    id: turnId,
    items: [],
    status: "inProgress",
    ...overrides,
  };
}

function recordCall<T>(calls: Array<[string, string]>, kind: string, id: string, response: T): T {
  calls.push([kind, id]);
  return response;
}

async function tick(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0));
}
