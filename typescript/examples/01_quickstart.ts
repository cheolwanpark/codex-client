import { ApprovalPolicy, Session, TurnFailedError } from "../src/index.js";
import { CLIENT_INFO, printSection, withRetry } from "./_common.js";

const session = await Session.create({
  approvalPolicy: ApprovalPolicy.autoAccept(),
  clientInfo: CLIENT_INFO,
});

try {
  printSection("Quickstart");
  const thread = await session.startEphemeralThread();
  const prompt = "Reply with exactly OK.";
  console.log(`Thread: ${thread.id}`);
  console.log(`Prompt: ${prompt}`);

  try {
    const answer = await withRetry("ask()", async () => await thread.ask(prompt));
    console.log(`Answer: ${answer.trim()}`);
  } catch (error) {
    if (error instanceof TurnFailedError) {
      console.log(`Turn failed: ${error.message}`);
    } else {
      throw error;
    }
  }
} finally {
  await session.close();
}
