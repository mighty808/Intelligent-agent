import asyncio
import random
from datetime import datetime

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour


class DisasterEnvironment:
    """
    Simulated environment for disaster monitoring.
    Generates changing environmental conditions and flags events.
    """

    def __init__(self, seed: int | None = None):
        if seed is not None:
            random.seed(seed)

        # Baseline conditions (feel free to adjust)
        self.water_level_cm = 15.0
        self.temperature_c = 29.0
        self.smoke_ppm = 3.0
        self.tremor_index = 0.5  # 0–10 scale

    def step(self) -> dict:
        """Update environment values and return a new percept snapshot."""
        # Random drift (simple but valid for Lab 2)
        self.water_level_cm += random.uniform(-2, 6)
        self.temperature_c += random.uniform(-0.5, 1.0)
        self.smoke_ppm += random.uniform(-1, 8)
        self.tremor_index += random.uniform(-0.2, 1.2)

        # Clamp to realistic ranges
        self.water_level_cm = max(0, min(self.water_level_cm, 200))
        self.temperature_c = max(10, min(self.temperature_c, 60))
        self.smoke_ppm = max(0, min(self.smoke_ppm, 500))
        self.tremor_index = max(0, min(self.tremor_index, 10))

        return {
            "water_level_cm": round(self.water_level_cm, 1),
            "temperature_c": round(self.temperature_c, 1),
            "smoke_ppm": round(self.smoke_ppm, 1),
            "tremor_index": round(self.tremor_index, 2),
        }

    def detect_event(self, percept: dict) -> dict | None:
        """
        Detect disaster events from percepts and return an event object if any.
        Severity levels: LOW, MODERATE, HIGH, CRITICAL
        """

        # Simple rule-based detection (good for Lab 2)
        flood_score = percept["water_level_cm"]
        fire_score = percept["smoke_ppm"] + max(0, (percept["temperature_c"] - 35) * 2)
        quake_score = percept["tremor_index"] * 10

        # Pick the dominant hazard
        hazard_scores = {
            "FLOOD": flood_score,
            "FIRE": fire_score,
            "EARTHQUAKE": quake_score,
        }

        hazard = max(hazard_scores, key=hazard_scores.get)
        score = hazard_scores[hazard]

        # Thresholds for event creation
        if hazard == "FLOOD" and score < 40:
            return None
        if hazard == "FIRE" and score < 80:
            return None
        if hazard == "EARTHQUAKE" and score < 35:
            return None

        # Map score to severity
        severity = self._severity_from_score(score)

        return {
            "event_type": hazard,
            "severity": severity,
            "score": round(score, 1),
            "percept": percept,
        }

    @staticmethod
    def _severity_from_score(score: float) -> str:
        if score < 60:
            return "LOW"
        if score < 100:
            return "MODERATE"
        if score < 140:
            return "HIGH"
        return "CRITICAL"


class SensorAgent(Agent):
    class MonitorBehaviour(PeriodicBehaviour):
        async def run(self):
            env: DisasterEnvironment = self.agent.env
            percept = env.step()

            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            event = env.detect_event(percept)

            if event:
                log_line = (
                    f"[{timestamp}] EVENT={event['event_type']} "
                    f"SEVERITY={event['severity']} SCORE={event['score']} "
                    f"PERCEPT={event['percept']}\n"
                )
            else:
                log_line = f"[{timestamp}] NO_EVENT PERCEPT={percept}\n"

            # Print to terminal + append to file
            print(log_line.strip())
            with open(self.agent.log_file, "a", encoding="utf-8") as f:
                f.write(log_line)

    async def setup(self):
        print("SensorAgent starting... (Lab 2)")
        self.env = DisasterEnvironment()
        self.log_file = "lab2_event_logs.txt"

        # Write header once
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("\n--- LAB 2 EVENT LOG START ---\n")

        # Monitor every 5 seconds (change if your lab requires different timing)
        self.add_behaviour(self.MonitorBehaviour(period=5))


async def main():
    jid = "mighty808@xmpp.jp"
    password = "Paakwesi888"

    agent = SensorAgent(jid, password, verify_security=False)

    await agent.start()
    # run for 60 seconds then stop (change if needed)
    await asyncio.sleep(60)
    await agent.stop()
    print("SensorAgent stopped. Logs saved to lab2_event_logs.txt")


if __name__ == "__main__":
    asyncio.run(main())
