/* Auto-generated typed request wrappers for TypedCodexClient. */

import type * as ProtocolTypes from "./generated.js";

type RequestOptions = { timeoutMs?: number };

export abstract class GeneratedTypedCodexClient {
  protected abstract request<TResult = unknown>(
    method: string,
    params?: unknown,
    options?: RequestOptions,
  ): Promise<TResult>;

  protected requestTyped<M extends ProtocolTypes.ClientRequestMethod>(
    method: M,
    params: unknown,
    options?: RequestOptions,
  ): Promise<ProtocolTypes.ClientRequestResultByMethod[M]> {
    return this.request<ProtocolTypes.ClientRequestResultByMethod[M]>(method, params, options);
  }

  async initialize(params: ProtocolTypes.InitializeParams, options?: RequestOptions): Promise<ProtocolTypes.InitializeResponse> {
    return this.requestTyped("initialize", params, options);
  }

  async threadStart(params?: ProtocolTypes.ThreadStartParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadStartResponse> {
    const payload = params ?? {};
    return this.requestTyped("thread/start", payload, options);
  }

  async threadResume(params: ProtocolTypes.ThreadResumeParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadResumeResponse> {
    return this.requestTyped("thread/resume", params, options);
  }

  async threadFork(params: ProtocolTypes.ThreadForkParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadForkResponse> {
    return this.requestTyped("thread/fork", params, options);
  }

  async threadArchive(params: ProtocolTypes.ThreadArchiveParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadArchiveResponse> {
    return this.requestTyped("thread/archive", params, options);
  }

  async threadUnsubscribe(params: ProtocolTypes.ThreadUnsubscribeParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadUnsubscribeResponse> {
    return this.requestTyped("thread/unsubscribe", params, options);
  }

  async threadNameSet(params: ProtocolTypes.ThreadSetNameParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadSetNameResponse> {
    return this.requestTyped("thread/name/set", params, options);
  }

  async threadMetadataUpdate(params: ProtocolTypes.ThreadMetadataUpdateParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadMetadataUpdateResponse> {
    return this.requestTyped("thread/metadata/update", params, options);
  }

  async threadUnarchive(params: ProtocolTypes.ThreadUnarchiveParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadUnarchiveResponse> {
    return this.requestTyped("thread/unarchive", params, options);
  }

  async threadCompactStart(params: ProtocolTypes.ThreadCompactStartParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadCompactStartResponse> {
    return this.requestTyped("thread/compact/start", params, options);
  }

  async threadRollback(params: ProtocolTypes.ThreadRollbackParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadRollbackResponse> {
    return this.requestTyped("thread/rollback", params, options);
  }

  async threadList(params?: ProtocolTypes.ThreadListParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadListResponse> {
    const payload = params ?? {};
    return this.requestTyped("thread/list", payload, options);
  }

  async threadLoadedList(params?: ProtocolTypes.ThreadLoadedListParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadLoadedListResponse> {
    const payload = params ?? {};
    return this.requestTyped("thread/loaded/list", payload, options);
  }

  async threadRead(params: ProtocolTypes.ThreadReadParams, options?: RequestOptions): Promise<ProtocolTypes.ThreadReadResponse> {
    return this.requestTyped("thread/read", params, options);
  }

  async skillsList(params?: ProtocolTypes.SkillsListParams, options?: RequestOptions): Promise<ProtocolTypes.SkillsListResponse> {
    const payload = params ?? {};
    return this.requestTyped("skills/list", payload, options);
  }

  async skillsRemoteList(params?: ProtocolTypes.SkillsRemoteReadParams, options?: RequestOptions): Promise<ProtocolTypes.SkillsRemoteReadResponse> {
    const payload = params ?? {};
    return this.requestTyped("skills/remote/list", payload, options);
  }

  async skillsRemoteExport(params: ProtocolTypes.SkillsRemoteWriteParams, options?: RequestOptions): Promise<ProtocolTypes.SkillsRemoteWriteResponse> {
    return this.requestTyped("skills/remote/export", params, options);
  }

  async appList(params?: ProtocolTypes.AppsListParams, options?: RequestOptions): Promise<ProtocolTypes.AppsListResponse> {
    const payload = params ?? {};
    return this.requestTyped("app/list", payload, options);
  }

  async skillsConfigWrite(params: ProtocolTypes.SkillsConfigWriteParams, options?: RequestOptions): Promise<ProtocolTypes.SkillsConfigWriteResponse> {
    return this.requestTyped("skills/config/write", params, options);
  }

  async pluginInstall(params: ProtocolTypes.PluginInstallParams, options?: RequestOptions): Promise<ProtocolTypes.PluginInstallResponse> {
    return this.requestTyped("plugin/install", params, options);
  }

  async turnStart(params: ProtocolTypes.TurnStartParams, options?: RequestOptions): Promise<ProtocolTypes.TurnStartResponse> {
    return this.requestTyped("turn/start", params, options);
  }

  async turnSteer(params: ProtocolTypes.TurnSteerParams, options?: RequestOptions): Promise<ProtocolTypes.TurnSteerResponse> {
    return this.requestTyped("turn/steer", params, options);
  }

  async turnInterrupt(params: ProtocolTypes.TurnInterruptParams, options?: RequestOptions): Promise<ProtocolTypes.TurnInterruptResponse> {
    return this.requestTyped("turn/interrupt", params, options);
  }

  async reviewStart(params: ProtocolTypes.ReviewStartParams, options?: RequestOptions): Promise<ProtocolTypes.ReviewStartResponse> {
    return this.requestTyped("review/start", params, options);
  }

  async modelList(params?: ProtocolTypes.ModelListParams, options?: RequestOptions): Promise<ProtocolTypes.ModelListResponse> {
    const payload = params ?? {};
    return this.requestTyped("model/list", payload, options);
  }

  async experimentalFeatureList(params?: ProtocolTypes.ExperimentalFeatureListParams, options?: RequestOptions): Promise<ProtocolTypes.ExperimentalFeatureListResponse> {
    const payload = params ?? {};
    return this.requestTyped("experimentalFeature/list", payload, options);
  }

  async mcpServerOauthLogin(params: ProtocolTypes.McpServerOauthLoginParams, options?: RequestOptions): Promise<ProtocolTypes.McpServerOauthLoginResponse> {
    return this.requestTyped("mcpServer/oauth/login", params, options);
  }

  async configMcpServerReload(options?: RequestOptions): Promise<ProtocolTypes.McpServerRefreshResponse> {
    return this.requestTyped("config/mcpServer/reload", null, options);
  }

  async mcpServerStatusList(params?: ProtocolTypes.ListMcpServerStatusParams, options?: RequestOptions): Promise<ProtocolTypes.ListMcpServerStatusResponse> {
    const payload = params ?? {};
    return this.requestTyped("mcpServerStatus/list", payload, options);
  }

  async windowsSandboxSetupStart(params: ProtocolTypes.WindowsSandboxSetupStartParams, options?: RequestOptions): Promise<ProtocolTypes.WindowsSandboxSetupStartResponse> {
    return this.requestTyped("windowsSandbox/setupStart", params, options);
  }

  async accountLoginStart(params: ProtocolTypes.LoginAccountParams, options?: RequestOptions): Promise<ProtocolTypes.LoginAccountResponse> {
    return this.requestTyped("account/login/start", params, options);
  }

  async accountLoginCancel(params: ProtocolTypes.CancelLoginAccountParams, options?: RequestOptions): Promise<ProtocolTypes.CancelLoginAccountResponse> {
    return this.requestTyped("account/login/cancel", params, options);
  }

  async accountLogout(options?: RequestOptions): Promise<ProtocolTypes.LogoutAccountResponse> {
    return this.requestTyped("account/logout", null, options);
  }

  async accountRateLimitsRead(options?: RequestOptions): Promise<ProtocolTypes.GetAccountRateLimitsResponse> {
    return this.requestTyped("account/rateLimits/read", null, options);
  }

  async feedbackUpload(params: ProtocolTypes.FeedbackUploadParams, options?: RequestOptions): Promise<ProtocolTypes.FeedbackUploadResponse> {
    return this.requestTyped("feedback/upload", params, options);
  }

  async commandExec(params: ProtocolTypes.CommandExecParams, options?: RequestOptions): Promise<ProtocolTypes.CommandExecResponse> {
    return this.requestTyped("command/exec", params, options);
  }

  async configRead(params?: ProtocolTypes.ConfigReadParams, options?: RequestOptions): Promise<ProtocolTypes.ConfigReadResponse> {
    const payload = params ?? {};
    return this.requestTyped("config/read", payload, options);
  }

  async externalAgentConfigDetect(params?: ProtocolTypes.ExternalAgentConfigDetectParams, options?: RequestOptions): Promise<ProtocolTypes.ExternalAgentConfigDetectResponse> {
    const payload = params ?? {};
    return this.requestTyped("externalAgentConfig/detect", payload, options);
  }

  async externalAgentConfigImport(params: ProtocolTypes.ExternalAgentConfigImportParams, options?: RequestOptions): Promise<ProtocolTypes.ExternalAgentConfigImportResponse> {
    return this.requestTyped("externalAgentConfig/import", params, options);
  }

  async configValueWrite(params: ProtocolTypes.ConfigValueWriteParams, options?: RequestOptions): Promise<ProtocolTypes.ConfigWriteResponse> {
    return this.requestTyped("config/value/write", params, options);
  }

  async configBatchWrite(params: ProtocolTypes.ConfigBatchWriteParams, options?: RequestOptions): Promise<ProtocolTypes.ConfigWriteResponse> {
    return this.requestTyped("config/batchWrite", params, options);
  }

  async configRequirementsRead(options?: RequestOptions): Promise<ProtocolTypes.ConfigRequirementsReadResponse> {
    return this.requestTyped("configRequirements/read", null, options);
  }

  async accountRead(params?: ProtocolTypes.GetAccountParams, options?: RequestOptions): Promise<ProtocolTypes.GetAccountResponse> {
    const payload = params ?? {};
    return this.requestTyped("account/read", payload, options);
  }

  async fuzzyFileSearch(params: ProtocolTypes.FuzzyFileSearchParams, options?: RequestOptions): Promise<ProtocolTypes.FuzzyFileSearchResponse> {
    return this.requestTyped("fuzzyFileSearch", params, options);
  }

}
