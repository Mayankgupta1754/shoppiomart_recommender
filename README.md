# Shoppiomart Product Finder

A CrewAI project with **3 agents** that work one after another:

1. **Scout** searches Google Shopping (India) and picks real products.
2. **Writer** turns those products into listing copy in `report.md`.
3. **Notifier** sends only the product **names** to your phone with Pushover.

The scout can only use products that Serper actually returns. It does not make up product names. If Serper is down, the run stops before any agent starts.

---

## How it works

You give a category (default: wireless earbuds). Then each box runs in order, like an n8n workflow. Agent = who thinks. Tool = what it calls.

```mermaid
flowchart TB
    START([crewai run]) --> IN[Input: category]
    IN --> CHECK[Ping Serper<br/>POST google.serper.dev/shopping]
    CHECK -->|fail| STOP([Stop. No agents.])
    CHECK -->|ok| KICK[Start sequential crew]

    KICK --> SCOUT[Agent: trend_scout]
    SCOUT --> T1{{Tool: serper_shopping_search}}
    T1 --> API1[Serper → Google Shopping India]
    API1 --> PICK[Keep 6–8 products<br/>drop category pages]
    PICK --> LIST[Product list<br/>name · price · site]

    LIST --> WRITER[Agent: listing_writer<br/>no tool]
    WRITER --> MD[Write report.md<br/>copy + Names block]

    MD --> DISP[Agent: pushover_dispatcher]
    DISP --> T2{{Tool: pushover_send_names}}
    T2 --> API2[Pushover API]
    API2 --> PHONE([Phone: names only])
```

| Who | Job | Tool |
|---|---|---|
| Scout | Find 6–8 products (name, price, site) | Serper Shopping |
| Writer | Write titles, descriptions, bullets | none |
| Notifier | Push the names list | Pushover |

---

## How to run

```
cd shoppiomart_recommender
uv sync
crewai run
```

Python 3.10–3.13. Put this in `.env`:

```
OPENAI_API_KEY=
SERPER_API_KEY=
PUSHOVER_TOKEN=
PUSHOVER_USER=
```

`Serper_API_KEY`, `PUSHOVER_APP_TOKEN`, and `PUSHOVER_USER_KEY` also work.

---

## Example run

**Traces** — one timeline: scout searched → writer wrote → names were sent.

![CrewAI traces](assets/traces.png)

**Phone** — title is `Shoppiomart`. Body is a numbered list of names only.

![Pushover notification](assets/notification.png)

---

## What you get

- `report.md` — listing copy plus a Names list at the end
- CrewAI traces of the run
- A Pushover message on your device

---

## Project files

```
src/shioppiomart_recommender/
  crew.py                 the 3 agents and 3 tasks
  main.py                 start the crew; check Serper first
  config/agents.yaml
  config/tasks.yaml
  tools/
    serper_tools.py       Google Shopping search
    pushover_tool.py      send names to the phone
    http.py               HTTP calls with a timeout (so a dead API does not hang)
```
