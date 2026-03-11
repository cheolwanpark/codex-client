/* Auto-generated protocol types and method registries. */

import type { JSONValue } from "./messages.js";

export interface AccountLoginCompletedNotification {
  error?: string | null;
  loginId?: string | null;
  success: boolean;
}

export interface CreditsSnapshot {
  balance?: string | null;
  hasCredits: boolean;
  unlimited: boolean;
}

export type PlanType = "free" | "go" | "plus" | "pro" | "team" | "business" | "enterprise" | "edu" | "unknown";

export interface RateLimitSnapshot {
  credits?: CreditsSnapshot | null;
  limitId?: string | null;
  limitName?: string | null;
  planType?: PlanType | null;
  primary?: RateLimitWindow | null;
  secondary?: RateLimitWindow | null;
}

export interface RateLimitWindow {
  resetsAt?: number | null;
  usedPercent: number;
  windowDurationMins?: number | null;
}

export interface AccountRateLimitsUpdatedNotification {
  rateLimits: RateLimitSnapshot;
}

export type AuthMode = "apikey" | "chatgpt" | "chatgptAuthTokens";

export interface AccountUpdatedNotification {
  authMode?: AuthMode | null;
  planType?: PlanType | null;
}

export interface AgentMessageDeltaNotification {
  delta: string;
  itemId: string;
  threadId: string;
  turnId: string;
}

export interface AppBranding {
  category?: string | null;
  developer?: string | null;
  isDiscoverableApp: boolean;
  privacyPolicy?: string | null;
  termsOfService?: string | null;
  website?: string | null;
}

export interface AppInfo {
  appMetadata?: AppMetadata | null;
  branding?: AppBranding | null;
  description?: string | null;
  distributionChannel?: string | null;
  id: string;
  installUrl?: string | null;
  isAccessible?: boolean;
  isEnabled?: boolean;
  labels?: Record<string, string> | null;
  logoUrl?: string | null;
  logoUrlDark?: string | null;
  name: string;
}

export interface AppMetadata {
  categories?: Array<string> | null;
  developer?: string | null;
  firstPartyRequiresInstall?: boolean | null;
  firstPartyType?: string | null;
  review?: AppReview | null;
  screenshots?: Array<AppScreenshot> | null;
  seoDescription?: string | null;
  showInComposerWhenUnlinked?: boolean | null;
  subCategories?: Array<string> | null;
  version?: string | null;
  versionId?: string | null;
  versionNotes?: string | null;
}

export interface AppReview {
  status: string;
}

export interface AppScreenshot {
  fileId?: string | null;
  url?: string | null;
  userPrompt: string;
}

export interface AppListUpdatedNotification {
  data: Array<AppInfo>;
}

export interface AddFileChange {
  content: string;
  type: "add";
}

export interface DeleteFileChange {
  content: string;
  type: "delete";
}

export interface UpdateFileChange {
  move_path?: string | null;
  type: "update";
  unified_diff: string;
}

export type FileChange = AddFileChange | DeleteFileChange | UpdateFileChange;

export type ThreadId = string;

export interface ApplyPatchApprovalParams {
  callId: string;
  conversationId: ThreadId;
  fileChanges: Record<string, FileChange>;
  grantRoot?: string | null;
  reason?: string | null;
}

export interface NetworkPolicyAmendment {
  action: NetworkPolicyRuleAction;
  host: string;
}

export type NetworkPolicyRuleAction = "allow" | "deny";

export interface ApprovedExecpolicyAmendmentReviewDecisionApprovedExecpolicyAmendmentVariant {
  proposed_execpolicy_amendment: Array<string>;
}

export interface ApprovedExecpolicyAmendmentReviewDecision {
  approved_execpolicy_amendment: ApprovedExecpolicyAmendmentReviewDecisionApprovedExecpolicyAmendmentVariant;
}

export interface NetworkPolicyAmendmentReviewDecisionNetworkPolicyAmendmentVariant {
  network_policy_amendment: NetworkPolicyAmendment;
}

export interface NetworkPolicyAmendmentReviewDecision {
  network_policy_amendment: NetworkPolicyAmendmentReviewDecisionNetworkPolicyAmendmentVariant;
}

export type ReviewDecision = "approved" | ApprovedExecpolicyAmendmentReviewDecision | "approved_for_session" | NetworkPolicyAmendmentReviewDecision | "denied" | "abort";

export interface ApplyPatchApprovalResponse {
  decision: ReviewDecision;
}

export interface AppsListParams {
  cursor?: string | null;
  forceRefetch?: boolean;
  limit?: number | null;
  threadId?: string | null;
}

export interface AppsListResponse {
  data: Array<AppInfo>;
  nextCursor?: string | null;
}

export interface CancelLoginAccountParams {
  loginId: string;
}

export type CancelLoginAccountStatus = "canceled" | "notFound";

export interface CancelLoginAccountResponse {
  status: CancelLoginAccountStatus;
}

export type ChatgptAuthTokensRefreshReason = "unauthorized";

export interface ChatgptAuthTokensRefreshParams {
  previousAccountId?: string | null;
  reason: ChatgptAuthTokensRefreshReason;
}

export interface ChatgptAuthTokensRefreshResponse {
  accessToken: string;
  chatgptAccountId: string;
  chatgptPlanType?: string | null;
}

export type AbsolutePathBuf = string;

export type NetworkAccess = "restricted" | "enabled";

export interface RestrictedReadOnlyAccess {
  includePlatformDefaults?: boolean;
  readableRoots?: Array<AbsolutePathBuf>;
  type: "restricted";
}

export interface FullAccessReadOnlyAccess {
  type: "fullAccess";
}

export type ReadOnlyAccess = RestrictedReadOnlyAccess | FullAccessReadOnlyAccess;

export interface DangerFullAccessSandboxPolicy {
  type: "dangerFullAccess";
}

export interface ReadOnlySandboxPolicy {
  access?: ReadOnlyAccess;
  networkAccess?: boolean;
  type: "readOnly";
}

export interface ExternalSandboxSandboxPolicy {
  networkAccess?: NetworkAccess;
  type: "externalSandbox";
}

export interface WorkspaceWriteSandboxPolicy {
  excludeSlashTmp?: boolean;
  excludeTmpdirEnvVar?: boolean;
  networkAccess?: boolean;
  readOnlyAccess?: ReadOnlyAccess;
  type: "workspaceWrite";
  writableRoots?: Array<AbsolutePathBuf>;
}

export type SandboxPolicy = DangerFullAccessSandboxPolicy | ReadOnlySandboxPolicy | ExternalSandboxSandboxPolicy | WorkspaceWriteSandboxPolicy;

export interface CommandExecParams {
  command: Array<string>;
  cwd?: string | null;
  sandboxPolicy?: SandboxPolicy | null;
  timeoutMs?: number | null;
}

export interface CommandExecResponse {
  exitCode: number;
  stderr: string;
  stdout: string;
}

export interface CommandExecutionOutputDeltaNotification {
  delta: string;
  itemId: string;
  threadId: string;
  turnId: string;
}

export interface AdditionalFileSystemPermissions {
  read?: Array<AbsolutePathBuf> | null;
  write?: Array<AbsolutePathBuf> | null;
}

export interface AdditionalMacOsPermissions {
  accessibility?: boolean | null;
  automations?: MacOsAutomationValue | null;
  calendar?: boolean | null;
  preferences?: MacOsPreferencesValue | null;
}

export interface AdditionalNetworkPermissions {
  enabled?: boolean | null;
}

export interface AdditionalPermissionProfile {
  fileSystem?: AdditionalFileSystemPermissions | null;
  macos?: AdditionalMacOsPermissions | null;
  network?: AdditionalNetworkPermissions | null;
}

export interface ReadCommandAction {
  command: string;
  name: string;
  path: string;
  type: "read";
}

export interface ListFilesCommandAction {
  command: string;
  path?: string | null;
  type: "listFiles";
}

export interface SearchCommandAction {
  command: string;
  path?: string | null;
  query?: string | null;
  type: "search";
}

export interface UnknownCommandAction {
  command: string;
  type: "unknown";
}

export type CommandAction = ReadCommandAction | ListFilesCommandAction | SearchCommandAction | UnknownCommandAction;

export interface AcceptWithExecpolicyAmendmentCommandExecutionApprovalDecisionAcceptWithExecpolicyAmendmentVariant {
  execpolicy_amendment: Array<string>;
}

export interface AcceptWithExecpolicyAmendmentCommandExecutionApprovalDecision {
  acceptWithExecpolicyAmendment: AcceptWithExecpolicyAmendmentCommandExecutionApprovalDecisionAcceptWithExecpolicyAmendmentVariant;
}

export interface ApplyNetworkPolicyAmendmentCommandExecutionApprovalDecisionApplyNetworkPolicyAmendmentVariant {
  network_policy_amendment: NetworkPolicyAmendment;
}

export interface ApplyNetworkPolicyAmendmentCommandExecutionApprovalDecision {
  applyNetworkPolicyAmendment: ApplyNetworkPolicyAmendmentCommandExecutionApprovalDecisionApplyNetworkPolicyAmendmentVariant;
}

export type CommandExecutionApprovalDecision = "accept" | "acceptForSession" | AcceptWithExecpolicyAmendmentCommandExecutionApprovalDecision | ApplyNetworkPolicyAmendmentCommandExecutionApprovalDecision | "decline" | "cancel";

export type MacOsAutomationValue = boolean | Array<string>;

export type MacOsPreferencesValue = boolean | string;

export interface NetworkApprovalContext {
  host: string;
  protocol: NetworkApprovalProtocol;
}

export type NetworkApprovalProtocol = "http" | "https" | "socks5Tcp" | "socks5Udp";

export interface CommandExecutionRequestApprovalParams {
  turnId: string;
  approvalId?: string | null;
  threadId: string;
  command?: string | null;
  commandActions?: Array<CommandAction> | null;
  cwd?: string | null;
  itemId: string;
  networkApprovalContext?: NetworkApprovalContext | null;
  proposedExecpolicyAmendment?: Array<string> | null;
  proposedNetworkPolicyAmendments?: Array<NetworkPolicyAmendment> | null;
  reason?: string | null;
}

export interface CommandExecutionRequestApprovalResponse {
  decision: CommandExecutionApprovalDecision;
}

export interface ConfigEdit {
  keyPath: string;
  mergeStrategy: MergeStrategy;
  value: JSONValue;
}

export type MergeStrategy = "replace" | "upsert";

export interface ConfigBatchWriteParams {
  edits: Array<ConfigEdit>;
  expectedVersion?: string | null;
  filePath?: string | null;
}

export interface ConfigReadParams {
  cwd?: string | null;
  includeLayers?: boolean;
}

export type AnalyticsConfig = Record<string, JSONValue>;

export interface AppConfig {
  default_tools_approval_mode?: AppToolApproval | null;
  default_tools_enabled?: boolean | null;
  destructive_enabled?: boolean | null;
  enabled?: boolean;
  open_world_enabled?: boolean | null;
  tools?: AppToolsConfig | null;
}

export type AppToolApproval = "auto" | "prompt" | "approve";

export interface AppToolConfig {
  approval_mode?: AppToolApproval | null;
  enabled?: boolean | null;
}

export type AppToolsConfig = Record<string, JSONValue>;

export interface AppsConfig {
  _default?: AppsDefaultConfig | null;
}

export interface AppsDefaultConfig {
  destructive_enabled?: boolean;
  enabled?: boolean;
  open_world_enabled?: boolean;
}

export interface RejectAskForApprovalRejectVariant {
  mcp_elicitations: boolean;
  rules: boolean;
  sandbox_approval: boolean;
}

