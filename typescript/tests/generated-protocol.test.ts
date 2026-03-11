import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import {
  CLIENT_REQUEST_METHODS,
  SERVER_NOTIFICATION_METHODS,
  SERVER_REQUEST_METHODS,
  ProtocolConnection,
  TypedCodexClient,
} from "../src/index.js";
import { MockTransport } from "./helpers/mock-transport.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const NULL_PARAM_METHODS = new Set([
  "account/logout",
  "account/rateLimits/read",
  "config/mcpServer/reload",
  "configRequirements/read",
]);

describe("generated protocol", () => {
  it("matches schema method registries", () => {
    expect(new Set(CLIENT_REQUEST_METHODS)).toEqual(
      extractMethods(path.join(REPO_ROOT, "schema", "ClientRequest.json")),
    );
    expect(new Set(SERVER_REQUEST_METHODS)).toEqual(
      extractMethods(path.join(REPO_ROOT, "schema", "ServerRequest.json")),
    );
    expect(new Set(SERVER_NOTIFICATION_METHODS)).toEqual(
      extractMethods(path.join(REPO_ROOT, "schema", "ServerNotification.json")),
    );
  });

  it("generated wrappers send expected methods and params", async () => {
    const transport = new MockTransport();
    const client = new TypedCodexClient(new ProtocolConnection(transport));
    const optionalMethods = extractOptionalClientMethods();

    try {
      for (const method of CLIENT_REQUEST_METHODS) {
        const wrapper = (
          client as unknown as Record<string, (...args: unknown[]) => Promise<unknown>>
        )[methodToCamelCase(method)];
        expect(typeof wrapper).toBe("function");
        if (wrapper === undefined) {
          throw new Error(`Missing generated wrapper for ${method}`);
        }
        const task = callWrapper(client, wrapper, method, optionalMethods);
        const sent = await transport.nextSent();

        expect(sent.method).toBe(method);
        if (NULL_PARAM_METHODS.has(method)) {
          expect(sent.params).toBeNull();
        } else if (method === "initialize") {
          expect(sent.params).toEqual({ clientInfo: { name: "test", version: "0.1.0" } });
        } else if (optionalMethods.has(method)) {
          expect(sent.params).toEqual({});
        } else {
          expect(sent.params).toEqual({ probe: true });
        }

        await transport.inject({ id: sent.id, result: {} });
        await task;
      }
    } finally {
      await client.close();
    }
  });
});

function extractMethods(schemaPath: string): Set<string> {
  const data = JSON.parse(fs.readFileSync(schemaPath, "utf8")) as {
    oneOf: Array<{ properties: { method: { enum: [string] } } }>;
  };
  return new Set(data.oneOf.map((variant) => variant.properties.method.enum[0]));
}

function extractOptionalClientMethods(): Set<string> {
  const schema = JSON.parse(
    fs.readFileSync(path.join(REPO_ROOT, "schema", "ClientRequest.json"), "utf8"),
  ) as {
    definitions: Record<string, { required?: string[]; type?: string }>;
    oneOf: Array<{
      properties: {
        method: { enum: [string] };
        params: { $ref?: string; type?: string };
      };
    }>;
  };

  return new Set(
    schema.oneOf
      .filter((variant) => {
        const params = variant.properties.params;
        if (!params.$ref) {
          return false;
        }
        const definition = schema.definitions[params.$ref.split("/").at(-1) ?? ""];
        return definition?.type === "object" && (definition.required?.length ?? 0) === 0;
      })
      .map((variant) => variant.properties.method.enum[0]),
  );
}

async function callWrapper(
  client: TypedCodexClient,
  wrapper: (...args: unknown[]) => Promise<unknown>,
  method: string,
  optionalMethods: Set<string>,
): Promise<unknown> {
  if (NULL_PARAM_METHODS.has(method)) {
    return wrapper.call(client);
  }
  if (method === "initialize") {
    return wrapper.call(client, { clientInfo: { name: "test", version: "0.1.0" } });
  }
  if (optionalMethods.has(method)) {
    return wrapper.call(client);
  }
  return wrapper.call(client, { probe: true });
}

function methodToCamelCase(method: string): string {
  const joined = method
    .split(/[/-]/)
    .filter(Boolean)
    .join(" ");
  const withBoundaries = joined.replace(/([a-z0-9])([A-Z])/g, "$1 $2");
  return withBoundaries
    .split(/\s+/)
    .filter(Boolean)
    .map((part, index) => {
      const lower = part.toLowerCase();
      if (index === 0) {
        return lower;
      }
      return lower.slice(0, 1).toUpperCase() + lower.slice(1);
    })
    .join("");
}
