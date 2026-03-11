import { Session, clientInfo, threadParams } from "../src/index.js";

const firstSession = await Session.create({
  clientInfo: clientInfo("typescript-example", "0.1.0"),
});

const thread = await firstSession.startThread(threadParams({ ephemeral: false }));
console.log(`Started thread ${thread.id}`);
await firstSession.close();

const secondSession = await Session.create({
  clientInfo: clientInfo("typescript-example", "0.1.0"),
});

try {
  const resumed = await secondSession.resumeThread(thread.id);
  const answer = await resumed.ask("Reply with exactly RESUMED.");
  console.log(answer);
} finally {
  await secondSession.close();
}
