"""Auto-generated protocol types and method registries."""

from __future__ import annotations

from typing import Any, Final, Literal, Never, NotRequired, Required, TypeAlias, TypedDict

from .messages import JSONValue

class AccountLoginCompletedNotification(TypedDict, total=False):
    error: NotRequired[str | None]
    loginId: NotRequired[str | None]
    success: Required[bool]

class CreditsSnapshot(TypedDict, total=False):
    balance: NotRequired[str | None]
    hasCredits: Required[bool]
    unlimited: Required[bool]

PlanType: TypeAlias = "Literal['free', 'go', 'plus', 'pro', 'team', 'business', 'enterprise', 'edu', 'unknown']"

class RateLimitSnapshot(TypedDict, total=False):
    credits: NotRequired[CreditsSnapshot | None]
    limitId: NotRequired[str | None]
    limitName: NotRequired[str | None]
    planType: NotRequired[PlanType | None]
    primary: NotRequired[RateLimitWindow | None]
    secondary: NotRequired[RateLimitWindow | None]

class RateLimitWindow(TypedDict, total=False):
    resetsAt: NotRequired[int | None]
    usedPercent: Required[int]
    windowDurationMins: NotRequired[int | None]

class AccountRateLimitsUpdatedNotification(TypedDict, total=False):
    rateLimits: Required[RateLimitSnapshot]

AuthMode: TypeAlias = "Literal['apikey'] | Literal['chatgpt'] | Literal['chatgptAuthTokens']"

class AccountUpdatedNotification(TypedDict, total=False):
    authMode: NotRequired[AuthMode | None]
    planType: NotRequired[PlanType | None]

class AgentMessageDeltaNotification(TypedDict, total=False):
    delta: Required[str]
    itemId: Required[str]
    threadId: Required[str]
    turnId: Required[str]

class AppBranding(TypedDict, total=False):
    category: NotRequired[str | None]
    developer: NotRequired[str | None]
    isDiscoverableApp: Required[bool]
    privacyPolicy: NotRequired[str | None]
    termsOfService: NotRequired[str | None]
    website: NotRequired[str | None]

class AppInfo(TypedDict, total=False):
    appMetadata: NotRequired[AppMetadata | None]
    branding: NotRequired[AppBranding | None]
    description: NotRequired[str | None]
    distributionChannel: NotRequired[str | None]
    id: Required[str]
    installUrl: NotRequired[str | None]
    isAccessible: NotRequired[bool]
    isEnabled: NotRequired[bool]
    labels: NotRequired[dict[str, str] | None]
    logoUrl: NotRequired[str | None]
    logoUrlDark: NotRequired[str | None]
    name: Required[str]

class AppMetadata(TypedDict, total=False):
    categories: NotRequired[list[str] | None]
    developer: NotRequired[str | None]
    firstPartyRequiresInstall: NotRequired[bool | None]
    firstPartyType: NotRequired[str | None]
    review: NotRequired[AppReview | None]
    screenshots: NotRequired[list[AppScreenshot] | None]
    seoDescription: NotRequired[str | None]
    showInComposerWhenUnlinked: NotRequired[bool | None]
    subCategories: NotRequired[list[str] | None]
    version: NotRequired[str | None]
    versionId: NotRequired[str | None]
    versionNotes: NotRequired[str | None]

class AppReview(TypedDict, total=False):
    status: Required[str]

class AppScreenshot(TypedDict, total=False):
    fileId: NotRequired[str | None]
    url: NotRequired[str | None]
    userPrompt: Required[str]

class AppListUpdatedNotification(TypedDict, total=False):
    data: Required[list[AppInfo]]

class AddFileChange(TypedDict, total=False):
    content: Required[str]
    type: Required[Literal['add']]

class DeleteFileChange(TypedDict, total=False):
    content: Required[str]
    type: Required[Literal['delete']]

class UpdateFileChange(TypedDict, total=False):
    move_path: NotRequired[str | None]
    type: Required[Literal['update']]
    unified_diff: Required[str]

FileChange: TypeAlias = 'AddFileChange | DeleteFileChange | UpdateFileChange'

ThreadId: TypeAlias = 'str'

class ApplyPatchApprovalParams(TypedDict, total=False):
    callId: Required[str]
    conversationId: Required[ThreadId]
    fileChanges: Required[dict[str, FileChange]]
    grantRoot: NotRequired[str | None]
    reason: NotRequired[str | None]

class NetworkPolicyAmendment(TypedDict, total=False):
    action: Required[NetworkPolicyRuleAction]
    host: Required[str]

NetworkPolicyRuleAction: TypeAlias = "Literal['allow', 'deny']"

class ApprovedExecpolicyAmendmentReviewDecisionApprovedExecpolicyAmendmentVariant(TypedDict, total=False):
    proposed_execpolicy_amendment: Required[list[str]]

class ApprovedExecpolicyAmendmentReviewDecision(TypedDict, total=False):
    approved_execpolicy_amendment: Required[ApprovedExecpolicyAmendmentReviewDecisionApprovedExecpolicyAmendmentVariant]

class NetworkPolicyAmendmentReviewDecisionNetworkPolicyAmendmentVariant(TypedDict, total=False):
    network_policy_amendment: Required[NetworkPolicyAmendment]

class NetworkPolicyAmendmentReviewDecision(TypedDict, total=False):
    network_policy_amendment: Required[NetworkPolicyAmendmentReviewDecisionNetworkPolicyAmendmentVariant]

ReviewDecision: TypeAlias = "Literal['approved'] | ApprovedExecpolicyAmendmentReviewDecision | Literal['approved_for_session'] | NetworkPolicyAmendmentReviewDecision | Literal['denied'] | Literal['abort']"

class ApplyPatchApprovalResponse(TypedDict, total=False):
    decision: Required[ReviewDecision]

class AppsListParams(TypedDict, total=False):
    cursor: NotRequired[str | None]
    forceRefetch: NotRequired[bool]
    limit: NotRequired[int | None]
    threadId: NotRequired[str | None]

class AppsListResponse(TypedDict, total=False):
    data: Required[list[AppInfo]]
    nextCursor: NotRequired[str | None]

class CancelLoginAccountParams(TypedDict, total=False):
    loginId: Required[str]

CancelLoginAccountStatus: TypeAlias = "Literal['canceled', 'notFound']"

class CancelLoginAccountResponse(TypedDict, total=False):
    status: Required[CancelLoginAccountStatus]

ChatgptAuthTokensRefreshReason: TypeAlias = "Literal['unauthorized']"

class ChatgptAuthTokensRefreshParams(TypedDict, total=False):
    previousAccountId: NotRequired[str | None]
    reason: Required[ChatgptAuthTokensRefreshReason]

class ChatgptAuthTokensRefreshResponse(TypedDict, total=False):
    accessToken: Required[str]
    chatgptAccountId: Required[str]
    chatgptPlanType: NotRequired[str | None]

AbsolutePathBuf: TypeAlias = 'str'

NetworkAccess: TypeAlias = "Literal['restricted', 'enabled']"

class RestrictedReadOnlyAccess(TypedDict, total=False):
    includePlatformDefaults: NotRequired[bool]
    readableRoots: NotRequired[list[AbsolutePathBuf]]
    type: Required[Literal['restricted']]

class FullAccessReadOnlyAccess(TypedDict, total=False):
    type: Required[Literal['fullAccess']]

ReadOnlyAccess: TypeAlias = 'RestrictedReadOnlyAccess | FullAccessReadOnlyAccess'

class DangerFullAccessSandboxPolicy(TypedDict, total=False):
    type: Required[Literal['dangerFullAccess']]

class ReadOnlySandboxPolicy(TypedDict, total=False):
    access: NotRequired[ReadOnlyAccess]
    networkAccess: NotRequired[bool]
    type: Required[Literal['readOnly']]

class ExternalSandboxSandboxPolicy(TypedDict, total=False):
    networkAccess: NotRequired[NetworkAccess]
    type: Required[Literal['externalSandbox']]

class WorkspaceWriteSandboxPolicy(TypedDict, total=False):
    excludeSlashTmp: NotRequired[bool]
    excludeTmpdirEnvVar: NotRequired[bool]
    networkAccess: NotRequired[bool]
    readOnlyAccess: NotRequired[ReadOnlyAccess]
    type: Required[Literal['workspaceWrite']]
    writableRoots: NotRequired[list[AbsolutePathBuf]]

SandboxPolicy: TypeAlias = 'DangerFullAccessSandboxPolicy | ReadOnlySandboxPolicy | ExternalSandboxSandboxPolicy | WorkspaceWriteSandboxPolicy'

class CommandExecParams(TypedDict, total=False):
    command: Required[list[str]]
    cwd: NotRequired[str | None]
    sandboxPolicy: NotRequired[SandboxPolicy | None]
    timeoutMs: NotRequired[int | None]

class CommandExecResponse(TypedDict, total=False):
    exitCode: Required[int]
    stderr: Required[str]
    stdout: Required[str]

class CommandExecutionOutputDeltaNotification(TypedDict, total=False):
    delta: Required[str]
    itemId: Required[str]
    threadId: Required[str]
    turnId: Required[str]

class AdditionalFileSystemPermissions(TypedDict, total=False):
    read: NotRequired[list[AbsolutePathBuf] | None]
    write: NotRequired[list[AbsolutePathBuf] | None]

class AdditionalMacOsPermissions(TypedDict, total=False):
    accessibility: NotRequired[bool | None]
    automations: NotRequired[MacOsAutomationValue | None]
    calendar: NotRequired[bool | None]
    preferences: NotRequired[MacOsPreferencesValue | None]

class AdditionalNetworkPermissions(TypedDict, total=False):
    enabled: NotRequired[bool | None]

class AdditionalPermissionProfile(TypedDict, total=False):
    fileSystem: NotRequired[AdditionalFileSystemPermissions | None]
    macos: NotRequired[AdditionalMacOsPermissions | None]
    network: NotRequired[AdditionalNetworkPermissions | None]

class ReadCommandAction(TypedDict, total=False):
    command: Required[str]
    name: Required[str]
    path: Required[str]
    type: Required[Literal['read']]

class ListFilesCommandAction(TypedDict, total=False):
    command: Required[str]
    path: NotRequired[str | None]
    type: Required[Literal['listFiles']]

class SearchCommandAction(TypedDict, total=False):
    command: Required[str]
    path: NotRequired[str | None]
    query: NotRequired[str | None]
    type: Required[Literal['search']]

class UnknownCommandAction(TypedDict, total=False):
    command: Required[str]
    type: Required[Literal['unknown']]

CommandAction: TypeAlias = 'ReadCommandAction | ListFilesCommandAction | SearchCommandAction | UnknownCommandAction'

class AcceptWithExecpolicyAmendmentCommandExecutionApprovalDecisionAcceptWithExecpolicyAmendmentVariant(TypedDict, total=False):
    execpolicy_amendment: Required[list[str]]

class AcceptWithExecpolicyAmendmentCommandExecutionApprovalDecision(TypedDict, total=False):
    acceptWithExecpolicyAmendment: Required[AcceptWithExecpolicyAmendmentCommandExecutionApprovalDecisionAcceptWithExecpolicyAmendmentVariant]

class ApplyNetworkPolicyAmendmentCommandExecutionApprovalDecisionApplyNetworkPolicyAmendmentVariant(TypedDict, total=False):
    network_policy_amendment: Required[NetworkPolicyAmendment]

class ApplyNetworkPolicyAmendmentCommandExecutionApprovalDecision(TypedDict, total=False):
    applyNetworkPolicyAmendment: Required[ApplyNetworkPolicyAmendmentCommandExecutionApprovalDecisionApplyNetworkPolicyAmendmentVariant]

CommandExecutionApprovalDecision: TypeAlias = "Literal['accept'] | Literal['acceptForSession'] | AcceptWithExecpolicyAmendmentCommandExecutionApprovalDecision | ApplyNetworkPolicyAmendmentCommandExecutionApprovalDecision | Literal['decline'] | Literal['cancel']"

MacOsAutomationValue: TypeAlias = 'bool | list[str]'

MacOsPreferencesValue: TypeAlias = 'bool | str'

class NetworkApprovalContext(TypedDict, total=False):
    host: Required[str]
    protocol: Required[NetworkApprovalProtocol]

NetworkApprovalProtocol: TypeAlias = "Literal['http', 'https', 'socks5Tcp', 'socks5Udp']"

class CommandExecutionRequestApprovalParams(TypedDict, total=False):
    turnId: Required[str]
    approvalId: NotRequired[str | None]
    threadId: Required[str]
    command: NotRequired[str | None]
    commandActions: NotRequired[list[CommandAction] | None]
    cwd: NotRequired[str | None]
    itemId: Required[str]
    networkApprovalContext: NotRequired[NetworkApprovalContext | None]
    proposedExecpolicyAmendment: NotRequired[list[str] | None]
    proposedNetworkPolicyAmendments: NotRequired[list[NetworkPolicyAmendment] | None]
    reason: NotRequired[str | None]

class CommandExecutionRequestApprovalResponse(TypedDict, total=False):
    decision: Required[CommandExecutionApprovalDecision]

class ConfigEdit(TypedDict, total=False):
    keyPath: Required[str]
    mergeStrategy: Required[MergeStrategy]
    value: Required[Any]

MergeStrategy: TypeAlias = "Literal['replace', 'upsert']"

class ConfigBatchWriteParams(TypedDict, total=False):
    edits: Required[list[ConfigEdit]]
    expectedVersion: NotRequired[str | None]
    filePath: NotRequired[str | None]

class ConfigReadParams(TypedDict, total=False):
    cwd: NotRequired[str | None]
    includeLayers: NotRequired[bool]

AnalyticsConfig: TypeAlias = 'dict[str, JSONValue]'

class AppConfig(TypedDict, total=False):
    default_tools_approval_mode: NotRequired[AppToolApproval | None]
    default_tools_enabled: NotRequired[bool | None]
    destructive_enabled: NotRequired[bool | None]
    enabled: NotRequired[bool]
    open_world_enabled: NotRequired[bool | None]
    tools: NotRequired[AppToolsConfig | None]

AppToolApproval: TypeAlias = "Literal['auto', 'prompt', 'approve']"