export interface RejectAskForApproval {
  reject: RejectAskForApprovalRejectVariant;
}

export type AskForApproval = "untrusted" | "on-failure" | "on-request" | "never" | RejectAskForApproval;

export type Config = Record<string, JSONValue>;

export interface ConfigLayer {
  config: JSONValue;
  disabledReason?: string | null;
  name: ConfigLayerSource;
  version: string;
}

export interface ConfigLayerMetadata {
  name: ConfigLayerSource;
  version: string;
}

export interface MdmConfigLayerSource {
  domain: string;
  key: string;
  type: "mdm";
}

export interface SystemConfigLayerSource {
  file: AbsolutePathBuf;
  type: "system";
}

export interface UserConfigLayerSource {
  file: AbsolutePathBuf;
  type: "user";
}

export interface ProjectConfigLayerSource {
  dotCodexFolder: AbsolutePathBuf;
  type: "project";
}

export interface SessionFlagsConfigLayerSource {
  type: "sessionFlags";
}

export interface LegacyManagedConfigTomlFromFileConfigLayerSource {
  file: AbsolutePathBuf;
  type: "legacyManagedConfigTomlFromFile";
}

export interface LegacyManagedConfigTomlFromMdmConfigLayerSource {
  type: "legacyManagedConfigTomlFromMdm";
}

export type ConfigLayerSource = MdmConfigLayerSource | SystemConfigLayerSource | UserConfigLayerSource | ProjectConfigLayerSource | SessionFlagsConfigLayerSource | LegacyManagedConfigTomlFromFileConfigLayerSource | LegacyManagedConfigTomlFromMdmConfigLayerSource;

export type ForcedLoginMethod = "chatgpt" | "api";

export type ProfileV2 = Record<string, JSONValue>;

export type ReasoningEffort = "none" | "minimal" | "low" | "medium" | "high" | "xhigh";

export type ReasoningSummary = "auto" | "concise" | "detailed" | "none";

export type SandboxMode = "read-only" | "workspace-write" | "danger-full-access";

export interface SandboxWorkspaceWrite {
  exclude_slash_tmp?: boolean;
  exclude_tmpdir_env_var?: boolean;
  network_access?: boolean;
  writable_roots?: Array<string>;
}

export type ServiceTier = "fast" | "flex";

export interface ToolsV2 {
  view_image?: boolean | null;
  web_search?: boolean | null;
}

export type Verbosity = "low" | "medium" | "high";

export type WebSearchMode = "disabled" | "cached" | "live";

export interface ConfigReadResponse {
  config: Config;
  layers?: Array<ConfigLayer> | null;
  origins: Record<string, ConfigLayerMetadata>;
}

export interface ConfigRequirements {
  allowedApprovalPolicies?: Array<AskForApproval> | null;
  allowedSandboxModes?: Array<SandboxMode> | null;
  allowedWebSearchModes?: Array<WebSearchMode> | null;
  enforceResidency?: ResidencyRequirement | null;
  featureRequirements?: Record<string, boolean> | null;
}

export interface NetworkRequirements {
  allowLocalBinding?: boolean | null;
  allowUnixSockets?: Array<string> | null;
  allowUpstreamProxy?: boolean | null;
  allowedDomains?: Array<string> | null;
  dangerouslyAllowAllUnixSockets?: boolean | null;
  dangerouslyAllowNonLoopbackAdmin?: boolean | null;
  dangerouslyAllowNonLoopbackProxy?: boolean | null;
  deniedDomains?: Array<string> | null;
  enabled?: boolean | null;
  httpPort?: number | null;
  socksPort?: number | null;
}

export type ResidencyRequirement = "us";

export interface ConfigRequirementsReadResponse {
  requirements?: ConfigRequirements | null;
}

export interface ConfigValueWriteParams {
  expectedVersion?: string | null;
  filePath?: string | null;
  keyPath: string;
  mergeStrategy: MergeStrategy;
  value: JSONValue;
}

export interface TextPosition {
  column: number;
  line: number;
}

export interface TextRange {
  end: TextPosition;
  start: TextPosition;
}

export interface ConfigWarningNotification {
  details?: string | null;
  path?: string | null;
  range?: TextRange | null;
  summary: string;
}

export interface OverriddenMetadata {
  effectiveValue: JSONValue;
  message: string;
  overridingLayer: ConfigLayerMetadata;
}

export type WriteStatus = "ok" | "okOverridden";

export interface ConfigWriteResponse {
  filePath: AbsolutePathBuf;
  overriddenMetadata?: OverriddenMetadata | null;
  status: WriteStatus;
  version: string;
}

export interface ContextCompactedNotification {
  threadId: string;
  turnId: string;
}

export interface DeprecationNoticeNotification {
  details?: string | null;
  summary: string;
}

export interface DynamicToolCallParams {
  arguments: JSONValue;
  callId: string;
  threadId: string;
  tool: string;
  turnId: string;
}

export interface InputTextDynamicToolCallOutputContentItem {
  text: string;
  type: "inputText";
}

export interface InputImageDynamicToolCallOutputContentItem {
  imageUrl: string;
  type: "inputImage";
}

export type DynamicToolCallOutputContentItem = InputTextDynamicToolCallOutputContentItem | InputImageDynamicToolCallOutputContentItem;

export interface DynamicToolCallResponse {
  contentItems: Array<DynamicToolCallOutputContentItem>;
  success: boolean;
}

export interface HttpConnectionFailedCodexErrorInfoHttpConnectionFailedVariant {
  httpStatusCode?: number | null;
}

export interface HttpConnectionFailedCodexErrorInfo {
  httpConnectionFailed: HttpConnectionFailedCodexErrorInfoHttpConnectionFailedVariant;
}

export interface ResponseStreamConnectionFailedCodexErrorInfoResponseStreamConnectionFailedVariant {
  httpStatusCode?: number | null;
}

export interface ResponseStreamConnectionFailedCodexErrorInfo {
  responseStreamConnectionFailed: ResponseStreamConnectionFailedCodexErrorInfoResponseStreamConnectionFailedVariant;
}

export interface ResponseStreamDisconnectedCodexErrorInfoResponseStreamDisconnectedVariant {
  httpStatusCode?: number | null;
}

export interface ResponseStreamDisconnectedCodexErrorInfo {
  responseStreamDisconnected: ResponseStreamDisconnectedCodexErrorInfoResponseStreamDisconnectedVariant;
}

export interface ResponseTooManyFailedAttemptsCodexErrorInfoResponseTooManyFailedAttemptsVariant {
  httpStatusCode?: number | null;
}

export interface ResponseTooManyFailedAttemptsCodexErrorInfo {
  responseTooManyFailedAttempts: ResponseTooManyFailedAttemptsCodexErrorInfoResponseTooManyFailedAttemptsVariant;
}

export type CodexErrorInfo = "contextWindowExceeded" | "usageLimitExceeded" | "serverOverloaded" | "internalServerError" | "unauthorized" | "badRequest" | "threadRollbackFailed" | "sandboxError" | "other" | HttpConnectionFailedCodexErrorInfo | ResponseStreamConnectionFailedCodexErrorInfo | ResponseStreamDisconnectedCodexErrorInfo | ResponseTooManyFailedAttemptsCodexErrorInfo;

export interface TurnError {
  additionalDetails?: string | null;
  codexErrorInfo?: CodexErrorInfo | null;
  message: string;
}

export interface ErrorNotification {
  error: TurnError;
  threadId: string;
  turnId: string;
  willRetry: boolean;
}

export interface TextAgentMessageContent {
  text: string;
  type: "Text";
}

export type AgentMessageContent = TextAgentMessageContent;

export interface CompletedAgentStatus {
  completed: string | null;
}

export interface ErroredAgentStatus {
  errored: string;
}

export type AgentStatus = "pending_init" | "running" | CompletedAgentStatus | ErroredAgentStatus | "shutdown" | "not_found";

export interface ByteRange {
  end: number;
  start: number;
}

export interface CallToolResult {
  _meta?: JSONValue;
  content: Array<JSONValue>;
  isError?: boolean | null;
  structuredContent?: JSONValue;
}

export interface CollabAgentRef {
  agent_nickname?: string | null;
  agent_role?: string | null;
  thread_id: ThreadId;
}

export interface CollabAgentStatusEntry {
  agent_nickname?: string | null;
  agent_role?: string | null;
  status: AgentStatus;
  thread_id: ThreadId;
}

export interface InputTextContentItem {
  text: string;
  type: "input_text";
}

export interface InputImageContentItem {
  image_url: string;
  type: "input_image";
}

export interface OutputTextContentItem {
  text: string;
  type: "output_text";
}

export type ContentItem = InputTextContentItem | InputImageContentItem | OutputTextContentItem;

export interface CustomPrompt {
  argument_hint?: string | null;
  content: string;
  description?: string | null;
  name: string;
  path: string;
}

export interface Duration {
  nanos: number;
  secs: number;
}

export interface ElicitationRequestVariant {
  message: string;
  mode: "form";
  requested_schema: JSONValue;
}

export interface ElicitationRequestVariant2 {
  elicitation_id: string;
  message: string;
  mode: "url";
  url: string;
}

export type ElicitationRequest = ElicitationRequestVariant | ElicitationRequestVariant2;

export interface ErrorEventMsg {
  codex_error_info?: CodexErrorInfo | null;
  message: string;
  type: "error";
}

export interface WarningEventMsg {
  message: string;
  type: "warning";
}

export interface RealtimeConversationStartedEventMsg {
  session_id?: string | null;
  type: "realtime_conversation_started";
}

export interface RealtimeConversationRealtimeEventMsg {
  payload: RealtimeEvent;
  type: "realtime_conversation_realtime";
}

export interface RealtimeConversationClosedEventMsg {
  reason?: string | null;
  type: "realtime_conversation_closed";
}

export interface ModelRerouteEventMsg {
  from_model: string;
  reason: ModelRerouteReason;
  to_model: string;
  type: "model_reroute";
}

export interface ContextCompactedEventMsg {
  type: "context_compacted";
}

export interface ThreadRolledBackEventMsg {
  num_turns: number;
  type: "thread_rolled_back";
}

export interface TaskStartedEventMsg {
  collaboration_mode_kind?: ModeKind;
  model_context_window?: number | null;
  turn_id: string;
  type: "task_started";
}

export interface TaskCompleteEventMsg {
  last_agent_message?: string | null;
  turn_id: string;
  type: "task_complete";
}

export interface TokenCountEventMsg {
  info?: TokenUsageInfo | null;
  rate_limits?: RateLimitSnapshot | null;
  type: "token_count";
}

export interface AgentMessageEventMsg {
  message: string;
  phase?: MessagePhase | null;
  type: "agent_message";
}

export interface UserMessageEventMsg {
  images?: Array<string> | null;
  local_images?: Array<string>;
  message: string;
  text_elements?: Array<TextElement>;
  type: "user_message";
}

export interface AgentMessageDeltaEventMsg {
  delta: string;
  type: "agent_message_delta";
}

export interface AgentReasoningEventMsg {
  text: string;
  type: "agent_reasoning";
}

export interface AgentReasoningDeltaEventMsg {
  delta: string;
  type: "agent_reasoning_delta";
}

export interface AgentReasoningRawContentEventMsg {
  text: string;
  type: "agent_reasoning_raw_content";
}

export interface AgentReasoningRawContentDeltaEventMsg {
  delta: string;
  type: "agent_reasoning_raw_content_delta";
}

