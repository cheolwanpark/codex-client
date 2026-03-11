import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PACKAGE_ROOT = path.resolve(__dirname, "..");
const REPO_ROOT = path.resolve(PACKAGE_ROOT, "..");
const SCHEMA_ROOT = path.join(REPO_ROOT, "schema");
const SRC_ROOT = path.join(PACKAGE_ROOT, "src");
const GENERATED_TYPES_PATH = path.join(SRC_ROOT, "generated.ts");
const GENERATED_CLIENT_PATH = path.join(SRC_ROOT, "generated-client.ts");

const EXCLUDED_TYPE_FILES = new Set([
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
]);

const METHOD_RESPONSE_TYPES = {
  "account/logout": "LogoutAccountResponse",
  "account/rateLimits/read": "GetAccountRateLimitsResponse",
  "config/batchWrite": "ConfigWriteResponse",
  "config/mcpServer/reload": "McpServerRefreshResponse",
  "configRequirements/read": "ConfigRequirementsReadResponse",
  "config/value/write": "ConfigWriteResponse",
};

class SchemaRenderer {
  constructor() {
    this.rendered = new Map();
    this.anonymousNameCounts = new Map();
    this.schemaByTitle = new Map();
    this.clientRequestSpecs = [];
    this.serverRequestSpecs = [];
    this.serverNotificationSpecs = [];
  }

  renderAll() {
    for (const schemaPath of this.iterTypeSchemaFiles()) {
      const schema = this.loadSchema(schemaPath);
      const title = this.schemaTitle(schemaPath, schema);
      this.schemaByTitle.set(title, schema);
    }

    this.clientRequestSpecs = this.loadMethodSpecs(path.join(SCHEMA_ROOT, "ClientRequest.json"));
    this.serverRequestSpecs = this.loadMethodSpecs(path.join(SCHEMA_ROOT, "ServerRequest.json"));
    this.serverNotificationSpecs = this.loadServerNotificationSpecs();

    const sortedTitles = [...this.schemaByTitle.keys()].sort((left, right) =>
      left.localeCompare(right),
    );
    for (const title of sortedTitles) {
      this.ensureNamedSymbol(title, this.schemaByTitle.get(title), title);
    }
  }

  renderTypesModule() {
    const lines = [
      "/* Auto-generated protocol types and method registries. */",
      "",
      'import type { JSONValue } from "./messages.js";',
      "",
    ];

    if (this.rendered.size > 0) {
      lines.push(...this.rendered.values());
    }

    lines.push(
      this.renderMethodMap("ClientRequestParamsByMethod", this.clientRequestSpecs, "paramsType"),
      this.renderMethodMap("ClientRequestResultByMethod", this.clientRequestSpecs, "resultType"),
      this.renderMethodMap("ServerRequestParamsByMethod", this.serverRequestSpecs, "paramsType"),
      this.renderMethodMap("ServerRequestResultByMethod", this.serverRequestSpecs, "resultType"),
      this.renderMethodMap(
        "ServerNotificationParamsByMethod",
        this.serverNotificationSpecs,
        "paramsType",
      ),
      this.renderMethodLiteral(
        "ClientRequestMethod",
        this.clientRequestSpecs.map((spec) => spec.method),
      ),
      this.renderMethodLiteral(
        "ServerRequestMethod",
        this.serverRequestSpecs.map((spec) => spec.method),
      ),
      this.renderMethodLiteral(
        "ServerNotificationMethod",
        this.serverNotificationSpecs.map((spec) => spec.method),
      ),
      this.renderMethodTuple(
        "CLIENT_REQUEST_METHODS",
        "ClientRequestMethod",
        this.clientRequestSpecs.map((spec) => spec.method),
      ),
      this.renderMethodTuple(
        "SERVER_REQUEST_METHODS",
        "ServerRequestMethod",
        this.serverRequestSpecs.map((spec) => spec.method),
      ),
      this.renderMethodTuple(
        "SERVER_NOTIFICATION_METHODS",
        "ServerNotificationMethod",
        this.serverNotificationSpecs.map((spec) => spec.method),
      ),
      "",
    );

    return `${lines.join("\n").trimEnd()}\n`;
  }

