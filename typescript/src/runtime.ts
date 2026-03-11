import {
  SERVER_NOTIFICATION_METHODS,
  type AgentMessageDeltaNotification,
  type AskForApproval,
  type ClientInfo,
  type CommandExecParams,
  type CommandExecResponse,
  type CommandExecutionRequestApprovalParams,
  type CommandExecutionRequestApprovalResponse,
  type DynamicToolCallParams,
  type DynamicToolCallResponse,
  type FileChangeOutputDeltaNotification,
  type FileChangeRequestApprovalParams,
  type FileChangeRequestApprovalResponse,
  type InitializeCapabilities,
  type ItemCompletedNotification,
  type ItemStartedNotification,
  type ModelListParams,
  type ModelListResponse,
  type PlanDeltaNotification,
  type ReasoningEffort,
  type ReasoningSummary,
  type ReasoningSummaryTextDeltaNotification,
  type ReasoningTextDeltaNotification,
  type ReviewDelivery,
  type ReviewStartResponse,
  type ReviewTarget,
  type SandboxPolicy,
  type ServerNotificationMethod,
  type ServerNotificationParamsByMethod,
  type ServiceTier,
  type TextUserInput,
  type Thread,
  type ThreadForkResponse,
  type ThreadItem,
  type ThreadListParams,
  type ThreadListResponse,
  type ThreadReadResponse,
  type ThreadResumeParams,
  type ThreadResumeResponse,
  type ThreadStartParams,
  type ThreadStartResponse,
  type ThreadStatus,
  type ToolRequestUserInputParams,
  type ToolRequestUserInputResponse,
  type Turn,
  type TurnCompletedNotification,
  type TurnDiffUpdatedNotification,
  type TurnPlanStep,
  type TurnPlanUpdatedNotification,
  type TurnStartedNotification,
  type UserInput,
} from "./generated.js";
import { StdioTransport, type Transport } from "./transport.js";
import type { Middleware, TypedCodexClient } from "./client.js";
import { TypedCodexClient as TypedCodexClientImpl } from "./client.js";
import type { JSONValue } from "./messages.js";

type MaybePromise<T> = T | Promise<T>;
type AnyNotificationHandler = (params: unknown) => MaybePromise<void>;

export interface TurnOptions {
  approvalPolicy?: AskForApproval | null;
  cwd?: string | null;
  effort?: ReasoningEffort | null;
  model?: string | null;
  outputSchema?: JSONValue;
  personality?: "none" | "friendly" | "pragmatic" | null;
  sandboxPolicy?: SandboxPolicy | null;
  serviceTier?: ServiceTier | null;
  summary?: ReasoningSummary | null;
}

export interface SessionCreateOptions {
  approvalPolicy?: ApprovalPolicy;
  args?: readonly string[];
  capabilities?: InitializeCapabilities | null;
  clientInfo: ClientInfo;
  command?: string;
  cwd?: string;
  env?: Readonly<Record<string, string>>;
  middleware?: readonly Middleware[];
  transport?: Transport;
}

export interface SessionExecOptions {
  cwd?: string;
  sandboxPolicy?: SandboxPolicy | null;
  timeoutMs?: number;
}

export interface ApprovalPolicyOptions {
  onCommandExecution?: (
    params: CommandExecutionRequestApprovalParams,
  ) => MaybePromise<CommandExecutionRequestApprovalResponse>;
  onDynamicToolCall?: (
    params: DynamicToolCallParams,
  ) => MaybePromise<DynamicToolCallResponse>;
  onFileChange?: (
    params: FileChangeRequestApprovalParams,
  ) => MaybePromise<FileChangeRequestApprovalResponse>;
  onToolRequestUserInput?: (
    params: ToolRequestUserInputParams,
  ) => MaybePromise<ToolRequestUserInputResponse>;
}

export interface ItemStartedEvent {
  item: ThreadItem;
  type: "item_started";
}

export interface ItemCompletedEvent {
  item: ThreadItem;
  type: "item_completed";
}

export interface AgentMessageDeltaEvent {
  delta: string;
  itemId: string;
  type: "agent_message_delta";
}

export interface PlanDeltaEvent {
  delta: string;
  itemId: string;
  type: "plan_delta";
}

