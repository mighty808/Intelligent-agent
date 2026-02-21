import asyncio
from datetime import datetime, timezone

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

LOG_FILE = "lab4_message_logs.txt"


def log(line: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"[{ts}] {line}\n"
    print(entry.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


class RescueAgent(Agent):
    class ReceiveRequest(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if not msg:
                return

            # SPADE get_metadata() in your version takes only ONE argument (key)
            perf = (msg.get_metadata("performative") or "").lower()
            onto = msg.get_metadata("ontology") or ""
            body = msg.body or ""

            if perf == "request" and onto == "rescue-task":
                log(f"RESCUE <- RECEIVED REQUEST from {str(msg.sender)} | body='{body}'")

                # Trigger action from parsed content
                action = "DISPATCH TEAM"
                if "FIRE" in body.upper():
                    action = "DISPATCH FIRE UNIT"
                elif "FLOOD" in body.upper():
                    action = "DISPATCH FLOOD RESPONSE UNIT"
                elif "EARTHQUAKE" in body.upper():
                    action = "DISPATCH SEARCH & RESCUE UNIT"

                log(f"RESCUE -> ACTION TRIGGERED: {action}")

                # Reply with INFORM (FIPA-ACL performative)
                reply = Message(to=str(msg.sender))
                reply.set_metadata("performative", "inform")
                reply.set_metadata("ontology", "rescue-status")
                reply.set_metadata("language", "en")
                reply.body = f"STATUS: {action} completed; outcome=SUCCESS"

                await self.send(reply)
                log(f"RESCUE -> SENT INFORM to {str(msg.sender)} | body='{reply.body}'")

            else:
                log(
                    f"RESCUE <- RECEIVED OTHER msg from {str(msg.sender)} "
                    f"| performative={perf} ontology={onto} body='{body}'"
                )

    async def setup(self):
        log("RescueAgent started (Lab 4).")
        self.add_behaviour(self.ReceiveRequest())


async def main():
    rescue_jid = "groupworklab4.2@xmpp.jp"
    rescue_pass = "groupworklab4pass"

    agent = RescueAgent(rescue_jid, rescue_pass, verify_security=False)
    await agent.start()

    await asyncio.sleep(60)

    await agent.stop()
    log("RESCUE stopped.")


if __name__ == "__main__":
    asyncio.run(main())