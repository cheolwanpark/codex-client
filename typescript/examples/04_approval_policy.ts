import {
  ApprovalPolicy,
  Session,
  approveCommand,
  clientInfo,
  declineFileChange,
  toolAnswers,
  toolCallFailure,
} from "../src/index.js";

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
  clientInfo: clientInfo("typescript-example", "0.1.0"),
});

try {
  const thread = await session.startEphemeralThread();
  const answer = await thread.ask("Tell me what approval policy the host is using.");
  console.log(answer);
} finally {
  await session.close();
}