class AppToolConfig(TypedDict, total=False):
    approval_mode: NotRequired[AppToolApproval | None]
    enabled: NotRequired[bool | None]

AppToolsConfig: TypeAlias = 'dict[str, JSONValue]'

class AppsConfig(TypedDict, total=False):
    _default: NotRequired[AppsDefaultConfig | None]

class AppsDefaultConfig(TypedDict, total=False):
    destructive_enabled: NotRequired[bool]
    enabled: NotRequired[bool]
    open_world_enabled: NotRequired[bool]

class RejectAskForApprovalRejectVariant(TypedDict, total=False):
    mcp_elicitations: Required[bool]
    rules: Required[bool]
    sandbox_approval: Required[bool]

class RejectAskForApproval(TypedDict, total=False):
    reject: Required[RejectAskForApprovalRejectVariant]

AskForApproval: TypeAlias = "Literal['untrusted', 'on-failure', 'on-request', 'never'] | RejectAskForApproval"

Config: TypeAlias = 'dict[str, JSONValue]'

class ConfigLayer(TypedDict, total=False):
    config: Required[Any]
    disabledReason: NotRequired[str | None]
    name: Required[ConfigLayerSource]
    version: Required[str]

class ConfigLayerMetadata(TypedDict, total=False):
    name: Required[ConfigLayerSource]
    version: Required[str]

class MdmConfigLayerSource(TypedDict, total=False):
    domain: Required[str]
    key: Required[str]
    type: Required[Literal['mdm']]

class SystemConfigLayerSource(TypedDict, total=False):
    file: Required[AbsolutePathBuf]
    type: Required[Literal['system']]

class UserConfigLayerSource(TypedDict, total=False):
    file: Required[AbsolutePathBuf]
    type: Required[Literal['user']]

class ProjectConfigLayerSource(TypedDict, total=False):
    dotCodexFolder: Required[AbsolutePathBuf]
    type: Required[Literal['project']]

class SessionFlagsConfigLayerSource(TypedDict, total=False):
    type: Required[Literal['sessionFlags']]

class LegacyManagedConfigTomlFromFileConfigLayerSource(TypedDict, total=False):
    file: Required[AbsolutePathBuf]
    type: Required[Literal['legacyManagedConfigTomlFromFile']]

class LegacyManagedConfigTomlFromMdmConfigLayerSource(TypedDict, total=False):
    type: Required[Literal['legacyManagedConfigTomlFromMdm']]

ConfigLayerSource: TypeAlias = 'MdmConfigLayerSource | SystemConfigLayerSource | UserConfigLayerSource | ProjectConfigLayerSource | SessionFlagsConfigLayerSource | LegacyManagedConfigTomlFromFileConfigLayerSource | LegacyManagedConfigTomlFromMdmConfigLayerSource'

ForcedLoginMethod: TypeAlias = "Literal['chatgpt', 'api']"

ProfileV2: TypeAlias = 'dict[str, JSONValue]'

ReasoningEffort: TypeAlias = "Literal['none', 'minimal', 'low', 'medium', 'high', 'xhigh']"

ReasoningSummary: TypeAlias = "Literal['auto', 'concise', 'detailed'] | Literal['none']"

SandboxMode: TypeAlias = "Literal['read-only', 'workspace-write', 'danger-full-access']"

class SandboxWorkspaceWrite(TypedDict, total=False):
    exclude_slash_tmp: NotRequired[bool]
    exclude_tmpdir_env_var: NotRequired[bool]
    network_access: NotRequired[bool]
    writable_roots: NotRequired[list[str]]

ServiceTier: TypeAlias = "Literal['fast', 'flex']"

class ToolsV2(TypedDict, total=False):
    view_image: NotRequired[bool | None]
    web_search: NotRequired[bool | None]

Verbosity: TypeAlias = "Literal['low', 'medium', 'high']"

WebSearchMode: TypeAlias = "Literal['disabled', 'cached', 'live']"

class ConfigReadResponse(TypedDict, total=False):
    config: Required[Config]
    layers: NotRequired[list[ConfigLayer] | None]
    origins: Required[dict[str, ConfigLayerMetadata]]

class ConfigRequirements(TypedDict, total=False):
    allowedApprovalPolicies: NotRequired[list[AskForApproval] | None]
    allowedSandboxModes: NotRequired[list[SandboxMode] | None]
    allowedWebSearchModes: NotRequired[list[WebSearchMode] | None]
    enforceResidency: NotRequired[ResidencyRequirement | None]
    featureRequirements: NotRequired[dict[str, bool] | None]

class NetworkRequirements(TypedDict, total=False):
    allowLocalBinding: NotRequired[bool | None]
    allowUnixSockets: NotRequired[list[str] | None]
    allowUpstreamProxy: NotRequired[bool | None]
    allowedDomains: NotRequired[list[str] | None]
    dangerouslyAllowAllUnixSockets: NotRequired[bool | None]
    dangerouslyAllowNonLoopbackAdmin: NotRequired[bool | None]
    dangerouslyAllowNonLoopbackProxy: NotRequired[bool | None]
    deniedDomains: NotRequired[list[str] | None]
    enabled: NotRequired[bool | None]
    httpPort: NotRequired[int | None]
    socksPort: NotRequired[int | None]

ResidencyRequirement: TypeAlias = "Literal['us']"

class ConfigRequirementsReadResponse(TypedDict, total=False):
    requirements: NotRequired[ConfigRequirements | None]

class ConfigValueWriteParams(TypedDict, total=False):
    expectedVersion: NotRequired[str | None]
    filePath: NotRequired[str | None]
    keyPath: Required[str]
    mergeStrategy: Required[MergeStrategy]
    value: Required[Any]

class TextPosition(TypedDict, total=False):
    column: Required[int]
    line: Required[int]

class TextRange(TypedDict, total=False):
    end: Required[TextPosition]
    start: Required[TextPosition]

class ConfigWarningNotification(TypedDict, total=False):
    details: NotRequired[str | None]
    path: NotRequired[str | None]
    range: NotRequired[TextRange | None]
    summary: Required[str]

class OverriddenMetadata(TypedDict, total=False):
    effectiveValue: Required[Any]
    message: Required[str]
    overridingLayer: Required[ConfigLayerMetadata]

WriteStatus: TypeAlias = "Literal['ok', 'okOverridden']"

class ConfigWriteResponse(TypedDict, total=False):
    filePath: Required[AbsolutePathBuf]
    overriddenMetadata: NotRequired[OverriddenMetadata | None]
    status: Required[WriteStatus]
    version: Required[str]

class ContextCompactedNotification(TypedDict, total=False):
    threadId: Required[str]
    turnId: Required[str]

class DeprecationNoticeNotification(TypedDict, total=False):
    details: NotRequired[str | None]
    summary: Required[str]

class DynamicToolCallParams(TypedDict, total=False):
    arguments: Required[Any]
    callId: Required[str]
    threadId: Required[str]
    tool: Required[str]
    turnId: Required[str]

class InputTextDynamicToolCallOutputContentItem(TypedDict, total=False):
    text: Required[str]
    type: Required[Literal['inputText']]

class InputImageDynamicToolCallOutputContentItem(TypedDict, total=False):
    imageUrl: Required[str]
    type: Required[Literal['inputImage']]

DynamicToolCallOutputContentItem: TypeAlias = 'InputTextDynamicToolCallOutputContentItem | InputImageDynamicToolCallOutputContentItem'

class DynamicToolCallResponse(TypedDict, total=False):
    contentItems: Required[list[DynamicToolCallOutputContentItem]]
    success: Required[bool]

class HttpConnectionFailedCodexErrorInfoHttpConnectionFailedVariant(TypedDict, total=False):
    httpStatusCode: NotRequired[int | None]

class HttpConnectionFailedCodexErrorInfo(TypedDict, total=False):
    httpConnectionFailed: Required[HttpConnectionFailedCodexErrorInfoHttpConnectionFailedVariant]

class ResponseStreamConnectionFailedCodexErrorInfoResponseStreamConnectionFailedVariant(TypedDict, total=False):
    httpStatusCode: NotRequired[int | None]

class ResponseStreamConnectionFailedCodexErrorInfo(TypedDict, total=False):
    responseStreamConnectionFailed: Required[ResponseStreamConnectionFailedCodexErrorInfoResponseStreamConnectionFailedVariant]

class ResponseStreamDisconnectedCodexErrorInfoResponseStreamDisconnectedVariant(TypedDict, total=False):
    httpStatusCode: NotRequired[int | None]

class ResponseStreamDisconnectedCodexErrorInfo(TypedDict, total=False):
    responseStreamDisconnected: Required[ResponseStreamDisconnectedCodexErrorInfoResponseStreamDisconnectedVariant]

class ResponseTooManyFailedAttemptsCodexErrorInfoResponseTooManyFailedAttemptsVariant(TypedDict, total=False):
    httpStatusCode: NotRequired[int | None]

class ResponseTooManyFailedAttemptsCodexErrorInfo(TypedDict, total=False):
    responseTooManyFailedAttempts: Required[ResponseTooManyFailedAttemptsCodexErrorInfoResponseTooManyFailedAttemptsVariant]

CodexErrorInfo: TypeAlias = "Literal['contextWindowExceeded', 'usageLimitExceeded', 'serverOverloaded', 'internalServerError', 'unauthorized', 'badRequest', 'threadRollbackFailed', 'sandboxError', 'other'] | HttpConnectionFailedCodexErrorInfo | ResponseStreamConnectionFailedCodexErrorInfo | ResponseStreamDisconnectedCodexErrorInfo | ResponseTooManyFailedAttemptsCodexErrorInfo"

class TurnError(TypedDict, total=False):
    additionalDetails: NotRequired[str | None]
    codexErrorInfo: NotRequired[CodexErrorInfo | None]
    message: Required[str]

class ErrorNotification(TypedDict, total=False):
    error: Required[TurnError]
    threadId: Required[str]
    turnId: Required[str]
    willRetry: Required[bool]

class TextAgentMessageContent(TypedDict, total=False):
    text: Required[str]
    type: Required[Literal['Text']]

AgentMessageContent: TypeAlias = 'TextAgentMessageContent'

class CompletedAgentStatus(TypedDict, total=False):
    completed: Required[str | None]

class ErroredAgentStatus(TypedDict, total=False):
    errored: Required[str]

AgentStatus: TypeAlias = "Literal['pending_init'] | Literal['running'] | CompletedAgentStatus | ErroredAgentStatus | Literal['shutdown'] | Literal['not_found']"

class ByteRange(TypedDict, total=False):
    end: Required[int]
    start: Required[int]

class CallToolResult(TypedDict, total=False):
    _meta: NotRequired[Any]
    content: Required[list[Any]]
    isError: NotRequired[bool | None]
    structuredContent: NotRequired[Any]

class CollabAgentRef(TypedDict, total=False):
    agent_nickname: NotRequired[str | None]
    agent_role: NotRequired[str | None]
    thread_id: Required[ThreadId]

class CollabAgentStatusEntry(TypedDict, total=False):
    agent_nickname: NotRequired[str | None]
    agent_role: NotRequired[str | None]
    status: Required[AgentStatus]
    thread_id: Required[ThreadId]

class InputTextContentItem(TypedDict, total=False):
    text: Required[str]
    type: Required[Literal['input_text']]

class InputImageContentItem(TypedDict, total=False):
    image_url: Required[str]
    type: Required[Literal['input_image']]

class OutputTextContentItem(TypedDict, total=False):
    text: Required[str]
    type: Required[Literal['output_text']]

ContentItem: TypeAlias = 'InputTextContentItem | InputImageContentItem | OutputTextContentItem'

class CustomPrompt(TypedDict, total=False):
    argument_hint: NotRequired[str | None]
    content: Required[str]
    description: NotRequired[str | None]
    name: Required[str]
    path: Required[str]

class Duration(TypedDict, total=False):
    nanos: Required[int]
    secs: Required[int]

class ElicitationRequestVariant(TypedDict, total=False):
    message: Required[str]
    mode: Required[Literal['form']]
    requested_schema: Required[Any]

class ElicitationRequestVariant2(TypedDict, total=False):
    elicitation_id: Required[str]
    message: Required[str]
    mode: Required[Literal['url']]
    url: Required[str]

ElicitationRequest: TypeAlias = 'ElicitationRequestVariant | ElicitationRequestVariant2'

class ErrorEventMsg(TypedDict, total=False):
    codex_error_info: NotRequired[CodexErrorInfo | None]
    message: Required[str]
    type: Required[Literal['error']]

class WarningEventMsg(TypedDict, total=False):
    message: Required[str]
    type: Required[Literal['warning']]

class RealtimeConversationStartedEventMsg(TypedDict, total=False):
    session_id: NotRequired[str | None]
    type: Required[Literal['realtime_conversation_started']]

class RealtimeConversationRealtimeEventMsg(TypedDict, total=False):
    payload: Required[RealtimeEvent]
    type: Required[Literal['realtime_conversation_realtime']]

class RealtimeConversationClosedEventMsg(TypedDict, total=False):
    reason: NotRequired[str | None]
    type: Required[Literal['realtime_conversation_closed']]

class ModelRerouteEventMsg(TypedDict, total=False):
    from_model: Required[str]
    reason: Required[ModelRerouteReason]
    to_model: Required[str]
    type: Required[Literal['model_reroute']]

class ContextCompactedEventMsg(TypedDict, total=False):
    type: Required[Literal['context_compacted']]

class ThreadRolledBackEventMsg(TypedDict, total=False):
    num_turns: Required[int]
    type: Required[Literal['thread_rolled_back']]

class TaskStartedEventMsg(TypedDict, total=False):
    collaboration_mode_kind: NotRequired[ModeKind]
    model_context_window: NotRequired[int | None]
    turn_id: Required[str]
    type: Required[Literal['task_started']]

class TaskCompleteEventMsg(TypedDict, total=False):
    last_agent_message: NotRequired[str | None]
    turn_id: Required[str]
    type: Required[Literal['task_complete']]

class TokenCountEventMsg(TypedDict, total=False):
    info: NotRequired[TokenUsageInfo | None]
    rate_limits: NotRequired[RateLimitSnapshot | None]
    type: Required[Literal['token_count']]