export interface AgentReasoningSectionBreakEventMsg {
  item_id?: string;
  summary_index?: number;
  type: "agent_reasoning_section_break";
}

export interface SessionConfiguredEventMsg {
  approval_policy: AskForApproval;
  cwd: string;
  forked_from_id?: ThreadId | null;
  history_entry_count: number;
  history_log_id: number;
  initial_messages?: Array<EventMsg> | null;
  model: string;
  model_provider_id: string;
  network_proxy?: SessionNetworkProxyRuntime | null;
  reasoning_effort?: ReasoningEffort | null;
  rollout_path?: string | null;
  sandbox_policy: SandboxPolicy;
  service_tier?: ServiceTier | null;
  session_id: ThreadId;
  thread_name?: string | null;
  type: "session_configured";
}

export interface ThreadNameUpdatedEventMsg {
  thread_id: ThreadId;
  thread_name?: string | null;
  type: "thread_name_updated";
}

export interface McpStartupUpdateEventMsg {
  server: string;
  status: McpStartupStatus;
  type: "mcp_startup_update";
}

export interface McpStartupCompleteEventMsg {
  cancelled: Array<string>;
  failed: Array<McpStartupFailure>;
  ready: Array<string>;
  type: "mcp_startup_complete";
}

export interface McpToolCallBeginEventMsg {
  call_id: string;
  invocation: McpInvocation;
  type: "mcp_tool_call_begin";
}

export interface McpToolCallEndEventMsg {
  call_id: string;
  duration: Duration;
  invocation: McpInvocation;
  result: ResultOfCallToolResultOrString;
  type: "mcp_tool_call_end";
}

export interface WebSearchBeginEventMsg {
  call_id: string;
  type: "web_search_begin";
}

export interface WebSearchEndEventMsg {
  action: WebSearchAction;
  call_id: string;
  query: string;
  type: "web_search_end";
}

export interface ImageGenerationBeginEventMsg {
  call_id: string;
  type: "image_generation_begin";
}

export interface ImageGenerationEndEventMsg {
  call_id: string;
  result: string;
  revised_prompt?: string | null;
  status: string;
  type: "image_generation_end";
}

export interface ExecCommandBeginEventMsg {
  call_id: string;
  command: Array<string>;
  cwd: string;
  interaction_input?: string | null;
  parsed_cmd: Array<ParsedCommand>;
  process_id?: string | null;
  source?: ExecCommandSource;
  turn_id: string;
  type: "exec_command_begin";
}

export interface ExecCommandOutputDeltaEventMsg {
  call_id: string;
  chunk: string;
  stream: ExecOutputStream;
  type: "exec_command_output_delta";
}

export interface TerminalInteractionEventMsg {
  call_id: string;
  process_id: string;
  stdin: string;
  type: "terminal_interaction";
}

export interface ExecCommandEndEventMsg {
  aggregated_output?: string;
  call_id: string;
  command: Array<string>;
  cwd: string;
  duration: Duration;
  exit_code: number;
  formatted_output: string;
  interaction_input?: string | null;
  parsed_cmd: Array<ParsedCommand>;
  process_id?: string | null;
  source?: ExecCommandSource;
  status: ExecCommandStatus;
  stderr: string;
  stdout: string;
  turn_id: string;
  type: "exec_command_end";
}

export interface ViewImageToolCallEventMsg {
  call_id: string;
  path: string;
  type: "view_image_tool_call";
}

export interface ExecApprovalRequestEventMsg {
  additional_permissions?: PermissionProfile | null;
  approval_id?: string | null;
  available_decisions?: Array<ReviewDecision> | null;
  call_id: string;
  command: Array<string>;
  cwd: string;
  network_approval_context?: NetworkApprovalContext | null;
  parsed_cmd: Array<ParsedCommand>;
  proposed_execpolicy_amendment?: Array<string> | null;
  proposed_network_policy_amendments?: Array<NetworkPolicyAmendment> | null;
  reason?: string | null;
  turn_id?: string;
  type: "exec_approval_request";
}

export interface RequestUserInputEventMsg {
  call_id: string;
  questions: Array<RequestUserInputQuestion>;
  turn_id?: string;
  type: "request_user_input";
}

export interface DynamicToolCallRequestEventMsg {
  arguments: JSONValue;
  callId: string;
  tool: string;
  turnId: string;
  type: "dynamic_tool_call_request";
}

export interface DynamicToolCallResponseEventMsg {
  arguments: JSONValue;
  call_id: string;
  content_items: Array<DynamicToolCallOutputContentItem>;
  duration: Duration;
  error?: string | null;
  success: boolean;
  tool: string;
  turn_id: string;
  type: "dynamic_tool_call_response";
}

export interface ElicitationRequestEventMsg {
  id: RequestId;
  request: ElicitationRequest;
  server_name: string;
  type: "elicitation_request";
}

export interface ApplyPatchApprovalRequestEventMsg {
  call_id: string;
  changes: Record<string, FileChange>;
  grant_root?: string | null;
  reason?: string | null;
  turn_id?: string;
  type: "apply_patch_approval_request";
}

export interface DeprecationNoticeEventMsg {
  details?: string | null;
  summary: string;
  type: "deprecation_notice";
}

export interface BackgroundEventEventMsg {
  message: string;
  type: "background_event";
}

export interface UndoStartedEventMsg {
  message?: string | null;
  type: "undo_started";
}

export interface UndoCompletedEventMsg {
  message?: string | null;
  success: boolean;
  type: "undo_completed";
}

export interface StreamErrorEventMsg {
  additional_details?: string | null;
  codex_error_info?: CodexErrorInfo | null;
  message: string;
  type: "stream_error";
}

export interface PatchApplyBeginEventMsg {
  auto_approved: boolean;
  call_id: string;
  changes: Record<string, FileChange>;
  turn_id?: string;
  type: "patch_apply_begin";
}

export interface PatchApplyEndEventMsg {
  call_id: string;
  changes?: Record<string, FileChange>;
  status: PatchApplyStatus;
  stderr: string;
  stdout: string;
  success: boolean;
  turn_id?: string;
  type: "patch_apply_end";
}

export interface TurnDiffEventMsg {
  type: "turn_diff";
  unified_diff: string;
}

export interface GetHistoryEntryResponseEventMsg {
  entry?: HistoryEntry | null;
  log_id: number;
  offset: number;
  type: "get_history_entry_response";
}

export interface McpListToolsResponseEventMsg {
  auth_statuses: Record<string, McpAuthStatus>;
  resource_templates: Record<string, Array<ResourceTemplate>>;
  resources: Record<string, Array<Resource>>;
  tools: Record<string, Tool>;
  type: "mcp_list_tools_response";
}

export interface ListCustomPromptsResponseEventMsg {
  custom_prompts: Array<CustomPrompt>;
  type: "list_custom_prompts_response";
}

export interface ListSkillsResponseEventMsg {
  skills: Array<SkillsListEntry>;
  type: "list_skills_response";
}

export interface ListRemoteSkillsResponseEventMsg {
  skills: Array<RemoteSkillSummary>;
  type: "list_remote_skills_response";
}

export interface RemoteSkillDownloadedEventMsg {
  id: string;
  name: string;
  path: string;
  type: "remote_skill_downloaded";
}

export interface SkillsUpdateAvailableEventMsg {
  type: "skills_update_available";
}

export interface PlanUpdateEventMsg {
  explanation?: string | null;
  plan: Array<PlanItemArg>;
  type: "plan_update";
}

export interface TurnAbortedEventMsg {
  reason: TurnAbortReason;
  turn_id?: string | null;
  type: "turn_aborted";
}

export interface ShutdownCompleteEventMsg {
  type: "shutdown_complete";
}

export interface EnteredReviewModeEventMsg {
  target: ReviewTarget;
  type: "entered_review_mode";
  user_facing_hint?: string | null;
}

export interface ExitedReviewModeEventMsg {
  review_output?: ReviewOutputEvent | null;
  type: "exited_review_mode";
}

export interface RawResponseItemEventMsg {
  item: ResponseItem;
  type: "raw_response_item";
}

export interface ItemStartedEventMsg {
  item: TurnItem;
  thread_id: ThreadId;
  turn_id: string;
  type: "item_started";
}

export interface ItemCompletedEventMsg {
  item: TurnItem;
  thread_id: ThreadId;
  turn_id: string;
  type: "item_completed";
}

export interface AgentMessageContentDeltaEventMsg {
  delta: string;
  item_id: string;
  thread_id: string;
  turn_id: string;
  type: "agent_message_content_delta";
}

export interface PlanDeltaEventMsg {
  delta: string;
  item_id: string;
  thread_id: string;
  turn_id: string;
  type: "plan_delta";
}

export interface ReasoningContentDeltaEventMsg {
  delta: string;
  item_id: string;
  summary_index?: number;
  thread_id: string;
  turn_id: string;
  type: "reasoning_content_delta";
}

export interface ReasoningRawContentDeltaEventMsg {
  content_index?: number;
  delta: string;
  item_id: string;
  thread_id: string;
  turn_id: string;
  type: "reasoning_raw_content_delta";
}

export interface CollabAgentSpawnBeginEventMsg {
  call_id: string;
  prompt: string;
  sender_thread_id: ThreadId;
  type: "collab_agent_spawn_begin";
}

export interface CollabAgentSpawnEndEventMsg {
  call_id: string;
  new_agent_nickname?: string | null;
  new_agent_role?: string | null;
  new_thread_id?: ThreadId | null;
  prompt: string;
  sender_thread_id: ThreadId;
  status: AgentStatus;
  type: "collab_agent_spawn_end";
}

export interface CollabAgentInteractionBeginEventMsg {
  call_id: string;
  prompt: string;
  receiver_thread_id: ThreadId;
  sender_thread_id: ThreadId;
  type: "collab_agent_interaction_begin";
}

export interface CollabAgentInteractionEndEventMsg {
  call_id: string;
  prompt: string;
  receiver_agent_nickname?: string | null;
  receiver_agent_role?: string | null;
  receiver_thread_id: ThreadId;
  sender_thread_id: ThreadId;
  status: AgentStatus;
  type: "collab_agent_interaction_end";
}

export interface CollabWaitingBeginEventMsg {
  call_id: string;
  receiver_agents?: Array<CollabAgentRef>;
  receiver_thread_ids: Array<ThreadId>;
  sender_thread_id: ThreadId;
  type: "collab_waiting_begin";
}

export interface CollabWaitingEndEventMsg {
  agent_statuses?: Array<CollabAgentStatusEntry>;
  call_id: string;
  sender_thread_id: ThreadId;
  statuses: Record<string, AgentStatus>;
  type: "collab_waiting_end";
}

export interface CollabCloseBeginEventMsg {
  call_id: string;
  receiver_thread_id: ThreadId;
  sender_thread_id: ThreadId;
  type: "collab_close_begin";
}

export interface CollabCloseEndEventMsg {
  call_id: string;
  receiver_agent_nickname?: string | null;
  receiver_agent_role?: string | null;
  receiver_thread_id: ThreadId;
  sender_thread_id: ThreadId;
  status: AgentStatus;
  type: "collab_close_end";
}

export interface CollabResumeBeginEventMsg {
  call_id: string;
  receiver_agent_nickname?: string | null;
  receiver_agent_role?: string | null;
  receiver_thread_id: ThreadId;
  sender_thread_id: ThreadId;
  type: "collab_resume_begin";
}

export interface CollabResumeEndEventMsg {
  call_id: string;
  receiver_agent_nickname?: string | null;
  receiver_agent_role?: string | null;
  receiver_thread_id: ThreadId;
  sender_thread_id: ThreadId;
  status: AgentStatus;
  type: "collab_resume_end";
}

