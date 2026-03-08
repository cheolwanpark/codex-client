from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from . import _generated as generated
from .messages import JSONValue

if TYPE_CHECKING:
    from .runtime import TurnOptions


def client_info(
    name: str,
    version: str,
    *,
    title: str | None = None,
) -> generated.ClientInfo:
    payload: generated.ClientInfo = {"name": name, "version": version}
    if title is not None:
        payload["title"] = title
    return payload


def text_input(text: str) -> generated.TextUserInput:
    return {"type": "text", "text": text}


def thread_params(
    *,
    approval_policy: generated.AskForApproval | None = None,
    base_instructions: str | None = None,
    config: dict[str, JSONValue] | None = None,
    cwd: str | None = None,
    developer_instructions: str | None = None,
    ephemeral: bool = True,
    model: str | None = None,
    model_provider: str | None = None,
    personality: generated.Personality | None = None,
    sandbox: generated.SandboxMode | None = None,
    service_name: str | None = None,
    service_tier: generated.ServiceTier | None = None,
) -> generated.ThreadStartParams:
    payload: generated.ThreadStartParams = {"ephemeral": ephemeral}
    if approval_policy is not None:
        payload["approvalPolicy"] = approval_policy
    if base_instructions is not None:
        payload["baseInstructions"] = base_instructions
    if config is not None:
        payload["config"] = config
    if cwd is not None:
        payload["cwd"] = cwd
    if developer_instructions is not None:
        payload["developerInstructions"] = developer_instructions
    if model is not None:
        payload["model"] = model
    if model_provider is not None:
        payload["modelProvider"] = model_provider
    if personality is not None:
        payload["personality"] = personality
    if sandbox is not None:
        payload["sandbox"] = sandbox
    if service_name is not None:
        payload["serviceName"] = service_name
    if service_tier is not None:
        payload["serviceTier"] = service_tier
    return payload


def turn_options(
    *,
    approval_policy: generated.AskForApproval | None = None,
    cwd: str | None = None,
    effort: generated.ReasoningEffort | None = None,
    model: str | None = None,
    output_schema: JSONValue | None = None,
    personality: generated.Personality | None = None,
    sandbox_policy: generated.SandboxPolicy | None = None,
    service_tier: generated.ServiceTier | None = None,
    summary: generated.ReasoningSummary | None = None,
) -> "TurnOptions":
    payload: TurnOptions = {}
    if approval_policy is not None:
        payload["approvalPolicy"] = approval_policy
    if cwd is not None:
        payload["cwd"] = cwd
    if effort is not None:
        payload["effort"] = effort
    if model is not None:
        payload["model"] = model
    if output_schema is not None:
        payload["outputSchema"] = output_schema
    if personality is not None:
        payload["personality"] = personality
    if sandbox_policy is not None:
        payload["sandboxPolicy"] = sandbox_policy
    if service_tier is not None:
        payload["serviceTier"] = service_tier
    if summary is not None:
        payload["summary"] = summary
    return payload


def approve_command() -> generated.CommandExecutionRequestApprovalResponse:
    return {"decision": "accept"}


def decline_command() -> generated.CommandExecutionRequestApprovalResponse:
    return {"decision": "decline"}


def approve_file_change() -> generated.FileChangeRequestApprovalResponse:
    return {"decision": "accept"}


def decline_file_change() -> generated.FileChangeRequestApprovalResponse:
    return {"decision": "decline"}


def approve_file_change_for_session() -> generated.FileChangeRequestApprovalResponse:
    return {"decision": "acceptForSession"}


def tool_answers(
    answers_by_question: Mapping[str, Sequence[str]],
) -> generated.ToolRequestUserInputResponse:
    return {
        "answers": {
            question_id: {"answers": list(answers)}
            for question_id, answers in answers_by_question.items()
        }
    }


def tool_call_success(
    content_items: Sequence[generated.DynamicToolCallOutputContentItem] | None = None,
) -> generated.DynamicToolCallResponse:
    return {"success": True, "contentItems": list(content_items or ())}


def tool_call_failure(
    content_items: Sequence[generated.DynamicToolCallOutputContentItem] | None = None,
) -> generated.DynamicToolCallResponse:
    return {"success": False, "contentItems": list(content_items or ())}


__all__ = [
    "approve_command",
    "approve_file_change",
    "approve_file_change_for_session",
    "client_info",
    "decline_command",
    "decline_file_change",
    "text_input",
    "thread_params",
    "tool_answers",
    "tool_call_failure",
    "tool_call_success",
    "turn_options",
]