class AgentMessageEventMsg(TypedDict, total=False):
    message: Required[str]
    phase: NotRequired[MessagePhase | None]
    type: Required[Literal['agent_message']]

class UserMessageEventMsg(TypedDict, total=False):
    images: NotRequired[list[str] | None]
    local_images: NotRequired[list[str]]
    message: Required[str]
    text_elements: NotRequired[list[TextElement]]
    type: Required[Literal['user_message']]

class AgentMessageDeltaEventMsg(TypedDict, total=False):
    delta: Required[str]
    type: Required[Literal['agent_message_delta']]

class AgentReasoningEventMsg(TypedDict, total=False):
    text: Required[str]
    type: Required[Literal['agent_reasoning']]

class AgentReasoningDeltaEventMsg(TypedDict, total=False):
    delta: Required[str]
    type: Required[Literal['agent_reasoning_delta']]

class AgentReasoningRawContentEventMsg(TypedDict, total=False):
    text: Required[str]
    type: Required[Literal['agent_reasoning_raw_content']]

class AgentReasoningRawContentDeltaEventMsg(TypedDict, total=False):
    delta: Required[str]
    type: Required[Literal['agent_reasoning_raw_content_delta']]

class AgentReasoningSectionBreakEventMsg(TypedDict, total=False):
    item_id: NotRequired[str]
    summary_index: NotRequired[int]
    type: Required[Literal['agent_reasoning_section_break']]

class SessionConfiguredEventMsg(TypedDict, total=False):
    approval_policy: Required[AskForApproval]
    cwd: Required[str]
    forked_from_id: NotRequired[ThreadId | None]
    history_entry_count: Required[int]
    history_log_id: Required[int]
    initial_messages: NotRequired[list[EventMsg] | None]
    model: Required[str]
    model_provider_id: Required[str]
    network_proxy: NotRequired[SessionNetworkProxyRuntime | None]
    reasoning_effort: NotRequired[ReasoningEffort | None]
    rollout_path: NotRequired[str | None]
    sandbox_policy: Required[SandboxPolicy]
    service_tier: NotRequired[ServiceTier | None]
    session_id: Required[ThreadId]
    thread_name: NotRequired[str | None]
    type: Required[Literal['session_configured']]

class ThreadNameUpdatedEventMsg(TypedDict, total=False):
    thread_id: Required[ThreadId]
    thread_name: NotRequired[str | None]
    type: Required[Literal['thread_name_updated']]

class McpStartupUpdateEventMsg(TypedDict, total=False):
    server: Required[str]
    status: Required[McpStartupStatus]
    type: Required[Literal['mcp_startup_update']]

class McpStartupCompleteEventMsg(TypedDict, total=False):
    cancelled: Required[list[str]]
    failed: Required[list[McpStartupFailure]]
    ready: Required[list[str]]
    type: Required[Literal['mcp_startup_complete']]

class McpToolCallBeginEventMsg(TypedDict, total=False):
    call_id: Required[str]
    invocation: Required[McpInvocation]
    type: Required[Literal['mcp_tool_call_begin']]

class McpToolCallEndEventMsg(TypedDict, total=False):
    call_id: Required[str]
    duration: Required[Duration]
    invocation: Required[McpInvocation]
    result: Required[ResultOfCallToolResultOrString]
    type: Required[Literal['mcp_tool_call_end']]

class WebSearchBeginEventMsg(TypedDict, total=False):
    call_id: Required[str]
    type: Required[Literal['web_search_begin']]

class WebSearchEndEventMsg(TypedDict, total=False):
    action: Required[WebSearchAction]
    call_id: Required[str]
    query: Required[str]
    type: Required[Literal['web_search_end']]

class ImageGenerationBeginEventMsg(TypedDict, total=False):
    call_id: Required[str]
    type: Required[Literal['image_generation_begin']]

class ImageGenerationEndEventMsg(TypedDict, total=False):
    call_id: Required[str]
    result: Required[str]
    revised_prompt: NotRequired[str | None]
    status: Required[str]
    type: Required[Literal['image_generation_end']]

class ExecCommandBeginEventMsg(TypedDict, total=False):
    call_id: Required[str]
    command: Required[list[str]]
    cwd: Required[str]
    interaction_input: NotRequired[str | None]
    parsed_cmd: Required[list[ParsedCommand]]
    process_id: NotRequired[str | None]
    source: NotRequired[ExecCommandSource]
    turn_id: Required[str]
    type: Required[Literal['exec_command_begin']]

class ExecCommandOutputDeltaEventMsg(TypedDict, total=False):
    call_id: Required[str]
    chunk: Required[str]
    stream: Required[ExecOutputStream]
    type: Required[Literal['exec_command_output_delta']]

class TerminalInteractionEventMsg(TypedDict, total=False):
    call_id: Required[str]
    process_id: Required[str]
    stdin: Required[str]
    type: Required[Literal['terminal_interaction']]

class ExecCommandEndEventMsg(TypedDict, total=False):
    aggregated_output: NotRequired[str]
    call_id: Required[str]
    command: Required[list[str]]
    cwd: Required[str]
    duration: Required[Duration]
    exit_code: Required[int]
    formatted_output: Required[str]
    interaction_input: NotRequired[str | None]
    parsed_cmd: Required[list[ParsedCommand]]
    process_id: NotRequired[str | None]
    source: NotRequired[ExecCommandSource]
    status: Required[ExecCommandStatus]
    stderr: Required[str]
    stdout: Required[str]
    turn_id: Required[str]
    type: Required[Literal['exec_command_end']]

class ViewImageToolCallEventMsg(TypedDict, total=False):
    call_id: Required[str]
    path: Required[str]
    type: Required[Literal['view_image_tool_call']]

class ExecApprovalRequestEventMsg(TypedDict, total=False):
    additional_permissions: NotRequired[PermissionProfile | None]
    approval_id: NotRequired[str | None]
    available_decisions: NotRequired[list[ReviewDecision] | None]
    call_id: Required[str]
    command: Required[list[str]]
    cwd: Required[str]
    network_approval_context: NotRequired[NetworkApprovalContext | None]
    parsed_cmd: Required[list[ParsedCommand]]
    proposed_execpolicy_amendment: NotRequired[list[str] | None]
    proposed_network_policy_amendments: NotRequired[list[NetworkPolicyAmendment] | None]
    reason: NotRequired[str | None]
    turn_id: NotRequired[str]
    type: Required[Literal['exec_approval_request']]

class RequestUserInputEventMsg(TypedDict, total=False):
    call_id: Required[str]
    questions: Required[list[RequestUserInputQuestion]]
    turn_id: NotRequired[str]
    type: Required[Literal['request_user_input']]

class DynamicToolCallRequestEventMsg(TypedDict, total=False):
    arguments: Required[Any]
    callId: Required[str]
    tool: Required[str]
    turnId: Required[str]
    type: Required[Literal['dynamic_tool_call_request']]

class DynamicToolCallResponseEventMsg(TypedDict, total=False):
    arguments: Required[JSONValue]
    call_id: Required[str]
    content_items: Required[list[DynamicToolCallOutputContentItem]]
    duration: Required[Duration]
    error: NotRequired[str | None]
    success: Required[bool]
    tool: Required[str]
    turn_id: Required[str]
    type: Required[Literal['dynamic_tool_call_response']]

class ElicitationRequestEventMsg(TypedDict, total=False):
    id: Required[RequestId]
    request: Required[ElicitationRequest]
    server_name: Required[str]
    type: Required[Literal['elicitation_request']]

class ApplyPatchApprovalRequestEventMsg(TypedDict, total=False):
    call_id: Required[str]
    changes: Required[dict[str, FileChange]]
    grant_root: NotRequired[str | None]
    reason: NotRequired[str | None]
    turn_id: NotRequired[str]
    type: Required[Literal['apply_patch_approval_request']]

class DeprecationNoticeEventMsg(TypedDict, total=False):
    details: NotRequired[str | None]
    summary: Required[str]
    type: Required[Literal['deprecation_notice']]

class BackgroundEventEventMsg(TypedDict, total=False):
    message: Required[str]
    type: Required[Literal['background_event']]

class UndoStartedEventMsg(TypedDict, total=False):
    message: NotRequired[str | None]
    type: Required[Literal['undo_started']]

class UndoCompletedEventMsg(TypedDict, total=False):
    message: NotRequired[str | None]
    success: Required[bool]
    type: Required[Literal['undo_completed']]

class StreamErrorEventMsg(TypedDict, total=False):
    additional_details: NotRequired[str | None]
    codex_error_info: NotRequired[CodexErrorInfo | None]
    message: Required[str]
    type: Required[Literal['stream_error']]

class PatchApplyBeginEventMsg(TypedDict, total=False):
    auto_approved: Required[bool]
    call_id: Required[str]
    changes: Required[dict[str, FileChange]]
    turn_id: NotRequired[str]
    type: Required[Literal['patch_apply_begin']]

class PatchApplyEndEventMsg(TypedDict, total=False):
    call_id: Required[str]
    changes: NotRequired[dict[str, FileChange]]
    status: Required[PatchApplyStatus]
    stderr: Required[str]
    stdout: Required[str]
    success: Required[bool]
    turn_id: NotRequired[str]
    type: Required[Literal['patch_apply_end']]

class TurnDiffEventMsg(TypedDict, total=False):
    type: Required[Literal['turn_diff']]
    unified_diff: Required[str]

class GetHistoryEntryResponseEventMsg(TypedDict, total=False):
    entry: NotRequired[HistoryEntry | None]
    log_id: Required[int]
    offset: Required[int]
    type: Required[Literal['get_history_entry_response']]

class McpListToolsResponseEventMsg(TypedDict, total=False):
    auth_statuses: Required[dict[str, McpAuthStatus]]
    resource_templates: Required[dict[str, list[ResourceTemplate]]]
    resources: Required[dict[str, list[Resource]]]
    tools: Required[dict[str, Tool]]
    type: Required[Literal['mcp_list_tools_response']]

class ListCustomPromptsResponseEventMsg(TypedDict, total=False):
    custom_prompts: Required[list[CustomPrompt]]
    type: Required[Literal['list_custom_prompts_response']]

class ListSkillsResponseEventMsg(TypedDict, total=False):
    skills: Required[list[SkillsListEntry]]
    type: Required[Literal['list_skills_response']]

class ListRemoteSkillsResponseEventMsg(TypedDict, total=False):
    skills: Required[list[RemoteSkillSummary]]
    type: Required[Literal['list_remote_skills_response']]

class RemoteSkillDownloadedEventMsg(TypedDict, total=False):
    id: Required[str]
    name: Required[str]
    path: Required[str]
    type: Required[Literal['remote_skill_downloaded']]

class SkillsUpdateAvailableEventMsg(TypedDict, total=False):
    type: Required[Literal['skills_update_available']]

class PlanUpdateEventMsg(TypedDict, total=False):
    explanation: NotRequired[str | None]
    plan: Required[list[PlanItemArg]]
    type: Required[Literal['plan_update']]

class TurnAbortedEventMsg(TypedDict, total=False):
    reason: Required[TurnAbortReason]
    turn_id: NotRequired[str | None]
    type: Required[Literal['turn_aborted']]

class ShutdownCompleteEventMsg(TypedDict, total=False):
    type: Required[Literal['shutdown_complete']]

class EnteredReviewModeEventMsg(TypedDict, total=False):
    target: Required[ReviewTarget]
    type: Required[Literal['entered_review_mode']]
    user_facing_hint: NotRequired[str | None]

class ExitedReviewModeEventMsg(TypedDict, total=False):
    review_output: NotRequired[ReviewOutputEvent | None]
    type: Required[Literal['exited_review_mode']]

class RawResponseItemEventMsg(TypedDict, total=False):
    item: Required[ResponseItem]
    type: Required[Literal['raw_response_item']]

class ItemStartedEventMsg(TypedDict, total=False):
    item: Required[TurnItem]
    thread_id: Required[ThreadId]
    turn_id: Required[str]
    type: Required[Literal['item_started']]

class ItemCompletedEventMsg(TypedDict, total=False):
    item: Required[TurnItem]
    thread_id: Required[ThreadId]
    turn_id: Required[str]
    type: Required[Literal['item_completed']]

class AgentMessageContentDeltaEventMsg(TypedDict, total=False):
    delta: Required[str]
    item_id: Required[str]
    thread_id: Required[str]
    turn_id: Required[str]
    type: Required[Literal['agent_message_content_delta']]

class PlanDeltaEventMsg(TypedDict, total=False):
    delta: Required[str]
    item_id: Required[str]
    thread_id: Required[str]
    turn_id: Required[str]
    type: Required[Literal['plan_delta']]

class ReasoningContentDeltaEventMsg(TypedDict, total=False):
    delta: Required[str]
    item_id: Required[str]
    summary_index: NotRequired[int]
    thread_id: Required[str]
    turn_id: Required[str]
    type: Required[Literal['reasoning_content_delta']]

class ReasoningRawContentDeltaEventMsg(TypedDict, total=False):
    content_index: NotRequired[int]
    delta: Required[str]
    item_id: Required[str]
    thread_id: Required[str]
    turn_id: Required[str]
    type: Required[Literal['reasoning_raw_content_delta']]

class CollabAgentSpawnBeginEventMsg(TypedDict, total=False):
    call_id: Required[str]
    prompt: Required[str]
    sender_thread_id: Required[ThreadId]
    type: Required[Literal['collab_agent_spawn_begin']]

class CollabAgentSpawnEndEventMsg(TypedDict, total=False):
    call_id: Required[str]
    new_agent_nickname: NotRequired[str | None]
    new_agent_role: NotRequired[str | None]
    new_thread_id: NotRequired[ThreadId | None]
    prompt: Required[str]
    sender_thread_id: Required[ThreadId]
    status: Required[AgentStatus]
    type: Required[Literal['collab_agent_spawn_end']]

class CollabAgentInteractionBeginEventMsg(TypedDict, total=False):
    call_id: Required[str]
    prompt: Required[str]
    receiver_thread_id: Required[ThreadId]
    sender_thread_id: Required[ThreadId]
    type: Required[Literal['collab_agent_interaction_begin']]