export type EventMsg = ErrorEventMsg | WarningEventMsg | RealtimeConversationStartedEventMsg | RealtimeConversationRealtimeEventMsg | RealtimeConversationClosedEventMsg | ModelRerouteEventMsg | ContextCompactedEventMsg | ThreadRolledBackEventMsg | TaskStartedEventMsg | TaskCompleteEventMsg | TokenCountEventMsg | AgentMessageEventMsg | UserMessageEventMsg | AgentMessageDeltaEventMsg | AgentReasoningEventMsg | AgentReasoningDeltaEventMsg | AgentReasoningRawContentEventMsg | AgentReasoningRawContentDeltaEventMsg | AgentReasoningSectionBreakEventMsg | SessionConfiguredEventMsg | ThreadNameUpdatedEventMsg | McpStartupUpdateEventMsg | McpStartupCompleteEventMsg | McpToolCallBeginEventMsg | McpToolCallEndEventMsg | WebSearchBeginEventMsg | WebSearchEndEventMsg | ImageGenerationBeginEventMsg | ImageGenerationEndEventMsg | ExecCommandBeginEventMsg | ExecCommandOutputDeltaEventMsg | TerminalInteractionEventMsg | ExecCommandEndEventMsg | ViewImageToolCallEventMsg | ExecApprovalRequestEventMsg | RequestUserInputEventMsg | DynamicToolCallRequestEventMsg | DynamicToolCallResponseEventMsg | ElicitationRequestEventMsg | ApplyPatchApprovalRequestEventMsg | DeprecationNoticeEventMsg | BackgroundEventEventMsg | UndoStartedEventMsg | UndoCompletedEventMsg | StreamErrorEventMsg | PatchApplyBeginEventMsg | PatchApplyEndEventMsg | TurnDiffEventMsg | GetHistoryEntryResponseEventMsg | McpListToolsResponseEventMsg | ListCustomPromptsResponseEventMsg | ListSkillsResponseEventMsg | ListRemoteSkillsResponseEventMsg | RemoteSkillDownloadedEventMsg | SkillsUpdateAvailableEventMsg | PlanUpdateEventMsg | TurnAbortedEventMsg | ShutdownCompleteEventMsg | EnteredReviewModeEventMsg | ExitedReviewModeEventMsg | RawResponseItemEventMsg | ItemStartedEventMsg | ItemCompletedEventMsg | AgentMessageContentDeltaEventMsg | PlanDeltaEventMsg | ReasoningContentDeltaEventMsg | ReasoningRawContentDeltaEventMsg | CollabAgentSpawnBeginEventMsg | CollabAgentSpawnEndEventMsg | CollabAgentInteractionBeginEventMsg | CollabAgentInteractionEndEventMsg | CollabWaitingBeginEventMsg | CollabWaitingEndEventMsg | CollabCloseBeginEventMsg | CollabCloseEndEventMsg | CollabResumeBeginEventMsg | CollabResumeEndEventMsg;

export type ExecCommandSource = "agent" | "user_shell" | "unified_exec_startup" | "unified_exec_interaction";

export type ExecCommandStatus = "completed" | "failed" | "declined";

export type ExecOutputStream = "stdout" | "stderr";

export interface FileSystemPermissions {
  read?: Array<AbsolutePathBuf> | null;
  write?: Array<AbsolutePathBuf> | null;
}

export type FunctionCallOutputBody = string | Array<FunctionCallOutputContentItem>;

export interface InputTextFunctionCallOutputContentItem {
  text: string;
  type: "input_text";
}

export interface InputImageFunctionCallOutputContentItem {
  detail?: ImageDetail | null;
  image_url: string;
  type: "input_image";
}

export type FunctionCallOutputContentItem = InputTextFunctionCallOutputContentItem | InputImageFunctionCallOutputContentItem;

export interface FunctionCallOutputPayload {
  body: FunctionCallOutputBody;
  success?: boolean | null;
}

export interface GhostCommit {
  id: string;
  parent?: string | null;
  preexisting_untracked_dirs: Array<string>;
  preexisting_untracked_files: Array<string>;
}

export interface HistoryEntry {
  conversation_id: string;
  text: string;
  ts: number;
}

export type ImageDetail = "auto" | "low" | "high" | "original";

export interface ExecLocalShellAction {
  command: Array<string>;
  env?: Record<string, string> | null;
  timeout_ms?: number | null;
  type: "exec";
  user?: string | null;
  working_directory?: string | null;
}

export type LocalShellAction = ExecLocalShellAction;

export type LocalShellStatus = "completed" | "in_progress" | "incomplete";

export interface MacOsPermissions {
  accessibility?: boolean | null;
  automations?: MacOsAutomationValue | null;
  calendar?: boolean | null;
  preferences?: MacOsPreferencesValue | null;
}

export type McpAuthStatus = "unsupported" | "not_logged_in" | "bearer_token" | "o_auth";

export interface McpInvocation {
  arguments?: JSONValue;
  server: string;
  tool: string;
}

export interface McpStartupFailure {
  error: string;
  server: string;
}

export interface StartingMcpStartupStatus {
  state: "starting";
}

export interface ReadyMcpStartupStatus {
  state: "ready";
}

export interface McpStartupStatusVariant {
  error: string;
  state: "failed";
}

export interface CancelledMcpStartupStatus {
  state: "cancelled";
}

export type McpStartupStatus = StartingMcpStartupStatus | ReadyMcpStartupStatus | McpStartupStatusVariant | CancelledMcpStartupStatus;

export type MessagePhase = "commentary" | "final_answer";

export type ModeKind = "plan" | "default";

export type ModelRerouteReason = "high_risk_cyber_activity";

export interface NetworkPermissions {
  enabled?: boolean | null;
}

export interface ReadParsedCommand {
  cmd: string;
  name: string;
  path: string;
  type: "read";
}

export interface ListFilesParsedCommand {
  cmd: string;
  path?: string | null;
  type: "list_files";
}

export interface SearchParsedCommand {
  cmd: string;
  path?: string | null;
  query?: string | null;
  type: "search";
}

export interface UnknownParsedCommand {
  cmd: string;
  type: "unknown";
}

export type ParsedCommand = ReadParsedCommand | ListFilesParsedCommand | SearchParsedCommand | UnknownParsedCommand;

export type PatchApplyStatus = "completed" | "failed" | "declined";

export interface PermissionProfile {
  file_system?: FileSystemPermissions | null;
  macos?: MacOsPermissions | null;
  network?: NetworkPermissions | null;
}

export interface PlanItemArg {
  status: StepStatus;
  step: string;
}

export interface RealtimeAudioFrame {
  data: string;
  num_channels: number;
  sample_rate: number;
  samples_per_channel?: number | null;
}

export interface SessionUpdatedRealtimeEventSessionUpdatedVariant {
  instructions?: string | null;
  session_id: string;
}

export interface SessionUpdatedRealtimeEvent {
  SessionUpdated: SessionUpdatedRealtimeEventSessionUpdatedVariant;
}

export interface AudioOutRealtimeEvent {
  AudioOut: RealtimeAudioFrame;
}

export interface ConversationItemAddedRealtimeEvent {
  ConversationItemAdded: JSONValue;
}

export interface ConversationItemDoneRealtimeEventConversationItemDoneVariant {
  item_id: string;
}

export interface ConversationItemDoneRealtimeEvent {
  ConversationItemDone: ConversationItemDoneRealtimeEventConversationItemDoneVariant;
}

export interface HandoffRequestedRealtimeEvent {
  HandoffRequested: RealtimeHandoffRequested;
}

export interface ErrorRealtimeEvent {
  Error: string;
}

export type RealtimeEvent = SessionUpdatedRealtimeEvent | AudioOutRealtimeEvent | ConversationItemAddedRealtimeEvent | ConversationItemDoneRealtimeEvent | HandoffRequestedRealtimeEvent | ErrorRealtimeEvent;

export interface RealtimeHandoffMessage {
  role: string;
  text: string;
}

export interface RealtimeHandoffRequested {
  handoff_id: string;
  input_transcript: string;
  item_id: string;
  messages: Array<RealtimeHandoffMessage>;
}

export interface ReasoningTextReasoningItemContent {
  text: string;
  type: "reasoning_text";
}

export interface TextReasoningItemContent {
  text: string;
  type: "text";
}

export type ReasoningItemContent = ReasoningTextReasoningItemContent | TextReasoningItemContent;

export interface SummaryTextReasoningItemReasoningSummary {
  text: string;
  type: "summary_text";
}

export type ReasoningItemReasoningSummary = SummaryTextReasoningItemReasoningSummary;

export interface RejectConfig {
  mcp_elicitations: boolean;
  rules: boolean;
  sandbox_approval: boolean;
}

export interface RemoteSkillSummary {
  description: string;
  id: string;
  name: string;
}

export type RequestId = string | number;

export interface RequestUserInputQuestion {
  header: string;
  id: string;
  isOther?: boolean;
  isSecret?: boolean;
  options?: Array<RequestUserInputQuestionOption> | null;
  question: string;
}

export interface RequestUserInputQuestionOption {
  description: string;
  label: string;
}

export interface Resource {
  _meta?: JSONValue;
  annotations?: JSONValue;
  description?: string | null;
  icons?: Array<JSONValue> | null;
  mimeType?: string | null;
  name: string;
  size?: number | null;
  title?: string | null;
  uri: string;
}

export interface ResourceTemplate {
  annotations?: JSONValue;
  description?: string | null;
  mimeType?: string | null;
  name: string;
  title?: string | null;
  uriTemplate: string;
}

export interface MessageResponseItem {
  content: Array<ContentItem>;
  end_turn?: boolean | null;
  id?: string | null;
  phase?: MessagePhase | null;
  role: string;
  type: "message";
}

export interface ReasoningResponseItem {
  content?: Array<ReasoningItemContent> | null;
  encrypted_content?: string | null;
  id: string;
  summary: Array<ReasoningItemReasoningSummary>;
  type: "reasoning";
}

export interface LocalShellCallResponseItem {
  action: LocalShellAction;
  call_id?: string | null;
  id?: string | null;
  status: LocalShellStatus;
  type: "local_shell_call";
}

export interface FunctionCallResponseItem {
  arguments: string;
  call_id: string;
  id?: string | null;
  name: string;
  type: "function_call";
}

export interface FunctionCallOutputResponseItem {
  call_id: string;
  output: FunctionCallOutputPayload;
  type: "function_call_output";
}

export interface CustomToolCallResponseItem {
  call_id: string;
  id?: string | null;
  input: string;
  name: string;
  status?: string | null;
  type: "custom_tool_call";
}

export interface CustomToolCallOutputResponseItem {
  call_id: string;
  output: FunctionCallOutputPayload;
  type: "custom_tool_call_output";
}

export interface WebSearchCallResponseItem {
  action?: WebSearchAction | null;
  id?: string | null;
  status?: string | null;
  type: "web_search_call";
}

export interface ImageGenerationCallResponseItem {
  id: string;
  result: string;
  revised_prompt?: string | null;
  status: string;
  type: "image_generation_call";
}

export interface GhostSnapshotResponseItem {
  ghost_commit: GhostCommit;
  type: "ghost_snapshot";
}

export interface CompactionResponseItem {
  encrypted_content: string;
  type: "compaction";
}

export interface OtherResponseItem {
  type: "other";
}

export type ResponseItem = MessageResponseItem | ReasoningResponseItem | LocalShellCallResponseItem | FunctionCallResponseItem | FunctionCallOutputResponseItem | CustomToolCallResponseItem | CustomToolCallOutputResponseItem | WebSearchCallResponseItem | ImageGenerationCallResponseItem | GhostSnapshotResponseItem | CompactionResponseItem | OtherResponseItem;

