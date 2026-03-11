import { Session, clientInfo } from "../src/index.js";

const session = await Session.create({
  clientInfo: clientInfo("typescript-example", "0.1.0"),
});

try {
  const thread = await session.startEphemeralThread();
  const answer = await thread.ask("Reply with exactly OK.");
  console.log(answer);
} finally {
  await session.close();
}
