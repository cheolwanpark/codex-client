from __future__ import annotations

from codex_client import (
    NotificationMethod,
    ServerRequestMethod,
    TurnEventType,
    approve_command,
    approve_file_change,
    approve_file_change_for_session,
    client_info,
    decline_command,
    decline_file_change,
    text_input,
    thread_params,
    tool_answers,
    tool_call_failure,
    tool_call_success,
    turn_options,
)
from codex_client import protocol_types
from codex_client._generated import SERVER_NOTIFICATION_METHODS, SERVER_REQUEST_METHODS


def test_protocol_types_re_exports_generated_symbols() -> None:
    assert protocol_types.ClientInfo.__name__ == "ClientInfo"


def test_notification_and_request_constants_match_protocol_registries() -> None:
    assert {method.value for method in NotificationMethod} <= set(SERVER_NOTIFICATION_METHODS)
    assert {method.value for method in ServerRequestMethod} <= set(SERVER_REQUEST_METHODS)


def test_turn_event_type_constants_match_runtime_event_strings() -> None:
    assert TurnEventType.AGENT_MESSAGE_DELTA == "agent_message_delta"
    assert TurnEventType.PLAN_UPDATED == "plan_updated"
    assert TurnEventType.COMPLETED == "completed"


def test_client_info_and_text_input_helpers_return_expected_shapes() -> None:
    assert client_info("app", "0.1.0") == {"name": "app", "version": "0.1.0"}
    assert client_info("app", "0.1.0", title="App") == {
        "name": "app",
        "version": "0.1.0",
        "title": "App",
    }
    assert text_input("hello") == {"type": "text", "text": "hello"}


def test_thread_params_defaults_to_ephemeral_and_preserves_overrides() -> None:
    assert thread_params() == {"ephemeral": True}
    assert thread_params(ephemeral=False, cwd="/tmp", model="gpt-5.1-codex") == {
        "ephemeral": False,
        "cwd": "/tmp",
        "model": "gpt-5.1-codex",
    }


def test_turn_options_only_includes_provided_fields() -> None:
    assert turn_options() == {}
    assert turn_options(cwd="/tmp", model="gpt-5.1-codex", output_schema={"type": "object"}) == {
        "cwd": "/tmp",
        "model": "gpt-5.1-codex",
        "outputSchema": {"type": "object"},
    }


def test_approval_helpers_return_expected_shapes() -> None:
    assert approve_command() == {"decision": "accept"}
    assert decline_command() == {"decision": "decline"}
    assert approve_file_change() == {"decision": "accept"}
    assert decline_file_change() == {"decision": "decline"}
    assert approve_file_change_for_session() == {"decision": "acceptForSession"}
    assert tool_answers({"question_1": ["yes"], "question_2": []}) == {
        "answers": {
            "question_1": {"answers": ["yes"]},
            "question_2": {"answers": []},
        }
    }
    assert tool_call_success() == {"success": True, "contentItems": []}
    assert tool_call_failure([{"type": "inputText", "text": "nope"}]) == {
        "success": False,
        "contentItems": [{"type": "inputText", "text": "nope"}],
    }
