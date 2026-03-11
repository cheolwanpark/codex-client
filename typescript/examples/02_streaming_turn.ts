import { ApprovalPolicy, Session, TurnFailedError } from "../src/index.js";
import { CLIENT_INFO, printSection, withRetry } from "./_common.js";

const session = await Session.create({
  approvalPolicy: ApprovalPolicy.autoAccept(),
  clientInfo: CLIENT_INFO,
});

try {
  printSection("Streaming Turn Events");
  const thread = await session.startEphemeralThread();
  const prompt = "Plan a short explanation of this SDK, then explain it in one paragraph.";
  try {
    await withRetry("streaming turn", async () => {
      const turn = await thread.startTurn(prompt);
      let sawPlanUpdate = false;

      console.log(`Thread: ${thread.id}`);
      console.log(`Turn: ${turn.id}`);
      console.log(`Prompt: ${prompt}`);
      console.log("\nAgent stream:");

      for await (const event of turn) {
        if (event.type === "agent_message_delta") {
          process.stdout.write(event.delta);
          continue;
        }

        if (event.type === "plan_updated") {
          sawPlanUpdate = true;
          process.stdout.write("\n\n[plan_updated]\n");
          if (event.explanation !== null) {
            process.stdout.write(`Explanation: ${event.explanation}\n`);
          }
          for (const step of event.plan) {
            process.stdout.write(`- ${step.status}: ${step.step}\n`);
          }
          continue;
        }

        if (event.type === "completed") {
          process.stdout.write(`\n\n[completed] status=${event.turn.status}\n`);
        }
      }

      if (!sawPlanUpdate) {
        console.log("[no plan updates were emitted for this prompt]");
      }

      console.log("\nBuffered final text:");
      console.log((await turn.text()).trim());
    });
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