  renderClientModule() {
    const lines = [
      "/* Auto-generated typed request wrappers for TypedCodexClient. */",
      "",
      'import type * as ProtocolTypes from "./generated.js";',
      "",
      "type RequestOptions = { timeoutMs?: number };",
      "",
      "export abstract class GeneratedTypedCodexClient {",
      "  protected abstract request<TResult = unknown>(",
      "    method: string,",
      "    params?: unknown,",
      "    options?: RequestOptions,",
      "  ): Promise<TResult>;",
      "",
    ];

    if (this.clientRequestSpecs.length === 0) {
      lines.push("  // No generated client wrappers.", "}");
      return `${lines.join("\n").trimEnd()}\n`;
    }

    lines.push(
      "  protected requestTyped<M extends ProtocolTypes.ClientRequestMethod>(",
      "    method: M,",
      "    params: unknown,",
      "    options?: RequestOptions,",
      "  ): Promise<ProtocolTypes.ClientRequestResultByMethod[M]> {",
      "    return this.request<ProtocolTypes.ClientRequestResultByMethod[M]>(method, params, options);",
      "  }",
      "",
    );

    for (const spec of this.clientRequestSpecs) {
      const methodName = methodToCamelCase(spec.method);
      if (spec.paramsMode === "null") {
        lines.push(
          `  async ${methodName}(options?: RequestOptions): Promise<ProtocolTypes.${spec.resultType}> {`,
          `    return this.requestTyped("${spec.method}", null, options);`,
          "  }",
          "",
        );
        continue;
      }

      if (spec.paramsMode === "optional") {
        lines.push(
          `  async ${methodName}(params?: ProtocolTypes.${spec.paramsType}, options?: RequestOptions): Promise<ProtocolTypes.${spec.resultType}> {`,
          "    const payload = params ?? {};",
          `    return this.requestTyped("${spec.method}", payload, options);`,
          "  }",
          "",
        );
        continue;
      }

      lines.push(
        `  async ${methodName}(params: ProtocolTypes.${spec.paramsType}, options?: RequestOptions): Promise<ProtocolTypes.${spec.resultType}> {`,
        `    return this.requestTyped("${spec.method}", params, options);`,
        "  }",
        "",
      );
    }

    lines.push("}");
    return `${lines.join("\n").trimEnd()}\n`;
  }

  iterTypeSchemaFiles() {
    const files = [];
    walkJsonFiles(SCHEMA_ROOT, files);
    return files
      .filter((filePath) => !EXCLUDED_TYPE_FILES.has(path.basename(filePath)))
      .sort((left, right) => left.localeCompare(right));
  }

  loadSchema(schemaPath) {
    return JSON.parse(fs.readFileSync(schemaPath, "utf8"));
  }

  schemaTitle(schemaPath, schema) {
    if (typeof schema.title === "string" && schema.title.length > 0) {
      return sanitizeSymbol(schema.title);
    }
    return sanitizeSymbol(path.basename(schemaPath, path.extname(schemaPath)));
  }

  loadMethodSpecs(schemaPath) {
    const schema = this.loadSchema(schemaPath);
    const specs = [];
    for (const variant of schema.oneOf ?? []) {
      const method = variant.properties.method.enum[0];
      const paramsSchema = variant.properties.params;
      let paramsType;
      let paramsMode;
      let resultType;

      if (paramsSchema.$ref) {
        paramsType = this.refToSymbol(paramsSchema.$ref);
        resultType =
          METHOD_RESPONSE_TYPES[method] ?? `${paramsType.replace(/Params$/, "")}Response`;
        paramsMode = this.paramsAreOptional(paramsType) ? "optional" : "required";
      } else if (paramsSchema.type === "null") {
        paramsType = "null";
        resultType = METHOD_RESPONSE_TYPES[method];
        paramsMode = "null";
      } else {
        throw new Error(
          `Unsupported params schema for ${method}: ${JSON.stringify(paramsSchema, null, 2)}`,
        );
      }

      specs.push({ method, paramsType, resultType, paramsMode });
    }
    return specs;
  }