class CollabAgentInteractionEndEventMsg(TypedDict, total=False):
    call_id: Required[str]
    prompt: Required[str]
    receiver_agent_nickname: NotRequired[str | None]
    receiver_agent_role: NotRequired[str | None]
    receiver_thread_id: Required[ThreadId]
    sender_thread_id: Required[ThreadId]
    status: Required[AgentStatus]
    type: Required[Literal['collab_agent_interaction_end']]

class CollabWaitingBeginEventMsg(TypedDict, total=False):
    call_id: Required[str]
    receiver_agents: NotRequired[list[CollabAgentRef]]
    receiver_thread_ids: Required[list[ThreadId]]
    sender_thread_id: Required[ThreadId]
    type: Required[Literal['collab_waiting_begin']]

class CollabWaitingEndEventMsg(TypedDict, total=False):
    agent_statuses: NotRequired[list[CollabAgentStatusEntry]]
    call_id: Required[str]
    sender_thread_id: Required[ThreadId]
    statuses: Required[dict[str, AgentStatus]]
    type: Required[Literal['collab_waiting_end']]

class CollabCloseBeginEventMsg(TypedDict, total=False):
    call_id: Required[str]
    receiver_thread_id: Required[ThreadId]
    sender_thread_id: Required[ThreadId]
    type: Required[Literal['collab_close_begin']]

class CollabCloseEndEventMsg(TypedDict, total=False):
    call_id: Required[str]
    receiver_agent_nickname: NotRequired[str | None]
    receiver_agent_role: NotRequired[str | None]
    receiver_thread_id: Required[ThreadId]
    sender_thread_id: Required[ThreadId]
    status: Required[AgentStatus]
    type: Required[Literal['collab_close_end']]

class CollabResumeBeginEventMsg(TypedDict, total=False):
    call_id: Required[str]
    receiver_agent_nickname: NotRequired[str | None]
    receiver_agent_role: NotRequired[str | None]
    receiver_thread_id: Required[ThreadId]
    sender_thread_id: Required[ThreadId]
    type: Required[Literal['collab_resume_begin']]

class CollabResumeEndEventMsg(TypedDict, total=False):
    call_id: Required[str]
    receiver_agent_nickname: NotRequired[str | None]
    receiver_agent_role: NotRequired[str | None]
    receiver_thread_id: Required[ThreadId]
    sender_thread_id: Required[ThreadId]
    status: Required[AgentStatus]
    type: Required[Literal['collab_resume_end']]

EventMsg: TypeAlias = 'ErrorEventMsg | WarningEventMsg | RealtimeConversationStartedEventMsg | RealtimeConversationRealtimeEventMsg | RealtimeConversationClosedEventMsg | ModelRerouteEventMsg | ContextCompactedEventMsg | ThreadRolledBackEventMsg | TaskStartedEventMsg | TaskCompleteEventMsg | TokenCountEventMsg | AgentMessageEventMsg | UserMessageEventMsg | AgentMessageDeltaEventMsg | AgentReasoningEventMsg | AgentReasoningDeltaEventMsg | AgentReasoningRawContentEventMsg | AgentReasoningRawContentDeltaEventMsg | AgentReasoningSectionBreakEventMsg | SessionConfiguredEventMsg | ThreadNameUpdatedEventMsg | McpStartupUpdateEventMsg | McpStartupCompleteEventMsg | McpToolCallBeginEventMsg | McpToolCallEndEventMsg | WebSearchBeginEventMsg | WebSearchEndEventMsg | ImageGenerationBeginEventMsg | ImageGenerationEndEventMsg | ExecCommandBeginEventMsg | ExecCommandOutputDeltaEventMsg | TerminalInteractionEventMsg | ExecCommandEndEventMsg | ViewImageToolCallEventMsg | ExecApprovalRequestEventMsg | RequestUserInputEventMsg | DynamicToolCallRequestEventMsg | DynamicToolCallResponseEventMsg | ElicitationRequestEventMsg | ApplyPatchApprovalRequestEventMsg | DeprecationNoticeEventMsg | BackgroundEventEventMsg | UndoStartedEventMsg | UndoCompletedEventMsg | StreamErrorEventMsg | PatchApplyBeginEventMsg | PatchApplyEndEventMsg | TurnDiffEventMsg | GetHistoryEntryResponseEventMsg | McpListToolsResponseEventMsg | ListCustomPromptsResponseEventMsg | ListSkillsResponseEventMsg | ListRemoteSkillsResponseEventMsg | RemoteSkillDownloadedEventMsg | SkillsUpdateAvailableEventMsg | PlanUpdateEventMsg | TurnAbortedEventMsg | ShutdownCompleteEventMsg | EnteredReviewModeEventMsg | ExitedReviewModeEventMsg | RawResponseItemEventMsg | ItemStartedEventMsg | ItemCompletedEventMsg | AgentMessageContentDeltaEventMsg | PlanDeltaEventMsg | ReasoningContentDeltaEventMsg | ReasoningRawContentDeltaEventMsg | CollabAgentSpawnBeginEventMsg | CollabAgentSpawnEndEventMsg | CollabAgentInteractionBeginEventMsg | CollabAgentInteractionEndEventMsg | CollabWaitingBeginEventMsg | CollabWaitingEndEventMsg | CollabCloseBeginEventMsg | CollabCloseEndEventMsg | CollabResumeBeginEventMsg | CollabResumeEndEventMsg'

ExecCommandSource: TypeAlias = "Literal['agent', 'user_shell', 'unified_exec_startup', 'unified_exec_interaction']"

ExecCommandStatus: TypeAlias = "Literal['completed', 'failed', 'declined']"

ExecOutputStream: TypeAlias = "Literal['stdout', 'stderr']"

class FileSystemPermissions(TypedDict, total=False):
    read: NotRequired[list[AbsolutePathBuf] | None]
    write: NotRequired[list[AbsolutePathBuf] | None]

FunctionCallOutputBody: TypeAlias = 'str | list[FunctionCallOutputContentItem]'

class InputTextFunctionCallOutputContentItem(TypedDict, total=False):
    text: Required[str]
    type: Required[Literal['input_text']]

class InputImageFunctionCallOutputContentItem(TypedDict, total=False):
    detail: NotRequired[ImageDetail | None]
    image_url: Required[str]
    type: Required[Literal['input_image']]

FunctionCallOutputContentItem: TypeAlias = 'InputTextFunctionCallOutputContentItem | InputImageFunctionCallOutputContentItem'

class FunctionCallOutputPayload(TypedDict, total=False):
    body: Required[FunctionCallOutputBody]
    success: NotRequired[bool | None]

class GhostCommit(TypedDict, total=False):
    id: Required[str]
    parent: NotRequired[str | None]
    preexisting_untracked_dirs: Required[list[str]]
    preexisting_untracked_files: Required[list[str]]

class HistoryEntry(TypedDict, total=False):
    conversation_id: Required[str]
    text: Required[str]
    ts: Required[int]

ImageDetail: TypeAlias = "Literal['auto', 'low', 'high', 'original']"

class ExecLocalShellAction(TypedDict, total=False):
    command: Required[list[str]]
    env: NotRequired[dict[str, str] | None]
    timeout_ms: NotRequired[int | None]
    type: Required[Literal['exec']]
    user: NotRequired[str | None]
    working_directory: NotRequired[str | None]

LocalShellAction: TypeAlias = 'ExecLocalShellAction'

LocalShellStatus: TypeAlias = "Literal['completed', 'in_progress', 'incomplete']"

class MacOsPermissions(TypedDict, total=False):
    accessibility: NotRequired[bool | None]
    automations: NotRequired[MacOsAutomationValue | None]
    calendar: NotRequired[bool | None]
    preferences: NotRequired[MacOsPreferencesValue | None]

McpAuthStatus: TypeAlias = "Literal['unsupported', 'not_logged_in', 'bearer_token', 'o_auth']"

class McpInvocation(TypedDict, total=False):
    arguments: NotRequired[JSONValue]
    server: Required[str]
    tool: Required[str]

class McpStartupFailure(TypedDict, total=False):
    error: Required[str]
    server: Required[str]

class StartingMcpStartupStatus(TypedDict, total=False):
    state: Required[Literal['starting']]

class ReadyMcpStartupStatus(TypedDict, total=False):
    state: Required[Literal['ready']]

class McpStartupStatusVariant(TypedDict, total=False):
    error: Required[str]
    state: Required[Literal['failed']]

class CancelledMcpStartupStatus(TypedDict, total=False):
    state: Required[Literal['cancelled']]

McpStartupStatus: TypeAlias = 'StartingMcpStartupStatus | ReadyMcpStartupStatus | McpStartupStatusVariant | CancelledMcpStartupStatus'

MessagePhase: TypeAlias = "Literal['commentary'] | Literal['final_answer']"

ModeKind: TypeAlias = "Literal['plan', 'default']"

ModelRerouteReason: TypeAlias = "Literal['high_risk_cyber_activity']"

class NetworkPermissions(TypedDict, total=False):
    enabled: NotRequired[bool | None]

class ReadParsedCommand(TypedDict, total=False):
    cmd: Required[str]
    name: Required[str]
    path: Required[str]
    type: Required[Literal['read']]

class ListFilesParsedCommand(TypedDict, total=False):
    cmd: Required[str]
    path: NotRequired[str | None]
    type: Required[Literal['list_files']]

class SearchParsedCommand(TypedDict, total=False):
    cmd: Required[str]
    path: NotRequired[str | None]
    query: NotRequired[str | None]
    type: Required[Literal['search']]

class UnknownParsedCommand(TypedDict, total=False):
    cmd: Required[str]
    type: Required[Literal['unknown']]

ParsedCommand: TypeAlias = 'ReadParsedCommand | ListFilesParsedCommand | SearchParsedCommand | UnknownParsedCommand'

PatchApplyStatus: TypeAlias = "Literal['completed', 'failed', 'declined']"

class PermissionProfile(TypedDict, total=False):
    file_system: NotRequired[FileSystemPermissions | None]
    macos: NotRequired[MacOsPermissions | None]
    network: NotRequired[NetworkPermissions | None]

class PlanItemArg(TypedDict, total=False):
    status: Required[StepStatus]
    step: Required[str]

class RealtimeAudioFrame(TypedDict, total=False):
    data: Required[str]
    num_channels: Required[int]
    sample_rate: Required[int]
    samples_per_channel: NotRequired[int | None]

class SessionUpdatedRealtimeEventSessionUpdatedVariant(TypedDict, total=False):
    instructions: NotRequired[str | None]
    session_id: Required[str]

class SessionUpdatedRealtimeEvent(TypedDict, total=False):
    SessionUpdated: Required[SessionUpdatedRealtimeEventSessionUpdatedVariant]

class AudioOutRealtimeEvent(TypedDict, total=False):
    AudioOut: Required[RealtimeAudioFrame]

class ConversationItemAddedRealtimeEvent(TypedDict, total=False):
    ConversationItemAdded: Required[Any]

class ConversationItemDoneRealtimeEventConversationItemDoneVariant(TypedDict, total=False):
    item_id: Required[str]

class ConversationItemDoneRealtimeEvent(TypedDict, total=False):
    ConversationItemDone: Required[ConversationItemDoneRealtimeEventConversationItemDoneVariant]

class HandoffRequestedRealtimeEvent(TypedDict, total=False):
    HandoffRequested: Required[RealtimeHandoffRequested]

class ErrorRealtimeEvent(TypedDict, total=False):
    Error: Required[str]

RealtimeEvent: TypeAlias = 'SessionUpdatedRealtimeEvent | AudioOutRealtimeEvent | ConversationItemAddedRealtimeEvent | ConversationItemDoneRealtimeEvent | HandoffRequestedRealtimeEvent | ErrorRealtimeEvent'

class RealtimeHandoffMessage(TypedDict, total=False):
    role: Required[str]
    text: Required[str]

class RealtimeHandoffRequested(TypedDict, total=False):
    handoff_id: Required[str]
    input_transcript: Required[str]
    item_id: Required[str]
    messages: Required[list[RealtimeHandoffMessage]]

class ReasoningTextReasoningItemContent(TypedDict, total=False):
    text: Required[str]
    type: Required[Literal['reasoning_text']]

class TextReasoningItemContent(TypedDict, total=False):
    text: Required[str]
    type: Required[Literal['text']]

ReasoningItemContent: TypeAlias = 'ReasoningTextReasoningItemContent | TextReasoningItemContent'

class SummaryTextReasoningItemReasoningSummary(TypedDict, total=False):
    text: Required[str]
    type: Required[Literal['summary_text']]

ReasoningItemReasoningSummary: TypeAlias = 'SummaryTextReasoningItemReasoningSummary'

class RejectConfig(TypedDict, total=False):
    mcp_elicitations: Required[bool]
    rules: Required[bool]
    sandbox_approval: Required[bool]

class RemoteSkillSummary(TypedDict, total=False):
    description: Required[str]
    id: Required[str]
    name: Required[str]

RequestId: TypeAlias = 'str | int'

class RequestUserInputQuestion(TypedDict, total=False):
    header: Required[str]
    id: Required[str]
    isOther: NotRequired[bool]
    isSecret: NotRequired[bool]
    options: NotRequired[list[RequestUserInputQuestionOption] | None]
    question: Required[str]

class RequestUserInputQuestionOption(TypedDict, total=False):
    description: Required[str]
    label: Required[str]

class Resource(TypedDict, total=False):
    _meta: NotRequired[Any]
    annotations: NotRequired[Any]
    description: NotRequired[str | None]
    icons: NotRequired[list[Any] | None]
    mimeType: NotRequired[str | None]
    name: Required[str]
    size: NotRequired[int | None]
    title: NotRequired[str | None]
    uri: Required[str]

class ResourceTemplate(TypedDict, total=False):
    annotations: NotRequired[Any]
    description: NotRequired[str | None]
    mimeType: NotRequired[str | None]
    name: Required[str]
    title: NotRequired[str | None]
    uriTemplate: Required[str]