export interface OkResultOfCallToolResultOrString {
  Ok: CallToolResult;
}

export interface ErrResultOfCallToolResultOrString {
  Err: string;
}

export type ResultOfCallToolResultOrString = OkResultOfCallToolResultOrString | ErrResultOfCallToolResultOrString;

export interface ReviewCodeLocation {
  absolute_file_path: string;
  line_range: ReviewLineRange;
}

export interface ReviewFinding {
  body: string;
  code_location: ReviewCodeLocation;
  confidence_score: number;
  priority: number;
  title: string;
}

export interface ReviewLineRange {
  end: number;
  start: number;
}

export interface ReviewOutputEvent {
  findings: Array<ReviewFinding>;
  overall_confidence_score: number;
  overall_correctness: string;
  overall_explanation: string;
}

export interface UncommittedChangesReviewTarget {
  type: "uncommittedChanges";
}

export interface BaseBranchReviewTarget {
  branch: string;
  type: "baseBranch";
}

export interface CommitReviewTarget {
  sha: string;
  title?: string | null;
  type: "commit";
}

export interface CustomReviewTarget {
  instructions: string;
  type: "custom";
}

export type ReviewTarget = UncommittedChangesReviewTarget | BaseBranchReviewTarget | CommitReviewTarget | CustomReviewTarget;

export interface SessionNetworkProxyRuntime {
  admin_addr: string;
  http_addr: string;
  socks_addr: string;
}

export interface SkillDependencies {
  tools: Array<SkillToolDependency>;
}

export interface SkillErrorInfo {
  message: string;
  path: string;
}

export interface SkillInterface {
  brand_color?: string | null;
  default_prompt?: string | null;
  display_name?: string | null;
  icon_large?: string | null;
  icon_small?: string | null;
  short_description?: string | null;
}

export interface SkillMetadata {
  dependencies?: SkillDependencies | null;
  description: string;
  enabled: boolean;
  interface?: SkillInterface | null;
  name: string;
  path: string;
  scope: SkillScope;
  short_description?: string | null;
}

export type SkillScope = "user" | "repo" | "system" | "admin";

export interface SkillToolDependency {
  command?: string | null;
  description?: string | null;
  transport?: string | null;
  type: string;
  url?: string | null;
  value: string;
}

export interface SkillsListEntry {
  cwd: string;
  errors: Array<SkillErrorInfo>;
  skills: Array<SkillMetadata>;
}

export type StepStatus = "pending" | "in_progress" | "completed";

export interface TextElement {
  byte_range: ByteRange;
  placeholder?: string | null;
}

export interface TokenUsage {
  cached_input_tokens: number;
  input_tokens: number;
  output_tokens: number;
  reasoning_output_tokens: number;
  total_tokens: number;
}

export interface TokenUsageInfo {
  last_token_usage: TokenUsage;
  model_context_window?: number | null;
  total_token_usage: TokenUsage;
}

export interface Tool {
  _meta?: JSONValue;
  annotations?: JSONValue;
  description?: string | null;
  icons?: Array<JSONValue> | null;
  inputSchema: JSONValue;
  name: string;
  outputSchema?: JSONValue;
  title?: string | null;
}

export type TurnAbortReason = "interrupted" | "replaced" | "review_ended";

export interface UserMessageTurnItem {
  content: Array<UserInput>;
  id: string;
  type: "UserMessage";
}

export interface AgentMessageTurnItem {
  content: Array<AgentMessageContent>;
  id: string;
  phase?: MessagePhase | null;
  type: "AgentMessage";
}

export interface PlanTurnItem {
  id: string;
  text: string;
  type: "Plan";
}

export interface ReasoningTurnItem {
  id: string;
  raw_content?: Array<string>;
  summary_text: Array<string>;
  type: "Reasoning";
}

export interface WebSearchTurnItem {
  action: WebSearchAction;
  id: string;
  query: string;
  type: "WebSearch";
}

export interface ImageGenerationTurnItem {
  id: string;
  result: string;
  revised_prompt?: string | null;
  status: string;
  type: "ImageGeneration";
}

export interface ContextCompactionTurnItem {
  id: string;
  type: "ContextCompaction";
}

export type TurnItem = UserMessageTurnItem | AgentMessageTurnItem | PlanTurnItem | ReasoningTurnItem | WebSearchTurnItem | ImageGenerationTurnItem | ContextCompactionTurnItem;

export interface TextUserInput {
  text: string;
  text_elements?: Array<TextElement>;
  type: "text";
}

export interface ImageUserInput {
  image_url: string;
  type: "image";
}

export interface LocalImageUserInput {
  path: string;
  type: "local_image";
}

export interface SkillUserInput {
  name: string;
  path: string;
  type: "skill";
}

export interface MentionUserInput {
  name: string;
  path: string;
  type: "mention";
}

export type UserInput = TextUserInput | ImageUserInput | LocalImageUserInput | SkillUserInput | MentionUserInput;

export interface SearchWebSearchAction {
  queries?: Array<string> | null;
  query?: string | null;
  type: "search";
}

export interface OpenPageWebSearchAction {
  type: "open_page";
  url?: string | null;
}

export interface FindInPageWebSearchAction {
  pattern?: string | null;
  type: "find_in_page";
  url?: string | null;
}

export interface OtherWebSearchAction {
  type: "other";
}

export type WebSearchAction = SearchWebSearchAction | OpenPageWebSearchAction | FindInPageWebSearchAction | OtherWebSearchAction;

export interface ExecCommandApprovalParams {
  approvalId?: string | null;
  callId: string;
  command: Array<string>;
  conversationId: ThreadId;
  cwd: string;
  parsedCmd: Array<ParsedCommand>;
  reason?: string | null;
}

export interface ExecCommandApprovalResponse {
  decision: ReviewDecision;
}

export interface ExperimentalFeatureListParams {
  cursor?: string | null;
  limit?: number | null;
}

export interface ExperimentalFeature {
  announcement?: string | null;
  defaultEnabled: boolean;
  description?: string | null;
  displayName?: string | null;
  enabled: boolean;
  name: string;
  stage: ExperimentalFeatureStage;
}

export type ExperimentalFeatureStage = "beta" | "underDevelopment" | "stable" | "deprecated" | "removed";

export interface ExperimentalFeatureListResponse {
  data: Array<ExperimentalFeature>;
  nextCursor?: string | null;
}

export interface ExternalAgentConfigDetectParams {
  cwds?: Array<string> | null;
  includeHome?: boolean;
}

export interface ExternalAgentConfigMigrationItem {
  cwd?: string | null;
  description: string;
  itemType: ExternalAgentConfigMigrationItemType;
}

export type ExternalAgentConfigMigrationItemType = "AGENTS_MD" | "CONFIG" | "SKILLS" | "MCP_SERVER_CONFIG";

export interface ExternalAgentConfigDetectResponse {
  items: Array<ExternalAgentConfigMigrationItem>;
}

export interface ExternalAgentConfigImportParams {
  migrationItems: Array<ExternalAgentConfigMigrationItem>;
}

export type ExternalAgentConfigImportResponse = Record<string, JSONValue>;

export interface FeedbackUploadParams {
  classification: string;
  extraLogFiles?: Array<string> | null;
  includeLogs: boolean;
  reason?: string | null;
  threadId?: string | null;
}

export interface FeedbackUploadResponse {
  threadId: string;
}

export interface FileChangeOutputDeltaNotification {
  delta: string;
  itemId: string;
  threadId: string;
  turnId: string;
}

export interface FileChangeRequestApprovalParams {
  grantRoot?: string | null;
  itemId: string;
  reason?: string | null;
  threadId: string;
  turnId: string;
}

export type FileChangeApprovalDecision = "accept" | "acceptForSession" | "decline" | "cancel";

export interface FileChangeRequestApprovalResponse {
  decision: FileChangeApprovalDecision;
}

export interface FuzzyFileSearchParams {
  cancellationToken?: string | null;
  query: string;
  roots: Array<string>;
}

export interface FuzzyFileSearchResult {
  file_name: string;
  indices?: Array<number> | null;
  path: string;
  root: string;
  score: number;
}

export interface FuzzyFileSearchResponse {
  files: Array<FuzzyFileSearchResult>;
}

export interface FuzzyFileSearchSessionCompletedNotification {
  sessionId: string;
}

export interface FuzzyFileSearchSessionUpdatedNotification {
  files: Array<FuzzyFileSearchResult>;
  query: string;
  sessionId: string;
}

export interface GetAccountParams {
  refreshToken?: boolean;
}

export interface GetAccountRateLimitsResponse {
  rateLimits: RateLimitSnapshot;
  rateLimitsByLimitId?: Record<string, RateLimitSnapshot> | null;
}

export interface ApiKeyAccount {
  type: "apiKey";
}

export interface ChatgptAccount {
  email: string;
  planType: PlanType;
  type: "chatgpt";
}

export type Account = ApiKeyAccount | ChatgptAccount;

export interface GetAccountResponse {
  account?: Account | null;
  requiresOpenaiAuth: boolean;
}

export interface ClientInfo {
  name: string;
  title?: string | null;
  version: string;
}

export interface InitializeCapabilities {
  experimentalApi?: boolean;
  optOutNotificationMethods?: Array<string> | null;
}

export interface InitializeParams {
  capabilities?: InitializeCapabilities | null;
  clientInfo: ClientInfo;
}

export interface InitializeResponse {
  userAgent: string;
}

export interface CollabAgentState {
  message?: string | null;
  status: CollabAgentStatus;
}

export type CollabAgentStatus = "pendingInit" | "running" | "completed" | "errored" | "shutdown" | "notFound";

export type CollabAgentTool = "spawnAgent" | "sendInput" | "resumeAgent" | "wait" | "closeAgent";

export type CollabAgentToolCallStatus = "inProgress" | "completed" | "failed";

export type CommandExecutionStatus = "inProgress" | "completed" | "failed" | "declined";

export type DynamicToolCallStatus = "inProgress" | "completed" | "failed";

export interface FileUpdateChange {
  diff: string;
  kind: PatchChangeKind;
  path: string;
}

export interface McpToolCallError {
  message: string;
}

export interface McpToolCallResult {
  content: Array<JSONValue>;
  structuredContent?: JSONValue;
}

export type McpToolCallStatus = "inProgress" | "completed" | "failed";

export interface AddPatchChangeKind {
  type: "add";
}

export interface DeletePatchChangeKind {
  type: "delete";
}

export interface UpdatePatchChangeKind {
  move_path?: string | null;
  type: "update";
}

export type PatchChangeKind = AddPatchChangeKind | DeletePatchChangeKind | UpdatePatchChangeKind;

export interface UserMessageThreadItem {
  content: Array<UserInput>;
  id: string;
  type: "userMessage";
}

export interface AgentMessageThreadItem {
  id: string;
  phase?: MessagePhase | null;
  text: string;
  type: "agentMessage";
}

export interface PlanThreadItem {
  id: string;
  text: string;
  type: "plan";
}

export interface ReasoningThreadItem {
  content?: Array<string>;
  id: string;
  summary?: Array<string>;
  type: "reasoning";
}

export interface CommandExecutionThreadItem {
  aggregatedOutput?: string | null;
  command: string;
  commandActions: Array<CommandAction>;
  cwd: string;
  durationMs?: number | null;
  exitCode?: number | null;
  id: string;
  processId?: string | null;
  status: CommandExecutionStatus;
  type: "commandExecution";
}

