import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour


class TestAgent(Agent):
    class StartBehaviour(OneShotBehaviour):
        async def run(self):
            print(f"Connected successfully as: {self.agent.jid}")
            print("Remote XMPP server connection verified (Lab 1).")

    async def setup(self):
        print("Setting up agent...")
        self.add_behaviour(self.StartBehaviour())


async def main():
    jid = "mighty808@xmpp.jp"
    password = "Paakwesi888"

    agent = TestAgent(jid, password, verify_security=False)

    try:
        print("Connecting to remote XMPP server (xmpp.jp)...")
        await asyncio.wait_for(agent.start(), timeout=15)
        print("Agent started.")
        await asyncio.sleep(10)
    except asyncio.TimeoutError:
        print("Connection timed out. Check internet access and credentials.")
    except Exception as e:
        print(f"Failed: {type(e).__name__}: {e}")
    finally:
        try:
            await agent.stop()
        except Exception:
            pass
        print("Agent stopped. Done.")


if __name__ == "__main__":
    asyncio.run(main())