class MessageResponseItem(TypedDict, total=False):
    content: Required[list[ContentItem]]
    end_turn: NotRequired[bool | None]
    id: NotRequired[str | None]
    phase: NotRequired[MessagePhase | None]
    role: Required[str]
    type: Required[Literal['message']]

class ReasoningResponseItem(TypedDict, total=False):
    content: NotRequired[list[ReasoningItemContent] | None]
    encrypted_content: NotRequired[str | None]
    id: Required[str]
    summary: Required[list[ReasoningItemReasoningSummary]]
    type: Required[Literal['reasoning']]

class LocalShellCallResponseItem(TypedDict, total=False):
    action: Required[LocalShellAction]
    call_id: NotRequired[str | None]
    id: NotRequired[str | None]
    status: Required[LocalShellStatus]
    type: Required[Literal['local_shell_call']]

class FunctionCallResponseItem(TypedDict, total=False):
    arguments: Required[str]
    call_id: Required[str]
    id: NotRequired[str | None]
    name: Required[str]
    type: Required[Literal['function_call']]

class FunctionCallOutputResponseItem(TypedDict, total=False):
    call_id: Required[str]
    output: Required[FunctionCallOutputPayload]
    type: Required[Literal['function_call_output']]

class CustomToolCallResponseItem(TypedDict, total=False):
    call_id: Required[str]
    id: NotRequired[str | None]
    input: Required[str]
    name: Required[str]
    status: NotRequired[str | None]
    type: Required[Literal['custom_tool_call']]

class CustomToolCallOutputResponseItem(TypedDict, total=False):
    call_id: Required[str]
    output: Required[FunctionCallOutputPayload]
    type: Required[Literal['custom_tool_call_output']]

class WebSearchCallResponseItem(TypedDict, total=False):
    action: NotRequired[WebSearchAction | None]
    id: NotRequired[str | None]
    status: NotRequired[str | None]
    type: Required[Literal['web_search_call']]

class ImageGenerationCallResponseItem(TypedDict, total=False):
    id: Required[str]
    result: Required[str]
    revised_prompt: NotRequired[str | None]
    status: Required[str]
    type: Required[Literal['image_generation_call']]

class GhostSnapshotResponseItem(TypedDict, total=False):
    ghost_commit: Required[GhostCommit]
    type: Required[Literal['ghost_snapshot']]

class CompactionResponseItem(TypedDict, total=False):
    encrypted_content: Required[str]
    type: Required[Literal['compaction']]

class OtherResponseItem(TypedDict, total=False):
    type: Required[Literal['other']]

ResponseItem: TypeAlias = 'MessageResponseItem | ReasoningResponseItem | LocalShellCallResponseItem | FunctionCallResponseItem | FunctionCallOutputResponseItem | CustomToolCallResponseItem | CustomToolCallOutputResponseItem | WebSearchCallResponseItem | ImageGenerationCallResponseItem | GhostSnapshotResponseItem | CompactionResponseItem | OtherResponseItem'

class OkResultOfCallToolResultOrString(TypedDict, total=False):
    Ok: Required[CallToolResult]

class ErrResultOfCallToolResultOrString(TypedDict, total=False):
    Err: Required[str]

ResultOfCallToolResultOrString: TypeAlias = 'OkResultOfCallToolResultOrString | ErrResultOfCallToolResultOrString'

class ReviewCodeLocation(TypedDict, total=False):
    absolute_file_path: Required[str]
    line_range: Required[ReviewLineRange]

class ReviewFinding(TypedDict, total=False):
    body: Required[str]
    code_location: Required[ReviewCodeLocation]
    confidence_score: Required[float]
    priority: Required[int]
    title: Required[str]

class ReviewLineRange(TypedDict, total=False):
    end: Required[int]
    start: Required[int]

class ReviewOutputEvent(TypedDict, total=False):
    findings: Required[list[ReviewFinding]]
    overall_confidence_score: Required[float]
    overall_correctness: Required[str]
    overall_explanation: Required[str]

class UncommittedChangesReviewTarget(TypedDict, total=False):
    type: Required[Literal['uncommittedChanges']]

class BaseBranchReviewTarget(TypedDict, total=False):
    branch: Required[str]
    type: Required[Literal['baseBranch']]

class CommitReviewTarget(TypedDict, total=False):
    sha: Required[str]
    title: NotRequired[str | None]
    type: Required[Literal['commit']]

class CustomReviewTarget(TypedDict, total=False):
    instructions: Required[str]
    type: Required[Literal['custom']]

ReviewTarget: TypeAlias = 'UncommittedChangesReviewTarget | BaseBranchReviewTarget | CommitReviewTarget | CustomReviewTarget'

class SessionNetworkProxyRuntime(TypedDict, total=False):
    admin_addr: Required[str]
    http_addr: Required[str]
    socks_addr: Required[str]

class SkillDependencies(TypedDict, total=False):
    tools: Required[list[SkillToolDependency]]

class SkillErrorInfo(TypedDict, total=False):
    message: Required[str]
    path: Required[str]

class SkillInterface(TypedDict, total=False):
    brand_color: NotRequired[str | None]
    default_prompt: NotRequired[str | None]
    display_name: NotRequired[str | None]
    icon_large: NotRequired[str | None]
    icon_small: NotRequired[str | None]
    short_description: NotRequired[str | None]

class SkillMetadata(TypedDict, total=False):
    dependencies: NotRequired[SkillDependencies | None]
    description: Required[str]
    enabled: Required[bool]
    interface: NotRequired[SkillInterface | None]
    name: Required[str]
    path: Required[str]
    scope: Required[SkillScope]
    short_description: NotRequired[str | None]

SkillScope: TypeAlias = "Literal['user', 'repo', 'system', 'admin']"

class SkillToolDependency(TypedDict, total=False):
    command: NotRequired[str | None]
    description: NotRequired[str | None]
    transport: NotRequired[str | None]
    type: Required[str]
    url: NotRequired[str | None]
    value: Required[str]

class SkillsListEntry(TypedDict, total=False):
    cwd: Required[str]
    errors: Required[list[SkillErrorInfo]]
    skills: Required[list[SkillMetadata]]

StepStatus: TypeAlias = "Literal['pending', 'in_progress', 'completed']"

class TextElement(TypedDict, total=False):
    byte_range: Required[ByteRange]
    placeholder: NotRequired[str | None]

class TokenUsage(TypedDict, total=False):
    cached_input_tokens: Required[int]
    input_tokens: Required[int]
    output_tokens: Required[int]
    reasoning_output_tokens: Required[int]
    total_tokens: Required[int]

class TokenUsageInfo(TypedDict, total=False):
    last_token_usage: Required[TokenUsage]
    model_context_window: NotRequired[int | None]
    total_token_usage: Required[TokenUsage]

class Tool(TypedDict, total=False):
    _meta: NotRequired[Any]
    annotations: NotRequired[Any]
    description: NotRequired[str | None]
    icons: NotRequired[list[Any] | None]
    inputSchema: Required[Any]
    name: Required[str]
    outputSchema: NotRequired[Any]
    title: NotRequired[str | None]

TurnAbortReason: TypeAlias = "Literal['interrupted', 'replaced', 'review_ended']"

class UserMessageTurnItem(TypedDict, total=False):
    content: Required[list[UserInput]]
    id: Required[str]
    type: Required[Literal['UserMessage']]

class AgentMessageTurnItem(TypedDict, total=False):
    content: Required[list[AgentMessageContent]]
    id: Required[str]
    phase: NotRequired[MessagePhase | None]
    type: Required[Literal['AgentMessage']]

class PlanTurnItem(TypedDict, total=False):
    id: Required[str]
    text: Required[str]
    type: Required[Literal['Plan']]

class ReasoningTurnItem(TypedDict, total=False):
    id: Required[str]
    raw_content: NotRequired[list[str]]
    summary_text: Required[list[str]]
    type: Required[Literal['Reasoning']]

class WebSearchTurnItem(TypedDict, total=False):
    action: Required[WebSearchAction]
    id: Required[str]
    query: Required[str]
    type: Required[Literal['WebSearch']]

class ImageGenerationTurnItem(TypedDict, total=False):
    id: Required[str]
    result: Required[str]
    revised_prompt: NotRequired[str | None]
    status: Required[str]
    type: Required[Literal['ImageGeneration']]

class ContextCompactionTurnItem(TypedDict, total=False):
    id: Required[str]
    type: Required[Literal['ContextCompaction']]

TurnItem: TypeAlias = 'UserMessageTurnItem | AgentMessageTurnItem | PlanTurnItem | ReasoningTurnItem | WebSearchTurnItem | ImageGenerationTurnItem | ContextCompactionTurnItem'

class TextUserInput(TypedDict, total=False):
    text: Required[str]
    text_elements: NotRequired[list[TextElement]]
    type: Required[Literal['text']]

class ImageUserInput(TypedDict, total=False):
    image_url: Required[str]
    type: Required[Literal['image']]

class LocalImageUserInput(TypedDict, total=False):
    path: Required[str]
    type: Required[Literal['local_image']]

class SkillUserInput(TypedDict, total=False):
    name: Required[str]
    path: Required[str]
    type: Required[Literal['skill']]

class MentionUserInput(TypedDict, total=False):
    name: Required[str]
    path: Required[str]
    type: Required[Literal['mention']]

UserInput: TypeAlias = 'TextUserInput | ImageUserInput | LocalImageUserInput | SkillUserInput | MentionUserInput'

class SearchWebSearchAction(TypedDict, total=False):
    queries: NotRequired[list[str] | None]
    query: NotRequired[str | None]
    type: Required[Literal['search']]

class OpenPageWebSearchAction(TypedDict, total=False):
    type: Required[Literal['open_page']]
    url: NotRequired[str | None]

class FindInPageWebSearchAction(TypedDict, total=False):
    pattern: NotRequired[str | None]
    type: Required[Literal['find_in_page']]
    url: NotRequired[str | None]

class OtherWebSearchAction(TypedDict, total=False):
    type: Required[Literal['other']]

WebSearchAction: TypeAlias = 'SearchWebSearchAction | OpenPageWebSearchAction | FindInPageWebSearchAction | OtherWebSearchAction'

class ExecCommandApprovalParams(TypedDict, total=False):
    approvalId: NotRequired[str | None]
    callId: Required[str]
    command: Required[list[str]]
    conversationId: Required[ThreadId]
    cwd: Required[str]
    parsedCmd: Required[list[ParsedCommand]]
    reason: NotRequired[str | None]

class ExecCommandApprovalResponse(TypedDict, total=False):
    decision: Required[ReviewDecision]

class ExperimentalFeatureListParams(TypedDict, total=False):
    cursor: NotRequired[str | None]
    limit: NotRequired[int | None]

class ExperimentalFeature(TypedDict, total=False):
    announcement: NotRequired[str | None]
    defaultEnabled: Required[bool]
    description: NotRequired[str | None]
    displayName: NotRequired[str | None]
    enabled: Required[bool]
    name: Required[str]
    stage: Required[ExperimentalFeatureStage]

ExperimentalFeatureStage: TypeAlias = "Literal['beta'] | Literal['underDevelopment'] | Literal['stable'] | Literal['deprecated'] | Literal['removed']"

class ExperimentalFeatureListResponse(TypedDict, total=False):
    data: Required[list[ExperimentalFeature]]
    nextCursor: NotRequired[str | None]

class ExternalAgentConfigDetectParams(TypedDict, total=False):
    cwds: NotRequired[list[str] | None]
    includeHome: NotRequired[bool]

class ExternalAgentConfigMigrationItem(TypedDict, total=False):
    cwd: NotRequired[str | None]
    description: Required[str]
    itemType: Required[ExternalAgentConfigMigrationItemType]

ExternalAgentConfigMigrationItemType: TypeAlias = "Literal['AGENTS_MD', 'CONFIG', 'SKILLS', 'MCP_SERVER_CONFIG']"

class ExternalAgentConfigDetectResponse(TypedDict, total=False):
    items: Required[list[ExternalAgentConfigMigrationItem]]

class ExternalAgentConfigImportParams(TypedDict, total=False):
    migrationItems: Required[list[ExternalAgentConfigMigrationItem]]

ExternalAgentConfigImportResponse: TypeAlias = 'dict[str, JSONValue]'

class FeedbackUploadParams(TypedDict, total=False):
    classification: Required[str]
    extraLogFiles: NotRequired[list[str] | None]
    includeLogs: Required[bool]
    reason: NotRequired[str | None]
    threadId: NotRequired[str | None]

class FeedbackUploadResponse(TypedDict, total=False):
    threadId: Required[str]

class FileChangeOutputDeltaNotification(TypedDict, total=False):
    delta: Required[str]
    itemId: Required[str]
    threadId: Required[str]
    turnId: Required[str]

class FileChangeRequestApprovalParams(TypedDict, total=False):
    grantRoot: NotRequired[str | None]
    itemId: Required[str]
    reason: NotRequired[str | None]
    threadId: Required[str]
    turnId: Required[str]

FileChangeApprovalDecision: TypeAlias = "Literal['accept'] | Literal['acceptForSession'] | Literal['decline'] | Literal['cancel']"

class FileChangeRequestApprovalResponse(TypedDict, total=False):
    decision: Required[FileChangeApprovalDecision]

class FuzzyFileSearchParams(TypedDict, total=False):
    cancellationToken: NotRequired[str | None]
    query: Required[str]
    roots: Required[list[str]]

class FuzzyFileSearchResult(TypedDict, total=False):
    file_name: Required[str]
    indices: NotRequired[list[int] | None]
    path: Required[str]
    root: Required[str]
    score: Required[int]

class FuzzyFileSearchResponse(TypedDict, total=False):
    files: Required[list[FuzzyFileSearchResult]]

class FuzzyFileSearchSessionCompletedNotification(TypedDict, total=False):
    sessionId: Required[str]

class FuzzyFileSearchSessionUpdatedNotification(TypedDict, total=False):
    files: Required[list[FuzzyFileSearchResult]]
    query: Required[str]
    sessionId: Required[str]

class GetAccountParams(TypedDict, total=False):
    refreshToken: NotRequired[bool]

class GetAccountRateLimitsResponse(TypedDict, total=False):
    rateLimits: Required[RateLimitSnapshot]
    rateLimitsByLimitId: NotRequired[dict[str, RateLimitSnapshot] | None]

