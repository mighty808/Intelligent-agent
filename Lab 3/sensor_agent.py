import asyncio
import random
from datetime import datetime

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message


def severity_from_score(score: float) -> str:
    if score < 60:
        return "LOW"
    if score < 100:
        return "MODERATE"
    if score < 140:
        return "HIGH"
    return "CRITICAL"


class SensorAgent(Agent):
    class MonitorAndSend(PeriodicBehaviour):
        async def run(self):
            water = round(max(0, random.uniform(10, 180)), 1)
            temp = round(random.uniform(24, 50), 1)
            smoke = round(max(0, random.uniform(0, 250)), 1)
            tremor = round(random.uniform(0, 10), 2)

            flood_score = water
            fire_score = smoke + max(0, (temp - 35) * 2)
            quake_score = tremor * 10

            hazard_scores = {"FLOOD": flood_score, "FIRE": fire_score, "EARTHQUAKE": quake_score}
            hazard = max(hazard_scores, key=hazard_scores.get)
            score = round(hazard_scores[hazard], 1)
            severity = severity_from_score(score)

            ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            details = f"water={water},temp={temp},smoke={smoke},tremor={tremor}"
            report = f"{ts}|{hazard}|{severity}|{score}|{details}"

            msg = Message(to=self.agent.receiver_jid)
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "sensor-report")
            msg.body = report

            await self.send(msg)
            print(f"[SENSOR] sent -> {report}")

    async def setup(self):
        print("SensorAgent started (Lab 3).")
        # Send to the FSM agent JID
        self.receiver_jid = "paakwesi8@xmpp.jp"
        self.add_behaviour(self.MonitorAndSend(period=5))


async def main():
    sensor_jid = "mighty899@xmpp.jp"
    sensor_pass = "123456"

    agent = SensorAgent(sensor_jid, sensor_pass, verify_security=False)
    await agent.start()

    await asyncio.sleep(120)

    await agent.stop()
    print("SensorAgent stopped.")


if __name__ == "__main__":
    asyncio.run(main())