export interface ReasoningDeltaEvent {
  delta: string;
  itemId: string;
  type: "reasoning_delta";
}

export interface ReasoningSummaryDeltaEvent {
  delta: string;
  itemId: string;
  summaryIndex: number;
  type: "reasoning_summary_delta";
}

export interface CommandOutputDeltaEvent {
  delta: string;
  itemId: string;
  type: "command_output_delta";
}

export interface FileChangeDeltaEvent {
  delta: string;
  itemId: string;
  type: "file_change_delta";
}

export interface TurnDiffUpdatedEvent {
  diff: string;
  type: "turn_diff_updated";
}

export interface PlanUpdatedEvent {
  explanation: string | null;
  plan: TurnPlanStep[];
  type: "plan_updated";
}

export interface ErrorEvent {
  error: NonNullable<Turn["error"]>;
  type: "error";
}

export interface CompletedEvent {
  turn: Turn;
  type: "completed";
}

export type TurnEvent =
  | AgentMessageDeltaEvent
  | CommandOutputDeltaEvent
  | CompletedEvent
  | ErrorEvent
  | FileChangeDeltaEvent
  | ItemCompletedEvent
  | ItemStartedEvent
  | PlanDeltaEvent
  | PlanUpdatedEvent
  | ReasoningDeltaEvent
  | ReasoningSummaryDeltaEvent
  | TurnDiffUpdatedEvent;

type ThreadDefaults = {
  approvalPolicy?: AskForApproval;
  cwd?: string;
  model?: string;
  modelProvider?: string;
  reasoningEffort?: ReasoningEffort | null;
  sandbox?: SandboxPolicy;
  serviceTier?: ServiceTier | null;
};

type TurnInput = string | UserInput[];
type TurnStreamEntry = TurnEvent | typeof TURN_STREAM_EOF;

const TURN_STREAM_EOF = Symbol("turn stream eof");

export class ApprovalPolicy {
  private constructor(private readonly options: ApprovalPolicyOptions = {}) {}

  static autoAccept(): ApprovalPolicy {
    return new ApprovalPolicy({
      onCommandExecution: () => ({ decision: "accept" }),
      onDynamicToolCall: () => ({ success: true, contentItems: [] }),
      onFileChange: () => ({ decision: "accept" }),
      onToolRequestUserInput: (params) => ({
        answers: Object.fromEntries(
          params.questions.map((question) => [question.id, { answers: [] }]),
        ),
      }),
    });
  }

  static autoDecline(): ApprovalPolicy {
    return new ApprovalPolicy({
      onCommandExecution: () => ({ decision: "decline" }),
      onDynamicToolCall: () => ({ success: false, contentItems: [] }),
      onFileChange: () => ({ decision: "decline" }),
      onToolRequestUserInput: () => ({ answers: {} }),
    });
  }

  static commandsOnly(): ApprovalPolicy {
    return new ApprovalPolicy({
      onCommandExecution: () => ({ decision: "accept" }),
      onDynamicToolCall: () => ({ success: false, contentItems: [] }),
      onFileChange: () => ({ decision: "decline" }),
      onToolRequestUserInput: () => ({ answers: {} }),
    });
  }

  static custom(options: ApprovalPolicyOptions): ApprovalPolicy {
    return new ApprovalPolicy(options);
  }

  async handleCommandExecution(
    params: CommandExecutionRequestApprovalParams,
  ): Promise<CommandExecutionRequestApprovalResponse> {
    if (this.options.onCommandExecution === undefined) {
      return { decision: "decline" };
    }
    return await this.options.onCommandExecution(params);
  }

  async handleFileChange(
    params: FileChangeRequestApprovalParams,
  ): Promise<FileChangeRequestApprovalResponse> {
    if (this.options.onFileChange === undefined) {
      return { decision: "decline" };
    }
    return await this.options.onFileChange(params);
  }

  async handleToolRequestUserInput(
    params: ToolRequestUserInputParams,
  ): Promise<ToolRequestUserInputResponse> {
    if (this.options.onToolRequestUserInput === undefined) {
      return { answers: {} };
    }
    return await this.options.onToolRequestUserInput(params);
  }

  async handleDynamicToolCall(params: DynamicToolCallParams): Promise<DynamicToolCallResponse> {
    if (this.options.onDynamicToolCall === undefined) {
      return { success: false, contentItems: [] };
    }
    return await this.options.onDynamicToolCall(params);
  }
}

