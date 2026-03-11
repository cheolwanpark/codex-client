export type JSONScalar = string | number | boolean | null;
export type JSONValue = JSONScalar | JSONArray | JSONObject;

export interface JSONObject {
  [key: string]: JSONValue;
}

export interface JSONArray extends Array<JSONValue> {}

export type RequestId = string | number;

export interface W3cTraceContext {
  traceparent?: string | null;
  tracestate?: string | null;
}

export interface JsonRpcRequest {
  id: RequestId;
  method: string;
  params?: JSONValue;
  trace?: W3cTraceContext | null;
  jsonrpc?: string;
}

export interface JsonRpcNotification {
  method: string;
  params?: JSONValue;
  jsonrpc?: string;
}

export interface JsonRpcResponse {
  id: RequestId;
  result: JSONValue;
  jsonrpc?: string;
}

export interface JsonRpcErrorObject {
  code: number;
  message: string;
  data?: JSONValue;
}

export interface JsonRpcErrorResponse {
  id: RequestId;
  error: JsonRpcErrorObject;
  jsonrpc?: string;
}

export type JsonRpcMessage =
  | JsonRpcRequest
  | JsonRpcNotification
  | JsonRpcResponse
  | JsonRpcErrorResponse;