class ApiKeyAccount(TypedDict, total=False):
    type: Required[Literal['apiKey']]

class ChatgptAccount(TypedDict, total=False):
    email: Required[str]
    planType: Required[PlanType]
    type: Required[Literal['chatgpt']]

Account: TypeAlias = 'ApiKeyAccount | ChatgptAccount'

class GetAccountResponse(TypedDict, total=False):
    account: NotRequired[Account | None]
    requiresOpenaiAuth: Required[bool]

class ClientInfo(TypedDict, total=False):
    name: Required[str]
    title: NotRequired[str | None]
    version: Required[str]

class InitializeCapabilities(TypedDict, total=False):
    experimentalApi: NotRequired[bool]
    optOutNotificationMethods: NotRequired[list[str] | None]

class InitializeParams(TypedDict, total=False):
    capabilities: NotRequired[InitializeCapabilities | None]
    clientInfo: Required[ClientInfo]

class InitializeResponse(TypedDict, total=False):
    userAgent: Required[str]

class CollabAgentState(TypedDict, total=False):
    message: NotRequired[str | None]
    status: Required[CollabAgentStatus]

CollabAgentStatus: TypeAlias = "Literal['pendingInit', 'running', 'completed', 'errored', 'shutdown', 'notFound']"

CollabAgentTool: TypeAlias = "Literal['spawnAgent', 'sendInput', 'resumeAgent', 'wait', 'closeAgent']"

CollabAgentToolCallStatus: TypeAlias = "Literal['inProgress', 'completed', 'failed']"

CommandExecutionStatus: TypeAlias = "Literal['inProgress', 'completed', 'failed', 'declined']"

DynamicToolCallStatus: TypeAlias = "Literal['inProgress', 'completed', 'failed']"

class FileUpdateChange(TypedDict, total=False):
    diff: Required[str]
    kind: Required[PatchChangeKind]
    path: Required[str]

class McpToolCallError(TypedDict, total=False):
    message: Required[str]

class McpToolCallResult(TypedDict, total=False):
    content: Required[list[Any]]
    structuredContent: NotRequired[Any]

McpToolCallStatus: TypeAlias = "Literal['inProgress', 'completed', 'failed']"

class AddPatchChangeKind(TypedDict, total=False):
    type: Required[Literal['add']]

class DeletePatchChangeKind(TypedDict, total=False):
    type: Required[Literal['delete']]

class UpdatePatchChangeKind(TypedDict, total=False):
    move_path: NotRequired[str | None]
    type: Required[Literal['update']]

PatchChangeKind: TypeAlias = 'AddPatchChangeKind | DeletePatchChangeKind | UpdatePatchChangeKind'

class UserMessageThreadItem(TypedDict, total=False):
    content: Required[list[UserInput]]
    id: Required[str]
    type: Required[Literal['userMessage']]

class AgentMessageThreadItem(TypedDict, total=False):
    id: Required[str]
    phase: NotRequired[MessagePhase | None]
    text: Required[str]
    type: Required[Literal['agentMessage']]

class PlanThreadItem(TypedDict, total=False):
    id: Required[str]
    text: Required[str]
    type: Required[Literal['plan']]

class ReasoningThreadItem(TypedDict, total=False):
    content: NotRequired[list[str]]
    id: Required[str]
    summary: NotRequired[list[str]]
    type: Required[Literal['reasoning']]

class CommandExecutionThreadItem(TypedDict, total=False):
    aggregatedOutput: NotRequired[str | None]
    command: Required[str]
    commandActions: Required[list[CommandAction]]
    cwd: Required[str]
    durationMs: NotRequired[int | None]
    exitCode: NotRequired[int | None]
    id: Required[str]
    processId: NotRequired[str | None]
    status: Required[CommandExecutionStatus]
    type: Required[Literal['commandExecution']]

class FileChangeThreadItem(TypedDict, total=False):
    changes: Required[list[FileUpdateChange]]
    id: Required[str]
    status: Required[PatchApplyStatus]
    type: Required[Literal['fileChange']]

class McpToolCallThreadItem(TypedDict, total=False):
    arguments: Required[Any]
    durationMs: NotRequired[int | None]
    error: NotRequired[McpToolCallError | None]
    id: Required[str]
    result: NotRequired[McpToolCallResult | None]
    server: Required[str]
    status: Required[McpToolCallStatus]
    tool: Required[str]
    type: Required[Literal['mcpToolCall']]

class DynamicToolCallThreadItem(TypedDict, total=False):
    arguments: Required[Any]
    contentItems: NotRequired[list[DynamicToolCallOutputContentItem] | None]
    durationMs: NotRequired[int | None]
    id: Required[str]
    status: Required[DynamicToolCallStatus]
    success: NotRequired[bool | None]
    tool: Required[str]
    type: Required[Literal['dynamicToolCall']]

class CollabAgentToolCallThreadItem(TypedDict, total=False):
    agentsStates: Required[dict[str, CollabAgentState]]
    id: Required[str]
    prompt: NotRequired[str | None]
    receiverThreadIds: Required[list[str]]
    senderThreadId: Required[str]
    status: Required[CollabAgentToolCallStatus]
    tool: Required[CollabAgentTool]
    type: Required[Literal['collabAgentToolCall']]

class WebSearchThreadItem(TypedDict, total=False):
    action: NotRequired[WebSearchAction | None]
    id: Required[str]
    query: Required[str]
    type: Required[Literal['webSearch']]

class ImageViewThreadItem(TypedDict, total=False):
    id: Required[str]
    path: Required[str]
    type: Required[Literal['imageView']]

class ImageGenerationThreadItem(TypedDict, total=False):
    id: Required[str]
    result: Required[str]
    revisedPrompt: NotRequired[str | None]
    status: Required[str]
    type: Required[Literal['imageGeneration']]

class EnteredReviewModeThreadItem(TypedDict, total=False):
    id: Required[str]
    review: Required[str]
    type: Required[Literal['enteredReviewMode']]

class ExitedReviewModeThreadItem(TypedDict, total=False):
    id: Required[str]
    review: Required[str]
    type: Required[Literal['exitedReviewMode']]

class ContextCompactionThreadItem(TypedDict, total=False):
    id: Required[str]
    type: Required[Literal['contextCompaction']]

ThreadItem: TypeAlias = 'UserMessageThreadItem | AgentMessageThreadItem | PlanThreadItem | ReasoningThreadItem | CommandExecutionThreadItem | FileChangeThreadItem | McpToolCallThreadItem | DynamicToolCallThreadItem | CollabAgentToolCallThreadItem | WebSearchThreadItem | ImageViewThreadItem | ImageGenerationThreadItem | EnteredReviewModeThreadItem | ExitedReviewModeThreadItem | ContextCompactionThreadItem'

class ItemCompletedNotification(TypedDict, total=False):
    item: Required[ThreadItem]
    threadId: Required[str]
    turnId: Required[str]

class ItemStartedNotification(TypedDict, total=False):
    item: Required[ThreadItem]
    threadId: Required[str]
    turnId: Required[str]

class ListMcpServerStatusParams(TypedDict, total=False):
    cursor: NotRequired[str | None]
    limit: NotRequired[int | None]

class McpServerStatus(TypedDict, total=False):
    authStatus: Required[McpAuthStatus]
    name: Required[str]
    resourceTemplates: Required[list[ResourceTemplate]]
    resources: Required[list[Resource]]
    tools: Required[dict[str, Tool]]

class ListMcpServerStatusResponse(TypedDict, total=False):
    data: Required[list[McpServerStatus]]
    nextCursor: NotRequired[str | None]

class ApiKeyv2LoginAccountParams(TypedDict, total=False):
    apiKey: Required[str]
    type: Required[Literal['apiKey']]

class Chatgptv2LoginAccountParams(TypedDict, total=False):
    type: Required[Literal['chatgpt']]

class ChatgptAuthTokensv2LoginAccountParams(TypedDict, total=False):
    accessToken: Required[str]
    chatgptAccountId: Required[str]
    chatgptPlanType: NotRequired[str | None]
    type: Required[Literal['chatgptAuthTokens']]

LoginAccountParams: TypeAlias = 'ApiKeyv2LoginAccountParams | Chatgptv2LoginAccountParams | ChatgptAuthTokensv2LoginAccountParams'

class ApiKeyv2LoginAccountResponse(TypedDict, total=False):
    type: Required[Literal['apiKey']]

class Chatgptv2LoginAccountResponse(TypedDict, total=False):
    authUrl: Required[str]
    loginId: Required[str]
    type: Required[Literal['chatgpt']]

class ChatgptAuthTokensv2LoginAccountResponse(TypedDict, total=False):
    type: Required[Literal['chatgptAuthTokens']]

LoginAccountResponse: TypeAlias = 'ApiKeyv2LoginAccountResponse | Chatgptv2LoginAccountResponse | ChatgptAuthTokensv2LoginAccountResponse'

LogoutAccountResponse: TypeAlias = 'dict[str, JSONValue]'

class McpServerElicitationRequestParams(TypedDict, total=False):
    serverName: Required[str]
    threadId: Required[str]
    turnId: NotRequired[str | None]

McpServerElicitationAction: TypeAlias = "Literal['accept', 'decline', 'cancel']"

class McpServerElicitationRequestResponse(TypedDict, total=False):
    action: Required[McpServerElicitationAction]
    content: NotRequired[JSONValue]

class McpServerOauthLoginCompletedNotification(TypedDict, total=False):
    error: NotRequired[str | None]
    name: Required[str]
    success: Required[bool]

class McpServerOauthLoginParams(TypedDict, total=False):
    name: Required[str]
    scopes: NotRequired[list[str] | None]
    timeoutSecs: NotRequired[int | None]

class McpServerOauthLoginResponse(TypedDict, total=False):
    authorizationUrl: Required[str]

McpServerRefreshResponse: TypeAlias = 'dict[str, JSONValue]'

class McpToolCallProgressNotification(TypedDict, total=False):
    itemId: Required[str]
    message: Required[str]
    threadId: Required[str]
    turnId: Required[str]

class ModelListParams(TypedDict, total=False):
    cursor: NotRequired[str | None]
    includeHidden: NotRequired[bool | None]
    limit: NotRequired[int | None]

InputModality: TypeAlias = "Literal['text'] | Literal['image']"

class Model(TypedDict, total=False):
    availabilityNux: NotRequired[ModelAvailabilityNux | None]
    defaultReasoningEffort: Required[ReasoningEffort]
    description: Required[str]
    displayName: Required[str]
    hidden: Required[bool]
    id: Required[str]
    inputModalities: NotRequired[list[InputModality]]
    isDefault: Required[bool]
    model: Required[str]
    supportedReasoningEfforts: Required[list[ReasoningEffortOption]]
    supportsPersonality: NotRequired[bool]
    upgrade: NotRequired[str | None]
    upgradeInfo: NotRequired[ModelUpgradeInfo | None]

class ModelAvailabilityNux(TypedDict, total=False):
    message: Required[str]

class ModelUpgradeInfo(TypedDict, total=False):
    migrationMarkdown: NotRequired[str | None]
    model: Required[str]
    modelLink: NotRequired[str | None]
    upgradeCopy: NotRequired[str | None]

class ReasoningEffortOption(TypedDict, total=False):
    description: Required[str]
    reasoningEffort: Required[ReasoningEffort]

class ModelListResponse(TypedDict, total=False):
    data: Required[list[Model]]
    nextCursor: NotRequired[str | None]

class ModelReroutedNotification(TypedDict, total=False):
    fromModel: Required[str]
    reason: Required[ModelRerouteReason]
    threadId: Required[str]
    toModel: Required[str]
    turnId: Required[str]

class PlanDeltaNotification(TypedDict, total=False):
    delta: Required[str]
    itemId: Required[str]
    threadId: Required[str]
    turnId: Required[str]

class PluginInstallParams(TypedDict, total=False):
    cwd: NotRequired[str | None]
    marketplaceName: Required[str]
    pluginName: Required[str]

PluginInstallResponse: TypeAlias = 'dict[str, JSONValue]'

class RawResponseItemCompletedNotification(TypedDict, total=False):
    item: Required[ResponseItem]
    threadId: Required[str]
    turnId: Required[str]

class ReasoningSummaryPartAddedNotification(TypedDict, total=False):
    itemId: Required[str]
    summaryIndex: Required[int]
    threadId: Required[str]
    turnId: Required[str]

class ReasoningSummaryTextDeltaNotification(TypedDict, total=False):
    delta: Required[str]
    itemId: Required[str]
    summaryIndex: Required[int]
    threadId: Required[str]
    turnId: Required[str]

class ReasoningTextDeltaNotification(TypedDict, total=False):
    contentIndex: Required[int]
    delta: Required[str]
    itemId: Required[str]
    threadId: Required[str]
    turnId: Required[str]

ReviewDelivery: TypeAlias = "Literal['inline', 'detached']"

class ReviewStartParams(TypedDict, total=False):
    delivery: NotRequired[ReviewDelivery | None]
    target: Required[ReviewTarget]
    threadId: Required[str]

class Turn(TypedDict, total=False):
    error: NotRequired[TurnError | None]
    id: Required[str]
    items: Required[list[ThreadItem]]
    status: Required[TurnStatus]

TurnStatus: TypeAlias = "Literal['completed', 'interrupted', 'failed', 'inProgress']"

class ReviewStartResponse(TypedDict, total=False):
    reviewThreadId: Required[str]
    turn: Required[Turn]

class ServerRequestResolvedNotification(TypedDict, total=False):
    requestId: Required[RequestId]
    threadId: Required[str]

SkillsChangedNotification: TypeAlias = 'dict[str, JSONValue]'

class SkillsConfigWriteParams(TypedDict, total=False):
    enabled: Required[bool]
    path: Required[str]

class SkillsConfigWriteResponse(TypedDict, total=False):
    effectiveEnabled: Required[bool]

class SkillsListExtraRootsForCwd(TypedDict, total=False):
    cwd: Required[str]
    extraUserRoots: Required[list[str]]

class SkillsListParams(TypedDict, total=False):
    cwds: NotRequired[list[str]]
    forceReload: NotRequired[bool]
    perCwdExtraUserRoots: NotRequired[list[SkillsListExtraRootsForCwd] | None]

