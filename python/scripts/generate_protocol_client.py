from __future__ import annotations

import json
import keyword
import re
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = REPO_ROOT / "schema"
PACKAGE_ROOT = REPO_ROOT / "python" / "src" / "codex_client"
GENERATED_TYPES_PATH = PACKAGE_ROOT / "_generated.py"
GENERATED_CLIENT_PATH = PACKAGE_ROOT / "_generated_client.py"

EXCLUDED_TYPE_FILES = {
    "ClientNotification.json",
    "ClientRequest.json",
    "JSONRPCError.json",
    "JSONRPCErrorError.json",
    "JSONRPCMessage.json",
    "JSONRPCNotification.json",
    "JSONRPCRequest.json",
    "JSONRPCResponse.json",
    "ServerNotification.json",
    "ServerRequest.json",
    "codex_app_server_protocol.schemas.json",
    "codex_app_server_protocol.v2.schemas.json",
}

METHOD_RESPONSE_TYPES = {
    "account/logout": "LogoutAccountResponse",
    "account/rateLimits/read": "GetAccountRateLimitsResponse",
    "config/batchWrite": "ConfigWriteResponse",
    "config/mcpServer/reload": "McpServerRefreshResponse",
    "configRequirements/read": "ConfigRequirementsReadResponse",
    "config/value/write": "ConfigWriteResponse",
}


@dataclass(frozen=True)
class MethodSpec:
    method: str
    params_type: str
    result_type: str
    params_mode: str


@dataclass(frozen=True)
class NotificationSpec:
    method: str
    params_type: str


