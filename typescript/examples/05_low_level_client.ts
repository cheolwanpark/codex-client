import {
  StdioTransport,
  TypedCodexClient,
  textInput,
} from "../src/index.js";
import { CLIENT_INFO, printSection } from "./_common.js";

const client = TypedCodexClient.fromTransport(new StdioTransport());
const deltas: string[] = [];

client.onNotification("item/agentMessage/delta", (params) => {
  deltas.push(params.delta);
  process.stdout.write(params.delta);
});

try {
  printSection("Low-Level Typed Client");
  await client.initialize({
    clientInfo: CLIENT_INFO,
  }, { timeoutMs: 10_000 });
  await client.sendInitialized();
  console.log("\nInitialized client and sent initialized notification.");

  const thread = await client.threadStart({ ephemeral: true }, { timeoutMs: 10_000 });
  console.log(`Thread: ${thread.thread.id}`);

  const turn = await client.turnStart({
    input: [textInput("Reply with exactly OK.")],
    threadId: thread.thread.id,
  }, { timeoutMs: 10_000 });
  console.log(`Turn: ${turn.turn.id}`);
  console.log(`Initial turn status: ${turn.turn.status}`);
  console.log("\nAgent stream:");

  const completed = await client.waitForNotification("turn/completed", {
    predicate: (params) => params.turn.id === turn.turn.id,
    timeoutMs: 60_000,
  });
  console.log("\n");
  console.log(`Completion status: ${completed.turn.status}`);
  if (completed.turn.status === "completed") {
    console.log(`Buffered text: ${deltas.join("").trim()}`);
  } else {
    console.log(`Turn failed: ${completed.turn.error?.message ?? "unknown error"}`);
  }
} finally {
  await client.close();
}
