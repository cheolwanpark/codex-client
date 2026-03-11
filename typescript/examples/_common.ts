import { TurnFailedError, clientInfo } from "../src/index.js";

export const CLIENT_INFO = clientInfo("codex-client-examples", "0.1.0");

export function printSection(title: string): void {
  console.log(`\n== ${title} ==`);
}

export function isRetryableTurnFailure(error: unknown): error is TurnFailedError {
  return (
    error instanceof TurnFailedError
    && error.message.includes("stream disconnected before completion")
  );
}

export async function withRetry<T>(
  label: string,
  action: () => Promise<T>,
  retries = 2,
): Promise<T> {
  let attempt = 0;

  while (true) {
    try {
      return await action();
    } catch (error) {
      if (!isRetryableTurnFailure(error) || attempt >= retries) {
        throw error;
      }

      attempt += 1;
      console.log(`${label} failed transiently, retrying (${attempt}/${retries})...`);
    }
  }
}