  loadServerNotificationSpecs() {
    const schema = this.loadSchema(path.join(SCHEMA_ROOT, "ServerNotification.json"));
    return (schema.oneOf ?? []).map((variant) => ({
      method: variant.properties.method.enum[0],
      paramsType: this.refToSymbol(variant.properties.params.$ref),
    }));
  }

  paramsAreOptional(paramsType) {
    const schema = this.schemaByTitle.get(paramsType);
    return schema?.type === "object" && !(schema.required?.length);
  }

  ensureNamedSymbol(symbol, schema, preferredName) {
    const sanitizedSymbol = sanitizeSymbol(symbol);
    if (this.rendered.has(sanitizedSymbol)) {
      return sanitizedSymbol;
    }

    if (schema === true) {
      this.rendered.set(sanitizedSymbol, `export type ${sanitizedSymbol} = JSONValue;\n`);
      return sanitizedSymbol;
    }
    if (schema === false) {
      this.rendered.set(sanitizedSymbol, `export type ${sanitizedSymbol} = never;\n`);
      return sanitizedSymbol;
    }

    for (const [definitionName, definitionSchema] of Object.entries(schema.definitions ?? {})) {
      this.ensureNamedSymbol(definitionName, definitionSchema, definitionName);
    }

    if (this.shouldRenderInterface(schema)) {
      const lines = [`export interface ${sanitizedSymbol} {`];
      const properties = schema.properties ?? {};
      const required = new Set(schema.required ?? []);
      for (const [propertyName, propertySchema] of Object.entries(properties)) {
        const propertySymbol = this.typeExpr(
          propertySchema,
          this.composeSymbolName(preferredName, propertyName),
        );
        const propertyKey = renderPropertyKey(propertyName);
        const suffix = required.has(propertyName) ? "" : "?";
        lines.push(`  ${propertyKey}${suffix}: ${propertySymbol};`);
      }
      lines.push("}\n");
      this.rendered.set(sanitizedSymbol, lines.join("\n"));
      return sanitizedSymbol;
    }

    const typeExpr = this.typeExpr(schema, preferredName);
    this.rendered.set(sanitizedSymbol, `export type ${sanitizedSymbol} = ${typeExpr};\n`);
    return sanitizedSymbol;
  }

  typeExpr(schema, preferredName) {
    if (schema === true) {
      return "JSONValue";
    }
    if (schema === false) {
      return "never";
    }
    if (schema.$ref) {
      return this.refToSymbol(schema.$ref);
    }
    if (schema.enum) {
      return this.literalExpr(schema.enum);
    }
    if (Object.hasOwn(schema, "const")) {
      return this.literalExpr([schema.const]);
    }
    if (schema.oneOf) {
      return this.unionExpr(schema.oneOf.map((option) => this.typeExpr(option, preferredName)));
    }
    if (schema.anyOf) {
      return this.unionExpr(schema.anyOf.map((option) => this.typeExpr(option, preferredName)));
    }
    if (schema.allOf) {
      return this.intersectionExpr(
        schema.allOf.map((option) => this.typeExpr(option, preferredName)),
      );
    }

    if (Array.isArray(schema.type)) {
      return this.unionExpr(
        schema.type.map((item) => this.typeExpr({ ...schema, type: item }, preferredName)),
      );
    }

    if (schema.type === "object") {
      if (schema.properties && !schema.additionalProperties) {
        const title =
          typeof schema.title === "string"
            ? sanitizeSymbol(schema.title)
            : this.reserveAnonymousName(this.composeSymbolName(preferredName, "Variant"));
        return this.ensureNamedSymbol(title, schema, title);
      }

      if (typeof schema.additionalProperties === "object") {
        const valueType = this.typeExpr(
          schema.additionalProperties,
          this.composeSymbolName(preferredName, "Value"),
        );
        return `Record<string, ${valueType}>`;
      }

      return "Record<string, JSONValue>";
    }

    if (schema.type === "array") {
      const itemType = this.typeExpr(
        schema.items ?? true,
        this.composeSymbolName(preferredName, "Item"),
      );
      return `Array<${itemType}>`;
    }
    if (schema.type === "string") {
      return "string";
    }
    if (schema.type === "integer" || schema.type === "number") {
      return "number";
    }
    if (schema.type === "boolean") {
      return "boolean";
    }
    if (schema.type === "null") {
      return "null";
    }

    return "JSONValue";
  }