class SchemaRenderer:
    def __init__(self) -> None:
        self._rendered: OrderedDict[str, str] = OrderedDict()
        self._anonymous_name_counts: dict[str, int] = {}
        self._schema_by_title: dict[str, dict[str, Any]] = {}
        self._client_request_specs: list[MethodSpec] = []
        self._server_request_specs: list[MethodSpec] = []
        self._server_notification_specs: list[NotificationSpec] = []

    def render_all(self) -> None:
        for schema_path in self._iter_type_schema_files():
            schema = self._load_schema(schema_path)
            title = self._schema_title(schema_path, schema)
            self._schema_by_title[title] = schema

        self._client_request_specs = self._load_method_specs(SCHEMA_ROOT / "ClientRequest.json")
        self._server_request_specs = self._load_method_specs(SCHEMA_ROOT / "ServerRequest.json")
        self._server_notification_specs = self._load_server_notification_specs()

        for title, schema in sorted(self._schema_by_title.items()):
            self._ensure_named_symbol(title, schema, title)

    def render_types_module(self) -> str:
        lines: list[str] = [
            '"""Auto-generated protocol types and method registries."""',
            "",
            "from __future__ import annotations",
            "",
            "from typing import Any, Final, Literal, Never, NotRequired, Required, TypeAlias, TypedDict",
            "",
            "from .messages import JSONValue",
            "",
        ]

        if self._rendered:
            lines.extend(self._rendered.values())

        lines.extend(
            [
                self._render_method_literal(
                    "ClientRequestMethod", [spec.method for spec in self._client_request_specs]
                ),
                self._render_method_literal(
                    "ServerRequestMethod", [spec.method for spec in self._server_request_specs]
                ),
                self._render_method_literal(
                    "ServerNotificationMethod",
                    [spec.method for spec in self._server_notification_specs],
                ),
                self._render_method_map(
                    "CLIENT_REQUEST_METHOD_TO_PARAMS",
                    [(spec.method, spec.params_type) for spec in self._client_request_specs],
                ),
                self._render_method_map(
                    "CLIENT_REQUEST_METHOD_TO_RESULT",
                    [(spec.method, spec.result_type) for spec in self._client_request_specs],
                ),
                self._render_method_map(
                    "SERVER_REQUEST_METHOD_TO_PARAMS",
                    [(spec.method, spec.params_type) for spec in self._server_request_specs],
                ),
                self._render_method_map(
                    "SERVER_REQUEST_METHOD_TO_RESULT",
                    [(spec.method, spec.result_type) for spec in self._server_request_specs],
                ),
                self._render_method_map(
                    "SERVER_NOTIFICATION_METHOD_TO_PARAMS",
                    [(spec.method, spec.params_type) for spec in self._server_notification_specs],
                ),
                self._render_method_tuple(
                    "CLIENT_REQUEST_METHODS", [spec.method for spec in self._client_request_specs]
                ),
                self._render_method_tuple(
                    "SERVER_REQUEST_METHODS", [spec.method for spec in self._server_request_specs]
                ),
                self._render_method_tuple(
                    "SERVER_NOTIFICATION_METHODS",
                    [spec.method for spec in self._server_notification_specs],
                ),
                "",
            ]
        )

        return "\n".join(lines).rstrip() + "\n"

    def render_client_module(self) -> str:
        lines: list[str] = [
            '"""Auto-generated typed request wrappers for TypedCodexClient."""',
            "",
            "from __future__ import annotations",
            "",
            "from typing import cast",
            "",
            "from ._generated import *",
            "",
            "",
            "class GeneratedClientMixin:",
        ]

        if not self._client_request_specs:
            lines.extend(["    pass", ""])
            return "\n".join(lines)

        for spec in self._client_request_specs:
            method_name = pythonize_method_name(spec.method)
            if spec.params_mode == "null":
                lines.extend(
                    [
                        f"    async def {method_name}(self, *, timeout: float | None = None) -> {spec.result_type}:",
                        f'        return cast({spec.result_type}, await self.request("{spec.method}", None, timeout=timeout))',
                        "",
                    ]
                )
                continue

            if spec.params_mode == "optional":
                lines.extend(
                    [
                        f"    async def {method_name}(",
                        f"        self, params: {spec.params_type} | None = None, *, timeout: float | None = None",
                        f"    ) -> {spec.result_type}:",
                        "        payload = {} if params is None else params",
                        f'        return cast({spec.result_type}, await self.request("{spec.method}", payload, timeout=timeout))',
                        "",
                    ]
                )
                continue

            lines.extend(
                [
                    f"    async def {method_name}(",
                    f"        self, params: {spec.params_type}, *, timeout: float | None = None",
                    f"    ) -> {spec.result_type}:",
                    f'        return cast({spec.result_type}, await self.request("{spec.method}", params, timeout=timeout))',
                    "",
                ]
            )

        return "\n".join(lines).rstrip() + "\n"

    def _iter_type_schema_files(self) -> list[Path]:
        return sorted(
            path
            for path in SCHEMA_ROOT.rglob("*.json")
            if path.name not in EXCLUDED_TYPE_FILES
        )

    def _load_schema(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _schema_title(self, path: Path, schema: dict[str, Any]) -> str:
        title = schema.get("title")
        if isinstance(title, str) and title:
            return sanitize_symbol(title)
        return sanitize_symbol(path.stem)

    def _load_method_specs(self, path: Path) -> list[MethodSpec]:
        schema = self._load_schema(path)
        specs: list[MethodSpec] = []
        for variant in schema.get("oneOf", []):
            method = variant["properties"]["method"]["enum"][0]
            params_schema = variant["properties"]["params"]
            if "$ref" in params_schema:
                params_type = self._ref_to_symbol(params_schema["$ref"])
                result_type = METHOD_RESPONSE_TYPES.get(
                    method, params_type.removesuffix("Params") + "Response"
                )
                params_mode = "optional" if self._params_are_optional(params_type) else "required"
            elif params_schema.get("type") == "null":
                params_type = "None"
                result_type = METHOD_RESPONSE_TYPES[method]
                params_mode = "null"
            else:
                raise ValueError(f"Unsupported params schema for {method}: {params_schema}")
            specs.append(
                MethodSpec(
                    method=method,
                    params_type=params_type,
                    result_type=result_type,
                    params_mode=params_mode,
                )
            )
        return specs

    def _load_server_notification_specs(self) -> list[NotificationSpec]:
        schema = self._load_schema(SCHEMA_ROOT / "ServerNotification.json")
        specs: list[NotificationSpec] = []
        for variant in schema.get("oneOf", []):
            method = variant["properties"]["method"]["enum"][0]
            params_type = self._ref_to_symbol(variant["properties"]["params"]["$ref"])
            specs.append(NotificationSpec(method=method, params_type=params_type))
        return specs

    def _params_are_optional(self, params_type: str) -> bool:
        schema = self._schema_by_title[params_type]
        return schema.get("type") == "object" and not schema.get("required")

    def _ensure_named_symbol(
        self, symbol: str, schema: dict[str, Any] | bool, preferred_name: str
    ) -> str:
        symbol = sanitize_symbol(symbol)
        if symbol in self._rendered:
            return symbol

        if schema is True:
            self._rendered[symbol] = f"{symbol}: TypeAlias = 'Any'\n"
            return symbol
        if schema is False:
            self._rendered[symbol] = f"{symbol}: TypeAlias = 'Never'\n"
            return symbol

        for definition_name, definition_schema in schema.get("definitions", {}).items():
            self._ensure_named_symbol(definition_name, definition_schema, definition_name)

        if self._should_render_typed_dict(schema):
            lines = [f"class {symbol}(TypedDict, total=False):"]
            properties = schema.get("properties", {})
            required = set(schema.get("required", []))
            if not properties:
                lines.append("    pass")
            else:
                for property_name, property_schema in properties.items():
                    property_symbol = self._type_expr(
                        property_schema,
                        self._compose_symbol_name(preferred_name, property_name),
                    )
                    wrapper = "Required" if property_name in required else "NotRequired"
                    lines.append(
                        f"    {sanitize_field_name(property_name)}: {wrapper}[{property_symbol}]"
                    )
            self._rendered[symbol] = "\n".join(lines) + "\n"
            return symbol

        type_expr = self._type_expr(schema, preferred_name)
        self._rendered[symbol] = f"{symbol}: TypeAlias = {type_expr!r}\n"
        return symbol

    def _type_expr(self, schema: dict[str, Any] | bool, preferred_name: str) -> str:
        if schema is True:
            return "Any"
        if schema is False:
            return "Never"
        if "$ref" in schema:
            return self._ref_to_symbol(schema["$ref"])
        if "enum" in schema:
            return self._literal_expr(schema["enum"])
        if "const" in schema:
            return self._literal_expr([schema["const"]])
        if "oneOf" in schema:
            return self._union_expr(
                [self._type_expr(option, preferred_name) for option in schema["oneOf"]]
            )
        if "anyOf" in schema:
            return self._union_expr(
                [self._type_expr(option, preferred_name) for option in schema["anyOf"]]
            )
        if "allOf" in schema:
            return self._union_expr(
                [self._type_expr(option, preferred_name) for option in schema["allOf"]]
            )

        schema_type = schema.get("type")
        if isinstance(schema_type, list):
            return self._union_expr(
                [self._type_expr({**schema, "type": item}, preferred_name) for item in schema_type]
            )
        if schema_type == "object":
            if schema.get("properties") and not schema.get("additionalProperties"):
                title = schema.get("title")
                anonymous_name = (
                    sanitize_symbol(title)
                    if isinstance(title, str)
                    else self._reserve_anonymous_name(
                        self._compose_symbol_name(preferred_name, "Variant")
                    )
                )
                return self._ensure_named_symbol(anonymous_name, schema, anonymous_name)
            additional_properties = schema.get("additionalProperties")
            if isinstance(additional_properties, dict):
                value_type = self._type_expr(
                    additional_properties, self._compose_symbol_name(preferred_name, "Value")
                )
                return f"dict[str, {value_type}]"
            return "dict[str, JSONValue]"
        if schema_type == "array":
            item_type = self._type_expr(
                schema.get("items", True), self._compose_symbol_name(preferred_name, "Item")
            )
            return f"list[{item_type}]"
        if schema_type == "string":
            return "str"
        if schema_type == "integer":
            return "int"
        if schema_type == "number":
            return "float"
        if schema_type == "boolean":
            return "bool"
        if schema_type == "null":
            return "None"

        return "JSONValue"

    def _should_render_typed_dict(self, schema: dict[str, Any]) -> bool:
        return (
            schema.get("type") == "object"
            and bool(schema.get("properties"))
            and not schema.get("additionalProperties")
        )

    def _ref_to_symbol(self, ref: str) -> str:
        if not ref.startswith("#/definitions/"):
            raise ValueError(f"Unsupported ref: {ref}")
        return sanitize_symbol(ref.rsplit("/", 1)[-1])

    def _literal_expr(self, values: list[Any]) -> str:
        return "Literal[" + ", ".join(repr(value) for value in values) + "]"

    def _union_expr(self, parts: list[str]) -> str:
        unique_parts: list[str] = []
        for part in parts:
            if part not in unique_parts:
                unique_parts.append(part)
        return " | ".join(unique_parts) if unique_parts else "JSONValue"

    def _reserve_anonymous_name(self, base: str) -> str:
        symbol = sanitize_symbol(base)
        count = self._anonymous_name_counts.get(symbol, 0)
        self._anonymous_name_counts[symbol] = count + 1
        if count == 0:
            return symbol
        return f"{symbol}{count + 1}"

    def _compose_symbol_name(self, *parts: str) -> str:
        return "".join(sanitize_symbol(part) for part in parts if part)

    def _render_method_literal(self, name: str, methods: list[str]) -> str:
        return f"{name}: TypeAlias = Literal[" + ", ".join(repr(method) for method in methods) + "]\n"

    def _render_method_map(self, name: str, items: list[tuple[str, str]]) -> str:
        lines = [f"{name}: Final[dict[str, str]] = {{"]
        for method, type_name in items:
            lines.append(f'    "{method}": "{type_name}",')
        lines.append("}\n")
        return "\n".join(lines)

    def _render_method_tuple(self, name: str, methods: list[str]) -> str:
        lines = [f"{name}: Final[tuple[str, ...]] = ("]
        for method in methods:
            lines.append(f'    "{method}",')
        lines.append(")\n")
        return "\n".join(lines)


def sanitize_symbol(value: str) -> str:
    parts = re.findall(r"[A-Za-z0-9]+", value)
    if not parts:
        return "Anonymous"
    symbol = "".join(part[:1].upper() + part[1:] for part in parts)
    if symbol[:1].isdigit():
        symbol = f"Type{symbol}"
    return symbol


def sanitize_field_name(value: str) -> str:
    field = re.sub(r"\W+", "_", value)
    if not field:
        field = "field"
    if field[:1].isdigit():
        field = f"field_{field}"
    if keyword.iskeyword(field):
        field = f"{field}_"
    return field


def pythonize_method_name(method: str) -> str:
    field = "_".join(segment for segment in re.split(r"[/\-]", method) if segment)
    field = re.sub(r"(?<!^)(?=[A-Z])", "_", field).lower()
    return sanitize_field_name(field)


def main() -> None:
    renderer = SchemaRenderer()
    renderer.render_all()
    GENERATED_TYPES_PATH.write_text(renderer.render_types_module(), encoding="utf-8")
    GENERATED_CLIENT_PATH.write_text(renderer.render_client_module(), encoding="utf-8")


if __name__ == "__main__":
    main()
