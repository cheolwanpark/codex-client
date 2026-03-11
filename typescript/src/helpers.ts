import type {
  AskForApproval,
  ClientInfo,
  CommandExecutionRequestApprovalResponse,
  DynamicToolCallOutputContentItem,
  DynamicToolCallResponse,
  FileChangeRequestApprovalResponse,
  Personality,
  SandboxMode,
  SandboxPolicy,
  ServiceTier,
  TextUserInput,
  ThreadStartParams,
  ToolRequestUserInputResponse,
} from "./generated.js";
import type { JSONValue } from "./messages.js";
import type { TurnOptions } from "./runtime.js";

export interface ClientInfoOptions {
  title?: string | null;
}

export interface ThreadParamsOptions {
  approvalPolicy?: AskForApproval | null;
  baseInstructions?: string | null;
  config?: Record<string, JSONValue> | null;
  cwd?: string | null;
  developerInstructions?: string | null;
  ephemeral?: boolean;
  model?: string | null;
  modelProvider?: string | null;
  personality?: Personality | null;
  sandbox?: SandboxMode | null;
  serviceName?: string | null;
  serviceTier?: ServiceTier | null;
}

export interface TurnOptionsInput {
  approvalPolicy?: AskForApproval | null;
  cwd?: string | null;
  effort?: TurnOptions["effort"];
  model?: string | null;
  outputSchema?: JSONValue;
  personality?: Personality | null;
  sandboxPolicy?: SandboxPolicy | null;
  serviceTier?: ServiceTier | null;
  summary?: TurnOptions["summary"];
}

export function clientInfo(
  name: string,
  version: string,
  options: ClientInfoOptions = {},
): ClientInfo {
  const payload: ClientInfo = { name, version };
  if (options.title !== undefined) {
    payload.title = options.title;
  }
  return payload;
}

export function textInput(text: string): TextUserInput {
  return { text, type: "text" };
}

export function threadParams(options: ThreadParamsOptions = {}): ThreadStartParams {
  const payload: ThreadStartParams = { ephemeral: options.ephemeral ?? true };
  if (options.approvalPolicy !== undefined) {
    payload.approvalPolicy = options.approvalPolicy;
  }
  if (options.baseInstructions !== undefined) {
    payload.baseInstructions = options.baseInstructions;
  }
  if (options.config !== undefined) {
    payload.config = options.config;
  }
  if (options.cwd !== undefined) {
    payload.cwd = options.cwd;
  }
  if (options.developerInstructions !== undefined) {
    payload.developerInstructions = options.developerInstructions;
  }
  if (options.model !== undefined) {
    payload.model = options.model;
  }
  if (options.modelProvider !== undefined) {
    payload.modelProvider = options.modelProvider;
  }
  if (options.personality !== undefined) {
    payload.personality = options.personality;
  }
  if (options.sandbox !== undefined) {
    payload.sandbox = options.sandbox;
  }
  if (options.serviceName !== undefined) {
    payload.serviceName = options.serviceName;
  }
  if (options.serviceTier !== undefined) {
    payload.serviceTier = options.serviceTier;
  }
  return payload;
}

export function turnOptions(options: TurnOptionsInput = {}): TurnOptions {
  const payload: TurnOptions = {};
  if (options.approvalPolicy !== undefined) {
    payload.approvalPolicy = options.approvalPolicy;
  }
  if (options.cwd !== undefined) {
    payload.cwd = options.cwd;
  }
  if (options.effort !== undefined) {
    payload.effort = options.effort;
  }
  if (options.model !== undefined) {
    payload.model = options.model;
  }
  if (options.outputSchema !== undefined) {
    payload.outputSchema = options.outputSchema;
  }
  if (options.personality !== undefined) {
    payload.personality = options.personality;
  }
  if (options.sandboxPolicy !== undefined) {
    payload.sandboxPolicy = options.sandboxPolicy;
  }
  if (options.serviceTier !== undefined) {
    payload.serviceTier = options.serviceTier;
  }
  if (options.summary !== undefined) {
    payload.summary = options.summary;
  }
  return payload;
}

export function approveCommand(): CommandExecutionRequestApprovalResponse {
  return { decision: "accept" };
}

export function declineCommand(): CommandExecutionRequestApprovalResponse {
  return { decision: "decline" };
}

export function approveFileChange(): FileChangeRequestApprovalResponse {
  return { decision: "accept" };
}

export function declineFileChange(): FileChangeRequestApprovalResponse {
  return { decision: "decline" };
}

export function approveFileChangeForSession(): FileChangeRequestApprovalResponse {
  return { decision: "acceptForSession" };
}

export function toolAnswers(
  answersByQuestion: Readonly<Record<string, readonly string[]>>,
): ToolRequestUserInputResponse {
  return {
    answers: Object.fromEntries(
      Object.entries(answersByQuestion).map(([questionId, answers]) => [
        questionId,
        { answers: [...answers] },
      ]),
    ),
  };
}

export function toolCallSuccess(
  contentItems: readonly DynamicToolCallOutputContentItem[] = [],
): DynamicToolCallResponse {
  return { contentItems: [...contentItems], success: true };
}

export function toolCallFailure(
  contentItems: readonly DynamicToolCallOutputContentItem[] = [],
): DynamicToolCallResponse {
  return { contentItems: [...contentItems], success: false };
}