export class Session {
  private readonly notificationHandlers = new Map<string, AnyNotificationHandler[]>();
  private readonly threads = new Map<string, ThreadHandle>();
  private closed = false;

  private constructor(
    private readonly typedClient: TypedCodexClient,
    private readonly approvalPolicy: ApprovalPolicy,
  ) {
    this.registerProtocolHandlers();
  }

  static async create(options: SessionCreateOptions): Promise<Session> {
    const {
      approvalPolicy,
      args = ["app-server"],
      capabilities,
      clientInfo,
      command = "codex",
      cwd,
      env,
      middleware = [],
      transport,
    } = options;

    if (
      transport !== undefined &&
      (command !== "codex" ||
        !readonlyArrayEquals(args, ["app-server"]) ||
        cwd !== undefined ||
        env !== undefined)
    ) {
      throw new Error("transport cannot be combined with custom stdio transport options");
    }

    const resolvedTransport =
      transport ??
      new StdioTransport({
        args,
        command,
        ...(cwd !== undefined ? { cwd } : {}),
        ...(env !== undefined ? { env } : {}),
      });

    const client = TypedCodexClientImpl.fromTransport(resolvedTransport);
    for (const entry of middleware) {
      client.use(entry);
    }

    const session = new Session(client, approvalPolicy ?? ApprovalPolicy.autoDecline());
    await client.initialize({ clientInfo, ...(capabilities !== undefined ? { capabilities } : {}) });
    await client.sendInitialized();
    return session;
  }

  get client(): TypedCodexClient {
    return this.typedClient;
  }

  on<M extends ServerNotificationMethod>(
    method: M,
    handler: (params: ServerNotificationParamsByMethod[M]) => MaybePromise<void>,
  ): () => void {
    const handlers = this.notificationHandlers.get(method) ?? [];
    const typedHandler: AnyNotificationHandler = (params) =>
      handler(params as ServerNotificationParamsByMethod[M]);
    handlers.push(typedHandler);
    this.notificationHandlers.set(method, handlers);

    return () => {
      removeHandler(this.notificationHandlers, method, typedHandler);
    };
  }

  async startThread(params?: ThreadStartParams): Promise<ThreadHandle> {
    const response = await this.typedClient.threadStart(params);
    return this.hydrateThread(response.thread, response);
  }

  async startEphemeralThread(params?: ThreadStartParams): Promise<ThreadHandle> {
    const payload: ThreadStartParams = { ...(params ?? {}), ephemeral: true };
    return await this.startThread(payload);
  }

  async resumeThread(threadId: string, params?: Omit<ThreadResumeParams, "threadId">): Promise<ThreadHandle> {
    const response = await this.typedClient.threadResume({ ...(params ?? {}), threadId });
    return this.hydrateThread(response.thread, response);
  }

  async forkThread(threadId: string): Promise<ThreadHandle> {
    const response = await this.typedClient.threadFork({ threadId });
    return this.hydrateThread(response.thread, response);
  }

  async listThreads(params?: ThreadListParams): Promise<ThreadListResponse> {
    return await this.typedClient.threadList(params);
  }

  async readThread(threadId: string, includeTurns = false): Promise<Thread> {
    const response: ThreadReadResponse = await this.typedClient.threadRead({ threadId, includeTurns });
    return response.thread;
  }

  async listModels(params?: ModelListParams): Promise<ModelListResponse> {
    return await this.typedClient.modelList(params);
  }

  async exec(command: string[], options: SessionExecOptions = {}): Promise<CommandExecResponse> {
    const payload: CommandExecParams = { command };
    if (options.cwd !== undefined) {
      payload.cwd = options.cwd;
    }
    if (options.sandboxPolicy !== undefined) {
      payload.sandboxPolicy = options.sandboxPolicy;
    }
    if (options.timeoutMs !== undefined) {
      payload.timeoutMs = options.timeoutMs;
    }
    return await this.typedClient.commandExec(payload);
  }

  async close(): Promise<void> {
    if (this.closed) {
      return;
    }

    this.closed = true;
    await this.typedClient.close();
  }

