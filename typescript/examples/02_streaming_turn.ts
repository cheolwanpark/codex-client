import { Session, clientInfo } from "../src/index.js";

const session = await Session.create({
  clientInfo: clientInfo("typescript-example", "0.1.0"),
});

try {
  const thread = await session.startEphemeralThread();
  const turn = await thread.startTurn("Explain in one short sentence what you are doing.");

  for await (const event of turn) {
    if (event.type === "agent_message_delta") {
      process.stdout.write(event.delta);
      continue;
    }

    if (event.type === "completed") {
      process.stdout.write("\n");
    }
  }
} finally {
  await session.close();
}