  shouldRenderInterface(schema) {
    return schema.type === "object" && Boolean(schema.properties) && !schema.additionalProperties;
  }

  refToSymbol(ref) {
    if (!ref.startsWith("#/definitions/")) {
      throw new Error(`Unsupported ref: ${ref}`);
    }
    return sanitizeSymbol(ref.split("/").at(-1));
  }

  literalExpr(values) {
    return values.map((value) => JSON.stringify(value)).join(" | ");
  }

  unionExpr(parts) {
    return unique(parts).join(" | ") || "JSONValue";
  }

  intersectionExpr(parts) {
    return unique(parts).join(" & ") || "JSONValue";
  }

  reserveAnonymousName(base) {
    const symbol = sanitizeSymbol(base);
    const count = this.anonymousNameCounts.get(symbol) ?? 0;
    this.anonymousNameCounts.set(symbol, count + 1);
    if (count === 0) {
      return symbol;
    }
    return `${symbol}${count + 1}`;
  }

  composeSymbolName(...parts) {
    return parts.map((part) => sanitizeSymbol(part)).join("");
  }

  renderMethodLiteral(name, methods) {
    if (methods.length === 0) {
      return `export type ${name} = never;\n`;
    }
    return `export type ${name} = ${methods.map((method) => JSON.stringify(method)).join(" | ")};\n`;
  }

  renderMethodMap(name, specs, valueKey) {
    const lines = [`export interface ${name} {`];
    for (const spec of specs) {
      lines.push(`  ${JSON.stringify(spec.method)}: ${spec[valueKey]};`);
    }
    lines.push("}\n");
    return lines.join("\n");
  }

  renderMethodTuple(name, typeName, methods) {
    const lines = [`export const ${name} = [`];
    for (const method of methods) {
      lines.push(`  ${JSON.stringify(method)},`);
    }
    lines.push(`] as const satisfies ReadonlyArray<${typeName}>;\n`);
    return lines.join("\n");
  }
}

function walkJsonFiles(root, files) {
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const resolved = path.join(root, entry.name);
    if (entry.isDirectory()) {
      walkJsonFiles(resolved, files);
      continue;
    }
    if (entry.isFile() && entry.name.endsWith(".json")) {
      files.push(resolved);
    }
  }
}

function unique(values) {
  return [...new Set(values)];
}

function sanitizeSymbol(value) {
  const parts = String(value).match(/[A-Za-z0-9]+/g) ?? [];
  if (parts.length === 0) {
    return "Anonymous";
  }
  let symbol = parts
    .map((part) => part.slice(0, 1).toUpperCase() + part.slice(1))
    .join("");
  if (/^\d/.test(symbol)) {
    symbol = `Type${symbol}`;
  }
  return symbol;
}

function renderPropertyKey(value) {
  return /^[A-Za-z_$][A-Za-z0-9_$]*$/.test(value) ? value : JSON.stringify(value);
}

function methodToCamelCase(method) {
  const joined = method
    .split(/[/-]/)
    .filter(Boolean)
    .join(" ");
  const withBoundaries = joined.replace(/([a-z0-9])([A-Z])/g, "$1 $2");
  const parts = withBoundaries.split(/\s+/).filter(Boolean);
  return parts
    .map((part, index) => {
      const lower = part.toLowerCase();
      if (index === 0) {
        return lower;
      }
      return lower.slice(0, 1).toUpperCase() + lower.slice(1);
    })
    .join("");
}

function main() {
  const renderer = new SchemaRenderer();
  renderer.renderAll();
  fs.writeFileSync(GENERATED_TYPES_PATH, renderer.renderTypesModule(), "utf8");
  fs.writeFileSync(GENERATED_CLIENT_PATH, renderer.renderClientModule(), "utf8");
}

main();