  private registerProtocolHandlers(): void {
    for (const method of SERVER_NOTIFICATION_METHODS) {
      this.typedClient.onNotification(method, async (params) => {
        await this.handleNotification(method, params);
      });
    }

    this.typedClient.onServerRequest("item/commandExecution/requestApproval", async (params) => {
      return await this.approvalPolicy.handleCommandExecution(params);
    });
    this.typedClient.onServerRequest("item/fileChange/requestApproval", async (params) => {
      return await this.approvalPolicy.handleFileChange(params);
    });
    this.typedClient.onServerRequest("item/tool/requestUserInput", async (params) => {
      return await this.approvalPolicy.handleToolRequestUserInput(params);
    });
    this.typedClient.onServerRequest("item/tool/call", async (params) => {
      return await this.approvalPolicy.handleDynamicToolCall(params);
    });
  }

  private async handleNotification<M extends ServerNotificationMethod>(
    method: M,
    params: ServerNotificationParamsByMethod[M],
  ): Promise<void> {
    const thread = this.applyNotification(method, params);
    await emitHandlers(this.notificationHandlers.get(method) ?? [], params);
    if (thread !== null) {
      await thread.emitNotification(method, params);
    }
  }

  private applyNotification<M extends ServerNotificationMethod>(
    method: M,
    params: ServerNotificationParamsByMethod[M],
  ): ThreadHandle | null {
    if (method === "thread/started") {
      return this.getOrCreateThread((params as ServerNotificationParamsByMethod["thread/started"]).thread);
    }

    const threadId = threadIdFromNotification(method, params);
    if (threadId === null) {
      return null;
    }

    const thread = this.threads.get(threadId) ?? null;
    if (thread === null) {
      return null;
    }

    thread.applyNotification(method, params);
    return thread;
  }

  private hydrateThread(
    threadSnapshot: Thread,
    response: ThreadStartResponse | ThreadResumeResponse | ThreadForkResponse,
  ): ThreadHandle {
    const thread = this.getOrCreateThread(threadSnapshot);
    thread.applyThreadDefaults(response);
    return thread;
  }

  getOrCreateThread(threadSnapshot: Thread): ThreadHandle {
    const existing = this.threads.get(threadSnapshot.id);
    if (existing !== undefined) {
      existing.replaceSnapshot(threadSnapshot);
      return existing;
    }

    const thread = new ThreadHandle(this, threadSnapshot);
    this.threads.set(threadSnapshot.id, thread);
    return thread;
  }
}

export class ThreadHandle {
  private readonly notificationHandlers = new Map<string, AnyNotificationHandler[]>();
  private readonly turns = new Map<string, TurnHandle>();
  private dataSnapshot: Thread;
  private defaults: ThreadDefaults = {};

  constructor(
    private readonly session: Session,
    snapshot: Thread,
  ) {
    this.dataSnapshot = clone(snapshot);
    for (const turn of this.dataSnapshot.turns) {
      this.turns.set(turn.id, new TurnHandle(this, turn));
    }
  }

  get id(): string {
    return this.dataSnapshot.id;
  }

  get name(): string | null | undefined {
    return this.dataSnapshot.name;
  }

  get status(): ThreadStatus {
    return this.dataSnapshot.status;
  }

  get data(): Thread {
    return this.dataSnapshot;
  }

  get activeTurn(): TurnHandle | null {
    for (const turn of this.turns.values()) {
      if (turn.status === "inProgress") {
        return turn;
      }
    }
    return null;
  }

  on<M extends ServerNotificationMethod>(
    method: M,
    handler: (params: ServerNotificationParamsByMethod[M]) => MaybePromise<void>,
  ): () => void {
    const handlers = this.notificationHandlers.get(method) ?? [];
    const typedHandler: AnyNotificationHandler = (params) =>
      handler(params as ServerNotificationParamsByMethod[M]);
    handlers.push(typedHandler);
    this.notificationHandlers.set(method, handlers);

    return () => {
      removeHandler(this.notificationHandlers, method, typedHandler);
    };
  }

  async startTurn(input: TurnInput, options?: TurnOptions): Promise<TurnHandle> {
    const response = await this.session.client.turnStart({
      ...(options ?? {}),
      input: normalizeInput(input),
      threadId: this.id,
    });
    const turn = this.getOrCreateTurn(response.turn);
    this.upsertTurnSnapshot(response.turn);
    return turn;
  }

