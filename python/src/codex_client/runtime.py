from __future__ import annotations

import asyncio
import contextlib
from collections import defaultdict
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Literal, TypeAlias, TypedDict, cast

from . import _generated as generated
from .client import Middleware, TypedCodexClient
from .messages import JSONValue
from .transport import StdioTransport, Transport

NotificationHandler: TypeAlias = Callable[[JSONValue], Awaitable[None] | None]
CommandApprovalHook: TypeAlias = Callable[
    [generated.CommandExecutionRequestApprovalParams],
    Awaitable[generated.CommandExecutionRequestApprovalResponse]
    | generated.CommandExecutionRequestApprovalResponse,
]
FileChangeApprovalHook: TypeAlias = Callable[
    [generated.FileChangeRequestApprovalParams],
    Awaitable[generated.FileChangeRequestApprovalResponse]
    | generated.FileChangeRequestApprovalResponse,
]
ToolUserInputHook: TypeAlias = Callable[
    [generated.ToolRequestUserInputParams],
    Awaitable[generated.ToolRequestUserInputResponse]
    | generated.ToolRequestUserInputResponse,
]
DynamicToolCallHook: TypeAlias = Callable[
    [generated.DynamicToolCallParams],
    Awaitable[generated.DynamicToolCallResponse] | generated.DynamicToolCallResponse,
]


class ItemStartedEvent(TypedDict):
    type: Literal["item_started"]
    item: generated.ThreadItem


class ItemCompletedEvent(TypedDict):
    type: Literal["item_completed"]
    item: generated.ThreadItem


class AgentMessageDeltaEvent(TypedDict):
    type: Literal["agent_message_delta"]
    item_id: str
    delta: str


class PlanDeltaEvent(TypedDict):
    type: Literal["plan_delta"]
    item_id: str
    delta: str


class ReasoningDeltaEvent(TypedDict):
    type: Literal["reasoning_delta"]
    item_id: str
    delta: str


class ReasoningSummaryDeltaEvent(TypedDict):
    type: Literal["reasoning_summary_delta"]
    item_id: str
    delta: str
    summary_index: int


class CommandOutputDeltaEvent(TypedDict):
    type: Literal["command_output_delta"]
    item_id: str
    delta: str


class FileChangeDeltaEvent(TypedDict):
    type: Literal["file_change_delta"]
    item_id: str
    delta: str


class TurnDiffUpdatedEvent(TypedDict):
    type: Literal["turn_diff_updated"]
    diff: str


class PlanUpdatedEvent(TypedDict):
    type: Literal["plan_updated"]
    plan: list[generated.TurnPlanStep]
    explanation: str | None


class ErrorEvent(TypedDict):
    type: Literal["error"]
    error: generated.TurnError


class CompletedEvent(TypedDict):
    type: Literal["completed"]
    turn: generated.Turn


class TurnOptions(TypedDict, total=False):
    approvalPolicy: generated.AskForApproval | None
    cwd: str | None
    effort: generated.ReasoningEffort | None
    model: str | None
    outputSchema: JSONValue
    personality: generated.Personality | None
    sandboxPolicy: generated.SandboxPolicy | None
    serviceTier: generated.ServiceTier | None
    summary: generated.ReasoningSummary | None


TurnEvent: TypeAlias = (
    ItemStartedEvent
    | ItemCompletedEvent
    | AgentMessageDeltaEvent
    | PlanDeltaEvent
    | ReasoningDeltaEvent
    | ReasoningSummaryDeltaEvent
    | CommandOutputDeltaEvent
    | FileChangeDeltaEvent
    | TurnDiffUpdatedEvent
    | PlanUpdatedEvent
    | ErrorEvent
    | CompletedEvent
)

_TURN_STREAM_EOF = object()