class SkillsListResponse(TypedDict, total=False):
    data: Required[list[SkillsListEntry]]

HazelnutScope: TypeAlias = "Literal['example', 'workspace-shared', 'all-shared', 'personal']"

ProductSurface: TypeAlias = "Literal['chatgpt', 'codex', 'api', 'atlas']"

class SkillsRemoteReadParams(TypedDict, total=False):
    enabled: NotRequired[bool]
    hazelnutScope: NotRequired[HazelnutScope]
    productSurface: NotRequired[ProductSurface]

class SkillsRemoteReadResponse(TypedDict, total=False):
    data: Required[list[RemoteSkillSummary]]

class SkillsRemoteWriteParams(TypedDict, total=False):
    hazelnutId: Required[str]

class SkillsRemoteWriteResponse(TypedDict, total=False):
    id: Required[str]
    path: Required[str]

class TerminalInteractionNotification(TypedDict, total=False):
    itemId: Required[str]
    processId: Required[str]
    stdin: Required[str]
    threadId: Required[str]
    turnId: Required[str]

class ThreadArchiveParams(TypedDict, total=False):
    threadId: Required[str]

ThreadArchiveResponse: TypeAlias = 'dict[str, JSONValue]'

class ThreadArchivedNotification(TypedDict, total=False):
    threadId: Required[str]

class ThreadClosedNotification(TypedDict, total=False):
    threadId: Required[str]

class ThreadCompactStartParams(TypedDict, total=False):
    threadId: Required[str]

ThreadCompactStartResponse: TypeAlias = 'dict[str, JSONValue]'

class ThreadForkParams(TypedDict, total=False):
    approvalPolicy: NotRequired[AskForApproval | None]
    baseInstructions: NotRequired[str | None]
    config: NotRequired[dict[str, JSONValue] | None]
    cwd: NotRequired[str | None]
    developerInstructions: NotRequired[str | None]
    model: NotRequired[str | None]
    modelProvider: NotRequired[str | None]
    threadId: Required[str]
    serviceTier: NotRequired[ServiceTier | None | None]
    sandbox: NotRequired[SandboxMode | None]

class GitInfo(TypedDict, total=False):
    branch: NotRequired[str | None]
    originUrl: NotRequired[str | None]
    sha: NotRequired[str | None]

class SubAgentSessionSource(TypedDict, total=False):
    subAgent: Required[SubAgentSource]

SessionSource: TypeAlias = "Literal['cli', 'vscode', 'exec', 'appServer', 'unknown'] | SubAgentSessionSource"

class ThreadSpawnSubAgentSourceThreadSpawnVariant(TypedDict, total=False):
    agent_nickname: NotRequired[str | None]
    agent_role: NotRequired[str | None]
    depth: Required[int]
    parent_thread_id: Required[ThreadId]

class ThreadSpawnSubAgentSource(TypedDict, total=False):
    thread_spawn: Required[ThreadSpawnSubAgentSourceThreadSpawnVariant]

class OtherSubAgentSource(TypedDict, total=False):
    other: Required[str]

SubAgentSource: TypeAlias = "Literal['review', 'compact', 'memory_consolidation'] | ThreadSpawnSubAgentSource | OtherSubAgentSource"

class Thread(TypedDict, total=False):
    agentNickname: NotRequired[str | None]
    agentRole: NotRequired[str | None]
    cliVersion: Required[str]
    createdAt: Required[int]
    cwd: Required[str]
    ephemeral: Required[bool]
    gitInfo: NotRequired[GitInfo | None]
    id: Required[str]
    modelProvider: Required[str]
    name: NotRequired[str | None]
    path: NotRequired[str | None]
    preview: Required[str]
    source: Required[SessionSource]
    status: Required[ThreadStatus]
    turns: Required[list[Turn]]
    updatedAt: Required[int]

ThreadActiveFlag: TypeAlias = "Literal['waitingOnApproval', 'waitingOnUserInput']"

class NotLoadedThreadStatus(TypedDict, total=False):
    type: Required[Literal['notLoaded']]

class IdleThreadStatus(TypedDict, total=False):
    type: Required[Literal['idle']]

class SystemErrorThreadStatus(TypedDict, total=False):
    type: Required[Literal['systemError']]

class ActiveThreadStatus(TypedDict, total=False):
    activeFlags: Required[list[ThreadActiveFlag]]
    type: Required[Literal['active']]

ThreadStatus: TypeAlias = 'NotLoadedThreadStatus | IdleThreadStatus | SystemErrorThreadStatus | ActiveThreadStatus'

class ThreadForkResponse(TypedDict, total=False):
    approvalPolicy: Required[AskForApproval]
    cwd: Required[str]
    model: Required[str]
    modelProvider: Required[str]
    reasoningEffort: NotRequired[ReasoningEffort | None]
    sandbox: Required[SandboxPolicy]
    serviceTier: NotRequired[ServiceTier | None]
    thread: Required[Thread]

ThreadSortKey: TypeAlias = "Literal['created_at', 'updated_at']"

ThreadSourceKind: TypeAlias = "Literal['cli', 'vscode', 'exec', 'appServer', 'subAgent', 'subAgentReview', 'subAgentCompact', 'subAgentThreadSpawn', 'subAgentOther', 'unknown']"

class ThreadListParams(TypedDict, total=False):
    archived: NotRequired[bool | None]
    cursor: NotRequired[str | None]
    cwd: NotRequired[str | None]
    limit: NotRequired[int | None]
    modelProviders: NotRequired[list[str] | None]
    searchTerm: NotRequired[str | None]
    sortKey: NotRequired[ThreadSortKey | None]
    sourceKinds: NotRequired[list[ThreadSourceKind] | None]

class ThreadListResponse(TypedDict, total=False):
    data: Required[list[Thread]]
    nextCursor: NotRequired[str | None]

class ThreadLoadedListParams(TypedDict, total=False):
    cursor: NotRequired[str | None]
    limit: NotRequired[int | None]

class ThreadLoadedListResponse(TypedDict, total=False):
    data: Required[list[str]]
    nextCursor: NotRequired[str | None]

class ThreadMetadataGitInfoUpdateParams(TypedDict, total=False):
    branch: NotRequired[str | None]
    originUrl: NotRequired[str | None]
    sha: NotRequired[str | None]

class ThreadMetadataUpdateParams(TypedDict, total=False):
    gitInfo: NotRequired[ThreadMetadataGitInfoUpdateParams | None]
    threadId: Required[str]

class ThreadMetadataUpdateResponse(TypedDict, total=False):
    thread: Required[Thread]

class ThreadNameUpdatedNotification(TypedDict, total=False):
    threadId: Required[str]
    threadName: NotRequired[str | None]

class ThreadReadParams(TypedDict, total=False):
    includeTurns: NotRequired[bool]
    threadId: Required[str]

class ThreadReadResponse(TypedDict, total=False):
    thread: Required[Thread]

class ThreadRealtimeClosedNotification(TypedDict, total=False):
    reason: NotRequired[str | None]
    threadId: Required[str]

class ThreadRealtimeErrorNotification(TypedDict, total=False):
    message: Required[str]
    threadId: Required[str]

class ThreadRealtimeItemAddedNotification(TypedDict, total=False):
    item: Required[Any]
    threadId: Required[str]

class ThreadRealtimeAudioChunk(TypedDict, total=False):
    data: Required[str]
    numChannels: Required[int]
    sampleRate: Required[int]
    samplesPerChannel: NotRequired[int | None]

class ThreadRealtimeOutputAudioDeltaNotification(TypedDict, total=False):
    audio: Required[ThreadRealtimeAudioChunk]
    threadId: Required[str]

class ThreadRealtimeStartedNotification(TypedDict, total=False):
    sessionId: NotRequired[str | None]
    threadId: Required[str]

Personality: TypeAlias = "Literal['none', 'friendly', 'pragmatic']"

class ThreadResumeParams(TypedDict, total=False):
    approvalPolicy: NotRequired[AskForApproval | None]
    baseInstructions: NotRequired[str | None]
    config: NotRequired[dict[str, JSONValue] | None]
    cwd: NotRequired[str | None]
    developerInstructions: NotRequired[str | None]
    serviceTier: NotRequired[ServiceTier | None | None]
    model: NotRequired[str | None]
    modelProvider: NotRequired[str | None]
    threadId: Required[str]
    sandbox: NotRequired[SandboxMode | None]
    personality: NotRequired[Personality | None]

class ThreadResumeResponse(TypedDict, total=False):
    approvalPolicy: Required[AskForApproval]
    cwd: Required[str]
    model: Required[str]
    modelProvider: Required[str]
    reasoningEffort: NotRequired[ReasoningEffort | None]
    sandbox: Required[SandboxPolicy]
    serviceTier: NotRequired[ServiceTier | None]
    thread: Required[Thread]

class ThreadRollbackParams(TypedDict, total=False):
    numTurns: Required[int]
    threadId: Required[str]

class ThreadRollbackResponse(TypedDict, total=False):
    thread: Required[Thread]

class ThreadSetNameParams(TypedDict, total=False):
    name: Required[str]
    threadId: Required[str]

ThreadSetNameResponse: TypeAlias = 'dict[str, JSONValue]'

class DynamicToolSpec(TypedDict, total=False):
    description: Required[str]
    inputSchema: Required[Any]
    name: Required[str]

class ThreadStartParams(TypedDict, total=False):
    approvalPolicy: NotRequired[AskForApproval | None]
    baseInstructions: NotRequired[str | None]
    config: NotRequired[dict[str, JSONValue] | None]
    cwd: NotRequired[str | None]
    developerInstructions: NotRequired[str | None]
    sandbox: NotRequired[SandboxMode | None]
    ephemeral: NotRequired[bool | None]
    serviceName: NotRequired[str | None]
    personality: NotRequired[Personality | None]
    model: NotRequired[str | None]
    modelProvider: NotRequired[str | None]
    serviceTier: NotRequired[ServiceTier | None | None]

class ThreadStartResponse(TypedDict, total=False):
    approvalPolicy: Required[AskForApproval]
    cwd: Required[str]
    model: Required[str]
    modelProvider: Required[str]
    reasoningEffort: NotRequired[ReasoningEffort | None]
    sandbox: Required[SandboxPolicy]
    serviceTier: NotRequired[ServiceTier | None]
    thread: Required[Thread]

class ThreadStartedNotification(TypedDict, total=False):
    thread: Required[Thread]

class ThreadStatusChangedNotification(TypedDict, total=False):
    status: Required[ThreadStatus]
    threadId: Required[str]

class ThreadTokenUsage(TypedDict, total=False):
    last: Required[TokenUsageBreakdown]
    modelContextWindow: NotRequired[int | None]
    total: Required[TokenUsageBreakdown]

class TokenUsageBreakdown(TypedDict, total=False):
    cachedInputTokens: Required[int]
    inputTokens: Required[int]
    outputTokens: Required[int]
    reasoningOutputTokens: Required[int]
    totalTokens: Required[int]

class ThreadTokenUsageUpdatedNotification(TypedDict, total=False):
    threadId: Required[str]
    tokenUsage: Required[ThreadTokenUsage]
    turnId: Required[str]

class ThreadUnarchiveParams(TypedDict, total=False):
    threadId: Required[str]

class ThreadUnarchiveResponse(TypedDict, total=False):
    thread: Required[Thread]

class ThreadUnarchivedNotification(TypedDict, total=False):
    threadId: Required[str]

class ThreadUnsubscribeParams(TypedDict, total=False):
    threadId: Required[str]

ThreadUnsubscribeStatus: TypeAlias = "Literal['notLoaded', 'notSubscribed', 'unsubscribed']"

class ThreadUnsubscribeResponse(TypedDict, total=False):
    status: Required[ThreadUnsubscribeStatus]

class ToolRequestUserInputOption(TypedDict, total=False):
    description: Required[str]
    label: Required[str]

class ToolRequestUserInputQuestion(TypedDict, total=False):
    header: Required[str]
    id: Required[str]
    isOther: NotRequired[bool]
    isSecret: NotRequired[bool]
    options: NotRequired[list[ToolRequestUserInputOption] | None]
    question: Required[str]

class ToolRequestUserInputParams(TypedDict, total=False):
    itemId: Required[str]
    questions: Required[list[ToolRequestUserInputQuestion]]
    threadId: Required[str]
    turnId: Required[str]

class ToolRequestUserInputAnswer(TypedDict, total=False):
    answers: Required[list[str]]

class ToolRequestUserInputResponse(TypedDict, total=False):
    answers: Required[dict[str, ToolRequestUserInputAnswer]]

class TurnCompletedNotification(TypedDict, total=False):
    threadId: Required[str]
    turn: Required[Turn]

class TurnDiffUpdatedNotification(TypedDict, total=False):
    diff: Required[str]
    threadId: Required[str]
    turnId: Required[str]

class TurnInterruptParams(TypedDict, total=False):
    threadId: Required[str]
    turnId: Required[str]

TurnInterruptResponse: TypeAlias = 'dict[str, JSONValue]'

class TurnPlanStep(TypedDict, total=False):
    status: Required[TurnPlanStepStatus]
    step: Required[str]

TurnPlanStepStatus: TypeAlias = "Literal['pending', 'inProgress', 'completed']"

class TurnPlanUpdatedNotification(TypedDict, total=False):
    explanation: NotRequired[str | None]
    plan: Required[list[TurnPlanStep]]
    threadId: Required[str]
    turnId: Required[str]

class CollaborationMode(TypedDict, total=False):
    mode: Required[ModeKind]
    settings: Required[Settings]

class Settings(TypedDict, total=False):
    developer_instructions: NotRequired[str | None]
    model: Required[str]
    reasoning_effort: NotRequired[ReasoningEffort | None]

class TurnStartParams(TypedDict, total=False):
    approvalPolicy: NotRequired[AskForApproval | None]
    threadId: Required[str]
    cwd: NotRequired[str | None]
    effort: NotRequired[ReasoningEffort | None]
    input: Required[list[UserInput]]
    model: NotRequired[str | None]
    outputSchema: NotRequired[JSONValue]
    personality: NotRequired[Personality | None]
    sandboxPolicy: NotRequired[SandboxPolicy | None]
    serviceTier: NotRequired[ServiceTier | None | None]
    summary: NotRequired[ReasoningSummary | None]