  async ask(input: TurnInput, options?: TurnOptions): Promise<string> {
    const turn = await this.startTurn(input, options);
    return await turn.text();
  }

  async steer(input: TurnInput, expectedTurnId: string): Promise<void> {
    await this.session.client.turnSteer({
      expectedTurnId,
      input: normalizeInput(input),
      threadId: this.id,
    });
  }

  async interrupt(turnId: string): Promise<void> {
    await this.session.client.turnInterrupt({ threadId: this.id, turnId });
  }

  async review(target: ReviewTarget, delivery?: ReviewDelivery | null): Promise<TurnHandle> {
    const response: ReviewStartResponse = await this.session.client.reviewStart({
      ...(delivery !== undefined ? { delivery } : {}),
      target,
      threadId: this.id,
    });
    const turn = this.getOrCreateTurn(response.turn);
    turn.reviewThreadId = response.reviewThreadId;
    this.upsertTurnSnapshot(response.turn);
    return turn;
  }

  async archive(): Promise<void> {
    await this.session.client.threadArchive({ threadId: this.id });
  }

  async unarchive(): Promise<ThreadHandle> {
    const response = await this.session.client.threadUnarchive({ threadId: this.id });
    return this.session.getOrCreateThread(response.thread);
  }

  async fork(): Promise<ThreadHandle> {
    return await this.session.forkThread(this.id);
  }

  async rollback(numTurns: number): Promise<void> {
    const response = await this.session.client.threadRollback({ numTurns, threadId: this.id });
    this.replaceSnapshot(response.thread);
  }

  async compact(): Promise<void> {
    await this.session.client.threadCompactStart({ threadId: this.id });
  }

  async unsubscribe(): Promise<void> {
    await this.session.client.threadUnsubscribe({ threadId: this.id });
  }

  async setName(name: string): Promise<void> {
    await this.session.client.threadNameSet({ name, threadId: this.id });
    this.dataSnapshot.name = name;
  }

  async emitNotification<M extends ServerNotificationMethod>(
    method: M,
    params: ServerNotificationParamsByMethod[M],
  ): Promise<void> {
    await emitHandlers(this.notificationHandlers.get(method) ?? [], params);
  }

  replaceSnapshot(snapshot: Thread): void {
    this.dataSnapshot = clone(snapshot);
    const seenTurnIds = new Set<string>();

    for (const turnSnapshot of this.dataSnapshot.turns) {
      seenTurnIds.add(turnSnapshot.id);
      this.getOrCreateTurn(turnSnapshot);
    }

    for (const turnId of [...this.turns.keys()]) {
      if (!seenTurnIds.has(turnId)) {
        this.turns.delete(turnId);
      }
    }
  }

  applyThreadDefaults(response: ThreadStartResponse | ThreadResumeResponse | ThreadForkResponse): void {
    this.defaults = {
      approvalPolicy: response.approvalPolicy,
      cwd: response.cwd,
      model: response.model,
      modelProvider: response.modelProvider,
      ...(response.reasoningEffort !== undefined
        ? { reasoningEffort: response.reasoningEffort }
        : {}),
      sandbox: response.sandbox,
      ...(response.serviceTier !== undefined ? { serviceTier: response.serviceTier } : {}),
    };
  }

  applyNotification<M extends ServerNotificationMethod>(
    method: M,
    params: ServerNotificationParamsByMethod[M],
  ): void {
    if (method === "thread/started") {
      this.replaceSnapshot((params as ServerNotificationParamsByMethod["thread/started"]).thread);
      return;
    }

    if (method === "thread/status/changed") {
      this.dataSnapshot.status = clone(
        (params as ServerNotificationParamsByMethod["thread/status/changed"]).status,
      );
      return;
    }

    if (method === "thread/name/updated") {
      this.dataSnapshot.name =
        clone((params as ServerNotificationParamsByMethod["thread/name/updated"]).threadName) ??
        null;
      return;
    }

    if (method === "turn/started") {
      const turnSnapshot = (params as TurnStartedNotification).turn;
      this.getOrCreateTurn(turnSnapshot);
      this.upsertTurnSnapshot(turnSnapshot);
      return;
    }

    if (method === "turn/completed") {
      const turnSnapshot = (params as TurnCompletedNotification).turn;
      const turn = this.turns.get(turnSnapshot.id) ?? this.getOrCreateTurn(turnSnapshot);
      turn.handleCompleted(turnSnapshot);
      this.upsertTurnSnapshot(turn.snapshot);
      return;
    }

    if (!hasStringTurnId(params)) {
      return;
    }

    const turn = this.ensureTurn(params.turnId);
    turn.applyNotification(method, params);
    this.upsertTurnSnapshot(turn.snapshot);
  }

