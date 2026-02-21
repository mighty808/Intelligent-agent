# Group Work Lab 4

This folder contains a minimal two-agent SPADE demo for a request/response rescue workflow. A Coordinator agent sends a rescue task request, and a Rescue agent interprets the request, triggers an action, and replies with a status update.

# Group Members
- Paakwesi Effah Aboagye - 11353372
- Kelvin Kweku Siaw Ashong - 11296303
- Abigail Ninsin - 11194673
- Sulemana Abubakar Saddique - 11355543
- 
- 
- 
- 



## Contents

- coordinator_agent.py: Sends a FIPA-ACL `request` message for a rescue task and waits for `inform` responses.
- rescue_agent.py: Receives rescue requests, selects an action based on the task type, and replies with a status update.
- lab4_message_logs.txt: Timestamped message logs produced by both agents.

## How It Works

1. `CoordinatorAgent` sends a request message with metadata:
   - performative: `request`
   - ontology: `rescue-task`
   - language: `en`
2. `RescueAgent` receives the request, parses the body to select an action (FIRE, FLOOD, EARTHQUAKE), and replies with:
   - performative: `inform`
   - ontology: `rescue-status`
   - language: `en`
3. Both agents log all sent and received messages to `lab4_message_logs.txt`.

## Requirements

- Python 3.10+ recommended
- SPADE (XMPP-based multi-agent framework)
- Valid XMPP accounts for both agents

Install SPADE:

```bash
pip install spade
```

## Configuration

Credentials are defined in each script:

- coordinator_agent.py
  - JID: `groupworklab4@xmpp.jp`
  - Password: `groupworklab4pass`
- rescue_agent.py
  - JID: `groupworklab4.2@xmpp.jp`
  - Password: `groupworklab4pass`

If you need to use your own XMPP accounts, update the `*_jid` and `*_pass` values in each script.

## Running the Demo

Open two terminals in this folder and run:

```bash
python rescue_agent.py
```

```bash
python coordinator_agent.py
```

Notes:
- Each agent runs for about 60 seconds, then stops automatically.
- The Coordinator sends one request on startup.
- You should see the request, action, and reply in the logs.

## Logs

All activity is appended to `lab4_message_logs.txt` with UTC timestamps. Each run inserts a header:

```
--- LAB 4 MESSAGE LOG START ---
```

## Customization Ideas

- Change the request body to test different actions:
  - `FIRE`, `FLOOD`, or `EARTHQUAKE`
- Add more ontologies or performatives to extend the protocol.
- Increase the runtime to allow multiple interactions.

## Troubleshooting

- If no messages are exchanged, verify both JIDs and passwords.
- Ensure the XMPP server allows client connections.
- If a message arrives with unexpected metadata, it will be logged as OTHER.

## License

This lab is provided for coursework and educational use.

