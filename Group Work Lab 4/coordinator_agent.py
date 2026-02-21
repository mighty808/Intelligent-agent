import asyncio
from datetime import datetime, timezone

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message

LOG_FILE = "lab4_message_logs.txt"


def log(line: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"[{ts}] {line}\n"
    print(entry.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


class CoordinatorAgent(Agent):
    class SendRequest(OneShotBehaviour):
        async def run(self):
            msg = Message(to=self.agent.rescue_jid)
            msg.set_metadata("performative", "request")
            msg.set_metadata("ontology", "rescue-task")
            msg.set_metadata("language", "en")
            msg.body = "TASK: Respond to FLOOD at Zone-A; severity=HIGH"

            await self.send(msg)
            log(f"COORDINATOR -> SENT REQUEST to {self.agent.rescue_jid} | body='{msg.body}'")

    class ReceiveInform(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if not msg:
                return

            perf = (msg.get_metadata("performative") or "").lower()
            onto = msg.get_metadata("ontology") or ""
            body = msg.body or ""

            if perf == "inform" and onto == "rescue-status":
                log(f"COORDINATOR <- RECEIVED INFORM from {str(msg.sender)} | body='{body}'")
            else:
                log(
                    f"COORDINATOR <- RECEIVED OTHER msg from {str(msg.sender)} "
                    f"| performative={perf} ontology={onto} body='{body}'"
                )

    async def setup(self):
        # Header
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\n--- LAB 4 MESSAGE LOG START ---\n")

        # ✅ Send REQUEST to RescueAgent
        self.rescue_jid = "groupworklab4.2@xmpp.jp"

        self.add_behaviour(self.SendRequest())
        self.add_behaviour(self.ReceiveInform())


async def main():
    coordinator_jid = "groupworklab4@xmpp.jp"
    coordinator_pass = "groupworklab4pass"

    agent = CoordinatorAgent(coordinator_jid, coordinator_pass, verify_security=False)
    await agent.start()

    await asyncio.sleep(60)

    await agent.stop()
    log("COORDINATOR stopped.")


if __name__ == "__main__":
    asyncio.run(main())