export interface FileChangeThreadItem {
  changes: Array<FileUpdateChange>;
  id: string;
  status: PatchApplyStatus;
  type: "fileChange";
}

export interface McpToolCallThreadItem {
  arguments: JSONValue;
  durationMs?: number | null;
  error?: McpToolCallError | null;
  id: string;
  result?: McpToolCallResult | null;
  server: string;
  status: McpToolCallStatus;
  tool: string;
  type: "mcpToolCall";
}

export interface DynamicToolCallThreadItem {
  arguments: JSONValue;
  contentItems?: Array<DynamicToolCallOutputContentItem> | null;
  durationMs?: number | null;
  id: string;
  status: DynamicToolCallStatus;
  success?: boolean | null;
  tool: string;
  type: "dynamicToolCall";
}

export interface CollabAgentToolCallThreadItem {
  agentsStates: Record<string, CollabAgentState>;
  id: string;
  prompt?: string | null;
  receiverThreadIds: Array<string>;
  senderThreadId: string;
  status: CollabAgentToolCallStatus;
  tool: CollabAgentTool;
  type: "collabAgentToolCall";
}

export interface WebSearchThreadItem {
  action?: WebSearchAction | null;
  id: string;
  query: string;
  type: "webSearch";
}

export interface ImageViewThreadItem {
  id: string;
  path: string;
  type: "imageView";
}

export interface ImageGenerationThreadItem {
  id: string;
  result: string;
  revisedPrompt?: string | null;
  status: string;
  type: "imageGeneration";
}

export interface EnteredReviewModeThreadItem {
  id: string;
  review: string;
  type: "enteredReviewMode";
}

export interface ExitedReviewModeThreadItem {
  id: string;
  review: string;
  type: "exitedReviewMode";
}

export interface ContextCompactionThreadItem {
  id: string;
  type: "contextCompaction";
}

export type ThreadItem = UserMessageThreadItem | AgentMessageThreadItem | PlanThreadItem | ReasoningThreadItem | CommandExecutionThreadItem | FileChangeThreadItem | McpToolCallThreadItem | DynamicToolCallThreadItem | CollabAgentToolCallThreadItem | WebSearchThreadItem | ImageViewThreadItem | ImageGenerationThreadItem | EnteredReviewModeThreadItem | ExitedReviewModeThreadItem | ContextCompactionThreadItem;

export interface ItemCompletedNotification {
  item: ThreadItem;
  threadId: string;
  turnId: string;
}

export interface ItemStartedNotification {
  item: ThreadItem;
  threadId: string;
  turnId: string;
}

export interface ListMcpServerStatusParams {
  cursor?: string | null;
  limit?: number | null;
}

export interface McpServerStatus {
  authStatus: McpAuthStatus;
  name: string;
  resourceTemplates: Array<ResourceTemplate>;
  resources: Array<Resource>;
  tools: Record<string, Tool>;
}

export interface ListMcpServerStatusResponse {
  data: Array<McpServerStatus>;
  nextCursor?: string | null;
}

export interface ApiKeyv2LoginAccountParams {
  apiKey: string;
  type: "apiKey";
}

export interface Chatgptv2LoginAccountParams {
  type: "chatgpt";
}

export interface ChatgptAuthTokensv2LoginAccountParams {
  accessToken: string;
  chatgptAccountId: string;
  chatgptPlanType?: string | null;
  type: "chatgptAuthTokens";
}

export type LoginAccountParams = ApiKeyv2LoginAccountParams | Chatgptv2LoginAccountParams | ChatgptAuthTokensv2LoginAccountParams;

export interface ApiKeyv2LoginAccountResponse {
  type: "apiKey";
}

export interface Chatgptv2LoginAccountResponse {
  authUrl: string;
  loginId: string;
  type: "chatgpt";
}

export interface ChatgptAuthTokensv2LoginAccountResponse {
  type: "chatgptAuthTokens";
}

export type LoginAccountResponse = ApiKeyv2LoginAccountResponse | Chatgptv2LoginAccountResponse | ChatgptAuthTokensv2LoginAccountResponse;

export type LogoutAccountResponse = Record<string, JSONValue>;

export interface McpServerElicitationRequestParams {
  serverName: string;
  threadId: string;
  turnId?: string | null;
}

export type McpServerElicitationAction = "accept" | "decline" | "cancel";

export interface McpServerElicitationRequestResponse {
  action: McpServerElicitationAction;
  content?: JSONValue;
}

export interface McpServerOauthLoginCompletedNotification {
  error?: string | null;
  name: string;
  success: boolean;
}

export interface McpServerOauthLoginParams {
  name: string;
  scopes?: Array<string> | null;
  timeoutSecs?: number | null;
}

export interface McpServerOauthLoginResponse {
  authorizationUrl: string;
}

export type McpServerRefreshResponse = Record<string, JSONValue>;

export interface McpToolCallProgressNotification {
  itemId: string;
  message: string;
  threadId: string;
  turnId: string;
}

export interface ModelListParams {
  cursor?: string | null;
  includeHidden?: boolean | null;
  limit?: number | null;
}

export type InputModality = "text" | "image";

export interface Model {
  availabilityNux?: ModelAvailabilityNux | null;
  defaultReasoningEffort: ReasoningEffort;
  description: string;
  displayName: string;
  hidden: boolean;
  id: string;
  inputModalities?: Array<InputModality>;
  isDefault: boolean;
  model: string;
  supportedReasoningEfforts: Array<ReasoningEffortOption>;
  supportsPersonality?: boolean;
  upgrade?: string | null;
  upgradeInfo?: ModelUpgradeInfo | null;
}

export interface ModelAvailabilityNux {
  message: string;
}

export interface ModelUpgradeInfo {
  migrationMarkdown?: string | null;
  model: string;
  modelLink?: string | null;
  upgradeCopy?: string | null;
}

export interface ReasoningEffortOption {
  description: string;
  reasoningEffort: ReasoningEffort;
}

export interface ModelListResponse {
  data: Array<Model>;
  nextCursor?: string | null;
}

export interface ModelReroutedNotification {
  fromModel: string;
  reason: ModelRerouteReason;
  threadId: string;
  toModel: string;
  turnId: string;
}

export interface PlanDeltaNotification {
  delta: string;
  itemId: string;
  threadId: string;
  turnId: string;
}

export interface PluginInstallParams {
  cwd?: string | null;
  marketplaceName: string;
  pluginName: string;
}

export type PluginInstallResponse = Record<string, JSONValue>;

export interface RawResponseItemCompletedNotification {
  item: ResponseItem;
  threadId: string;
  turnId: string;
}

export interface ReasoningSummaryPartAddedNotification {
  itemId: string;
  summaryIndex: number;
  threadId: string;
  turnId: string;
}

export interface ReasoningSummaryTextDeltaNotification {
  delta: string;
  itemId: string;
  summaryIndex: number;
  threadId: string;
  turnId: string;
}

export interface ReasoningTextDeltaNotification {
  contentIndex: number;
  delta: string;
  itemId: string;
  threadId: string;
  turnId: string;
}

export type ReviewDelivery = "inline" | "detached";

export interface ReviewStartParams {
  delivery?: ReviewDelivery | null;
  target: ReviewTarget;
  threadId: string;
}

export interface Turn {
  error?: TurnError | null;
  id: string;
  items: Array<ThreadItem>;
  status: TurnStatus;
}

export type TurnStatus = "completed" | "interrupted" | "failed" | "inProgress";

export interface ReviewStartResponse {
  reviewThreadId: string;
  turn: Turn;
}

export interface ServerRequestResolvedNotification {
  requestId: RequestId;
  threadId: string;
}

export type SkillsChangedNotification = Record<string, JSONValue>;

export interface SkillsConfigWriteParams {
  enabled: boolean;
  path: string;
}

export interface SkillsConfigWriteResponse {
  effectiveEnabled: boolean;
}

export interface SkillsListExtraRootsForCwd {
  cwd: string;
  extraUserRoots: Array<string>;
}

export interface SkillsListParams {
  cwds?: Array<string>;
  forceReload?: boolean;
  perCwdExtraUserRoots?: Array<SkillsListExtraRootsForCwd> | null;
}

export interface SkillsListResponse {
  data: Array<SkillsListEntry>;
}

export type HazelnutScope = "example" | "workspace-shared" | "all-shared" | "personal";

export type ProductSurface = "chatgpt" | "codex" | "api" | "atlas";

export interface SkillsRemoteReadParams {
  enabled?: boolean;
  hazelnutScope?: HazelnutScope;
  productSurface?: ProductSurface;
}

export interface SkillsRemoteReadResponse {
  data: Array<RemoteSkillSummary>;
}

export interface SkillsRemoteWriteParams {
  hazelnutId: string;
}

export interface SkillsRemoteWriteResponse {
  id: string;
  path: string;
}

export interface TerminalInteractionNotification {
  itemId: string;
  processId: string;
  stdin: string;
  threadId: string;
  turnId: string;
}

export interface ThreadArchivedNotification {
  threadId: string;
}

export interface ThreadArchiveParams {
  threadId: string;
}

export type ThreadArchiveResponse = Record<string, JSONValue>;

export interface ThreadClosedNotification {
  threadId: string;
}

export interface ThreadCompactStartParams {
  threadId: string;
}

export type ThreadCompactStartResponse = Record<string, JSONValue>;

export interface ThreadForkParams {
  approvalPolicy?: AskForApproval | null;
  baseInstructions?: string | null;
  config?: Record<string, JSONValue> | null;
  cwd?: string | null;
  developerInstructions?: string | null;
  model?: string | null;
  modelProvider?: string | null;
  threadId: string;
  serviceTier?: ServiceTier | null | null;
  sandbox?: SandboxMode | null;
}

export interface GitInfo {
  branch?: string | null;
  originUrl?: string | null;
  sha?: string | null;
}

export interface SubAgentSessionSource {
  subAgent: SubAgentSource;
}

export type SessionSource = "cli" | "vscode" | "exec" | "appServer" | "unknown" | SubAgentSessionSource;

export interface ThreadSpawnSubAgentSourceThreadSpawnVariant {
  agent_nickname?: string | null;
  agent_role?: string | null;
  depth: number;
  parent_thread_id: ThreadId;
}

export interface ThreadSpawnSubAgentSource {
  thread_spawn: ThreadSpawnSubAgentSourceThreadSpawnVariant;
}

export interface OtherSubAgentSource {
  other: string;
}

export type SubAgentSource = "review" | "compact" | "memory_consolidation" | ThreadSpawnSubAgentSource | OtherSubAgentSource;

export interface Thread {
  agentNickname?: string | null;
  agentRole?: string | null;
  cliVersion: string;
  createdAt: number;
  cwd: string;
  ephemeral: boolean;
  gitInfo?: GitInfo | null;
  id: string;
  modelProvider: string;
  name?: string | null;
  path?: string | null;
  preview: string;
  source: SessionSource;
  status: ThreadStatus;
  turns: Array<Turn>;
  updatedAt: number;
}

export type ThreadActiveFlag = "waitingOnApproval" | "waitingOnUserInput";

export interface NotLoadedThreadStatus {
  type: "notLoaded";
}

export interface IdleThreadStatus {
  type: "idle";
}

export interface SystemErrorThreadStatus {
  type: "systemError";
}

export interface ActiveThreadStatus {
  activeFlags: Array<ThreadActiveFlag>;
  type: "active";
}

export type ThreadStatus = NotLoadedThreadStatus | IdleThreadStatus | SystemErrorThreadStatus | ActiveThreadStatus;