@dataclass(slots=True)
class ApprovalPolicy:
    on_command_execution: CommandApprovalHook | None = None
    on_file_change: FileChangeApprovalHook | None = None
    on_tool_request_user_input: ToolUserInputHook | None = None
    on_dynamic_tool_call: DynamicToolCallHook | None = None

    @classmethod
    def auto_accept(cls) -> "ApprovalPolicy":
        return cls(
            on_command_execution=lambda _params: {"decision": "accept"},
            on_file_change=lambda _params: {"decision": "accept"},
            on_tool_request_user_input=lambda params: {
                "answers": {
                    question["id"]: {"answers": []} for question in params["questions"]
                }
            },
            on_dynamic_tool_call=lambda _params: {"success": True, "contentItems": []},
        )

    @classmethod
    def auto_decline(cls) -> "ApprovalPolicy":
        return cls(
            on_command_execution=lambda _params: {"decision": "decline"},
            on_file_change=lambda _params: {"decision": "decline"},
            on_tool_request_user_input=lambda _params: {"answers": {}},
            on_dynamic_tool_call=lambda _params: {"success": False, "contentItems": []},
        )

    @classmethod
    def commands_only(cls) -> "ApprovalPolicy":
        return cls(
            on_command_execution=lambda _params: {"decision": "accept"},
            on_file_change=lambda _params: {"decision": "decline"},
            on_tool_request_user_input=lambda _params: {"answers": {}},
            on_dynamic_tool_call=lambda _params: {"success": False, "contentItems": []},
        )

    @classmethod
    def custom(
        cls,
        *,
        on_command_execution: CommandApprovalHook | None = None,
        on_file_change: FileChangeApprovalHook | None = None,
        on_tool_request_user_input: ToolUserInputHook | None = None,
        on_dynamic_tool_call: DynamicToolCallHook | None = None,
    ) -> "ApprovalPolicy":
        return cls(
            on_command_execution=on_command_execution,
            on_file_change=on_file_change,
            on_tool_request_user_input=on_tool_request_user_input,
            on_dynamic_tool_call=on_dynamic_tool_call,
        )

    async def handle_command_execution(
        self, params: generated.CommandExecutionRequestApprovalParams
    ) -> generated.CommandExecutionRequestApprovalResponse:
        if self.on_command_execution is None:
            return {"decision": "decline"}
        return await _maybe_await(self.on_command_execution(params))

    async def handle_file_change(
        self, params: generated.FileChangeRequestApprovalParams
    ) -> generated.FileChangeRequestApprovalResponse:
        if self.on_file_change is None:
            return {"decision": "decline"}
        return await _maybe_await(self.on_file_change(params))

    async def handle_tool_request_user_input(
        self, params: generated.ToolRequestUserInputParams
    ) -> generated.ToolRequestUserInputResponse:
        if self.on_tool_request_user_input is None:
            return {"answers": {}}
        return await _maybe_await(self.on_tool_request_user_input(params))

    async def handle_dynamic_tool_call(
        self, params: generated.DynamicToolCallParams
    ) -> generated.DynamicToolCallResponse:
        if self.on_dynamic_tool_call is None:
            return {"success": False, "contentItems": []}
        return await _maybe_await(self.on_dynamic_tool_call(params))


