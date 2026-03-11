import {
  ApprovalPolicy,
  ProtocolClientError,
  Session,
  TurnFailedError,
  threadParams,
} from "../src/index.js";
import { CLIENT_INFO, printSection, withRetry } from "./_common.js";

const firstSession = await Session.create({
  approvalPolicy: ApprovalPolicy.autoAccept(),
  clientInfo: CLIENT_INFO,
});

let threadId = "";
let initialTurnCompleted = false;
printSection("Resume Thread Across Sessions");
try {
  const thread = await firstSession.startThread(threadParams({ ephemeral: false }));
  threadId = thread.id;
  console.log(`Created persistent thread: ${thread.id}`);
  try {
    const answer = await withRetry("initial ask()", async () => await thread.ask("Reply with exactly FIRST."));
    console.log(`First answer: ${answer.trim()}`);
    initialTurnCompleted = true;
  } catch (error) {
    if (error instanceof TurnFailedError) {
      console.log(`Initial turn failed: ${error.message}`);
    }
    if (!(error instanceof TurnFailedError)) {
      throw error;
    }
  }
} finally {
  await firstSession.close();
}

if (!initialTurnCompleted) {
  console.log("Skipping resume because the initial turn did not complete successfully.");
} else {
console.log("Closed the first session. Reconnecting with a fresh session.");

const secondSession = await Session.create({
  approvalPolicy: ApprovalPolicy.autoAccept(),
  clientInfo: CLIENT_INFO,
});

try {
  try {
    const resumed = await secondSession.resumeThread(threadId);
    const snapshot = await secondSession.readThread(resumed.id, true);
    console.log(`Turns already on thread: ${snapshot.turns.length}`);

    try {
      const answer = await withRetry("resumed ask()", async () => await resumed.ask("Reply with exactly SECOND."));
      console.log(`Second answer: ${answer.trim()}`);
    } catch (error) {
      if (error instanceof TurnFailedError) {
        console.log(`Resumed turn failed: ${error.message}`);
      } else {
        throw error;
      }
    }
  } catch (error) {
    if (error instanceof ProtocolClientError && error.code === -32600) {
      console.log(`Resume is not available on this local codex app-server instance: ${error.message}`);
    } else {
      throw error;
    }
  }
} finally {
  await secondSession.close();
}
}