export interface ThreadForkResponse {
  approvalPolicy: AskForApproval;
  cwd: string;
  model: string;
  modelProvider: string;
  reasoningEffort?: ReasoningEffort | null;
  sandbox: SandboxPolicy;
  serviceTier?: ServiceTier | null;
  thread: Thread;
}

export type ThreadSortKey = "created_at" | "updated_at";

export type ThreadSourceKind = "cli" | "vscode" | "exec" | "appServer" | "subAgent" | "subAgentReview" | "subAgentCompact" | "subAgentThreadSpawn" | "subAgentOther" | "unknown";

export interface ThreadListParams {
  archived?: boolean | null;
  cursor?: string | null;
  cwd?: string | null;
  limit?: number | null;
  modelProviders?: Array<string> | null;
  searchTerm?: string | null;
  sortKey?: ThreadSortKey | null;
  sourceKinds?: Array<ThreadSourceKind> | null;
}

export interface ThreadListResponse {
  data: Array<Thread>;
  nextCursor?: string | null;
}

export interface ThreadLoadedListParams {
  cursor?: string | null;
  limit?: number | null;
}

export interface ThreadLoadedListResponse {
  data: Array<string>;
  nextCursor?: string | null;
}

export interface ThreadMetadataGitInfoUpdateParams {
  branch?: string | null;
  originUrl?: string | null;
  sha?: string | null;
}

export interface ThreadMetadataUpdateParams {
  gitInfo?: ThreadMetadataGitInfoUpdateParams | null;
  threadId: string;
}

export interface ThreadMetadataUpdateResponse {
  thread: Thread;
}

export interface ThreadNameUpdatedNotification {
  threadId: string;
  threadName?: string | null;
}

export interface ThreadReadParams {
  includeTurns?: boolean;
  threadId: string;
}

export interface ThreadReadResponse {
  thread: Thread;
}

export interface ThreadRealtimeClosedNotification {
  reason?: string | null;
  threadId: string;
}

export interface ThreadRealtimeErrorNotification {
  message: string;
  threadId: string;
}

export interface ThreadRealtimeItemAddedNotification {
  item: JSONValue;
  threadId: string;
}

export interface ThreadRealtimeAudioChunk {
  data: string;
  numChannels: number;
  sampleRate: number;
  samplesPerChannel?: number | null;
}

export interface ThreadRealtimeOutputAudioDeltaNotification {
  audio: ThreadRealtimeAudioChunk;
  threadId: string;
}

export interface ThreadRealtimeStartedNotification {
  sessionId?: string | null;
  threadId: string;
}

export type Personality = "none" | "friendly" | "pragmatic";

export interface ThreadResumeParams {
  approvalPolicy?: AskForApproval | null;
  baseInstructions?: string | null;
  config?: Record<string, JSONValue> | null;
  cwd?: string | null;
  developerInstructions?: string | null;
  serviceTier?: ServiceTier | null | null;
  model?: string | null;
  modelProvider?: string | null;
  threadId: string;
  sandbox?: SandboxMode | null;
  personality?: Personality | null;
}

export interface ThreadResumeResponse {
  approvalPolicy: AskForApproval;
  cwd: string;
  model: string;
  modelProvider: string;
  reasoningEffort?: ReasoningEffort | null;
  sandbox: SandboxPolicy;
  serviceTier?: ServiceTier | null;
  thread: Thread;
}

export interface ThreadRollbackParams {
  numTurns: number;
  threadId: string;
}

export interface ThreadRollbackResponse {
  thread: Thread;
}

export interface ThreadSetNameParams {
  name: string;
  threadId: string;
}

export type ThreadSetNameResponse = Record<string, JSONValue>;

export interface ThreadStartedNotification {
  thread: Thread;
}

export interface DynamicToolSpec {
  description: string;
  inputSchema: JSONValue;
  name: string;
}

export interface ThreadStartParams {
  approvalPolicy?: AskForApproval | null;
  baseInstructions?: string | null;
  config?: Record<string, JSONValue> | null;
  cwd?: string | null;
  developerInstructions?: string | null;
  sandbox?: SandboxMode | null;
  ephemeral?: boolean | null;
  serviceName?: string | null;
  personality?: Personality | null;
  model?: string | null;
  modelProvider?: string | null;
  serviceTier?: ServiceTier | null | null;
}

export interface ThreadStartResponse {
  approvalPolicy: AskForApproval;
  cwd: string;
  model: string;
  modelProvider: string;
  reasoningEffort?: ReasoningEffort | null;
  sandbox: SandboxPolicy;
  serviceTier?: ServiceTier | null;
  thread: Thread;
}

export interface ThreadStatusChangedNotification {
  status: ThreadStatus;
  threadId: string;
}

export interface ThreadTokenUsage {
  last: TokenUsageBreakdown;
  modelContextWindow?: number | null;
  total: TokenUsageBreakdown;
}

export interface TokenUsageBreakdown {
  cachedInputTokens: number;
  inputTokens: number;
  outputTokens: number;
  reasoningOutputTokens: number;
  totalTokens: number;
}

export interface ThreadTokenUsageUpdatedNotification {
  threadId: string;
  tokenUsage: ThreadTokenUsage;
  turnId: string;
}

export interface ThreadUnarchivedNotification {
  threadId: string;
}

export interface ThreadUnarchiveParams {
  threadId: string;
}

export interface ThreadUnarchiveResponse {
  thread: Thread;
}

export interface ThreadUnsubscribeParams {
  threadId: string;
}

export type ThreadUnsubscribeStatus = "notLoaded" | "notSubscribed" | "unsubscribed";

export interface ThreadUnsubscribeResponse {
  status: ThreadUnsubscribeStatus;
}

export interface ToolRequestUserInputOption {
  description: string;
  label: string;
}

export interface ToolRequestUserInputQuestion {
  header: string;
  id: string;
  isOther?: boolean;
  isSecret?: boolean;
  options?: Array<ToolRequestUserInputOption> | null;
  question: string;
}

export interface ToolRequestUserInputParams {
  itemId: string;
  questions: Array<ToolRequestUserInputQuestion>;
  threadId: string;
  turnId: string;
}

export interface ToolRequestUserInputAnswer {
  answers: Array<string>;
}

export interface ToolRequestUserInputResponse {
  answers: Record<string, ToolRequestUserInputAnswer>;
}

export interface TurnCompletedNotification {
  threadId: string;
  turn: Turn;
}

export interface TurnDiffUpdatedNotification {
  diff: string;
  threadId: string;
  turnId: string;
}

export interface TurnInterruptParams {
  threadId: string;
  turnId: string;
}

export type TurnInterruptResponse = Record<string, JSONValue>;

export interface TurnPlanStep {
  status: TurnPlanStepStatus;
  step: string;
}

export type TurnPlanStepStatus = "pending" | "inProgress" | "completed";

export interface TurnPlanUpdatedNotification {
  explanation?: string | null;
  plan: Array<TurnPlanStep>;
  threadId: string;
  turnId: string;
}

export interface TurnStartedNotification {
  threadId: string;
  turn: Turn;
}

export interface CollaborationMode {
  mode: ModeKind;
  settings: Settings;
}

export interface Settings {
  developer_instructions?: string | null;
  model: string;
  reasoning_effort?: ReasoningEffort | null;
}

export interface TurnStartParams {
  approvalPolicy?: AskForApproval | null;
  threadId: string;
  cwd?: string | null;
  effort?: ReasoningEffort | null;
  input: Array<UserInput>;
  model?: string | null;
  outputSchema?: JSONValue;
  personality?: Personality | null;
  sandboxPolicy?: SandboxPolicy | null;
  serviceTier?: ServiceTier | null | null;
  summary?: ReasoningSummary | null;
}

export interface TurnStartResponse {
  turn: Turn;
}

export interface TurnSteerParams {
  expectedTurnId: string;
  input: Array<UserInput>;
  threadId: string;
}

export interface TurnSteerResponse {
  turnId: string;
}

export type WindowsSandboxSetupMode = "elevated" | "unelevated";

export interface WindowsSandboxSetupCompletedNotification {
  error?: string | null;
  mode: WindowsSandboxSetupMode;
  success: boolean;
}

export interface WindowsSandboxSetupStartParams {
  cwd?: string | null;
  mode: WindowsSandboxSetupMode;
}

export interface WindowsSandboxSetupStartResponse {
  started: boolean;
}

export interface WindowsWorldWritableWarningNotification {
  extraCount: number;
  failedScan: boolean;
  samplePaths: Array<string>;
}

export interface ClientRequestParamsByMethod {
  "initialize": InitializeParams;
  "thread/start": ThreadStartParams;
  "thread/resume": ThreadResumeParams;
  "thread/fork": ThreadForkParams;
  "thread/archive": ThreadArchiveParams;
  "thread/unsubscribe": ThreadUnsubscribeParams;
  "thread/name/set": ThreadSetNameParams;
  "thread/metadata/update": ThreadMetadataUpdateParams;
  "thread/unarchive": ThreadUnarchiveParams;
  "thread/compact/start": ThreadCompactStartParams;
  "thread/rollback": ThreadRollbackParams;
  "thread/list": ThreadListParams;
  "thread/loaded/list": ThreadLoadedListParams;
  "thread/read": ThreadReadParams;
  "skills/list": SkillsListParams;
  "skills/remote/list": SkillsRemoteReadParams;
  "skills/remote/export": SkillsRemoteWriteParams;
  "app/list": AppsListParams;
  "skills/config/write": SkillsConfigWriteParams;
  "plugin/install": PluginInstallParams;
  "turn/start": TurnStartParams;
  "turn/steer": TurnSteerParams;
  "turn/interrupt": TurnInterruptParams;
  "review/start": ReviewStartParams;
  "model/list": ModelListParams;
  "experimentalFeature/list": ExperimentalFeatureListParams;
  "mcpServer/oauth/login": McpServerOauthLoginParams;
  "config/mcpServer/reload": null;
  "mcpServerStatus/list": ListMcpServerStatusParams;
  "windowsSandbox/setupStart": WindowsSandboxSetupStartParams;
  "account/login/start": LoginAccountParams;
  "account/login/cancel": CancelLoginAccountParams;
  "account/logout": null;
  "account/rateLimits/read": null;
  "feedback/upload": FeedbackUploadParams;
  "command/exec": CommandExecParams;
  "config/read": ConfigReadParams;
  "externalAgentConfig/detect": ExternalAgentConfigDetectParams;
  "externalAgentConfig/import": ExternalAgentConfigImportParams;
  "config/value/write": ConfigValueWriteParams;
  "config/batchWrite": ConfigBatchWriteParams;
  "configRequirements/read": null;
  "account/read": GetAccountParams;
  "fuzzyFileSearch": FuzzyFileSearchParams;
}

