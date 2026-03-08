from __future__ import annotations

from enum import StrEnum


class NotificationMethod(StrEnum):
    ERROR = "error"
    THREAD_STARTED = "thread/started"
    THREAD_STATUS_CHANGED = "thread/status/changed"
    THREAD_NAME_UPDATED = "thread/name/updated"
    TURN_STARTED = "turn/started"
    TURN_COMPLETED = "turn/completed"
    TURN_DIFF_UPDATED = "turn/diff/updated"
    TURN_PLAN_UPDATED = "turn/plan/updated"
    ITEM_STARTED = "item/started"
    ITEM_COMPLETED = "item/completed"
    ITEM_AGENT_MESSAGE_DELTA = "item/agentMessage/delta"
    ITEM_PLAN_DELTA = "item/plan/delta"
    ITEM_REASONING_TEXT_DELTA = "item/reasoning/textDelta"
    ITEM_REASONING_SUMMARY_TEXT_DELTA = "item/reasoning/summaryTextDelta"
    ITEM_COMMAND_EXECUTION_OUTPUT_DELTA = "item/commandExecution/outputDelta"
    ITEM_FILE_CHANGE_OUTPUT_DELTA = "item/fileChange/outputDelta"


class ServerRequestMethod(StrEnum):
    ITEM_COMMAND_EXECUTION_REQUEST_APPROVAL = "item/commandExecution/requestApproval"
    ITEM_FILE_CHANGE_REQUEST_APPROVAL = "item/fileChange/requestApproval"
    ITEM_TOOL_REQUEST_USER_INPUT = "item/tool/requestUserInput"
    ITEM_TOOL_CALL = "item/tool/call"


class TurnEventType(StrEnum):
    ITEM_STARTED = "item_started"
    ITEM_COMPLETED = "item_completed"
    AGENT_MESSAGE_DELTA = "agent_message_delta"
    PLAN_DELTA = "plan_delta"
    REASONING_DELTA = "reasoning_delta"
    REASONING_SUMMARY_DELTA = "reasoning_summary_delta"
    COMMAND_OUTPUT_DELTA = "command_output_delta"
    FILE_CHANGE_DELTA = "file_change_delta"
    TURN_DIFF_UPDATED = "turn_diff_updated"
    PLAN_UPDATED = "plan_updated"
    ERROR = "error"
    COMPLETED = "completed"


__all__ = [
    "NotificationMethod",
    "ServerRequestMethod",
    "TurnEventType",
]
