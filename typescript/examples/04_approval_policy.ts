import {
  ApprovalPolicy,
  Session,
  TurnFailedError,
  approveCommand,
  declineFileChange,
  toolAnswers,
  toolCallFailure,
} from "../src/index.js";
import { CLIENT_INFO, printSection, withRetry } from "./_common.js";

const session = await Session.create({
  approvalPolicy: ApprovalPolicy.custom({
    onCommandExecution: () => approveCommand(),
    onDynamicToolCall: () => toolCallFailure(),
    onFileChange: () => declineFileChange(),
    onToolRequestUserInput: (params) =>
      toolAnswers(
        Object.fromEntries(params.questions.map((question) => [question.id, []])),
      ),
  }),
  clientInfo: CLIENT_INFO,
});

try {
  printSection("Custom Approval Policy");
  const thread = await session.startEphemeralThread();
  try {
    const answer = await withRetry("ask()", async () => await thread.ask("Reply with exactly OK."));
    console.log(`Thread: ${thread.id}`);
    console.log(`Answer: ${answer.trim()}`);
    console.log("This prompt does not need approvals, but the custom policy is now wired into the session.");
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