export interface ClientRequestResultByMethod {
  "initialize": InitializeResponse;
  "thread/start": ThreadStartResponse;
  "thread/resume": ThreadResumeResponse;
  "thread/fork": ThreadForkResponse;
  "thread/archive": ThreadArchiveResponse;
  "thread/unsubscribe": ThreadUnsubscribeResponse;
  "thread/name/set": ThreadSetNameResponse;
  "thread/metadata/update": ThreadMetadataUpdateResponse;
  "thread/unarchive": ThreadUnarchiveResponse;
  "thread/compact/start": ThreadCompactStartResponse;
  "thread/rollback": ThreadRollbackResponse;
  "thread/list": ThreadListResponse;
  "thread/loaded/list": ThreadLoadedListResponse;
  "thread/read": ThreadReadResponse;
  "skills/list": SkillsListResponse;
  "skills/remote/list": SkillsRemoteReadResponse;
  "skills/remote/export": SkillsRemoteWriteResponse;
  "app/list": AppsListResponse;
  "skills/config/write": SkillsConfigWriteResponse;
  "plugin/install": PluginInstallResponse;
  "turn/start": TurnStartResponse;
  "turn/steer": TurnSteerResponse;
  "turn/interrupt": TurnInterruptResponse;
  "review/start": ReviewStartResponse;
  "model/list": ModelListResponse;
  "experimentalFeature/list": ExperimentalFeatureListResponse;
  "mcpServer/oauth/login": McpServerOauthLoginResponse;
  "config/mcpServer/reload": McpServerRefreshResponse;
  "mcpServerStatus/list": ListMcpServerStatusResponse;
  "windowsSandbox/setupStart": WindowsSandboxSetupStartResponse;
  "account/login/start": LoginAccountResponse;
  "account/login/cancel": CancelLoginAccountResponse;
  "account/logout": LogoutAccountResponse;
  "account/rateLimits/read": GetAccountRateLimitsResponse;
  "feedback/upload": FeedbackUploadResponse;
  "command/exec": CommandExecResponse;
  "config/read": ConfigReadResponse;
  "externalAgentConfig/detect": ExternalAgentConfigDetectResponse;
  "externalAgentConfig/import": ExternalAgentConfigImportResponse;
  "config/value/write": ConfigWriteResponse;
  "config/batchWrite": ConfigWriteResponse;
  "configRequirements/read": ConfigRequirementsReadResponse;
  "account/read": GetAccountResponse;
  "fuzzyFileSearch": FuzzyFileSearchResponse;
}

export interface ServerRequestParamsByMethod {
  "item/commandExecution/requestApproval": CommandExecutionRequestApprovalParams;
  "item/fileChange/requestApproval": FileChangeRequestApprovalParams;
  "item/tool/requestUserInput": ToolRequestUserInputParams;
  "mcpServer/elicitation/request": McpServerElicitationRequestParams;
  "item/tool/call": DynamicToolCallParams;
  "account/chatgptAuthTokens/refresh": ChatgptAuthTokensRefreshParams;
  "applyPatchApproval": ApplyPatchApprovalParams;
  "execCommandApproval": ExecCommandApprovalParams;
}

export interface ServerRequestResultByMethod {
  "item/commandExecution/requestApproval": CommandExecutionRequestApprovalResponse;
  "item/fileChange/requestApproval": FileChangeRequestApprovalResponse;
  "item/tool/requestUserInput": ToolRequestUserInputResponse;
  "mcpServer/elicitation/request": McpServerElicitationRequestResponse;
  "item/tool/call": DynamicToolCallResponse;
  "account/chatgptAuthTokens/refresh": ChatgptAuthTokensRefreshResponse;
  "applyPatchApproval": ApplyPatchApprovalResponse;
  "execCommandApproval": ExecCommandApprovalResponse;
}

export interface ServerNotificationParamsByMethod {
  "error": ErrorNotification;
  "thread/started": ThreadStartedNotification;
  "thread/status/changed": ThreadStatusChangedNotification;
  "thread/archived": ThreadArchivedNotification;
  "thread/unarchived": ThreadUnarchivedNotification;
  "thread/closed": ThreadClosedNotification;
  "skills/changed": SkillsChangedNotification;
  "thread/name/updated": ThreadNameUpdatedNotification;
  "thread/tokenUsage/updated": ThreadTokenUsageUpdatedNotification;
  "turn/started": TurnStartedNotification;
  "turn/completed": TurnCompletedNotification;
  "turn/diff/updated": TurnDiffUpdatedNotification;
  "turn/plan/updated": TurnPlanUpdatedNotification;
  "item/started": ItemStartedNotification;
  "item/completed": ItemCompletedNotification;
  "item/agentMessage/delta": AgentMessageDeltaNotification;
  "item/plan/delta": PlanDeltaNotification;
  "item/commandExecution/outputDelta": CommandExecutionOutputDeltaNotification;
  "item/commandExecution/terminalInteraction": TerminalInteractionNotification;
  "item/fileChange/outputDelta": FileChangeOutputDeltaNotification;
  "serverRequest/resolved": ServerRequestResolvedNotification;
  "item/mcpToolCall/progress": McpToolCallProgressNotification;
  "mcpServer/oauthLogin/completed": McpServerOauthLoginCompletedNotification;
  "account/updated": AccountUpdatedNotification;
  "account/rateLimits/updated": AccountRateLimitsUpdatedNotification;
  "app/list/updated": AppListUpdatedNotification;
  "item/reasoning/summaryTextDelta": ReasoningSummaryTextDeltaNotification;
  "item/reasoning/summaryPartAdded": ReasoningSummaryPartAddedNotification;
  "item/reasoning/textDelta": ReasoningTextDeltaNotification;
  "thread/compacted": ContextCompactedNotification;
  "model/rerouted": ModelReroutedNotification;
  "deprecationNotice": DeprecationNoticeNotification;
  "configWarning": ConfigWarningNotification;
  "fuzzyFileSearch/sessionUpdated": FuzzyFileSearchSessionUpdatedNotification;
  "fuzzyFileSearch/sessionCompleted": FuzzyFileSearchSessionCompletedNotification;
  "thread/realtime/started": ThreadRealtimeStartedNotification;
  "thread/realtime/itemAdded": ThreadRealtimeItemAddedNotification;
  "thread/realtime/outputAudio/delta": ThreadRealtimeOutputAudioDeltaNotification;
  "thread/realtime/error": ThreadRealtimeErrorNotification;
  "thread/realtime/closed": ThreadRealtimeClosedNotification;
  "windows/worldWritableWarning": WindowsWorldWritableWarningNotification;
  "windowsSandbox/setupCompleted": WindowsSandboxSetupCompletedNotification;
  "account/login/completed": AccountLoginCompletedNotification;
}

export type ClientRequestMethod = "initialize" | "thread/start" | "thread/resume" | "thread/fork" | "thread/archive" | "thread/unsubscribe" | "thread/name/set" | "thread/metadata/update" | "thread/unarchive" | "thread/compact/start" | "thread/rollback" | "thread/list" | "thread/loaded/list" | "thread/read" | "skills/list" | "skills/remote/list" | "skills/remote/export" | "app/list" | "skills/config/write" | "plugin/install" | "turn/start" | "turn/steer" | "turn/interrupt" | "review/start" | "model/list" | "experimentalFeature/list" | "mcpServer/oauth/login" | "config/mcpServer/reload" | "mcpServerStatus/list" | "windowsSandbox/setupStart" | "account/login/start" | "account/login/cancel" | "account/logout" | "account/rateLimits/read" | "feedback/upload" | "command/exec" | "config/read" | "externalAgentConfig/detect" | "externalAgentConfig/import" | "config/value/write" | "config/batchWrite" | "configRequirements/read" | "account/read" | "fuzzyFileSearch";

export type ServerRequestMethod = "item/commandExecution/requestApproval" | "item/fileChange/requestApproval" | "item/tool/requestUserInput" | "mcpServer/elicitation/request" | "item/tool/call" | "account/chatgptAuthTokens/refresh" | "applyPatchApproval" | "execCommandApproval";

export type ServerNotificationMethod = "error" | "thread/started" | "thread/status/changed" | "thread/archived" | "thread/unarchived" | "thread/closed" | "skills/changed" | "thread/name/updated" | "thread/tokenUsage/updated" | "turn/started" | "turn/completed" | "turn/diff/updated" | "turn/plan/updated" | "item/started" | "item/completed" | "item/agentMessage/delta" | "item/plan/delta" | "item/commandExecution/outputDelta" | "item/commandExecution/terminalInteraction" | "item/fileChange/outputDelta" | "serverRequest/resolved" | "item/mcpToolCall/progress" | "mcpServer/oauthLogin/completed" | "account/updated" | "account/rateLimits/updated" | "app/list/updated" | "item/reasoning/summaryTextDelta" | "item/reasoning/summaryPartAdded" | "item/reasoning/textDelta" | "thread/compacted" | "model/rerouted" | "deprecationNotice" | "configWarning" | "fuzzyFileSearch/sessionUpdated" | "fuzzyFileSearch/sessionCompleted" | "thread/realtime/started" | "thread/realtime/itemAdded" | "thread/realtime/outputAudio/delta" | "thread/realtime/error" | "thread/realtime/closed" | "windows/worldWritableWarning" | "windowsSandbox/setupCompleted" | "account/login/completed";

export const CLIENT_REQUEST_METHODS = [
  "initialize",
  "thread/start",
  "thread/resume",
  "thread/fork",
  "thread/archive",
  "thread/unsubscribe",
  "thread/name/set",
  "thread/metadata/update",
  "thread/unarchive",
  "thread/compact/start",
  "thread/rollback",
  "thread/list",
  "thread/loaded/list",
  "thread/read",
  "skills/list",
  "skills/remote/list",
  "skills/remote/export",
  "app/list",
  "skills/config/write",
  "plugin/install",
  "turn/start",
  "turn/steer",
  "turn/interrupt",
  "review/start",
  "model/list",
  "experimentalFeature/list",
  "mcpServer/oauth/login",
  "config/mcpServer/reload",
  "mcpServerStatus/list",
  "windowsSandbox/setupStart",
  "account/login/start",
  "account/login/cancel",
  "account/logout",
  "account/rateLimits/read",
  "feedback/upload",
  "command/exec",
  "config/read",
  "externalAgentConfig/detect",
  "externalAgentConfig/import",
  "config/value/write",
  "config/batchWrite",
  "configRequirements/read",
  "account/read",
  "fuzzyFileSearch",
] as const satisfies ReadonlyArray<ClientRequestMethod>;

export const SERVER_REQUEST_METHODS = [
  "item/commandExecution/requestApproval",
  "item/fileChange/requestApproval",
  "item/tool/requestUserInput",
  "mcpServer/elicitation/request",
  "item/tool/call",
  "account/chatgptAuthTokens/refresh",
  "applyPatchApproval",
  "execCommandApproval",
] as const satisfies ReadonlyArray<ServerRequestMethod>;

export const SERVER_NOTIFICATION_METHODS = [
  "error",
  "thread/started",
  "thread/status/changed",
  "thread/archived",
  "thread/unarchived",
  "thread/closed",
  "skills/changed",
  "thread/name/updated",
  "thread/tokenUsage/updated",
  "turn/started",
  "turn/completed",
  "turn/diff/updated",
  "turn/plan/updated",
  "item/started",
  "item/completed",
  "item/agentMessage/delta",
  "item/plan/delta",
  "item/commandExecution/outputDelta",
  "item/commandExecution/terminalInteraction",
  "item/fileChange/outputDelta",
  "serverRequest/resolved",
  "item/mcpToolCall/progress",
  "mcpServer/oauthLogin/completed",
  "account/updated",
  "account/rateLimits/updated",
  "app/list/updated",
  "item/reasoning/summaryTextDelta",
  "item/reasoning/summaryPartAdded",
  "item/reasoning/textDelta",
  "thread/compacted",
  "model/rerouted",
  "deprecationNotice",
  "configWarning",
  "fuzzyFileSearch/sessionUpdated",
  "fuzzyFileSearch/sessionCompleted",
  "thread/realtime/started",
  "thread/realtime/itemAdded",
  "thread/realtime/outputAudio/delta",
  "thread/realtime/error",
  "thread/realtime/closed",
  "windows/worldWritableWarning",
  "windowsSandbox/setupCompleted",
  "account/login/completed",
] as const satisfies ReadonlyArray<ServerNotificationMethod>;