class TurnStartResponse(TypedDict, total=False):
    turn: Required[Turn]

class TurnStartedNotification(TypedDict, total=False):
    threadId: Required[str]
    turn: Required[Turn]

class TurnSteerParams(TypedDict, total=False):
    expectedTurnId: Required[str]
    input: Required[list[UserInput]]
    threadId: Required[str]

class TurnSteerResponse(TypedDict, total=False):
    turnId: Required[str]

WindowsSandboxSetupMode: TypeAlias = "Literal['elevated', 'unelevated']"

class WindowsSandboxSetupCompletedNotification(TypedDict, total=False):
    error: NotRequired[str | None]
    mode: Required[WindowsSandboxSetupMode]
    success: Required[bool]

class WindowsSandboxSetupStartParams(TypedDict, total=False):
    cwd: NotRequired[str | None]
    mode: Required[WindowsSandboxSetupMode]

class WindowsSandboxSetupStartResponse(TypedDict, total=False):
    started: Required[bool]

class WindowsWorldWritableWarningNotification(TypedDict, total=False):
    extraCount: Required[int]
    failedScan: Required[bool]
    samplePaths: Required[list[str]]

ClientRequestMethod: TypeAlias = Literal['initialize', 'thread/start', 'thread/resume', 'thread/fork', 'thread/archive', 'thread/unsubscribe', 'thread/name/set', 'thread/metadata/update', 'thread/unarchive', 'thread/compact/start', 'thread/rollback', 'thread/list', 'thread/loaded/list', 'thread/read', 'skills/list', 'skills/remote/list', 'skills/remote/export', 'app/list', 'skills/config/write', 'plugin/install', 'turn/start', 'turn/steer', 'turn/interrupt', 'review/start', 'model/list', 'experimentalFeature/list', 'mcpServer/oauth/login', 'config/mcpServer/reload', 'mcpServerStatus/list', 'windowsSandbox/setupStart', 'account/login/start', 'account/login/cancel', 'account/logout', 'account/rateLimits/read', 'feedback/upload', 'command/exec', 'config/read', 'externalAgentConfig/detect', 'externalAgentConfig/import', 'config/value/write', 'config/batchWrite', 'configRequirements/read', 'account/read', 'fuzzyFileSearch']

ServerRequestMethod: TypeAlias = Literal['item/commandExecution/requestApproval', 'item/fileChange/requestApproval', 'item/tool/requestUserInput', 'mcpServer/elicitation/request', 'item/tool/call', 'account/chatgptAuthTokens/refresh', 'applyPatchApproval', 'execCommandApproval']

ServerNotificationMethod: TypeAlias = Literal['error', 'thread/started', 'thread/status/changed', 'thread/archived', 'thread/unarchived', 'thread/closed', 'skills/changed', 'thread/name/updated', 'thread/tokenUsage/updated', 'turn/started', 'turn/completed', 'turn/diff/updated', 'turn/plan/updated', 'item/started', 'item/completed', 'item/agentMessage/delta', 'item/plan/delta', 'item/commandExecution/outputDelta', 'item/commandExecution/terminalInteraction', 'item/fileChange/outputDelta', 'serverRequest/resolved', 'item/mcpToolCall/progress', 'mcpServer/oauthLogin/completed', 'account/updated', 'account/rateLimits/updated', 'app/list/updated', 'item/reasoning/summaryTextDelta', 'item/reasoning/summaryPartAdded', 'item/reasoning/textDelta', 'thread/compacted', 'model/rerouted', 'deprecationNotice', 'configWarning', 'fuzzyFileSearch/sessionUpdated', 'fuzzyFileSearch/sessionCompleted', 'thread/realtime/started', 'thread/realtime/itemAdded', 'thread/realtime/outputAudio/delta', 'thread/realtime/error', 'thread/realtime/closed', 'windows/worldWritableWarning', 'windowsSandbox/setupCompleted', 'account/login/completed']

CLIENT_REQUEST_METHOD_TO_PARAMS: Final[dict[str, str]] = {
    "initialize": "InitializeParams",
    "thread/start": "ThreadStartParams",
    "thread/resume": "ThreadResumeParams",
    "thread/fork": "ThreadForkParams",
    "thread/archive": "ThreadArchiveParams",
    "thread/unsubscribe": "ThreadUnsubscribeParams",
    "thread/name/set": "ThreadSetNameParams",
    "thread/metadata/update": "ThreadMetadataUpdateParams",
    "thread/unarchive": "ThreadUnarchiveParams",
    "thread/compact/start": "ThreadCompactStartParams",
    "thread/rollback": "ThreadRollbackParams",
    "thread/list": "ThreadListParams",
    "thread/loaded/list": "ThreadLoadedListParams",
    "thread/read": "ThreadReadParams",
    "skills/list": "SkillsListParams",
    "skills/remote/list": "SkillsRemoteReadParams",
    "skills/remote/export": "SkillsRemoteWriteParams",
    "app/list": "AppsListParams",
    "skills/config/write": "SkillsConfigWriteParams",
    "plugin/install": "PluginInstallParams",
    "turn/start": "TurnStartParams",
    "turn/steer": "TurnSteerParams",
    "turn/interrupt": "TurnInterruptParams",
    "review/start": "ReviewStartParams",
    "model/list": "ModelListParams",
    "experimentalFeature/list": "ExperimentalFeatureListParams",
    "mcpServer/oauth/login": "McpServerOauthLoginParams",
    "config/mcpServer/reload": "None",
    "mcpServerStatus/list": "ListMcpServerStatusParams",
    "windowsSandbox/setupStart": "WindowsSandboxSetupStartParams",
    "account/login/start": "LoginAccountParams",
    "account/login/cancel": "CancelLoginAccountParams",
    "account/logout": "None",
    "account/rateLimits/read": "None",
    "feedback/upload": "FeedbackUploadParams",
    "command/exec": "CommandExecParams",
    "config/read": "ConfigReadParams",
    "externalAgentConfig/detect": "ExternalAgentConfigDetectParams",
    "externalAgentConfig/import": "ExternalAgentConfigImportParams",
    "config/value/write": "ConfigValueWriteParams",
    "config/batchWrite": "ConfigBatchWriteParams",
    "configRequirements/read": "None",
    "account/read": "GetAccountParams",
    "fuzzyFileSearch": "FuzzyFileSearchParams",
}

CLIENT_REQUEST_METHOD_TO_RESULT: Final[dict[str, str]] = {
    "initialize": "InitializeResponse",
    "thread/start": "ThreadStartResponse",
    "thread/resume": "ThreadResumeResponse",
    "thread/fork": "ThreadForkResponse",
    "thread/archive": "ThreadArchiveResponse",
    "thread/unsubscribe": "ThreadUnsubscribeResponse",
    "thread/name/set": "ThreadSetNameResponse",
    "thread/metadata/update": "ThreadMetadataUpdateResponse",
    "thread/unarchive": "ThreadUnarchiveResponse",
    "thread/compact/start": "ThreadCompactStartResponse",
    "thread/rollback": "ThreadRollbackResponse",
    "thread/list": "ThreadListResponse",
    "thread/loaded/list": "ThreadLoadedListResponse",
    "thread/read": "ThreadReadResponse",
    "skills/list": "SkillsListResponse",
    "skills/remote/list": "SkillsRemoteReadResponse",
    "skills/remote/export": "SkillsRemoteWriteResponse",
    "app/list": "AppsListResponse",
    "skills/config/write": "SkillsConfigWriteResponse",
    "plugin/install": "PluginInstallResponse",
    "turn/start": "TurnStartResponse",
    "turn/steer": "TurnSteerResponse",
    "turn/interrupt": "TurnInterruptResponse",
    "review/start": "ReviewStartResponse",
    "model/list": "ModelListResponse",
    "experimentalFeature/list": "ExperimentalFeatureListResponse",
    "mcpServer/oauth/login": "McpServerOauthLoginResponse",
    "config/mcpServer/reload": "McpServerRefreshResponse",
    "mcpServerStatus/list": "ListMcpServerStatusResponse",
    "windowsSandbox/setupStart": "WindowsSandboxSetupStartResponse",
    "account/login/start": "LoginAccountResponse",
    "account/login/cancel": "CancelLoginAccountResponse",
    "account/logout": "LogoutAccountResponse",
    "account/rateLimits/read": "GetAccountRateLimitsResponse",
    "feedback/upload": "FeedbackUploadResponse",
    "command/exec": "CommandExecResponse",
    "config/read": "ConfigReadResponse",
    "externalAgentConfig/detect": "ExternalAgentConfigDetectResponse",
    "externalAgentConfig/import": "ExternalAgentConfigImportResponse",
    "config/value/write": "ConfigWriteResponse",
    "config/batchWrite": "ConfigWriteResponse",
    "configRequirements/read": "ConfigRequirementsReadResponse",
    "account/read": "GetAccountResponse",
    "fuzzyFileSearch": "FuzzyFileSearchResponse",
}

SERVER_REQUEST_METHOD_TO_PARAMS: Final[dict[str, str]] = {
    "item/commandExecution/requestApproval": "CommandExecutionRequestApprovalParams",
    "item/fileChange/requestApproval": "FileChangeRequestApprovalParams",
    "item/tool/requestUserInput": "ToolRequestUserInputParams",
    "mcpServer/elicitation/request": "McpServerElicitationRequestParams",
    "item/tool/call": "DynamicToolCallParams",
    "account/chatgptAuthTokens/refresh": "ChatgptAuthTokensRefreshParams",
    "applyPatchApproval": "ApplyPatchApprovalParams",
    "execCommandApproval": "ExecCommandApprovalParams",
}

SERVER_REQUEST_METHOD_TO_RESULT: Final[dict[str, str]] = {
    "item/commandExecution/requestApproval": "CommandExecutionRequestApprovalResponse",
    "item/fileChange/requestApproval": "FileChangeRequestApprovalResponse",
    "item/tool/requestUserInput": "ToolRequestUserInputResponse",
    "mcpServer/elicitation/request": "McpServerElicitationRequestResponse",
    "item/tool/call": "DynamicToolCallResponse",
    "account/chatgptAuthTokens/refresh": "ChatgptAuthTokensRefreshResponse",
    "applyPatchApproval": "ApplyPatchApprovalResponse",
    "execCommandApproval": "ExecCommandApprovalResponse",
}

SERVER_NOTIFICATION_METHOD_TO_PARAMS: Final[dict[str, str]] = {
    "error": "ErrorNotification",
    "thread/started": "ThreadStartedNotification",
    "thread/status/changed": "ThreadStatusChangedNotification",
    "thread/archived": "ThreadArchivedNotification",
    "thread/unarchived": "ThreadUnarchivedNotification",
    "thread/closed": "ThreadClosedNotification",
    "skills/changed": "SkillsChangedNotification",
    "thread/name/updated": "ThreadNameUpdatedNotification",
    "thread/tokenUsage/updated": "ThreadTokenUsageUpdatedNotification",
    "turn/started": "TurnStartedNotification",
    "turn/completed": "TurnCompletedNotification",
    "turn/diff/updated": "TurnDiffUpdatedNotification",
    "turn/plan/updated": "TurnPlanUpdatedNotification",
    "item/started": "ItemStartedNotification",
    "item/completed": "ItemCompletedNotification",
    "item/agentMessage/delta": "AgentMessageDeltaNotification",
    "item/plan/delta": "PlanDeltaNotification",
    "item/commandExecution/outputDelta": "CommandExecutionOutputDeltaNotification",
    "item/commandExecution/terminalInteraction": "TerminalInteractionNotification",
    "item/fileChange/outputDelta": "FileChangeOutputDeltaNotification",
    "serverRequest/resolved": "ServerRequestResolvedNotification",
    "item/mcpToolCall/progress": "McpToolCallProgressNotification",
    "mcpServer/oauthLogin/completed": "McpServerOauthLoginCompletedNotification",
    "account/updated": "AccountUpdatedNotification",
    "account/rateLimits/updated": "AccountRateLimitsUpdatedNotification",
    "app/list/updated": "AppListUpdatedNotification",
    "item/reasoning/summaryTextDelta": "ReasoningSummaryTextDeltaNotification",
    "item/reasoning/summaryPartAdded": "ReasoningSummaryPartAddedNotification",
    "item/reasoning/textDelta": "ReasoningTextDeltaNotification",
    "thread/compacted": "ContextCompactedNotification",
    "model/rerouted": "ModelReroutedNotification",
    "deprecationNotice": "DeprecationNoticeNotification",
    "configWarning": "ConfigWarningNotification",
    "fuzzyFileSearch/sessionUpdated": "FuzzyFileSearchSessionUpdatedNotification",
    "fuzzyFileSearch/sessionCompleted": "FuzzyFileSearchSessionCompletedNotification",
    "thread/realtime/started": "ThreadRealtimeStartedNotification",
    "thread/realtime/itemAdded": "ThreadRealtimeItemAddedNotification",
    "thread/realtime/outputAudio/delta": "ThreadRealtimeOutputAudioDeltaNotification",
    "thread/realtime/error": "ThreadRealtimeErrorNotification",
    "thread/realtime/closed": "ThreadRealtimeClosedNotification",
    "windows/worldWritableWarning": "WindowsWorldWritableWarningNotification",
    "windowsSandbox/setupCompleted": "WindowsSandboxSetupCompletedNotification",
    "account/login/completed": "AccountLoginCompletedNotification",
}

CLIENT_REQUEST_METHODS: Final[tuple[str, ...]] = (
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
)

SERVER_REQUEST_METHODS: Final[tuple[str, ...]] = (
    "item/commandExecution/requestApproval",
    "item/fileChange/requestApproval",
    "item/tool/requestUserInput",
    "mcpServer/elicitation/request",
    "item/tool/call",
    "account/chatgptAuthTokens/refresh",
    "applyPatchApproval",
    "execCommandApproval",
)

SERVER_NOTIFICATION_METHODS: Final[tuple[str, ...]] = (
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
)