  private upsertTurnSnapshot(snapshot: Turn): void {
    const index = this.dataSnapshot.turns.findIndex((turn) => turn.id === snapshot.id);
    if (index >= 0) {
      this.dataSnapshot.turns[index] = clone(snapshot);
      return;
    }

    this.dataSnapshot.turns.push(clone(snapshot));
  }

  private ensureTurn(turnId: string): TurnHandle {
    const existing = this.turns.get(turnId);
    if (existing !== undefined) {
      return existing;
    }

    const turn = new TurnHandle(this, {
      error: null,
      id: turnId,
      items: [],
      status: "inProgress",
    });
    this.turns.set(turnId, turn);
    this.upsertTurnSnapshot(turn.snapshot);
    return turn;
  }

  private getOrCreateTurn(snapshot: Turn): TurnHandle {
    const existing = this.turns.get(snapshot.id);
    if (existing !== undefined) {
      existing.replaceSnapshot(snapshot);
      return existing;
    }

    const turn = new TurnHandle(this, snapshot);
    this.turns.set(snapshot.id, turn);
    return turn;
  }
}

export { ThreadHandle as Thread };

export class TurnHandle implements AsyncIterable<TurnEvent> {
  readonly events = new AsyncQueue<TurnStreamEntry>();
  reviewThreadId: string | null = null;
  private snapshotValue: Turn;
  private readonly completion = createDeferred<Turn>();
  private readonly itemIndexes = new Map<string, number>();
  private iterStarted = false;
  private streamClosed = false;

  constructor(
    private readonly thread: ThreadHandle,
    snapshot: Turn,
  ) {
    this.snapshotValue = clone(snapshot);
    this.rebuildItemIndexes();

    if (this.status !== "inProgress") {
      this.completion.resolve(clone(this.snapshotValue));
      this.closeStream();
    }
  }

  get id(): string {
    return this.snapshotValue.id;
  }

  get status(): Turn["status"] {
    return this.snapshotValue.status;
  }

  get items(): ThreadItem[] {
    return this.snapshotValue.items;
  }

  get error(): Turn["error"] {
    return this.snapshotValue.error;
  }

  get snapshot(): Turn {
    return this.snapshotValue;
  }

  [Symbol.asyncIterator](): AsyncIterator<TurnEvent> {
    if (this.iterStarted) {
      throw new Error("Turn can only be iterated once");
    }

    this.iterStarted = true;
    return this.iterate();
  }

  async waitForCompletion(): Promise<Turn> {
    return clone(await this.completion.promise);
  }

  async text(): Promise<string> {
    const turn = await this.waitForCompletion();
    return turn.items
      .filter((item): item is Extract<ThreadItem, { type: "agentMessage" }> => item.type === "agentMessage")
      .map((item) => item.text)
      .join("");
  }

  replaceSnapshot(snapshot: Turn): void {
    this.snapshotValue = clone(snapshot);
    this.rebuildItemIndexes();
    if (this.status !== "inProgress" && !this.completion.settled) {
      this.completion.resolve(clone(this.snapshotValue));
    }
  }

  handleCompleted(snapshot: Turn): void {
    const completedSnapshot = clone(snapshot);
    if (completedSnapshot.items.length === 0 && this.snapshotValue.items.length > 0) {
      completedSnapshot.items = clone(this.snapshotValue.items);
    }
    this.replaceSnapshot(completedSnapshot);
    this.emitEvent({ type: "completed", turn: clone(this.snapshotValue) });
    this.closeStream();
  }

