import asyncio
from datetime import datetime

from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State


def is_emergency(severity: str) -> bool:
    return severity in {"MODERATE", "HIGH", "CRITICAL"}


class Monitoring(State):
    async def run(self):
        print("[FSM] MONITORING: waiting for sensor report...")
        msg = await self.receive(timeout=10)

        if not msg or msg.get_metadata("ontology") != "sensor-report":
            self.set_next_state("MONITORING")
            return

        self.agent.last_report = msg.body
        self.set_next_state("ASSESSING")


class Assessing(State):
    async def run(self):
        print("[FSM] ASSESSING: parsing and classifying report...")

        # report format: timestamp|hazard|severity|score|details
        parts = (self.agent.last_report or "").split("|")
        if len(parts) < 5:
            print("[FSM] ASSESSING: bad report format -> back to MONITORING")
            self.set_next_state("MONITORING")
            return

        ts, hazard, severity, score, details = parts[0], parts[1], parts[2], parts[3], parts[4]

        self.agent.current_event = {
            "timestamp": ts,
            "hazard": hazard,
            "severity": severity,
            "score": score,
            "details": details,
        }

        print(f"[FSM] ASSESSING: hazard={hazard} severity={severity} score={score}")

        if is_emergency(severity):
            self.set_next_state("DISPATCHING")
        else:
            self.set_next_state("MONITORING")


class Dispatching(State):
    async def run(self):
        e = self.agent.current_event
        print("[FSM] DISPATCHING: selecting and executing response...")

        action_map = {
            "FLOOD": "Deploy sandbags; evacuate low-lying zones",
            "FIRE": "Dispatch fire team; isolate area; cut power supply",
            "EARTHQUAKE": "Send rescue team; initiate medical triage",
        }
        action = action_map.get(e["hazard"], "Dispatch general emergency response")

        line = (
            f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | ACTION | "
            f"{e['hazard']} | {e['severity']} | score={e['score']} | {action}\n"
        )
        print(line.strip())
        with open("lab3_execution_trace.txt", "a", encoding="utf-8") as f:
            f.write(line)

        await asyncio.sleep(3)  # simulate response time
        self.set_next_state("CONFIRMING")


class Confirming(State):
    async def run(self):
        e = self.agent.current_event
        print("[FSM] CONFIRMING: logging completion and resetting...")

        line = (
            f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | DONE | "
            f"{e['hazard']} | {e['severity']} | score={e['score']} | {e['details']}\n"
        )
        print(line.strip())
        with open("lab3_execution_trace.txt", "a", encoding="utf-8") as f:
            f.write(line)

        self.agent.last_report = None
        self.agent.current_event = None
        self.set_next_state("MONITORING")


class RescueFSMAgent(Agent):
    async def setup(self):
        print("RescueFSMAgent started (Lab 3).")
        self.last_report = None
        self.current_event = None

        # trace file header
        with open("lab3_execution_trace.txt", "a", encoding="utf-8") as f:
            f.write("\n--- LAB 3 EXECUTION TRACE START ---\n")

        fsm = FSMBehaviour()
        fsm.add_state("MONITORING", Monitoring(), initial=True)
        fsm.add_state("ASSESSING", Assessing())
        fsm.add_state("DISPATCHING", Dispatching())
        fsm.add_state("CONFIRMING", Confirming())

        fsm.add_transition("MONITORING", "MONITORING")
        fsm.add_transition("MONITORING", "ASSESSING")
        fsm.add_transition("ASSESSING", "MONITORING")
        fsm.add_transition("ASSESSING", "DISPATCHING")
        fsm.add_transition("DISPATCHING", "CONFIRMING")
        fsm.add_transition("CONFIRMING", "MONITORING")

        self.add_behaviour(fsm)


async def main():
    # Use your working remote XMPP credentials:
    rescue_jid = "paakwesi8@xmpp.jp"
    rescue_pass = "Paakwesi@888"

    agent = RescueFSMAgent(rescue_jid, rescue_pass, verify_security=False)
    await agent.start()

    # Keep running long enough to receive sensor reports
    await asyncio.sleep(90)

    await agent.stop()
    print("RescueFSMAgent stopped. Trace saved to lab3_execution_trace.txt")


if __name__ == "__main__":
    asyncio.run(main())