class Session:
    def __init__(
        self,
        client: TypedCodexClient,
        *,
        approval_policy: ApprovalPolicy,
    ) -> None:
        self._client = client
        self._approval_policy = approval_policy
        self._threads: dict[str, Thread] = {}
        self._notification_handlers: defaultdict[str, list[NotificationHandler]] = defaultdict(list)
        self._closed = False

        self._register_protocol_handlers()

    @classmethod
    async def create(
        cls,
        *,
        client_info: generated.ClientInfo,
        capabilities: generated.InitializeCapabilities | None = None,
        approval_policy: ApprovalPolicy | None = None,
        middleware: Sequence[Middleware] = (),
        transport: Transport | None = None,
        command: str = "codex",
        args: Sequence[str] = ("app-server",),
        cwd: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> "Session":
        if transport is not None and (
            command != "codex"
            or tuple(args) != ("app-server",)
            or cwd is not None
            or env is not None
        ):
            raise ValueError("transport cannot be combined with custom stdio transport options")

        if transport is None:
            transport = StdioTransport(command=command, args=args, cwd=cwd, env=env)

        client = TypedCodexClient.from_transport(transport)
        for entry in middleware:
            client.use(entry)

        session = cls(client, approval_policy=approval_policy or ApprovalPolicy.auto_decline())
        await client.initialize({"clientInfo": client_info, "capabilities": capabilities})
        await client.send_initialized()
        return session

    @property
    def client(self) -> TypedCodexClient:
        return self._client

    async def __aenter__(self) -> "Session":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    def on(self, method: str, handler: NotificationHandler) -> Callable[[], None]:
        handlers = self._notification_handlers[method]
        handlers.append(handler)

        def unsubscribe() -> None:
            with contextlib.suppress(ValueError):
                handlers.remove(handler)

        return unsubscribe

    async def start_thread(
        self, params: generated.ThreadStartParams | None = None
    ) -> "Thread":
        response = await self._client.thread_start(params)
        return self._hydrate_thread(response["thread"], response)

    async def start_ephemeral_thread(
        self, params: generated.ThreadStartParams | None = None
    ) -> "Thread":
        payload = dict(params or {})
        payload["ephemeral"] = True
        return await self.start_thread(payload)

    async def resume_thread(
        self,
        thread_id: str,
        params: generated.ThreadResumeParams | None = None,
    ) -> "Thread":
        payload = dict(params or {})
        payload["threadId"] = thread_id
        response = await self._client.thread_resume(payload)
        return self._hydrate_thread(response["thread"], response)

    async def fork_thread(self, thread_id: str) -> "Thread":
        response = await self._client.thread_fork({"threadId": thread_id})
        return self._hydrate_thread(response["thread"], response)

    async def list_threads(
        self, params: generated.ThreadListParams | None = None
    ) -> generated.ThreadListResponse:
        return await self._client.thread_list(params)

    async def read_thread(
        self, thread_id: str, include_turns: bool = False
    ) -> generated.Thread:
        response = await self._client.thread_read(
            {"threadId": thread_id, "includeTurns": include_turns}
        )
        return response["thread"]

    async def list_models(
        self, params: generated.ModelListParams | None = None
    ) -> generated.ModelListResponse:
        return await self._client.model_list(params)

    async def exec(
        self,
        command: list[str],
        *,
        cwd: str | None = None,
        sandbox_policy: generated.SandboxPolicy | None = None,
        timeout_ms: int | None = None,
    ) -> generated.CommandExecResponse:
        payload: generated.CommandExecParams = {"command": command}
        if cwd is not None:
            payload["cwd"] = cwd
        if sandbox_policy is not None:
            payload["sandboxPolicy"] = sandbox_policy
        if timeout_ms is not None:
            payload["timeoutMs"] = timeout_ms
        return await self._client.command_exec(payload)

    async def close(self) -> None:
        if self._closed:
            return

        self._closed = True
        await self._client.close()

    def _register_protocol_handlers(self) -> None:
        for method in generated.SERVER_NOTIFICATION_METHODS:
            self._client.on_notification(method, self._build_notification_handler(method))

        self._client.on_server_request(
            "item/commandExecution/requestApproval",
            self._approval_policy.handle_command_execution,
        )
        self._client.on_server_request(
            "item/fileChange/requestApproval",
            self._approval_policy.handle_file_change,
        )
        self._client.on_server_request(
            "item/tool/requestUserInput",
            self._approval_policy.handle_tool_request_user_input,
        )
        self._client.on_server_request(
            "item/tool/call",
            self._approval_policy.handle_dynamic_tool_call,
        )

    def _build_notification_handler(self, method: str) -> NotificationHandler:
        async def handler(params: JSONValue) -> None:
            await self._handle_notification(method, params)

        return handler

    async def _handle_notification(self, method: str, params: JSONValue) -> None:
        thread = self._apply_notification(method, params)
        await _emit_handlers(self._notification_handlers.get(method, ()), params)
        if thread is not None:
            await thread._emit_notification(method, params)

    def _apply_notification(self, method: str, params: JSONValue) -> Thread | None:
        if not isinstance(params, dict):
            return None

        if method == "thread/started" and "thread" in params:
            thread = self._get_or_create_thread(cast(generated.Thread, params["thread"]))
            return thread

        thread_id = _thread_id_from_notification(method, params)
        if thread_id is None:
            return None

        thread = self._threads.get(thread_id)
        if thread is None:
            return None

        thread._apply_notification(method, params)
        return thread

    def _hydrate_thread(
        self,
        thread_snapshot: generated.Thread,
        response: generated.ThreadStartResponse
        | generated.ThreadResumeResponse
        | generated.ThreadForkResponse,
    ) -> "Thread":
        thread = self._get_or_create_thread(thread_snapshot)
        thread._apply_thread_defaults(response)
        return thread

    def _get_or_create_thread(self, thread_snapshot: generated.Thread) -> "Thread":
        thread_id = thread_snapshot["id"]
        thread = self._threads.get(thread_id)
        if thread is None:
            thread = Thread(self, thread_snapshot)
            self._threads[thread_id] = thread
            return thread

        thread._replace_snapshot(thread_snapshot)
        return thread


class Thread:
    def __init__(self, session: Session, snapshot: generated.Thread) -> None:
        self._session = session
        self._data = _clone(snapshot)
        self._turns: dict[str, Turn] = {}
        self._notification_handlers: defaultdict[str, list[NotificationHandler]] = defaultdict(list)
        self._defaults: dict[str, JSONValue] = {}

        for turn in self._data.get("turns", []):
            self._turns[turn["id"]] = Turn(self, turn)

    @property
    def id(self) -> str:
        return self._data["id"]

    @property
    def name(self) -> str | None:
        return self._data.get("name")

    @property
    def status(self) -> generated.ThreadStatus:
        return self._data["status"]

    @property
    def data(self) -> generated.Thread:
        return self._data

    @property
    def active_turn(self) -> Turn | None:
        for turn in self._turns.values():
            if turn.status == "inProgress":
                return turn
        return None

    def on(self, method: str, handler: NotificationHandler) -> Callable[[], None]:
        handlers = self._notification_handlers[method]
        handlers.append(handler)

        def unsubscribe() -> None:
            with contextlib.suppress(ValueError):
                handlers.remove(handler)

        return unsubscribe

    async def start_turn(
        self,
        input: str | list[generated.UserInput],
        options: TurnOptions | None = None,
    ) -> "Turn":
        payload = dict(options or {})
        payload["threadId"] = self.id
        payload["input"] = _normalize_input(input)
        response = await self._session.client.turn_start(payload)
        turn = self._get_or_create_turn(response["turn"])
        self._upsert_turn_snapshot(response["turn"])
        return turn

    async def ask(
        self,
        input: str | list[generated.UserInput],
        options: TurnOptions | None = None,
    ) -> str:
        turn = await self.start_turn(input, options)
        return await turn.text()

    async def steer(self, input: str | list[generated.UserInput], expected_turn_id: str) -> None:
        await self._session.client.turn_steer(
            {
                "threadId": self.id,
                "expectedTurnId": expected_turn_id,
                "input": _normalize_input(input),
            }
        )

    async def interrupt(self, turn_id: str) -> None:
        await self._session.client.turn_interrupt({"threadId": self.id, "turnId": turn_id})

    async def review(
        self,
        target: generated.ReviewTarget,
        delivery: generated.ReviewDelivery | None = None,
    ) -> "Turn":
        payload: generated.ReviewStartParams = {"threadId": self.id, "target": target}
        if delivery is not None:
            payload["delivery"] = delivery

        response = await self._session.client.review_start(payload)
        turn = self._get_or_create_turn(response["turn"])
        turn._review_thread_id = response["reviewThreadId"]
        self._upsert_turn_snapshot(response["turn"])
        return turn

    async def archive(self) -> None:
        await self._session.client.thread_archive({"threadId": self.id})

    async def unarchive(self) -> "Thread":
        response = await self._session.client.thread_unarchive({"threadId": self.id})
        return self._session._get_or_create_thread(response["thread"])

    async def fork(self) -> "Thread":
        return await self._session.fork_thread(self.id)

    async def rollback(self, num_turns: int) -> None:
        response = await self._session.client.thread_rollback(
            {"threadId": self.id, "numTurns": num_turns}
        )
        self._replace_snapshot(response["thread"])

    async def compact(self) -> None:
        await self._session.client.thread_compact_start({"threadId": self.id})

    async def unsubscribe(self) -> None:
        await self._session.client.thread_unsubscribe({"threadId": self.id})

    async def set_name(self, name: str) -> None:
        await self._session.client.thread_name_set({"threadId": self.id, "name": name})
        self._data["name"] = name

    async def _emit_notification(self, method: str, params: JSONValue) -> None:
        await _emit_handlers(self._notification_handlers.get(method, ()), params)

    def _replace_snapshot(self, snapshot: generated.Thread) -> None:
        self._data = _clone(snapshot)
        turns = self._data.get("turns", [])
        seen_turn_ids: set[str] = set()
        for turn_snapshot in turns:
            seen_turn_ids.add(turn_snapshot["id"])
            self._get_or_create_turn(turn_snapshot)
        for turn_id in list(self._turns):
            if turn_id not in seen_turn_ids:
                del self._turns[turn_id]

    def _apply_thread_defaults(
        self,
        response: generated.ThreadStartResponse
        | generated.ThreadResumeResponse
        | generated.ThreadForkResponse,
    ) -> None:
        self._defaults = {
            key: _clone(value)
            for key, value in response.items()
            if key != "thread"
        }

    def _apply_notification(self, method: str, params: dict[str, Any]) -> None:
        if method == "thread/started":
            self._replace_snapshot(cast(generated.Thread, params["thread"]))
            return
        if method == "thread/status/changed":
            self._data["status"] = params["status"]
            return
        if method == "thread/name/updated":
            self._data["name"] = params.get("threadName")
            return
        if method == "turn/started":
            turn_snapshot = cast(generated.Turn, params["turn"])
            self._get_or_create_turn(turn_snapshot)
            self._upsert_turn_snapshot(turn_snapshot)
            return
        if method == "turn/completed":
            turn_snapshot = cast(generated.Turn, params["turn"])
            turn = self._turns.get(turn_snapshot["id"])
            if turn is None:
                turn = self._get_or_create_turn(turn_snapshot)
            turn._handle_completed(turn_snapshot)
            self._upsert_turn_snapshot(turn.snapshot)
            return

        turn_id = cast(str | None, params.get("turnId"))
        if turn_id is None:
            return

        turn = self._ensure_turn(turn_id)
        turn._apply_notification(method, params)
        self._upsert_turn_snapshot(turn.snapshot)

    def _upsert_turn_snapshot(self, snapshot: generated.Turn) -> None:
        turns = self._data.setdefault("turns", [])
        for index, existing in enumerate(turns):
            if existing["id"] == snapshot["id"]:
                turns[index] = _clone(snapshot)
                break
        else:
            turns.append(_clone(snapshot))

    def _ensure_turn(self, turn_id: str) -> "Turn":
        turn = self._turns.get(turn_id)
        if turn is not None:
            return turn

        turn = Turn(
            self,
            {
                "id": turn_id,
                "status": "inProgress",
                "items": [],
                "error": None,
            },
        )
        self._turns[turn_id] = turn
        self._upsert_turn_snapshot(turn.snapshot)
        return turn

    def _get_or_create_turn(self, snapshot: generated.Turn) -> "Turn":
        turn = self._turns.get(snapshot["id"])
        if turn is None:
            turn = Turn(self, snapshot)
            self._turns[snapshot["id"]] = turn
            return turn

        turn._replace_snapshot(snapshot)
        return turn


class Turn:
    def __init__(self, thread: Thread, snapshot: generated.Turn) -> None:
        self._thread = thread
        self._snapshot = _clone(snapshot)
        self._review_thread_id: str | None = None
        self._events: asyncio.Queue[TurnEvent | object] = asyncio.Queue()
        self._iter_started = False
        self._stream_closed = False
        self._completion = asyncio.get_running_loop().create_future()
        self._item_indexes: dict[str, int] = {}
        self._rebuild_item_indexes()

        if self.status != "inProgress":
            self._completion.set_result(_clone(self._snapshot))

    @property
    def id(self) -> str:
        return self._snapshot["id"]

    @property
    def status(self) -> generated.TurnStatus:
        return self._snapshot["status"]

    @property
    def items(self) -> list[generated.ThreadItem]:
        return self._snapshot["items"]

    @property
    def error(self) -> generated.TurnError | None:
        return self._snapshot.get("error")

    @property
    def review_thread_id(self) -> str | None:
        return self._review_thread_id

    @property
    def snapshot(self) -> generated.Turn:
        return self._snapshot

    def __aiter__(self) -> AsyncIterator[TurnEvent]:
        if self._iter_started:
            raise RuntimeError("Turn can only be iterated once")

        self._iter_started = True
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[TurnEvent]:
        while True:
            event = await self._events.get()
            if event is _TURN_STREAM_EOF:
                return
            yield cast(TurnEvent, event)

    async def wait_for_completion(self) -> generated.Turn:
        return cast(generated.Turn, await self._completion)

    async def text(self) -> str:
        turn = await self.wait_for_completion()
        chunks: list[str] = []
        for item in turn["items"]:
            if item["type"] == "agentMessage":
                chunks.append(item["text"])
        return "".join(chunks)

    def _replace_snapshot(self, snapshot: generated.Turn) -> None:
        self._snapshot = _clone(snapshot)
        self._rebuild_item_indexes()
        if self.status != "inProgress" and not self._completion.done():
            self._completion.set_result(_clone(self._snapshot))

    def _handle_completed(self, snapshot: generated.Turn) -> None:
        completed_snapshot = _clone(snapshot)
        if not completed_snapshot["items"] and self._snapshot["items"]:
            completed_snapshot["items"] = _clone(self._snapshot["items"])
        self._replace_snapshot(completed_snapshot)
        self._emit_event({"type": "completed", "turn": _clone(self._snapshot)})
        self._close_stream()

    def _apply_notification(self, method: str, params: dict[str, Any]) -> None:
        if method == "item/started":
            item = _clone(cast(generated.ThreadItem, params["item"]))
            self._upsert_item(item)
            self._emit_event({"type": "item_started", "item": _clone(item)})
            return
        if method == "item/completed":
            item = _clone(cast(generated.ThreadItem, params["item"]))
            self._upsert_item(item)
            self._emit_event({"type": "item_completed", "item": _clone(item)})
            return
        if method == "item/agentMessage/delta":
            self._append_agent_message_delta(params["itemId"], params["delta"])
            self._emit_event(
                {
                    "type": "agent_message_delta",
                    "item_id": params["itemId"],
                    "delta": params["delta"],
                }
            )
            return
        if method == "item/plan/delta":
            self._append_plan_delta(params["itemId"], params["delta"])
            self._emit_event(
                {"type": "plan_delta", "item_id": params["itemId"], "delta": params["delta"]}
            )
            return
        if method == "item/reasoning/textDelta":
            self._append_reasoning_delta(
                params["itemId"], params["contentIndex"], params["delta"]
            )
            self._emit_event(
                {
                    "type": "reasoning_delta",
                    "item_id": params["itemId"],
                    "delta": params["delta"],
                }
            )
            return
        if method == "item/reasoning/summaryTextDelta":
            self._append_reasoning_summary_delta(
                params["itemId"], params["summaryIndex"], params["delta"]
            )
            self._emit_event(
                {
                    "type": "reasoning_summary_delta",
                    "item_id": params["itemId"],
                    "delta": params["delta"],
                    "summary_index": params["summaryIndex"],
                }
            )
            return
        if method == "item/commandExecution/outputDelta":
            self._append_command_output_delta(params["itemId"], params["delta"])
            self._emit_event(
                {
                    "type": "command_output_delta",
                    "item_id": params["itemId"],
                    "delta": params["delta"],
                }
            )
            return
        if method == "item/fileChange/outputDelta":
            self._emit_event(
                {"type": "file_change_delta", "item_id": params["itemId"], "delta": params["delta"]}
            )
            return
        if method == "turn/diff/updated":
            self._emit_event({"type": "turn_diff_updated", "diff": params["diff"]})
            return
        if method == "turn/plan/updated":
            self._emit_event(
                {
                    "type": "plan_updated",
                    "plan": _clone(params["plan"]),
                    "explanation": params.get("explanation"),
                }
            )
            return
        if method == "error":
            self._snapshot["error"] = _clone(cast(generated.TurnError, params["error"]))
            self._emit_event({"type": "error", "error": _clone(params["error"])})

    def _upsert_item(self, item: generated.ThreadItem) -> None:
        index = self._item_indexes.get(item["id"])
        if index is None:
            self._snapshot["items"].append(item)
            self._item_indexes[item["id"]] = len(self._snapshot["items"]) - 1
            return

        self._snapshot["items"][index] = item

    def _append_agent_message_delta(self, item_id: str, delta: str) -> None:
        item = self._ensure_agent_message_item(item_id)
        item["text"] += delta

    def _append_plan_delta(self, item_id: str, delta: str) -> None:
        item = self._ensure_plan_item(item_id)
        item["text"] += delta

    def _append_reasoning_delta(self, item_id: str, content_index: int, delta: str) -> None:
        item = self._ensure_reasoning_item(item_id)
        content = item.setdefault("content", [])
        _ensure_list_size(content, content_index + 1)
        content[content_index] += delta

    def _append_reasoning_summary_delta(
        self, item_id: str, summary_index: int, delta: str
    ) -> None:
        item = self._ensure_reasoning_item(item_id)
        summary = item.setdefault("summary", [])
        _ensure_list_size(summary, summary_index + 1)
        summary[summary_index] += delta

    def _append_command_output_delta(self, item_id: str, delta: str) -> None:
        item = self._ensure_command_execution_item(item_id)
        item["aggregatedOutput"] = (item.get("aggregatedOutput") or "") + delta

    def _ensure_agent_message_item(self, item_id: str) -> generated.AgentMessageThreadItem:
        return cast(
            generated.AgentMessageThreadItem,
            self._ensure_item(item_id, {"id": item_id, "type": "agentMessage", "text": ""}),
        )

    def _ensure_plan_item(self, item_id: str) -> generated.PlanThreadItem:
        return cast(
            generated.PlanThreadItem,
            self._ensure_item(item_id, {"id": item_id, "type": "plan", "text": ""}),
        )

    def _ensure_reasoning_item(self, item_id: str) -> generated.ReasoningThreadItem:
        return cast(
            generated.ReasoningThreadItem,
            self._ensure_item(item_id, {"id": item_id, "type": "reasoning", "summary": []}),
        )

    def _ensure_command_execution_item(
        self, item_id: str
    ) -> generated.CommandExecutionThreadItem:
        return cast(
            generated.CommandExecutionThreadItem,
            self._ensure_item(
                item_id,
                {
                    "id": item_id,
                    "type": "commandExecution",
                    "command": "",
                    "commandActions": [],
                    "cwd": "",
                    "status": "inProgress",
                    "aggregatedOutput": "",
                },
            ),
        )

    def _ensure_item(self, item_id: str, placeholder: generated.ThreadItem) -> generated.ThreadItem:
        index = self._item_indexes.get(item_id)
        if index is None:
            self._snapshot["items"].append(_clone(placeholder))
            self._item_indexes[item_id] = len(self._snapshot["items"]) - 1
            index = self._item_indexes[item_id]
        return self._snapshot["items"][index]

    def _rebuild_item_indexes(self) -> None:
        self._item_indexes = {
            item["id"]: index for index, item in enumerate(self._snapshot.get("items", []))
        }

    def _emit_event(self, event: TurnEvent) -> None:
        if self._stream_closed:
            return
        self._events.put_nowait(event)

    def _close_stream(self) -> None:
        if self._stream_closed:
            return
        self._stream_closed = True
        self._events.put_nowait(_TURN_STREAM_EOF)


async def _maybe_await(value: Awaitable[Any] | Any) -> Any:
    if asyncio.iscoroutine(value) or isinstance(value, Awaitable):
        return await cast(Awaitable[Any], value)
    return value


async def _emit_handlers(
    handlers: Sequence[NotificationHandler], params: JSONValue
) -> None:
    for handler in list(handlers):
        result = handler(params)
        if asyncio.iscoroutine(result):
            await result


def _normalize_input(input: str | list[generated.UserInput]) -> list[generated.UserInput]:
    if isinstance(input, str):
        return [{"type": "text", "text": input}]
    return _clone(input)


def _thread_id_from_notification(method: str, params: dict[str, Any]) -> str | None:
    if method == "thread/started" and "thread" in params:
        return cast(str | None, params["thread"].get("id"))
    if "threadId" in params:
        return cast(str | None, params.get("threadId"))
    return None


def _clone(value: Any) -> Any:
    return deepcopy(value)


def _ensure_list_size(values: list[str], size: int) -> None:
    while len(values) < size:
        values.append("")
