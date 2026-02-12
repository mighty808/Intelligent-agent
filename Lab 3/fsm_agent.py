import asyncio
from datetime import datetime

from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message


def is_emergency(severity: str) -> bool:
    return severity in {"MODERATE", "HIGH", "CRITICAL"}


class Monitoring(State):
    async def run(self):
        print("[FSM] State=MONITORING | Waiting for sensor report...")

        msg = await self.receive(timeout=10)
        if not msg:
            # stay in monitoring
            self.set_next_state("MONITORING")
            return

        if msg.get_metadata("ontology") != "sensor-report":
            self.set_next_state("MONITORING")
            return

        self.agent.last_report = msg.body
        self.set_next_state("ASSESSING")


class Assessing(State):
    async def run(self):
        print("[FSM] State=ASSESSING | Classifying report...")

        # Report format: timestamp|hazard|severity|score|details
        parts = (self.agent.last_report or "").split("|")
        if len(parts) < 5:
            print("[FSM] Bad report format -> returning to MONITORING")
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

        print(f"[FSM] Event classified: {hazard} severity={severity} score={score}")

        if is_emergency(severity):
            self.set_next_state("DISPATCHING")
        else:
            self.set_next_state("MONITORING")


class Dispatching(State):
    async def run(self):
        e = self.agent.current_event
        print("[FSM] State=DISPATCHING | Sending response action...")

        # Simulate an action decision (reactive)
        action = {
            "FLOOD": "Deploy sandbags + evacuate low zones",
            "FIRE": "Dispatch fire team + isolate area",
            "EARTHQUAKE": "Send rescue + medical triage",
        }.get(e["hazard"], "Dispatch general response")

        # Log action (could message another agent later)
        log_line = f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | ACTION | {e['hazard']} | {e['severity']} | {action}\n"
        print(log_line.strip())
        with open("lab3_execution_trace.txt", "a", encoding="utf-8") as f:
            f.write(log_line)

        # simulate work time
        await asyncio.sleep(3)
        self.set_next_state("CONFIRMING")


class Confirming(State):
    async def run(self):
        e = self.agent.current_event
        print("[FSM] State=CONFIRMING | Confirming completion + logging...")

        line = f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | DONE | {e['hazard']} | {e['severity']} | score={e['score']} | {e['details']}\n"
        print(line.strip())
        with open("lab3_execution_trace.txt", "a", encoding="utf-8") as f:
            f.write(line)

        self.set_next_state("MONITORING")


class RescueFSMAgent(Agent):
    async def setup(self):
        print("RescueFSMAgent starting... (Lab 3)")
        self.last_report = None
        self.current_event = None

        # write header once
        with open("lab3_execution_trace.txt", "a", encoding="utf-8") as f:
            f.write("\n--- LAB 3 EXECUTION TRACE START ---\n")

        fsm = FSMBehaviour()
        fsm.add_state(name="MONITORING", state=Monitoring(), initial=True)
        fsm.add_state(name="ASSESSING", state=Assessing())
        fsm.add_state(name="DISPATCHING", state=Dispatching())
        fsm.add_state(name="CONFIRMING", state=Confirming())

        fsm.add_transition(source="MONITORING", dest="MONITORING")
        fsm.add_transition(source="MONITORING", dest="ASSESSING")
        fsm.add_transition(source="ASSESSING", dest="MONITORING")
        fsm.add_transition(source="ASSESSING", dest="DISPATCHING")
        fsm.add_transition(source="DISPATCHING", dest="CONFIRMING")
        fsm.add_transition(source="CONFIRMING", dest="MONITORING")

        self.add_behaviour(fsm)


async def main():
    rescue_jid = "mighty808@xmpp.jp"
    rescue_pass = "Paakwesi888"

    agent = RescueFSMAgent(rescue_jid, rescue_pass, verify_security=False)
    await agent.start()
    await asyncio.sleep(70)
    await agent.stop()
    print("Rescue FSM stopped. Trace saved to lab3_execution_trace.txt")


if __name__ == "__main__":
    asyncio.run(main())
