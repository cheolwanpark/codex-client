"""Auto-generated typed request wrappers for TypedCodexClient."""

from __future__ import annotations

from typing import cast

from ._generated import *


class GeneratedClientMixin:
    async def initialize(
        self, params: InitializeParams, *, timeout: float | None = None
    ) -> InitializeResponse:
        return cast(InitializeResponse, await self.request("initialize", params, timeout=timeout))

    async def thread_start(
        self, params: ThreadStartParams | None = None, *, timeout: float | None = None
    ) -> ThreadStartResponse:
        payload = {} if params is None else params
        return cast(ThreadStartResponse, await self.request("thread/start", payload, timeout=timeout))

    async def thread_resume(
        self, params: ThreadResumeParams, *, timeout: float | None = None
    ) -> ThreadResumeResponse:
        return cast(ThreadResumeResponse, await self.request("thread/resume", params, timeout=timeout))

    async def thread_fork(
        self, params: ThreadForkParams, *, timeout: float | None = None
    ) -> ThreadForkResponse:
        return cast(ThreadForkResponse, await self.request("thread/fork", params, timeout=timeout))

    async def thread_archive(
        self, params: ThreadArchiveParams, *, timeout: float | None = None
    ) -> ThreadArchiveResponse:
        return cast(ThreadArchiveResponse, await self.request("thread/archive", params, timeout=timeout))

    async def thread_unsubscribe(
        self, params: ThreadUnsubscribeParams, *, timeout: float | None = None
    ) -> ThreadUnsubscribeResponse:
        return cast(ThreadUnsubscribeResponse, await self.request("thread/unsubscribe", params, timeout=timeout))

    async def thread_name_set(
        self, params: ThreadSetNameParams, *, timeout: float | None = None
    ) -> ThreadSetNameResponse:
        return cast(ThreadSetNameResponse, await self.request("thread/name/set", params, timeout=timeout))

    async def thread_metadata_update(
        self, params: ThreadMetadataUpdateParams, *, timeout: float | None = None
    ) -> ThreadMetadataUpdateResponse:
        return cast(ThreadMetadataUpdateResponse, await self.request("thread/metadata/update", params, timeout=timeout))

    async def thread_unarchive(
        self, params: ThreadUnarchiveParams, *, timeout: float | None = None
    ) -> ThreadUnarchiveResponse:
        return cast(ThreadUnarchiveResponse, await self.request("thread/unarchive", params, timeout=timeout))

    async def thread_compact_start(
        self, params: ThreadCompactStartParams, *, timeout: float | None = None
    ) -> ThreadCompactStartResponse:
        return cast(ThreadCompactStartResponse, await self.request("thread/compact/start", params, timeout=timeout))

    async def thread_rollback(
        self, params: ThreadRollbackParams, *, timeout: float | None = None
    ) -> ThreadRollbackResponse:
        return cast(ThreadRollbackResponse, await self.request("thread/rollback", params, timeout=timeout))

    async def thread_list(
        self, params: ThreadListParams | None = None, *, timeout: float | None = None
    ) -> ThreadListResponse:
        payload = {} if params is None else params
        return cast(ThreadListResponse, await self.request("thread/list", payload, timeout=timeout))

    async def thread_loaded_list(
        self, params: ThreadLoadedListParams | None = None, *, timeout: float | None = None
    ) -> ThreadLoadedListResponse:
        payload = {} if params is None else params
        return cast(ThreadLoadedListResponse, await self.request("thread/loaded/list", payload, timeout=timeout))

    async def thread_read(
        self, params: ThreadReadParams, *, timeout: float | None = None
    ) -> ThreadReadResponse:
        return cast(ThreadReadResponse, await self.request("thread/read", params, timeout=timeout))

    async def skills_list(
        self, params: SkillsListParams | None = None, *, timeout: float | None = None
    ) -> SkillsListResponse:
        payload = {} if params is None else params
        return cast(SkillsListResponse, await self.request("skills/list", payload, timeout=timeout))

    async def skills_remote_list(
        self, params: SkillsRemoteReadParams | None = None, *, timeout: float | None = None
    ) -> SkillsRemoteReadResponse:
        payload = {} if params is None else params
        return cast(SkillsRemoteReadResponse, await self.request("skills/remote/list", payload, timeout=timeout))

    async def skills_remote_export(
        self, params: SkillsRemoteWriteParams, *, timeout: float | None = None
    ) -> SkillsRemoteWriteResponse:
        return cast(SkillsRemoteWriteResponse, await self.request("skills/remote/export", params, timeout=timeout))

    async def app_list(
        self, params: AppsListParams | None = None, *, timeout: float | None = None
    ) -> AppsListResponse:
        payload = {} if params is None else params
        return cast(AppsListResponse, await self.request("app/list", payload, timeout=timeout))

    async def skills_config_write(
        self, params: SkillsConfigWriteParams, *, timeout: float | None = None
    ) -> SkillsConfigWriteResponse:
        return cast(SkillsConfigWriteResponse, await self.request("skills/config/write", params, timeout=timeout))

    async def plugin_install(
        self, params: PluginInstallParams, *, timeout: float | None = None
    ) -> PluginInstallResponse:
        return cast(PluginInstallResponse, await self.request("plugin/install", params, timeout=timeout))

    async def turn_start(
        self, params: TurnStartParams, *, timeout: float | None = None
    ) -> TurnStartResponse:
        return cast(TurnStartResponse, await self.request("turn/start", params, timeout=timeout))

    async def turn_steer(
        self, params: TurnSteerParams, *, timeout: float | None = None
    ) -> TurnSteerResponse:
        return cast(TurnSteerResponse, await self.request("turn/steer", params, timeout=timeout))

    async def turn_interrupt(
        self, params: TurnInterruptParams, *, timeout: float | None = None
    ) -> TurnInterruptResponse:
        return cast(TurnInterruptResponse, await self.request("turn/interrupt", params, timeout=timeout))

    async def review_start(
        self, params: ReviewStartParams, *, timeout: float | None = None
    ) -> ReviewStartResponse:
        return cast(ReviewStartResponse, await self.request("review/start", params, timeout=timeout))

    async def model_list(
        self, params: ModelListParams | None = None, *, timeout: float | None = None
    ) -> ModelListResponse:
        payload = {} if params is None else params
        return cast(ModelListResponse, await self.request("model/list", payload, timeout=timeout))

    async def experimental_feature_list(
        self, params: ExperimentalFeatureListParams | None = None, *, timeout: float | None = None
    ) -> ExperimentalFeatureListResponse:
        payload = {} if params is None else params
        return cast(ExperimentalFeatureListResponse, await self.request("experimentalFeature/list", payload, timeout=timeout))

    async def mcp_server_oauth_login(
        self, params: McpServerOauthLoginParams, *, timeout: float | None = None
    ) -> McpServerOauthLoginResponse:
        return cast(McpServerOauthLoginResponse, await self.request("mcpServer/oauth/login", params, timeout=timeout))

    async def config_mcp_server_reload(self, *, timeout: float | None = None) -> McpServerRefreshResponse:
        return cast(McpServerRefreshResponse, await self.request("config/mcpServer/reload", None, timeout=timeout))

    async def mcp_server_status_list(
        self, params: ListMcpServerStatusParams | None = None, *, timeout: float | None = None
    ) -> ListMcpServerStatusResponse:
        payload = {} if params is None else params
        return cast(ListMcpServerStatusResponse, await self.request("mcpServerStatus/list", payload, timeout=timeout))

    async def windows_sandbox_setup_start(
        self, params: WindowsSandboxSetupStartParams, *, timeout: float | None = None
    ) -> WindowsSandboxSetupStartResponse:
        return cast(WindowsSandboxSetupStartResponse, await self.request("windowsSandbox/setupStart", params, timeout=timeout))

    async def account_login_start(
        self, params: LoginAccountParams, *, timeout: float | None = None
    ) -> LoginAccountResponse:
        return cast(LoginAccountResponse, await self.request("account/login/start", params, timeout=timeout))

    async def account_login_cancel(
        self, params: CancelLoginAccountParams, *, timeout: float | None = None
    ) -> CancelLoginAccountResponse:
        return cast(CancelLoginAccountResponse, await self.request("account/login/cancel", params, timeout=timeout))

    async def account_logout(self, *, timeout: float | None = None) -> LogoutAccountResponse:
        return cast(LogoutAccountResponse, await self.request("account/logout", None, timeout=timeout))

    async def account_rate_limits_read(self, *, timeout: float | None = None) -> GetAccountRateLimitsResponse:
        return cast(GetAccountRateLimitsResponse, await self.request("account/rateLimits/read", None, timeout=timeout))

    async def feedback_upload(
        self, params: FeedbackUploadParams, *, timeout: float | None = None
    ) -> FeedbackUploadResponse:
        return cast(FeedbackUploadResponse, await self.request("feedback/upload", params, timeout=timeout))

    async def command_exec(
        self, params: CommandExecParams, *, timeout: float | None = None
    ) -> CommandExecResponse:
        return cast(CommandExecResponse, await self.request("command/exec", params, timeout=timeout))

    async def config_read(
        self, params: ConfigReadParams | None = None, *, timeout: float | None = None
    ) -> ConfigReadResponse:
        payload = {} if params is None else params
        return cast(ConfigReadResponse, await self.request("config/read", payload, timeout=timeout))

    async def external_agent_config_detect(
        self, params: ExternalAgentConfigDetectParams | None = None, *, timeout: float | None = None
    ) -> ExternalAgentConfigDetectResponse:
        payload = {} if params is None else params
        return cast(ExternalAgentConfigDetectResponse, await self.request("externalAgentConfig/detect", payload, timeout=timeout))

    async def external_agent_config_import(
        self, params: ExternalAgentConfigImportParams, *, timeout: float | None = None
    ) -> ExternalAgentConfigImportResponse:
        return cast(ExternalAgentConfigImportResponse, await self.request("externalAgentConfig/import", params, timeout=timeout))

    async def config_value_write(
        self, params: ConfigValueWriteParams, *, timeout: float | None = None
    ) -> ConfigWriteResponse:
        return cast(ConfigWriteResponse, await self.request("config/value/write", params, timeout=timeout))

    async def config_batch_write(
        self, params: ConfigBatchWriteParams, *, timeout: float | None = None
    ) -> ConfigWriteResponse:
        return cast(ConfigWriteResponse, await self.request("config/batchWrite", params, timeout=timeout))

    async def config_requirements_read(self, *, timeout: float | None = None) -> ConfigRequirementsReadResponse:
        return cast(ConfigRequirementsReadResponse, await self.request("configRequirements/read", None, timeout=timeout))

    async def account_read(
        self, params: GetAccountParams | None = None, *, timeout: float | None = None
    ) -> GetAccountResponse:
        payload = {} if params is None else params
        return cast(GetAccountResponse, await self.request("account/read", payload, timeout=timeout))

    async def fuzzy_file_search(
        self, params: FuzzyFileSearchParams, *, timeout: float | None = None
    ) -> FuzzyFileSearchResponse:
        return cast(FuzzyFileSearchResponse, await self.request("fuzzyFileSearch", params, timeout=timeout))