  applyNotification<M extends ServerNotificationMethod>(
    method: M,
    params: ServerNotificationParamsByMethod[M],
  ): void {
    if (method === "item/started") {
      const item = clone((params as ItemStartedNotification).item);
      this.upsertItem(item);
      this.emitEvent({ item: clone(item), type: "item_started" });
      return;
    }

    if (method === "item/completed") {
      const item = clone((params as ItemCompletedNotification).item);
      this.upsertItem(item);
      this.emitEvent({ item: clone(item), type: "item_completed" });
      return;
    }

    if (method === "item/agentMessage/delta") {
      const notification = params as AgentMessageDeltaNotification;
      this.appendAgentMessageDelta(notification.itemId, notification.delta);
      this.emitEvent({
        delta: notification.delta,
        itemId: notification.itemId,
        type: "agent_message_delta",
      });
      return;
    }

    if (method === "item/plan/delta") {
      const notification = params as PlanDeltaNotification;
      this.appendPlanDelta(notification.itemId, notification.delta);
      this.emitEvent({ delta: notification.delta, itemId: notification.itemId, type: "plan_delta" });
      return;
    }

    if (method === "item/reasoning/textDelta") {
      const notification = params as ReasoningTextDeltaNotification;
      this.appendReasoningDelta(notification.itemId, notification.contentIndex, notification.delta);
      this.emitEvent({
        delta: notification.delta,
        itemId: notification.itemId,
        type: "reasoning_delta",
      });
      return;
    }

    if (method === "item/reasoning/summaryTextDelta") {
      const notification = params as ReasoningSummaryTextDeltaNotification;
      this.appendReasoningSummaryDelta(
        notification.itemId,
        notification.summaryIndex,
        notification.delta,
      );
      this.emitEvent({
        delta: notification.delta,
        itemId: notification.itemId,
        summaryIndex: notification.summaryIndex,
        type: "reasoning_summary_delta",
      });
      return;
    }

    if (method === "item/commandExecution/outputDelta") {
      const notification = params as ServerNotificationParamsByMethod["item/commandExecution/outputDelta"];
      this.appendCommandOutputDelta(notification.itemId, notification.delta);
      this.emitEvent({
        delta: notification.delta,
        itemId: notification.itemId,
        type: "command_output_delta",
      });
      return;
    }

    if (method === "item/fileChange/outputDelta") {
      const notification = params as FileChangeOutputDeltaNotification;
      this.emitEvent({
        delta: notification.delta,
        itemId: notification.itemId,
        type: "file_change_delta",
      });
      return;
    }

    if (method === "turn/diff/updated") {
      const notification = params as TurnDiffUpdatedNotification;
      this.emitEvent({ diff: notification.diff, type: "turn_diff_updated" });
      return;
    }

    if (method === "turn/plan/updated") {
      const notification = params as TurnPlanUpdatedNotification;
      this.emitEvent({
        explanation: notification.explanation ?? null,
        plan: clone(notification.plan),
        type: "plan_updated",
      });
      return;
    }

    if (method === "error") {
      const notification = params as ServerNotificationParamsByMethod["error"];
      this.snapshotValue.error = clone(notification.error);
      this.emitEvent({ error: clone(notification.error), type: "error" });
    }
  }

  private async *iterate(): AsyncGenerator<TurnEvent> {
    while (true) {
      const event = await this.events.dequeue();
      if (event === TURN_STREAM_EOF) {
        return;
      }
      yield event;
    }
  }

  private upsertItem(item: ThreadItem): void {
    const index = this.itemIndexes.get(item.id);
    if (index === undefined) {
      this.snapshotValue.items.push(item);
      this.itemIndexes.set(item.id, this.snapshotValue.items.length - 1);
      return;
    }

    this.snapshotValue.items[index] = item;
  }

  private appendAgentMessageDelta(itemId: string, delta: string): void {
    const item = this.ensureAgentMessageItem(itemId);
    item.text += delta;
  }

  private appendPlanDelta(itemId: string, delta: string): void {
    const item = this.ensurePlanItem(itemId);
    item.text += delta;
  }

  private appendReasoningDelta(itemId: string, contentIndex: number, delta: string): void {
    const item = this.ensureReasoningItem(itemId);
    const content = item.content ?? [];
    ensureListSize(content, contentIndex + 1);
    content[contentIndex] += delta;
    item.content = content;
  }

  private appendReasoningSummaryDelta(itemId: string, summaryIndex: number, delta: string): void {
    const item = this.ensureReasoningItem(itemId);
    const summary = item.summary ?? [];
    ensureListSize(summary, summaryIndex + 1);
    summary[summaryIndex] += delta;
    item.summary = summary;
  }

  private appendCommandOutputDelta(itemId: string, delta: string): void {
    const item = this.ensureCommandExecutionItem(itemId);
    item.aggregatedOutput = `${item.aggregatedOutput ?? ""}${delta}`;
  }

  private ensureAgentMessageItem(itemId: string): Extract<ThreadItem, { type: "agentMessage" }> {
    return this.ensureItem(itemId, { id: itemId, text: "", type: "agentMessage" });
  }

  private ensurePlanItem(itemId: string): Extract<ThreadItem, { type: "plan" }> {
    return this.ensureItem(itemId, { id: itemId, text: "", type: "plan" });
  }

  private ensureReasoningItem(itemId: string): Extract<ThreadItem, { type: "reasoning" }> {
    return this.ensureItem(itemId, { id: itemId, summary: [], type: "reasoning" });
  }

  private ensureCommandExecutionItem(
    itemId: string,
  ): Extract<ThreadItem, { type: "commandExecution" }> {
    return this.ensureItem(itemId, {
      aggregatedOutput: "",
      command: "",
      commandActions: [],
      cwd: "",
      id: itemId,
      status: "inProgress",
      type: "commandExecution",
    });
  }

  private ensureItem<TItem extends ThreadItem>(itemId: string, placeholder: TItem): TItem {
    const index = this.itemIndexes.get(itemId);
    if (index === undefined) {
      this.snapshotValue.items.push(clone(placeholder));
      this.itemIndexes.set(itemId, this.snapshotValue.items.length - 1);
      return this.snapshotValue.items[this.snapshotValue.items.length - 1] as TItem;
    }

    return this.snapshotValue.items[index] as TItem;
  }

  private rebuildItemIndexes(): void {
    this.itemIndexes.clear();
    this.snapshotValue.items.forEach((item, index) => {
      this.itemIndexes.set(item.id, index);
    });
  }

  private emitEvent(event: TurnEvent): void {
    if (this.streamClosed) {
      return;
    }
    this.events.enqueue(event);
  }

  private closeStream(): void {
    if (this.streamClosed) {
      return;
    }
    this.streamClosed = true;
    this.events.enqueue(TURN_STREAM_EOF);
  }
}

export { TurnHandle as Turn };

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

function createDeferred<T>(): {
  promise: Promise<T>;
  resolve: (value: T) => void;
  settled: boolean;
} {
  let resolve = (_value: T) => {};
  const deferred = {
    promise: new Promise<T>((promiseResolve) => {
      resolve = (value: T) => {
        deferred.settled = true;
        promiseResolve(value);
      };
    }),
    resolve,
    settled: false,
  };
  return deferred;
}

function clone<T>(value: T): T {
  return structuredClone(value);
}

function normalizeInput(input: TurnInput): UserInput[] {
  if (typeof input === "string") {
    const userInput: TextUserInput = { text: input, type: "text" };
    return [userInput];
  }
  return clone(input);
}

async function emitHandlers(handlers: readonly AnyNotificationHandler[], params: unknown): Promise<void> {
  for (const handler of [...handlers]) {
    await handler(params);
  }
}

function threadIdFromNotification<M extends ServerNotificationMethod>(
  method: M,
  params: ServerNotificationParamsByMethod[M],
): string | null {
  if (method === "thread/started") {
    return (params as ServerNotificationParamsByMethod["thread/started"]).thread.id;
  }

  if (isRecord(params) && typeof params.threadId === "string") {
    return params.threadId;
  }

  return null;
}

function hasStringTurnId(value: unknown): value is { turnId: string } {
  return isRecord(value) && typeof value.turnId === "string";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function removeHandler(
  handlersByMethod: Map<string, AnyNotificationHandler[]>,
  method: string,
  handler: AnyNotificationHandler,
): void {
  const handlers = handlersByMethod.get(method);
  if (handlers === undefined) {
    return;
  }
  const index = handlers.indexOf(handler);
  if (index >= 0) {
    handlers.splice(index, 1);
  }
}

function ensureListSize(values: string[], size: number): void {
  while (values.length < size) {
    values.push("");
  }
}

function readonlyArrayEquals(left: readonly string[], right: readonly string[]): boolean {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}
